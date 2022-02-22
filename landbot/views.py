from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='landbot/login')
def setup_campaigns_succeed(request):
    return render(request, 'campaigns/success.html')
