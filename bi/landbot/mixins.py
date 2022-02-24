


from django.shortcuts import redirect

class SuperUserMixin(object):
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        return redirect('login')