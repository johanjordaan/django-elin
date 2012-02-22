import uuid
import hashlib

from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

from elin.models import User

from support.mailer import send_mail

session_variables = {'ID':'elin_user_id','TARGET':'target_url','LOGIN_EMAIL_FROM':'login_email_from','LOGIN_EMAIL_SUBJECT':'login_email_subject','LOGIN_EMAIL_TEMPLATE':'login_email_template','LOGIN_MESSAGE':'login_message'}

def clean_session(request):
  for key in session_variables.keys():
    if session_variables[key] in request.session.keys():
      del(request.session[session_variables[key]])

def generate_token(email):
	m = hashlib.sha224()
	m.update(email)
	m.update(str(uuid.uuid4()))
	return m.hexdigest()

def get_user_token(email):
  user,created = User.objects.get_or_create(email=email)
  if user.token == None or user.token == '':
    user.token = generate_token(email)
    user.save()
  return user
  
def kill_token(user):
  user.token = ''
  user.save()
 
def authenticate(get_configuration):
  def _dec(func):
    def _wrapper(request,token=None,*args,**kwargs):
      login_email_from,login_email_subject,login_email_template,session_timeout = get_configuration()
      if login_email_from == None and login_email_subject == None and login_email_template == None and session_timeout == None:
        login_email_from = 'support@here.com'
        login_email_subject = 'Login e-mail'
        login_email_template = 'Click <a href="{{ target }}">here</a> to log in.'
        session_timeout = 300
      
      user = None
      if token == '' or token == None:
        if session_variables['ID'] in request.session.keys():
          try:
            user = User.objects.get(id=request.session[session_variables['ID']])
          except:
            return login(request,request.path,login_email_from,login_email_subject,login_email_template)
        else:
          login_message = None
          if request.method == 'POST':
            login_message='Session timed-out. Please complete the login process again.'
          return login(request,request.path,login_email_from,login_email_subject,login_email_template,login_message=login_message)
            
      else:
        try:
          user = User.objects.get(token=token)
          request.session[session_variables['ID']] = user.id
        except Exception,e:
          return login(request,request.path,login_email_from,login_email_subject,login_email_template,login_message='Invalid token. Please complete the login process again.')

      request.session.set_expiry(session_timeout)
      request.user = user
      retval = func(request,token,*args,**kwargs)
      return retval
    return _wrapper    
  return _dec
#NOTE : We need to figure out what to do if somebody goes directly to elin


def login(request,target,login_email_from,login_email_subject,login_email_template,login_message=None):
  request.session[session_variables['TARGET']] = target
  request.session[session_variables['LOGIN_EMAIL_FROM']] = login_email_from
  request.session[session_variables['LOGIN_EMAIL_SUBJECT']] = login_email_subject
  request.session[session_variables['LOGIN_EMAIL_TEMPLATE']] = login_email_template
  request.session[session_variables['LOGIN_MESSAGE']] = login_message
  return HttpResponseRedirect(reverse('elin.views.login',args=()))      

def send_login_email(request,email,token):
  subject = request.session[session_variables['LOGIN_EMAIL_SUBJECT']]
  from_email = request.session[session_variables['LOGIN_EMAIL_FROM']]
  template_str = request.session[session_variables['LOGIN_EMAIL_TEMPLATE']]
  target = '%s/%s'%(request.get_host(),request.session[session_variables['TARGET']])
  target_with_token = '%s/%s'%(target,token)
  template_context = {'target':target,'target_with_token':target_with_token}
  send_mail(to_email_list=[email],from_email=from_email,subject_str=subject,template_str=template_str,template_context= template_context)
