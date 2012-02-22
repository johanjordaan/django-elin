import httplib, urllib

def validate(request):
  challenge = request.POST['recaptcha_challenge_field']
  response = request.POST['recaptcha_response_field']
  private_key = '6Le3M8wSAAAAAJ4O-BEyvzzjMj3HZGzHSzAhgrUN'
  params = urllib.urlencode({'privatekey': private_key.encode('utf-8'), 'remoteip': '127.0.0.1', 'challenge': challenge,'response': response.encode('utf-8') })
  headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
  conn = httplib.HTTPConnection("www.google.com")
  conn.request("POST", "/recaptcha/api/verify", params, headers)
  resp = conn.getresponse()
  data = resp.read()
  conn.close()
  if resp.status == 200:
    data = data.split()[0]
    if data == 'true':
      return True
    else:
      return False
  else:
    return False
