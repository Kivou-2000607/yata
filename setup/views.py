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
from django.db.models.functions import TruncDay, TruncHour, TruncMinute
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

    minutely = list(
        ApiCallLog.objects.filter(timestamp__gte=now - timedelta(hours=1))
        .annotate(minute=TruncMinute("timestamp"))
        .values("minute")
        .annotate(total=Count("id"), errors=Count("id", filter=Q(is_error=True)))
        .order_by("minute")
    )

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

    error_code_labels = {
        0: "Unknown / unreachable",
        1: "Key is empty",
        2: "Incorrect key",
        3: "Wrong type",
        4: "Wrong fields",
        5: "Too many requests",
        6: "Incorrect ID",
        7: "Incorrect ID-entity relation",
        8: "IP block",
        9: "API disabled",
        10: "Key owner in federal jail",
        11: "Key change error",
        12: "Key read error",
        13: "Key disabled due to inactivity",
        14: "Daily read limit reached",
        15: "Temporary error",
        16: "Access level too low",
        17: "Backend error",
        18: "API key paused by owner",
    }

    error_codes = list(
        ApiCallLog.objects.filter(timestamp__gte=now - timedelta(days=30), is_error=True)
        .values("error_code")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    for e in error_codes:
        e["label"] = error_code_labels.get(e["error_code"], "HTTP error") if e["error_code"] is not None else "Unknown"

    # Format chart data for Google Charts
    minutely_chart = [["Minute", "Calls", "Errors"]]
    for m in minutely:
        minutely_chart.append([m["minute"].strftime("%H:%M"), m["total"], m["errors"]])

    hourly_chart = [["Hour", "Calls", "Errors"]]
    for h in hourly:
        hourly_chart.append([h["hour"].strftime("%H:%M"), h["total"], h["errors"]])

    daily_chart = [["Day", "Calls", "Errors"]]
    for d in daily:
        daily_chart.append([d["day"].strftime("%b %d"), d["total"], d["errors"]])

    context = {
        "minutely": minutely,
        "minutely_chart_json": json.dumps(minutely_chart),
        "this_hour": this_hour,
        "today": today,
        "this_week": this_week,
        "this_month": this_month,
        "hourly": hourly,
        "daily": daily,
        "top_sections": top_sections,
        "error_codes": error_codes,
        "hourly_chart_json": json.dumps(hourly_chart),
        "daily_chart_json": json.dumps(daily_chart),
        "now": now,
    }

    return render(request, "api-stats.html", context)
