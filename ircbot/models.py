from django.db import models
from django.contrib.auth.models import User

class IRCCommand(models.Model):
	name = models.CharField(max_length=63)
	command = models.CharField(max_length=63)
	level = models.IntegerField()
	color = models.CharField(max_length=63, null=True, blank=True)

	def __unicode__(self):
		return self.name

class IRCAutoMode(models.Model):
	name = models.CharField(max_length=63)
	command = models.ForeignKey(IRCCommand)

	def __unicode__(self):
		return self.name

class IRCUser(models.Model):
	user = models.ForeignKey(User)
	automode = models.ForeignKey(IRCAutoMode, null=True, blank=True)
	level = models.IntegerField()

	def __unicode__(self):
		return self.user.username

class IRCHost(models.Model):
	user = models.ForeignKey(IRCUser)
	hostname = models.CharField(max_length=255)

	def __unicode__(self):
		return self.hostname

class IRCAction(models.Model):
	datetime = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User, null=True, blank=True)
	command = models.ForeignKey(IRCCommand, help_text = "note: not all commands take both arguments.")

	target = models.CharField(max_length=63, null=True, blank=True, help_text = "for commands that effect a single user, this is required")
	args = models.CharField(max_length=1023, null=True, blank=True, help_text = "for commands that do not effect a single user, this is required. it may have an effect on single user commands as well")
	performed = models.BooleanField()

	def __unicode__(self):
		return str(self.datetime) + ": " + self.user.username + ": " + self.command.name + " " + self.args
