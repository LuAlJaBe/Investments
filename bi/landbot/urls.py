from django.urls import path
from .formsets import CampaignsPreparerFormSet
from . import views

app_name = 'landbot'
urlpatterns = [
    path('', views.home, name='home'),
    path('setup_campaigns_succeed', views.setup_campaigns_succeed, name='setup_campaigns_succeed'),
    path('setup_campaigns', CampaignsPreparerFormSet.as_view(), name='setup_campaigns'),
    path('clean_excel', views.match_users, name='clean_excel'),
]