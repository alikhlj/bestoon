from django.conf.urls import url
from . import views
from django.urls import path
import re
urlpatterns = [
    path('submit/expense/', views.submit_expense,name='submit_expense'),
    path('submit/income/', views.submit_income,name='submit_income'),
    path('accounts/register/', views.register, name='register'),
    path('', views.index, name='index'),

]