from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from landbot.forms import ExcelUsersMatcherForm
from landbot.models import Excel
from landbot.helpers.match_users import ZendeskExcelFile
from os.path import join, dirname
import mimetypes

# Create your views here.
@login_required(login_url='landbot/login')
def home(request):
    return render(request, 'index.html')

@login_required(login_url='landbot/login')
def setup_campaigns_succeed(request):
    return render(request, 'campaigns/success.html')

@login_required(login_url='landbot/login')
def clean_excel(request):
    return render(request, 'clean_excel.html')

@login_required(login_url='landbot/login')
def match_users(request):
    form = ExcelUsersMatcherForm()
    if request.method == 'POST':
        form = ExcelUsersMatcherForm(request.POST, request.FILES)
        if form.is_valid():
            filename = request.FILES['excel'].name
            filepath = join(dirname(dirname(dirname(__file__))), 'vol', 'web', 'media', 'uploads', filename)
            excel = Excel(excel=request.FILES['excel'])
            excel.save()
            zendesk_excel = ZendeskExcelFile(name=filename)
            zendesk_excel.match()
            path = open(filepath, 'rb')
            mime_type, _ = mimetypes.guess_type(filepath)
            response = HttpResponse(path, content_type=mime_type)
            response['Content-Disposition'] = "attachment; filename=%s" % filename
            return response
    return render(request, 'clean_excel.html', {'form':form})
