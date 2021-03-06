from django.db import models
from django.contrib.auth.models import User

class IRBan(models.Model):
	user = models.ForeignKey(User, null=True, blank=True)

	start_datetime = models.DateTimeField(auto_now_add=True)
	end_datetime = models.DateTimeField(null=True, blank=True)

	hostname = models.CharField(max_length=255)
	comment = models.CharField(max_length=1023, null=True, blank=True, help_text = "it is **highly** recommended to include a comment.")

	active = models.BooleanField()

	def __unicode__(self):
		return self.hostname

class IRCCommand(models.Model):
	name = models.CharField(max_length=63, unique=True)
	command = models.CharField(max_length=63, unique=True)
	chat_command = models.CharField(max_length=63, unique=True)
	level = models.IntegerField()
	color = models.CharField(max_length=63, null=True, blank=True)

	def __unicode__(self):
		return self.name

class IRCAutoMode(models.Model):
	name = models.CharField(max_length=63)
	command = models.ForeignKey(IRCCommand)

	def __unicode__(self):
		return self.name

class IRCHost(models.Model):
	user = models.ForeignKey(User)
	hostname = models.CharField(max_length=255, unique=True)

	def __unicode__(self):
		return self.hostname

class IRCAction(models.Model):
	datetime = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User, null=True, blank=True)
	command = models.ForeignKey(IRCCommand, help_text = "note: not all commands take both arguments.")

	target = models.CharField(max_length=63, null=True, blank=True, help_text = "for commands that effect a single user, this is required")
	args = models.CharField(max_length=1023, null=True, blank=True, help_text = "for commands that do not effect a single user, this is required. it may have an effect on single user commands as well")
	comment = models.CharField(max_length=1023, null=True, blank=True, help_text = "it is **highly** recommended to include a comment.")
	performed = models.BooleanField()

	def __unicode__(self):
		return str(self.datetime) + ": " + self.user.username + ": " + self.command.name + " " + self.args

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	level = models.IntegerField(default=0)
	#vhosts = models.ManyToManyField(IRCHost, null=True, blank=True)
	# moved here even though we don't support automodes currently
	#automode = models.ForeignKey(IRCAutoMode, null=True, blank=True)

	def __unicode__(self):
		return str(self.level)

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
