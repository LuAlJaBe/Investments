from django.shortcuts import render, HttpResponse

# Create your views here.
def setup_campaigns_succeed(request):
    return render(request, 'setup_campaigns/success.html')
