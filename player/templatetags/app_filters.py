# Copyright 2019 kivou.2000607@gmail.com
#
# This file is part of yata.
#
#     yata is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     any later version.
#
#     yata is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with yata. If not, see <https://www.gnu.org/licenses/>.

import math
import re
import os

from django import template
from django.utils.html import escape, format_html
from django.conf import settings

register = template.Library()


@register.filter(name="ts2date")
def ts2date(timestamp, fmt=None):
    import datetime

    import pytz

    if not timestamp:
        return "N/A"

    try:
        d = datetime.datetime.fromtimestamp(int(timestamp), tz=pytz.UTC)
    except BaseException:
        d = datetime.datetime.fromtimestamp(0, tz=pytz.UTC)

    # return "{:04d}/{:02d}/{:02d} {:02d}:{:02d}".format(d.year, d.month, d.day, d.hour, d.minute)
    if fmt is None:
        # return d.strftime("%Y/%m/%d %I:%M %p")
        return d.strftime("%Y/%m/%d %H:%M")
    else:
        return d.strftime(fmt)


@register.filter(name="ts2time")
def ts2time(timestamp, fmt=None):
    try:
        d = timestamp // 86400
        h = (timestamp - 86400 * d) // 3600 % 24
        m = (timestamp - 3600 * h) // 60 % 60
        s = (timestamp - 60 * m) % 60

        if fmt == "DHM":
            return "{} days {:02d} hrs {:02d} mins".format(d, h, m)
        elif fmt == "DH":
            return "{} days {:02d} hrs".format(d, h)
        if d:
            return "{} days {:02d} hrs {:02d} mins {:02d} s".format(d, h, m, s)
        elif h:
            return "{} hrs {:02d} mins {:02d} s".format(h, m, s)
        elif m:
            return "{} mins {:02d} s".format(m, s)
        else:
            return "{} s".format(s)
    except BaseException as e:
        return str(e)


@register.filter(name="ts2ago")
def ts2ago(timestamp):
    if not str(timestamp).isdigit():
        return "-"

    timestamp = int(timestamp)
    t = timestamp // 86400
    if t:
        s = "" if t == 1 else "s"
        return "{} day{} ago".format(t, s)
    t = (timestamp - 86400 * t) // 3600 % 24
    if t:
        s = "" if t == 1 else "s"
        return "{} hr{} ago".format(t, s)
    t = (timestamp - 3600 * t) // 60 % 60
    if t:
        s = "" if t == 1 else "s"
        return "{} min{} ago".format(t, s)
    t = (timestamp - 60 * t) % 60
    s = "" if t == 1 else "s"
    return "{} sec{} ago".format(t, s)


@register.filter(name="percent")
def percent(fl):
    try:
        return f"{fl * 100:.0f}%"
    except BaseException:
        return "-"


@register.filter(name="format")
def format(value, fmt):
    return fmt.format(value)


@register.filter(name="cmg")
def cmg(value):
    n = int(value)
    if n < 0:
        return format_html('<span style="opacity: 0.3;" title="Member not in YATA"><i class="far fa-star"></i><i class="far fa-star"></i><i class="far fa-star"></i></span>')

    honors = ["Carnage", "Massacre", "Genocide"]
    stars = ["far"] * 3
    for i in range(int(value)):
        stars[i] = "fas"
    title = ", ".join([h for h in honors[:value]])
    htmlstars = "".join([f'<i class="{s} fa-star"></i>' for s in stars])
    return format_html(f'<span title="{title}">{htmlstars}</span>')


@register.filter(name="rarity")
def rarity(circulation):
    try:
        return "{:.2g}%".format(100 / float(circulation))
    except BaseException:
        return ""


@register.filter(name="factionURL")
def factionURL(value, arg=0):
    if str(arg) == "0":
        return "-"
    elif arg:
        return '<a href="https://www.torn.com/factions.php?step=profile&ID={id}" target="_blank">{name} [{id}]</a>'.format(name=value, id=arg)
    else:
        return "-"


@register.filter(name="companyURL")
def companyURL(value, arg=0):
    if str(arg) == "0":
        return "-"
    elif arg:
        return '<a href="https://www.torn.com/joblist.php#?p=corpinfo&ID={id}" target="_blank">{name} [{id}]</a>'.format(name=value, id=arg)
    else:
        return "-"


@register.filter(name="factionURLShort")
def factionURLShort(value, arg=0):
    if str(arg) == "0":
        return "-"
    elif arg:
        return '<a href="https://www.torn.com/factions.php?step=profile&ID={id}" target="_blank">{name}</a>'.format(name=value, id=arg)
    else:
        return "-"


@register.filter(name="playerURL")
def playerURL(value, arg):
    if str(arg) == "0":
        return "-"
    elif arg:
        return '<a href="https://www.torn.com/profiles.php?XID={id}" target="_blank">{name} [{id}]</a>'.format(name=value, id=arg)
    else:
        return "-"


@register.filter(name="playerURLShort")
def playerURLShort(value, arg):
    return '<a href="https://www.torn.com/profiles.php?XID={id}" target="_blank">{name}</a>'.format(name=value, id=arg)


@register.filter(name="cleanhtml")
def cleanhtml(raw_html):
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html)
    return cleantext


@register.filter(name='clean_travel_status')
def clean_travel_status(raw_html):
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html)
    clean_travel_r = re.compile(r"^(?:Returning to Torn|Traveling)")

    if clean_travel_r.match(raw_html):
        travel_text = re.sub(clean_travel_r, "", cleantext).strip()
        if travel_text[0].islower():
            travel_text = travel_text[0].upper() + travel_text[1:]
        return travel_text

    return raw_html


@register.filter(name="string2List")
def string2List(string):
    string = string.replace('"', "'")
    string = string[1:-1]
    if len(string) != 3:
        return [s[1:] for s in string.split("',") if s]
    else:
        return []


@register.filter(name="badge")
def badge(value, arg):
    n = "{:,}".format(arg)
    b = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="112" height="20"><linearGradient id="b" x2="0" y2="100%">'
    b += '<stop offset="0" stop-color="#bbb" stop-opacity=".1"/>'
    b += '<stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="a"><rect width="112" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#a)">'
    b += '<path fill="#555" d="M0 0h71v20H0z"/><path fill="#447e9b" d="M71 0h41v20H71z"/>'
    b += '<path fill="url(#b)" d="M0 0h112v20H0z"/></g><g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110">'
    b += f' <text x="365" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="610">{value}</text><text x="365" y="140" transform="scale(.1)" textLength="610">{value}'
    b += f'</text><text x="905" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="310">{n}</text><text x="905" y="140" transform="scale(.1)" textLength="310">{n}'
    b += "</text></g> </svg>"

    return b


@register.filter(name="priceTendency")
def priceTendency(fl, arg="item"):
    if arg == "stock":
        # fl *= 1000
        # sign = "&permil;"
        fl *= 100
        sign = "%"
    else:
        fl *= 100
        sign = "%"
    colors = ["valid", "error"]
    if not isinstance(fl, float):
        fl = 0
    s = "caret-up" if fl > 0 else "caret-down"
    s = "sort" if fl == 0 else s
    if fl >= 1:
        return '<span class="{}">High</span> (<i class="fas fa-{}"></i> {:+.2f}{})'.format(colors[0], s, fl, sign)
    elif fl <= -1:
        return '<span class="{}">Low</span> (<i class="fas fa-{}"></i> {:+.2f}{})'.format(colors[1], s, fl, sign)
    else:
        return '<span class="neutral">Steady</span> (<i class="fas fa-{}"></i> {:+.2f}{})'.format(s, fl, sign)


@register.filter(name="priceTendencyShort")
def priceTendencyShort(fl, arg="item"):
    if arg == "stock":
        # fl *= 1000
        # sign = "&permil;"
        fl *= 100
        sign = "%"
    else:
        fl *= 100
        sign = "%"
    colors = ["valid", "error"]
    if not isinstance(fl, float):
        fl = 0
    s = "caret-up" if fl > 0 else "caret-down"
    s = "sort" if fl == 0 else s
    if fl >= 1:
        return '<span class="{}"><i class="fas fa-{}"></i> {:+.1f}{}</span>'.format(colors[0], s, fl, sign)
    elif fl <= -1:
        return '<span class="{}"><i class="fas fa-{}"></i> {:+.1f}{}</span>'.format(colors[1], s, fl, sign)
    else:
        return '<span class="neutral"><i class="fas fa-{}"></i> {:+.1f}{}</span>'.format(s, fl, sign)


@register.filter(name="forecast")
def forecast(forecast):
    if forecast in ["Good"]:
        return '<span class="valid"><i class="fas fa-sun"></i></span>'
    elif forecast in ["Very Good"]:
        return '<span class="valid"><i class="fas fa-umbrella-beach"></i></span>'
    elif forecast in ["Poor"]:
        return '<span class="error"><i class="fas fa-cloud-showers-heavy"></i></span>'
    elif forecast in ["Very Poor"]:
        return '<span class="error"><i class="fas fa-poo-storm"></i></span>'
    else:
        return '<span class="neutral"><i class="fas fa-cloud-sun"></i></span>'


@register.filter(name="demand")
def demand(demand):
    dStr = ["very low", "low", "average", "high", "very high"]
    dCol = ["error", "error", "neutral", "valid", "valid"]
    dImg = ['<i class="far fa-square"></i>'] * 4

    ind = dStr.index(demand.lower()) if demand.lower() in dStr else 0

    for i in range(ind):
        dImg[i] = '<i class="fas fa-square"></i>'

    return '<span class="{}">{}</span>'.format(dCol[ind], "".join(dImg))


@register.filter(name="short")
def short(num):
    num = float("{:.3g}".format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return "{}{}".format("{:f}".format(num).rstrip("0").rstrip("."), ["", "K", "M", "B", "T"][magnitude])


@register.filter(name="tTooltip")
def tTooltip(t):
    f = "{} [{}]".format(t.factionName, t.faction) if bool(t.faction) else "-"
    return '<div style="margin: 8px;"><h3>Territory {}</h3><b>Faction:</b> {}<br><b>Coordinates:</b> {}x{}<br><b>Respect:</b> {}</div>'.format(
        t.tId, f, t.coordinate_x, t.coordinate_y, t.daily_respect
    )


@register.filter(name="rTooltip")
def rTooltip(t):
    f = "{} [{}]".format(t.factionName, t.faction) if bool(t.faction) else "-"
    tooltip = f'<div style="margin: 8px;"><h3>Racket {t.tId}</h3><b>Faction:</b> {f}<br><b>Coordinates:</b> {t.coordinate_x}x{t.coordinate_y}<br><b>Respect:</b> {t.daily_respect}'
    tooltip += f"<br><b>Racket:</b> {t.name}<br><b>Reward:</b> {t.reward}<br><b>Distance:</b> {t.distance:0.2f}</div>"
    return tooltip


@register.filter(name="sTooltip")
def sTooltip(t):
    if t.get("factionName", False):
        return '<div style="margin: 8px;"><h3>Barycenter</h3><b>Faction:</b> {} [{}]<br><b>Coordinates:</b> {:.2f}x{:.2f}</div>'.format(
            t["factionName"], t["faction"], t["coordinate_x"], t["coordinate_y"]
        )
    else:
        return "-"


@register.filter(name="float2IfFloat")
def float2IfFloat(f):
    try:
        return "{:,.0f}".format(f) if int(f) == f else "{:,.2f}".format(f)
    except BaseException:
        return f


@register.filter(name="emptyIfFalse")
def emptyIfFalse(f):
    return f if f else ""


@register.filter(name="float2IfSmall")
def float2IfSmall(f):
    try:
        if f < 1:
            ret = f"{f:,.2g}"
        elif f < 100:
            ret = f"{f:,.3g}"
        else:
            ret = f"{f:,.0f}"
    except BaseException:
        ret = f
    return ret


@register.filter(name="convertInf")
def convertInf(f):
    return 1e10 if f in ["&infin;"] else f


@register.filter(name="lootLevel")
def lootLevel(lvl):
    if lvl == 1:
        return "I"
    elif lvl == 2:
        return "II"
    elif lvl == 3:
        return "III"
    elif lvl == 4:
        return "IV"
    elif lvl == 5:
        return "V"
    else:
        return "0"


@register.filter(name="getFromList")
def getFromList(array, n):
    try:
        return array[n]
    except BaseException:
        return -1


@register.filter(name="parseReportFile")
def parseReportFile(report):
    try:
        splt = report.split(".")[0].split("-")
        if len(splt) == 3:
            if splt[1] in ["last"]:
                return "Report of the last couple of days"
            else:
                return f"Report of {splt[1]}/{splt[2]}"
        elif len(splt) == 2:
            return f"Report of {splt[1]}"

    except BaseException:
        return "report"


@register.filter(name="signColor")
def signColor(i, inv=False):
    if i > 0:
        cl = "error" if inv else "valid"
        return format_html('<span class="{}">{:+,.0f}</span>'.format(escape(cl), i))
    elif i < 0:
        cl = "valid" if inv else "error"
        return format_html('<span class="{}">{:+,.0f}</span>'.format(escape(cl), i))
    else:
        return ""


@register.filter(name="signColor0")
def signColor0(i, inv=False):
    try:
        i = int(i)
        if i > 0:
            cl = "error" if inv else "valid"
            return format_html(f'<span class="{escape(cl)}">{i:+,.0f}</span>')
        elif i < 0:
            cl = "valid" if inv else "error"
            return format_html(f'<span class="{escape(cl)}">{i:+,.0f}</span>')
        else:
            return format_html('<span class="neutral">0</span>')
    except Exception:
        return i


@register.filter(name="hexa")
def hexa(tab):
    try:
        hexa = ""
        for i in tab:
            hexa = "{}{:02x}".format(hexa, i)
        return hexa
    except BaseException:
        return "FFFFFFFF"


@register.filter(name="trURL")
def trURL(string):
    regex = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
    words = []
    for w in string.split():
        if re.match(regex, w):
            words.append(format_html('<a href="{}" target="_blank">{}</a>', escape(w), escape(w)))
        else:
            words.append(escape(w))
    return format_html(" ".join(words))


@register.filter(name="attackLog")
def attackLog(code):
    return "https://www.torn.com/loader.php?sid=attackLog&ID={}".format(code)


@register.filter(name="key_to_title")
def key_to_title(key):
    return str(key).replace("_", " ").replace("-", " ").title()


@register.filter(name="workstats")
def workstats(value, arg):
    try:
        if str(value) == "0":
            return "-"
        elif str(arg) == "0":
            return f"{value:,d}"
        sta = int(arg)
        req = int(value)
        m = sta / float(req)
        fac = round(5 * math.log(m, 2)) if m > 1 else round(45 * (m - 1.0))

        cl = "valid"
        cl = "warning" if sta < 2 * req else cl
        cl = "error" if sta < req else cl
        return format_html(f'<span class="{cl}" title="Working stat: {sta:,d}">{req:,d} (<span title="Relative stats effectiveness compared to minimal requirement">{fac:+,d}</span>)</span>')

    except BaseException:
        return value


@register.filter(name="workstatsinv")
def workstatsinv(value, arg):
    try:
        if str(value) == "0":
            return "-"
        elif str(arg) == "0":
            return format_html(f'<i style="opacity: 0.5;">{value:,d}</i>')
        sta = int(value)
        req = int(arg)
        m = sta / float(req)
        fac = round(5 * math.log(m, 2)) if m > 1 else round(45 * (m - 1.0))

        cl = "valid"
        cl = "warning" if sta < 2 * req else cl
        cl = "error" if sta < req else cl
        return format_html(f'<span class="{cl}" title="Requirement: {req:,d}">{sta:,d} (<span title="Relative stats effectiveness compared to minimal requirement">{fac:+,d}</span>)</span>')

    except BaseException:
        return value


@register.filter(name="effpot")
def effpot(value, arg):
    try:
        if str(value) == "0":
            return "-"
        eff = int(value)
        pot = int(arg)

        cl = "valid"
        cl = "warning" if pot < 95 else cl
        cl = "error" if pot < 90 else cl
        return format_html(f'<span class="{cl}">{eff:,d} ({pot}%)</span>')

    except BaseException:
        return value


@register.simple_tag(name="workgains")
def workgains(gain, stat, req):
    if str(gain) == "0" or str(req) == "0":
        return "-"

    ratio = stat / float(req)
    if ratio < 1:
        return format_html(f'<span class="error">{ratio * gain:,.0f}/{gain}</span>')
    else:
        return gain


@register.filter(name="wage")
def wage(value):
    return "-" if str(value) == "0" else f"${value:,d}"


@register.filter(name="compstars")
def compstars(value):
    if not str(value).isdigit():
        return value

    n = int(value)
    stars = ["far"] * 10
    for i in range(int(value)):
        stars[i] = "fas"
    htmlstars = "".join([f'<i class="{s} fa-star"></i>' for s in stars])
    return format_html(f'<span title="{n} stars">{htmlstars}</span>')


@register.filter(name="compprice")
def compprice(value):
    if not str(value).isdigit():
        return value

    v = int(value)
    return f"${v:,d}" if v else "-"


@register.filter(name="compjp")
def compjp(value):
    if not str(value).isdigit():
        return value

    v = int(value)
    return f"{v:,d}" if v else "No cost"


@register.filter(name="compPopColor")
def compPopColor(p):
    cl = ""
    if str(p).isdigit():
        cl = "valid"
        cl = "warning" if int(p) < 85 else cl
        cl = "error" if int(p) < 50 else cl
    return format_html(f"<span class={cl}>{p}%</class>")


@register.filter(name="compOpeningsColor")
def compOpeningsColor(p):
    cl = ""
    if str(p).isdigit() and int(p):
        cl = "valid"
    else:
        cl = "error"
    return format_html(f'<span class="{cl}"><b>{p}</b></class>')


@register.simple_tag(name="url_img_npc")
def url_img_npc(key):
    try:
        return f"/media/loot/npc_{int(key)}.png"
    except BaseException:
        return "/media/loot/npc_default.png"


@register.simple_tag(name="url_img_honor")
def url_img_honor(key):
    if os.path.join(os.path.join(settings.MEDIA_ROOT, "honors"), f'{key}.png'):
        return f"/media/honors/{key}.png"
    else:
        return f"https://www.torn.com/images/honors/{key}/f.png"

@register.simple_tag(name="url_img_medal")
def url_img_medal(key):
    return f"/media/medals/{key}_r.png"


@register.simple_tag(name="url_img_stocks")
def url_img_stocks(key):
    try:
        return f"/media/stocks/{int(key)}.png"
    except BaseException:
        return "/media/stocks/default.png"


@register.simple_tag(name="url_img_item")
def url_img_item(key):
    try:
        return f"/media/items/{int(key)}.png"
    except BaseException:
        return "/media/items/default.png"


@register.simple_tag(name="url_img_flag")
def url_img_flag(key):
    try:
        return f"/media/flags/fl_{key}.png"
    except BaseException:
        return "/media/flags/fl_default.png"


@register.simple_tag(name="url_userscript")
def url_userscript(key):
    return f"https://github.com/Kivou-2000607/yata/raw/master/yata/static/yata/js/userscripts/{key}.user.js"


# TORN LINKS
@register.simple_tag(name="player_link")
def player_link(player_id, player_name="Player", page=None, short=False):
    if page == "attack":
        # path = f'loader2.php?sid=getInAttack&user2ID={player_id}'
        path = f"loader.php?sid=attack&user2ID={player_id}"
    elif page == "image":
        path = f"userimages.php?XID={player_id}"
    elif page == "message":
        path = f"messages.php#/p=compose&XID={player_id}"
    elif page == "profile":
        path = f"profiles.php?XID={player_id}"
    else:
        path = f"profiles.php?XID={player_id}"

    if short:
        return format_html(f'<a href="https://www.torn.com/{path}" title="{player_name} [{player_id}]" target="_blank">{player_name}</a>')
    else:
        return format_html(f'<a href="https://www.torn.com/{path}" title="{player_name} [{player_id}]" target="_blank">{player_name} [{player_id}]</a>')


@register.simple_tag(name="faction_link")
def faction_link(faction_id, faction_name="Faction", short=False):
    if not faction_id:
        return "-"
    if short:
        return format_html(f'<a href="https://www.torn.com/factions.php?step=profile&ID={faction_id}" title="{faction_name} [{faction_id}]" target="_blank">{faction_name}</a>')
    else:
        return format_html(f'<a href="https://www.torn.com/factions.php?step=profile&ID={faction_id}" title="{faction_name} [{faction_id}]" target="_blank">{faction_name} [{faction_id}]</a>')


@register.simple_tag(name="company_link")
def company_link(company_id, company_name="Company", short=False):
    if not company_id:
        return "-"
    url = f"https://www.torn.com/joblist.php#!p=corpinfo&ID={company_id}"
    company_name = company_name.replace("{", "{{").replace("}", "}}")
    if short:
        return format_html(f'<a href="{url}" title="{company_name} [{company_id}]" target="_blank">{company_name}</a>')
    else:
        return format_html(f'<a href="{url}" title="{company_name} [{company_id}]" target="_blank">{company_name} [{company_id}]</a>')


@register.simple_tag(name="key_access_html")
def key_access_html(access_level):
    if access_level == 1:
        tag = "pub"
    elif access_level == 2:
        tag = "min"
    elif access_level == 3:
        tag = "lim"
    elif access_level == 4:
        tag = "ful"
    else:
        tag = "unk"

    return format_html(f'<i title="API key level: {key_access(access_level)}" class="fas fa-key key-access key-access-{tag}"></i>')


@register.simple_tag(name="key_access")
def key_access(access_level):
    if access_level == 1:
        return "Public Only"
    elif access_level == 2:
        return "Minimal Access"
    elif access_level == 3:
        return "Limited Access"
    elif access_level == 4:
        return "Full Access"
    elif access_level == -1:
        return "No keys"
    else:
        return "Unknown"


@register.simple_tag(name="eng_fmt_letters")
def eng_fmt_letters(n):
    fmt = (
        ("b", 1e9),
        ("m", 1e6),
        ("k", 1e3),
    )
    for label, threshold in fmt:
        if abs(int(n)) > threshold:
            return f"{n / threshold:.1f}{label}"

    return n


@register.simple_tag(name="battle_stats")
def battle_stats(n):
    if n < 0:
        return "-"
    else:
        return eng_fmt_letters(n)


@register.simple_tag(name="life_percentage")
def life_percentage(life, life_max):
    return int(min(100 * life / life_max, 100))
