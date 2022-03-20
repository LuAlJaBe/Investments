from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from landbot.forms import ExcelUsersMatcherForm
from landbot.models import Excel
from landbot.helpers.match_users import ZendeskExcelFile
from os.path import join, dirname
import mimetypes
from io import BytesIO
from pandas import ExcelWriter

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
            excel = Excel(excel=request.FILES['excel'])
            excel.save()
            zendesk_excel = ZendeskExcelFile(name=filename)
            new_excel_df = zendesk_excel.match()
            with BytesIO() as b:
                # Use the StringIO object as the filehandle.
                writer = ExcelWriter(b, engine='xlsxwriter')
                new_excel_df.to_excel(writer, sheet_name='Sheet1')
                writer.save()
                b.seek(0)
                # Set up the Http response.
                filename = 'new_excel.xlsx'
                response = HttpResponse(
                    b.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename=%s' % filename
                return response
    return render(request, 'clean_excel.html', {'form':form})
