from django import template

register = template.Library()


@register.filter(name='ts2date')
def ts2date(timestamp):
    import datetime
    import pytz
    try:
        d = datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)
    except:
        d = datetime.datetime.fromtimestamp(0, tz=pytz.UTC)

    # return "{:04d}/{:02d}/{:02d} {:02d}:{:02d}".format(d.year, d.month, d.day, d.hour, d.minute)
    return d.strftime("%Y/%m/%d %I:%M %p")


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
