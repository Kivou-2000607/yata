"""
Copyright 2019 kivou.2000607@gmail.com

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

import json
from datetime import timedelta

from django.core.cache import cache
from django.db.models import Count, Q
from django.db.models.functions import TruncDay, TruncHour
from django.shortcuts import render
from django.utils import timezone

from setup.models import ApiCallLog


def api_stats(request):
    now = timezone.now()

    # Cleanup entries older than 30 days, at most once per hour
    if not cache.get("api_stats_cleanup"):
        ApiCallLog.objects.filter(timestamp__lt=now - timedelta(days=30)).delete()
        cache.set("api_stats_cleanup", True, 3600)

    def summarize(qs):
        return qs.aggregate(
            total=Count("id"),
            errors=Count("id", filter=Q(is_error=True)),
        )

    hour_start = now.replace(minute=0, second=0, microsecond=0)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    this_hour = summarize(ApiCallLog.objects.filter(timestamp__gte=hour_start))
    today = summarize(ApiCallLog.objects.filter(timestamp__gte=day_start))
    this_week = summarize(ApiCallLog.objects.filter(timestamp__gte=now - timedelta(days=7)))
    this_month = summarize(ApiCallLog.objects.filter(timestamp__gte=now - timedelta(days=30)))

    hourly = list(
        ApiCallLog.objects.filter(timestamp__gte=now - timedelta(hours=24))
        .annotate(hour=TruncHour("timestamp"))
        .values("hour")
        .annotate(total=Count("id"), errors=Count("id", filter=Q(is_error=True)))
        .order_by("hour")
    )

    daily = list(
        ApiCallLog.objects.filter(timestamp__gte=now - timedelta(days=30))
        .annotate(day=TruncDay("timestamp"))
        .values("day")
        .annotate(total=Count("id"), errors=Count("id", filter=Q(is_error=True)))
        .order_by("day")
    )

    top_sections = list(
        ApiCallLog.objects.filter(timestamp__gte=now - timedelta(days=30)).values("section").annotate(total=Count("id"), errors=Count("id", filter=Q(is_error=True))).order_by("-total")[:10]
    )

    # Format chart data for Google Charts
    hourly_chart = [["Hour", "Calls", "Errors"]]
    for h in hourly:
        hourly_chart.append([h["hour"].strftime("%H:%M"), h["total"], h["errors"]])

    daily_chart = [["Day", "Calls", "Errors"]]
    for d in daily:
        daily_chart.append([d["day"].strftime("%b %d"), d["total"], d["errors"]])

    context = {
        "this_hour": this_hour,
        "today": today,
        "this_week": this_week,
        "this_month": this_month,
        "hourly": hourly,
        "daily": daily,
        "top_sections": top_sections,
        "hourly_chart_json": json.dumps(hourly_chart),
        "daily_chart_json": json.dumps(daily_chart),
        "now": now,
    }

    return render(request, "api-stats.html", context)
