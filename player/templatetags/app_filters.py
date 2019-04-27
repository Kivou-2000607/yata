from django import template

register = template.Library()

@register.filter(name='ts2date')
def ts2date(timestamp):
    import datetime
    import pytz
    return datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)
