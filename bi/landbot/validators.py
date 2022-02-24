from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.utils import timezone

def validate_not_blank(value):
    if value  == "":
        raise ValidationError(_('Blank Value'))

def validate_not_empty(value):
    if value  == None:
        raise ValidationError(_('Missing Values'))

def validate_greater_than_zero(value):
    if value < 1:
        raise ValidationError(_('Audience must be greater than zero'))

def validate_one_hour_after_now(value):
    limit_datetime = timezone.now() + timedelta(hours=1)
    if value < limit_datetime:
        raise ValidationError(_('Schedule has to be, at least, 1 hour after now'))