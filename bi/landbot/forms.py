from django import forms
from landbot.models import Campaign

class CampaignsPreparerForm(forms.ModelForm):
    template_name = forms.CharField()
    audience = forms.IntegerField()
    schedule = forms.DateTimeField(widget= forms.DateTimeInput(attrs={'type':'datetime-local'}))
    
    template_name.widget.attrs.update({
        'class':''
    })
    audience.widget.attrs.update({
        'class':''
    })
    schedule.widget.attrs.update({
        'class':''
    })
    
    class Meta:
        model = Campaign
        fields = '__all__'
    
        
    

