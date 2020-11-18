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

from django.shortcuts import render
# from django.http import HttpResponse
# from django.utils import timezone
# from django.db import connection
# from django.views.decorators.csrf import csrf_exempt
# from django.core.paginator import Paginator

from company.models import CompanyDescription
from company.models import Company

from yata.handy import *
from player.models import Player
from player.functions import updatePlayer

# import json


def index(request):
    try:
        player = getPlayer(request.session.get("player", {}).get("tId", -1))

        context = {"player": player, "compcat": True, "view": {"index": True}}
        page = 'company/content-reload.html' if request.method == 'POST' else 'company.html'
        return render(request, page, context)

    except Exception as e:
        return returnError(exc=e, session=request.session)

def browse(request):
    try:
        player = getPlayer(request.session.get("player", {}).get("tId", -1))

        # get all companies
        companies = CompanyDescription.objects.order_by("name")

        if request.POST.get("type") == "company-details":
            company_details = companies.filter(tId=request.POST.get("company_id")).first()
            print(company_details)
            return render(request, "company/browse/details.html", {"player": player, "company_details": company_details})

        page = 'company/content-reload.html' if request.method == 'POST' else 'company.html'
        context = {"player": player, "companies": companies,"compcat": True, "view": {"browse": True}}
        return render(request, page, context)

    except Exception as e:
        return returnError(exc=e, session=request.session)

def supervise(request):
    try:
        player = getPlayer(request.session.get("player", {}).get("tId", -1))

        # get company
        company = Company.objects.filter(tId=player.companyId).first()
        if company is None and not player.companyDi:
            context = {"player": player, "compcat": True, "view": {"supervise": True}}
            page = 'company/content-reload.html' if request.method == 'POST' else 'company.html'
            return render(request, page, context)
        elif company is None and player.companyDi:
            updatePlayer(player)
            company = Company.objects.filter(tId=player.companyId).first()
            company.update_info()

        # add employees requirements and potential efficiency on the fly
        company_positions = company.company_description.position_set.all()
        employees = company.employee_set.all().order_by("-effectiveness_total")
        for employee in employees:
            position = company_positions.filter(name=employee.position).first()
            employee.man_required = 0 if position is None else position.man_required
            employee.int_required = 0 if position is None else position.int_required
            employee.end_required = 0 if position is None else position.end_required
            t = employee.effectiveness_total
            n = employee.effectiveness_addiction + employee.effectiveness_inactivity
            employee.effectiveness_potential = 100 * (t + n) / t

        context = {"player": player,
                   "company": company,
                   "employees": employees,
                   "compcat": True,
                   "view": {"supervise": True}}
        page = 'company/content-reload.html' if request.method == 'POST' else 'company.html'
        return render(request, page, context)

    except Exception as e:
        return returnError(exc=e, session=request.session)
