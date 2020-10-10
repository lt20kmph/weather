from scipy.stats import linregress
from maps.models import AnnualData, MonthlyData, SpaceHuman, Explanations, Xform
from calendar import monthrange, isleap
import requests
from os import path
from os import listdir
from numpy import round
from plotly.graph_objs import Scatter, Figure
from plotly.offline import plot
from django.conf import settings
import logging
from django.template.loader import render_to_string
from django.shortcuts import render
from django.template import engines
from django.http import HttpResponse
from django.conf.urls import url

fmt = getattr(settings, 'LOG_FORMAT', None)
lvl = getattr(settings, 'LOG_LEVEL', logging.DEBUG)

logger = logging.getLogger(__name__)
logging.basicConfig(format=fmt, level=lvl)
logger.debug("Logging started on %s for %s" %
             (logging.root.name, logging.getLevelName(lvl)))

pageTitle = 'Explore UK weather data'
months = ['Jan',
          'Feb',
          'Mar',
          'Apr',
          'May',
          'Jun',
          'Jul',
          'Aug',
          'Sep',
          'Oct',
          'Nov',
          'Dec']


def dist(p1, p2):
  d = (p1[0]-p2[0])**2+(p1[1]-p2[1])**2
  return(d)


def closestPoint(la, lo, t):
  Q = Xform.objects.filter(
      xlat__lte=la+t,
      xlat__gte=la-t,
      xlon__lte=lo+t,
      xlon__gte=lo-t,
  )
  d = 100
  for e in Q:
    dd = dist((e.xlat, e.xlon), (la, lo))
    if dd < d:
      d = dd
      p = e
  return(p.lat, p.lon)


def mean(xs):
  return(sum(xs)/len(xs))


def sma(xs, p):
  A = []
  for i in range(p+1):
    A += [[xs[j] for j in range(i+p+1)]]
  for i in range(p+1, len(xs)-p):
    A += [[xs[j] for j in range(i-p, i+p+1)]]
  for i in range(len(xs)-p, len(xs)):
    A += [[xs[j] for j in range(i-p, len(xs))]]
  return([mean(x) for x in A])


def number_of_days_in_month(year, month):
  return monthrange(year, month)[1]


def number_of_days_in_year(year, month):
  if isleap(year):
    return 366
  else:
    return 365


def normaliseIfSfcWind(stat):
  if stat == 'sfcWind':
    def N(x):
      return 5/18*x
  else:
    def N(x):
      return x
  return N

def defaultLayout(fig, title):
  fig.update_layout(
      title=dict(text=title, x=0.5, y=0.99, yanchor='top'),
      margin=dict(l=0.01,r=0.01,t=20,b=20),
      paper_bgcolor='rgba(0,0,0,0)',
      plot_bgcolor='rgba(0,0,0,0)',
      xaxis_gridcolor='gainsboro',
      yaxis_gridcolor='gainsboro',
      xaxis_zerolinecolor='gainsboro',
      yaxis_zerolinecolor='gainsboro',
      legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        bgcolor='beige',
        bordercolor='darkgray',
        borderwidth=1,
        x=0.01))
  return fig

def home(request):
  html = render_to_string('home.html', {
      'title': pageTitle,
      'cor': 0,
      'mon': 'A',
      'stat': 'tasmax',
      'months': months,
  })
  return HttpResponse(html)

# -- stat is the statistic for which the view is applied. Can be any of
#    {'sun','rainfall','tasmax'}.
# -- xr stands for xrange, rain and tas are 1884-2019, sun is 1929-2019.
#    Possible: remove xr!
# -- yr stands for yrange. Currently not used.
# -- n can be either of 'y' or 'n'.
#    Do we want to normalise the data so that it is per day?
# -- t is this the monthly or annual data set. Can be any of
#    {'A',0,..,11}. A in case it is annual data, other wise the number
#    corresponds to the month, 0 <-> Jan, etc...


def views(request, stat, t):

  info = Explanations.objects.get(stat=stat)
  if t == 'A':
    template = 'default.html'
    exp = str(info.exp)
  else:
    template = 'default_mon.html'
    exp = str(info.exp_mon)

  if request.method == 'GET':
    html = render_to_string(template, {'title': pageTitle,
                                       'cor': 0,
                                       'mon': t,
                                       'stat': stat,
                                       'exp': exp,
                                       'ln': str(info.longname),
                                       'months': months, })
    return HttpResponse(html)

  elif request.method == 'POST':
    if 'lat' in request.POST:
      lat = request.POST['lat']
      lon = request.POST['lon']

      if str(info.normalise) == 'n':
        def N(y, m): return 1
      elif t == 'A':
        N = number_of_days_in_year
      else:
        N = number_of_days_in_month

      cl = closestPoint(float(lat), float(lon), 0.45)

      if t == 'A':
        m = 0
        Q = AnnualData.objects.filter(lat=cl[0], lon=cl[1], stat=stat)
      else:
        m = t
        Q = MonthlyData.objects.filter(lat=cl[0],
                                       lon=cl[1],
                                       stat=stat,
                                       month=m,)
      X = [e.year for e in Q]
      Y = [normaliseIfSfcWind(stat)(e.data/N(e.year, int(m)+1)) for e in Q]

      loc = str(SpaceHuman.objects.get(lat=cl[0], lon=cl[1]))
      plotTitle = stat + ' time series at ' + loc
      fig = Figure()
      fig.add_trace(Scatter(x=X,
                            y=Y,
                            name=stat,
                            ))
      fig.add_trace(Scatter(x=X,
                            y=sma(Y,10),
                            name="CMA21",
                            ))
      fig = defaultLayout(fig, plotTitle)
      testPlot = plot(fig,
                      output_type='div',
                      include_plotlyjs=False)
      # logger.info(testPlot)
      html = render_to_string(template, {
          'testPlot': testPlot,
          'title': pageTitle,
          'cor': 0,
          'mon': t,
          'loc': loc,
          'exp': exp,
          'ln': str(info.longname),
          'stat': stat,
          'months': months,
      }, request,)
      response = HttpResponse(html)
      return response


def CorrelationViews(request, stat, t):

  info = Explanations.objects.get(stat=stat)
  if t == 'A':
    template = 'correlations.html'
    exp = str(info.exp)
  else:
    template = 'correlations_mon.html'
    exp = str(info.exp_mon)

  if request.method == 'GET':
    html = render_to_string(template, {'title': pageTitle,
                                       'cor': 1,
                                       'mon': t,
                                       'stat': stat,
                                       'exp': exp,
                                       'ln': str(info.longname),
                                       'months': months, })
    return HttpResponse(html)

  elif request.method == 'POST':
    if 'lat1' in request.POST:

      lat1, lon1 = request.POST['lat1'], request.POST['lon1']
      lat2, lon2 = request.POST['lat2'], request.POST['lon2']

      cl1 = closestPoint(float(lat1), float(lon1), 0.45)
      cl2 = closestPoint(float(lat2), float(lon2), 0.45)
      if t == 'A':
        m = 0
        Q1 = AnnualData.objects.filter(lat=cl1[0], lon=cl1[1], stat=stat)
        Q2 = AnnualData.objects.filter(lat=cl2[0], lon=cl2[1], stat=stat)
      else:
        m = t
        Q1 = MonthlyData.objects.filter(lat=cl1[0],
                                        lon=cl1[1],
                                        stat=stat,
                                        month=m,)
        Q2 = MonthlyData.objects.filter(lat=cl2[0],
                                        lon=cl2[1],
                                        stat=stat,
                                        month=m,)

      X = [normaliseIfSfcWind(stat)(e.data) for e in Q1]
      Y = [normaliseIfSfcWind(stat)(e.data) for e in Q2]

      lr = linregress(X, Y)
      Xlin = [min(X), max(X)]
      Ylin = [lr[0]*Xlin[0]+lr[1], lr[0]*Xlin[1]+lr[1]]
      loc1 = str(SpaceHuman.objects.get(lat=cl1[0], lon=cl1[1]))
      loc2 = str(SpaceHuman.objects.get(lat=cl2[0], lon=cl2[1]))
      plotTitle = 'Correlations between ' + loc1 + ' and ' + loc2

      fig = Figure()
      fig.add_trace(Scatter(x=X,
                            y=Y,
                            name=stat,
                            mode='markers',
                            showlegend=False,
                            ))
      fig.add_trace(Scatter(x=Xlin,
                            y=Ylin,
                            name='line of best fit',
                            ))
      fig = defaultLayout(fig, plotTitle)
      fig.update_layout(
          xaxis_title=loc1,
          yaxis_title=loc2,
      )
      testPlot = plot(fig,
                      output_type='div',
                      include_plotlyjs=False)
      html = render_to_string(template,
                              {
                                  'testPlot': testPlot,
                                  'title': pageTitle,
                                  'cor': 1,
                                  'mon': t,
                                  'stat': stat,
                                  'exp': exp,
                                  'ln': str(info.longname),
                                  'correlationCoeff': lr[2],
                                  'loc1': loc1,
                                  'loc2': loc2,
                                  'months': months,
                              }, request)
      return HttpResponse(html)


def CorrelationViews2(request, stat1, stat2, t):

  info1 = Explanations.objects.get(stat=stat1)
  info2 = Explanations.objects.get(stat=stat2)

  if t == 'A':
    template = 'correlations_2.html'
    exp1 = str(info1.exp)
    exp2 = str(info2.exp)
  else:
    template = 'correlations_2_mon.html'
    exp1 = str(info1.exp_mon)
    exp2 = str(info2.exp_mon)

  if request.method == 'GET':
    html = render_to_string(template, {'title': pageTitle,
                                       'mon': t,
                                       'stat1': stat1,
                                       'stat2': stat2,
                                       'exp1': exp1,
                                       'exp2': exp2,
                                       'cor': 2,
                                       'ln1': str(info1.longname),
                                       'ln2': str(info2.longname),
                                       'months': months, })
    return HttpResponse(html)

  elif request.method == 'POST':
    if 'lat' in request.POST:

      lat, lon = request.POST['lat'], request.POST['lon']

      cl = closestPoint(float(lat), float(lon), 0.45)

      nr = [max(info1.rangelower, info2.rangelower), 2019]

      if t == 'A':
        m = 0
        Q1 = AnnualData.objects.filter(lat=cl[0],
                                       lon=cl[1],
                                       stat=stat1,
                                       year__gte=nr[0],)
        Q2 = AnnualData.objects.filter(lat=cl[0],
                                       lon=cl[1],
                                       stat=stat2,
                                       year__gte=nr[0],)
      else:
        m = t
        Q1 = MonthlyData.objects.filter(lat=cl[0],
                                        lon=cl[1],
                                        stat=stat1,
                                        month=m,
                                        year__gte=nr[0],)
        Q2 = MonthlyData.objects.filter(lat=cl[0],
                                        lon=cl[1],
                                        stat=stat2,
                                        month=m,
                                        year__gte=nr[0],)

      X = [normaliseIfSfcWind(stat1)(e.data) for e in Q1]
      Y = [normaliseIfSfcWind(stat2)(e.data) for e in Q2]

      lr = linregress(X, Y)
      Xlin = [min(X), max(X)]
      Ylin = [lr[0]*Xlin[0]+lr[1], lr[0]*Xlin[1]+lr[1]]
      loc = str(SpaceHuman.objects.get(lat=cl[0], lon=cl[1]))
      plotTitle = 'Correlations between ' + stat1 + ' and ' + stat2

      fig = Figure()
      fig.add_trace(Scatter(x=X,
                            y=Y,
                            mode='markers',
                            showlegend=False,
                            ))
      fig.add_trace(Scatter(x=Xlin,
                            y=Ylin,
                            name='line of best fit',
                            ))
      fig = defaultLayout(fig, plotTitle)
      fig.update_layout(
          xaxis_title=stat1,
          yaxis_title=stat2,
      )
      testPlot = plot(fig,
                      output_type='div',
                      include_plotlyjs=False)
      html = render_to_string(template,
                              {
                                  'testPlot': testPlot,
                                  'title': pageTitle,
                                  'mon': t,
                                  'stat1': stat1,
                                  'stat2': stat2,
                                  'correlationCoeff': lr[2],
                                  'exp1': exp1,
                                  'exp2': exp2,
                                  'cor': 2,
                                  'ln1': str(info1.longname),
                                  'ln2': str(info2.longname),
                                  'loc': loc,
                                  'months': months,
                              }, request)
      return HttpResponse(html)
