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

from django import template
from django.conf import settings

register = template.Library()


@register.filter(name='ts2date')
def ts2date(timestamp, fmt=None):
    import datetime
    import pytz
    if not timestamp:
        return "N/A"

    try:
        d = datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)
    except BaseException:
        d = datetime.datetime.fromtimestamp(0, tz=pytz.UTC)

    # return "{:04d}/{:02d}/{:02d} {:02d}:{:02d}".format(d.year, d.month, d.day, d.hour, d.minute)
    if fmt is None:
        return d.strftime("%Y/%m/%d %I:%M %p")
    else:
        return d.strftime(fmt)


@register.filter(name='ts2time')
def ts2time(timestamp):
    d = timestamp // 86400
    h = (timestamp - 86400 * d) // 3600 % 24
    m = (timestamp - 3600 * h) // 60 % 60
    s = (timestamp - 60 * m) % 60
    if d:
        return "{} days {:02d} hrs {:02d} mins {:02d} s".format(d, h, m, s)
    elif h:
        return "{} hrs {:02d} mins {:02d} s".format(h, m, s)
    elif m:
        return "{} mins {:02d} s".format(m, s)
    else:
        return "{} s".format(s)


@register.filter(name='ts2ago')
def ts2ago(timestamp):
    t = timestamp // 86400
    if t:
        s = "" if t == 1 else "s"
        return f"{t} day{s} ago"
    t = (timestamp - 86400 * t) // 3600 % 24
    if t:
        s = "" if t == 1 else "s"
        return f"{t} hr{s} ago"
    t = (timestamp - 3600 * t) // 60 % 60
    if t:
        s = "" if t == 1 else "s"
        return f"{t} min{s} ago"
    t = (timestamp - 60 * t) % 60
    s = "" if t == 1 else "s"
    return f"{t} sec{s} ago"


@register.filter(name='format')
def format(value, fmt):
    return fmt.format(value)


@register.filter(name='rarity')
def rarity(circulation):
    try:
        return "{:.2g}%".format(100 / float(circulation))
    except BaseException:
        return ""


@register.filter(name='factionURL')
def factionURL(value, arg=0):
    if str(arg) == "0":
        return '-'
    elif arg:
        return '<a href="https://www.torn.com/factions.php?step=profile&ID={id}" target="_blank">{name} [{id}]</a>'.format(name=value, id=arg)
    else:
        return '-'


@register.filter(name='playerURL')
def playerURL(value, arg):
    return '<a href="https://www.torn.com/profiles.php?XID={id}" target="_blank">{name} [{id}]</a>'.format(name=value, id=arg)


@register.filter(name='cleanhtml')
def cleanhtml(raw_html):
    import re

    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


@register.filter(name='string2List')
def string2List(string):
    string = string.replace("\"", "\'")
    string = string[1:-1]
    if len(string) != 3:
        return [s[1:] for s in string.split('\',') if s]
    else:
        return []


@register.filter(name='badge')
def badge(value, arg):
    n = "{:,}".format(arg)
    b = '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="112" height="20"><linearGradient id="b" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="a"><rect width="112" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#a)"><path fill="#555" d="M0 0h71v20H0z"/><path fill="#447e9b" d="M71 0h41v20H71z"/><path fill="url(#b)" d="M0 0h112v20H0z"/></g><g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110"> <text x="365" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="610">{title}</text><text x="365" y="140" transform="scale(.1)" textLength="610">{title}</text><text x="905" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="310">{value}</text><text x="905" y="140" transform="scale(.1)" textLength="310">{value}</text></g> </svg>'.format(title=value, value=n)

    return b


@register.filter(name='honorUrl')
def honorUrl(url):
    return "https://awardimages.torn.com/435540163.png" if url is None else url


@register.filter(name='honorBanner')
def honorBanner(url, name):
    if url is None:
        return f"<div class=\"award-default\"><img class=\"award-default\" src=\"{settings.STATIC_URL}honors/defaultBanner.png\" title=\"{name}\"><span class=\"award-default\">{name}</span></div>"
    else:
        return f"<img class=\"award-default\" src=\"{url}\" title=\"{name}\">"


@register.filter(name='priceTendancy')
def priceTendancy(fl):
    fl *= 100
    s = "caret-up" if fl > 0 else "caret-down"
    s = "sort" if fl == 0 else s
    if fl >= 1:
        return '<span class="error">High (<i class="fas fa-{}"></i> {:+.1f}%)'.format(s, fl)
    elif fl <= -1:
        return '<span class="valid">Low (<i class="fas fa-{}"></i> {:+.1f}%)'.format(s, fl)
    else:
        return '<span class="neutral">Steady (<i class="fas fa-{}"></i> {:+.1f}%)'.format(s, fl)
