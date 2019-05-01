from django import template

register = template.Library()


@register.filter(name='ts2date')
def ts2date(timestamp):
    import datetime
    import pytz
    try:
        return datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)
    except:
        return datetime.datetime.fromtimestamp(0, tz=pytz.UTC)


@register.filter(name='format')
def format(value, fmt):
    return fmt.format(value)


@register.filter(name='rarity')
def rarity(circulation):
    try:
        return "{:.2g}%".format(100 / float(circulation))
    except:
        return ""
