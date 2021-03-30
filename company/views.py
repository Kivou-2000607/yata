"""
Copyright 2020 kivou.2000607@gmail.com

This file is part of yata.

    yata is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    yata is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with yata. If not, see <https://www.gnu.org/licenses/>.
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.forms.models import model_to_dict

# cache and rate limit
from django.views.decorators.cache import cache_page
from ratelimit.decorators import ratelimit
from ratelimit.core import get_usage, is_ratelimited

import math
import json
import scipy
import numpy

from company.models import CompanyDescription
from company.models import Company

from yata.handy import *
from player.models import Player
from player.functions import updatePlayer


def index(request):
    try:
        player = getPlayer(request.session.get("player", {}).get("tId", -1))

        if player.companyId:
            return redirect('company:supervise')
        else:
            return redirect('company:browse')

    except Exception as e:
        return returnError(exc=e, session=request.session)

def browse(request):
    try:
        player = getPlayer(request.session.get("player", {}).get("tId", -1))

        # get all companies
        companies = CompanyDescription.objects.order_by("name")

        if request.POST.get("type") == "company-details":
            company_details = companies.filter(tId=request.POST.get("company_id")).first()
            return render(request, "company/browse/details.html", {"player": player, "company_details": company_details})

        page = 'company/content-reload.html' if request.method == 'POST' else 'company.html'
        context = {"player": player, "companies": companies,"compcat": True, "view": {"browse": True}}
        return render(request, page, context)

    except Exception as e:
        return returnError(exc=e, session=request.session)

def supervise(request):
    try:
        player = getPlayer(request.session.get("player", {}).get("tId", -1))
        message = False

        # get company
        company = Company.objects.filter(tId=player.companyId).first()
        if company is None and not player.companyDi:
            context = {"player": player, "compcat": True, "view": {"supervise": True}}
            page = 'company/content-reload.html' if request.method == 'POST' else 'company.html'
            return render(request, page, context)
        elif company is None:
            updatePlayer(player)
            company = Company.objects.filter(tId=player.companyId).first()
            error, message = company.update_info()

        # update company
        if ((tsnow() - company.timestamp) > 3600 or request.POST.get("type") == "update-data"):
            error, message = company.update_info()

        # add employees requirements and potential efficiency on the fly
        company_positions = company.company_description.position_set.all()
        employees = company.employee_set.all().order_by("-effectiveness_total")

        # prepare effectiveness matrix
        ws_eff_matrix = []
        company.effectiveness_ws_act = 0
        hrm = 1.1 if company.director_hrm else 0.9

        # modify employees positions on the fy if simu
        employees_simu = {}
        if request.POST.get("type", False) == "employees-simu":
            for k, v in json.loads(request.POST.get("employees_position_simu", "{}")).items():
                e = employees.filter(tId=k).first()
                if e is None:
                    continue
                if e.position != v:
                    employees_simu[k] = v

        # get all current positions
        positions = [company_positions.filter(name=employees_simu.get(str(e.tId), e.position)).first() for e in employees]

        # loop over employees
        now = tsnow()
        for employee in employees:
            employee.last_action_relative = now - employee.last_action
            employee.position = employees_simu.get(str(employee.tId), employee.position)
            position = company_positions.filter(name=employee.position).first()
            employee.man_required = 0 if position is None else position.man_required
            employee.int_required = 0 if position is None else position.int_required
            employee.end_required = 0 if position is None else position.end_required

            # compute ws_eff matrix (each row is an employee, each column is a position)
            sta = [employee.manual_labor, employee.intelligence, employee.endurance]
            ws_eff_matrix_row = []
            for p in positions:
                # compute S and P
                req = [p.man_required, p.int_required, p.end_required]

                # test if not unassined
                if sum(req):
                    Pi = req.index(max(req))
                    Si = req.index(min([s for s in req if s]))
                    P = hrm * sta[Pi] / float(req[Pi])
                    S = hrm * sta[Si] / float(req[Si])
                    ws_eff = min(45, 45 * P) + 5*math.log2(max(P, 1)) + min(45, 45 * S) + 5*math.log2(max(S, 1)) + employee.effectiveness_merits
                else:
                    ws_eff = 0

                ws_eff_matrix_row.append(ws_eff)

                # use simu value if necessary
                if p.name == employee.position and employees_simu.get(str(employee.tId), False):
                    employee.effectiveness_total -= employee.effectiveness_working_stats
                    employee.effectiveness_working_stats = ws_eff
                    employee.effectiveness_total += employee.effectiveness_working_stats
                    employee.simu = True

            t = employee.effectiveness_total
            n = employee.effectiveness_addiction + employee.effectiveness_inactivity
            employee.effectiveness_potential = 100 * (t + n) / max(t, 1)
            company.effectiveness_ws_act += employee.effectiveness_working_stats

            ws_eff_matrix.append(ws_eff_matrix_row)
        try:
            ws_eff_matrix = numpy.array(ws_eff_matrix)
            row_ind, col_ind = scipy.optimize.linear_sum_assignment(ws_eff_matrix, maximize=True)
            company.effectiveness_ws_max = round(ws_eff_matrix[row_ind, col_ind].sum())
            company.effectiveness_ws_err = round(100 * (company.effectiveness_ws_act)/company.effectiveness_ws_max)
            company.employees_suggestion = [[list(employees)[i].name, list(employees)[i].tId, positions[j].name, ws_eff_matrix[i, j], list(employees)[i].effectiveness_working_stats] for i, j in zip(row_ind, col_ind)]
        except BaseException as e:
            print(e)
            company.effectiveness_ws_max = 0
            company.effectiveness_ws_err = 0
            company.employees_suggestion = []
            pass

        # send employees if simu
        if request.POST.get("type", False) == "employees-simu":
            context = {"company": company, "company_positions": company_positions, "employees": employees}
            return render(request, "company/supervise/employees.html", context)

        # send employees if show details
        if request.POST.get("type", False) == "show-details":
            company_data = company.companydata_set.filter(timestamp=request.POST.get("timestamp")).first()
            if company_data is not None:
                employees = json.loads(company_data.employees)
            return render(request, "company/supervise/details.html", {"company_data": company_data, "employees": employees})

        # get company data
        company_data = company.companydata_set.all().order_by("-timestamp")
        company_data_p = Paginator(company_data, 7)
        if request.GET.get('page_d') is not None:
            return render(request, "company/supervise/logs.html", {"company_data_p": company_data_p.get_page(request.GET.get('page_d'))})

        # get company stock
        company_stock = company.companystock_set.all().order_by("-timestamp")
        company_stock_p = Paginator(company_stock, 25)
        if request.GET.get('page_s') is not None:
            return render(request, "company/supervise/stock.html", {"company_stock_p": company_stock_p.get_page(request.GET.get('page_s'))})

        # create employee graph
        # current employees [id, name]
        employee_graph_headers = [[str(e.tId), f'{e.name} [{e.tId}]'] for e in employees]
        employee_graph_data = []
        for data in company_data:
            d = json.loads(data.employees)
            tmp_data = [data.timestamp, []]
            for e_id, e_name in employee_graph_headers:
                to_append = [d.get(e_id, {}).get("effectiveness_total", "undefined"), d.get(e_id, {}).get("position", "undefined")]
                if to_append[0] == 0:
                    to_append[0] = "undefined"
                tmp_data[1].append(to_append)

            employee_graph_data.append(tmp_data)

        employees_graph = {"header": employee_graph_headers, "data": employee_graph_data}

        company.save()

        context = {"player": player,
                   "company": company,
                   "company_positions": company_positions,
                   "company_data": company_data,
                   "company_data_p": company_data_p.get_page(1),
                   "company_stock": company_stock,
                   "company_stock_p": company_stock_p.get_page(1),
                   "employees": employees,
                   "employees_graph": employees_graph,
                   "compcat": True,
                   "view": {"supervise": True}}

        if message:
            sub = "Sub" if request.method == 'POST' else ""
            if error:
                if "apiErrorString" in message:
                    context["errorMessage" + sub] = f'Company: API error {message["apiErrorString"]}, data not updated'
                elif "error" in message:
                    context["errorMessage" + sub] = f'Company: {message["error"]}'
            else:
                context["validMessage" + sub] = "Company data has been updated."

        page = 'company/content-reload.html' if request.method == 'POST' else 'company.html'
        return render(request, page, context)

    except Exception as e:
        return returnError(exc=e, session=request.session)


# @cache_page(60*10)
# def ws(request):
#     payload = {"effectiveness": []}
#     for company in Company.objects.all():
#         if not company.director:
#             continue
#
#         # add employees requirements and potential efficiency on the fly
#         company_positions = company.company_description.position_set.all()
#         employees = company.employee_set.all().order_by("-effectiveness_total")
#
#         manager = employees.filter(position="Manager").first()
#         manager_effectiveness = manager.effectiveness_total if manager is not None else 0
#         for employee in employees:
#             position = company_positions.filter(name=employee.position).first()
#             if position is None:
#                 continue
#
#             employee.man_required = 0 if position is None else position.man_required
#             employee.int_required = 0 if position is None else position.int_required
#             employee.end_required = 0 if position is None else position.end_required
#             t = employee.effectiveness_total
#             n = employee.effectiveness_addiction + employee.effectiveness_inactivity
#             # compute theoretical efficiency
#             req = [employee.man_required, employee.int_required, employee.end_required]
#             sta = [employee.manual_labor, employee.intelligence, employee.endurance]
#             if sum(req):
#                 Pi = req.index(max(req))
#                 Si = req.index(min([s for s in req if s]))
#                 P = sta[Pi] / float(req[Pi])
#                 S = sta[Si] / float(req[Si])
#
#                 ws = {
#                       "working_stats": employee.effectiveness_working_stats,
#                       "settled_in": employee.effectiveness_settled_in,
#                       "director_education": employee.effectiveness_director_education,
#                       "addiction": employee.effectiveness_addiction,
#                       "inactivity": employee.effectiveness_inactivity,
#                       "management": employee.effectiveness_management,
#                       "book_bonus": employee.effectiveness_book_bonus,
#                       "merits": employee.effectiveness_merits,
#                       "effectiveness_total": employee.effectiveness_total,
#                       "manager_effectiveness": manager_effectiveness,
#                       "position": employee.position,
#                       "director_hrm": company.director_hrm,
#                       "primary_ratio": P,
#                       "secondary_ratio": S,
#                       "company_id": company.company_description.tId,
#                       "company_name": company.company_description.name
#                       }
#
#                 payload["effectiveness"].append(ws)
#
#     return JsonResponse(payload, status=200)
