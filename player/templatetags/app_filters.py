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

register = template.Library()


@register.filter(name='ts2date')
def ts2date(timestamp, fmt=None):
    import datetime
    import pytz
    if not timestamp:
        return "N/A"
        
    try:
        d = datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)
    except:
        d = datetime.datetime.fromtimestamp(0, tz=pytz.UTC)

    # return "{:04d}/{:02d}/{:02d} {:02d}:{:02d}".format(d.year, d.month, d.day, d.hour, d.minute)
    if fmt is None:
        return d.strftime("%Y/%m/%d %I:%M %p")
    else:
        return d.strftime(fmt)


@register.filter(name='ts2hhmmss')
def ts2mmss(timestamp):
    d = timestamp // 86400
    h = (timestamp - 86400*d) // 3600 % 24
    m = (timestamp - 3600*h) // 60 % 60
    s = (timestamp - 60*m) % 60
    if d:
        return "{} days {:02d} hrs {:02d} mins {:02d} s".format(d, h, m, s)
    elif h:
        return "{} hrs {:02d} mins {:02d} s".format(h, m, s)
    elif m:
        return "{} mins {:02d} s".format(m, s)
    else:
        return "{} s".format(s)




@register.filter(name='format')
def format(value, fmt):
    return fmt.format(value)


@register.filter(name='rarity')
def rarity(circulation):
    try:
        return "{:.2g}%".format(100 / float(circulation))
    except:
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
