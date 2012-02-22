from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext


from elin.models import User
import elin.recaptchawrapper 
import elin.utils
import elin.forms

def login(request):
  message = request.session[elin.utils.session_variables['LOGIN_MESSAGE']]
  if request.method == 'POST':
    form = elin.forms.LoginForm(request.POST)
    if form.is_valid():
      if elin.recaptchawrapper.validate(request):
        email = form.cleaned_data['email']
        user = elin.utils.get_user_token(email)
        request.session['email'] = email
        elin.utils.send_login_email(request,email,user.token)
        return HttpResponseRedirect(reverse('elin.views.thanks',args=()))
      else:
        message = 'Invalid Captcha'
  else:
    form = elin.forms.LoginForm()

  return render_to_response('templates/elin/index.html',{'message':message,'form':form},context_instance=RequestContext(request))
	
def thanks(request):
  email = request.session['email']
  del(request.session['email'])
  return render_to_response('templates/elin/thanks.html',{'email':email},context_instance=RequestContext(request))
  

