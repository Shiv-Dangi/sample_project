from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()


@register.filter
def mult(value):
    if value:
        return int(int(value) * 1.11)
    else:
        return value


@register.filter('get_value_from_dict')
def get_value_from_dict(dict_data, key):
    """
    usage example {{ your_dict|get_value_from_dict:your_key }}
    """
    if key:
        return dict_data.get(key)


@register.filter
@stringfilter
def upto(value):
    string = value
    value = [int(s) for s in value.split() if s.isdigit()]
    if len(value) == 1 and 'days' in string:
        value = "0" + str(value[0]) + ",00:00:00"
    elif len(value) == 1 and 'minutes' in string:
        if value[0] < 10:
            value = "00,00:0" + str(value[0]) + ":00"
        else:
            value = "00,00:" + str(value[0]) + ":00"
    elif len(value) == 2:
        if value[0] < 10 and value[1] < 10:
            value = "00,0" + str(value[0]) + ":0" + str(value[1]) + ":00"
        elif value[0] < 10 and value[1] >= 10:
            value = "00,0" + str(value[0]) + ":" + str(value[1]) + ":00"
        elif value[0] >= 10 and value[1] < 10:
            value = "00," + str(value[0]) + ":0" + str(value[1]) + ":00"
        else:
            value = "00," + str(value[0]) + ":" + str(value[1]) + ":00"
    return value


upto.is_safe = True