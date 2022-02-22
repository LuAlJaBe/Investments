from django.forms import formset_factory
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from landbot.forms import CampaignsPreparerForm
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin


from landbot.setup_campaigns import CampaignsPreparer
from pdb import set_trace as bp

class CampaignsPreparerFormSet(LoginRequiredMixin, FormView):
    template_name = 'campaigns/setup_form.html'
    form_class = formset_factory(CampaignsPreparerForm, extra=1)
    success_url = reverse_lazy('landbot:setup_campaigns_succeed')
    login_url = 'landbot/login'
    
    def form_valid(self, formset):
        response = super().form_valid(formset)
        if self.request.accepts('text/html'):
            cleaned_data = formset.cleaned_data
            setup_campaigns = CampaignsPreparer(cleaned_data)
            setup_campaigns.main()
            return response
        else:
            return JsonResponse(formset.errors, status=400, safe=False)
    