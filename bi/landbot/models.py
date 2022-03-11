from datetime import datetime
from django.db import models

from landbot.validators import validate_greater_than_zero, validate_one_hour_after_now

# Create your models here.
class Campaign(models.Model):
    template_name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    audience = models.IntegerField(null=False, blank=False,
                                   validators=[validate_greater_than_zero])
    schedule = models.DateTimeField(null=False,blank=False, auto_now=False,auto_now_add=False,
                                    default=datetime.now,
                                    validators=[validate_one_hour_after_now])
    
    class Meta:
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'
    
    def __str__(self):
        return self.template_name

class Excel(models.Model):
    excel = models.FileField(upload_to='uploads/',null=False, blank=False)
    class Meta:
        verbose_name = 'excel'
        verbose_name_plural = 'excel'
        db_table = 'excel'
    
    def __str__(self):
        return '{}'.format(self.excel)
        
    