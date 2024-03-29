from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'web'
urlpatterns = [
    path('', views.home, name='home'),
    path('results', views.result_links_view, name='result_links'),
    path('check/<str:batch>/<int:semester>', views.registration_no, name='registration_input'),
    path('check/Default.aspx',
         lambda request: redirect(request.META.get('HTTP_REFERER')) if request else redirect('web:home')),
    path('ranks', views.ranks, name='ranks'),
    path('ranks/<str:batch>/<str:branch>', views.rank_page, name='batch_rank'),
]
