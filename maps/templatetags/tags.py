from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag
def nav_urls (t,cor,**kwargs):

    if 'stat' in kwargs:
        stat = kwargs['stat']
    if 'stat1' in kwargs:
        stat1 = kwargs['stat1']
        stat2 = kwargs['stat2']

    if t == 'A' and cor == 0:
        return reverse('default',args=(stat,)) 
    elif t == 'A' and cor == 1:
        return reverse('correlations',args=(stat,))
    if t == 'A' and cor == 2:
        return reverse('correlations2', args=(stat1,stat2,)) 
    elif t != 'A' and cor == 0:
        return reverse('default_mon',args=(stat,t))
    if t != 'A' and cor == 1:
        return reverse('correlations_mon',args=(stat,t))
    elif t != 'A' and cor == 2:
       return reverse('correlations2_mon', args=(stat1,stat2,t)) 

@register.filter
def get_month(l, i):
    try:
        return l[int(i)]
    except:
        return None
