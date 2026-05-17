from django import template

register = template.Library()

@register.filter(name='currency')
def currency(value):
    try:
        value = int(value)
        return "{:,}".format(value).replace(',', '.') + " đ"
    except (ValueError, TypeError):
        return "0 đ"
