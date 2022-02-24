from re import search
from django.contrib import admin
from landbot.models import Campaign

# Register your models here.
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['template_name', 'audience', 'schedule']
    search_fields = ['template_name', 'audience', 'schedule']
    list_filter = ['schedule']
    date_hierarchy = 'schedule'

admin.site.register(Campaign, CampaignAdmin)