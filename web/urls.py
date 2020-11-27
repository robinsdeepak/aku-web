from django.urls import path
from . import views

app_name = 'web'
urlpatterns = [
    path('', views.home, name='home'),
    path('results', views.result_links_view, name='result_links'),
]
