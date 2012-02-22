from django.db import models

class User(models.Model):
	email = models.EmailField()
	token = models.CharField(max_length=200)
	timestamp = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return self.email

