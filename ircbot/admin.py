# django
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django import forms

# history tracking
from reversion.admin import VersionAdmin

# models
from ircbot.models import IRCUser, IRCHost, IRCCommand, IRCAction, IRCAutoMode
from ircbot.models import UserProfile

class IRCHostAdmin(VersionAdmin):
	pass

class IRCHostInline(admin.TabularInline):
	model = IRCHost

class IRCUserAdmin(VersionAdmin):
	inlines = [ IRCHostInline ]

	# only allow users to set their AutoMode up to their user level.
	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "user":
			kwargs['queryset'] = User.objects.all()
			return db_field.formfield(**kwargs)
		if db_field.name == "automode":
			try:
				kwargs['queryset'] = IRCAutoMode.objects.filter(command__level__lte=request.user.profile.irc_level)
				return db_field.formfield(**kwargs)
			except:
				pass

class IRCCommandAdmin(VersionAdmin):
	list_display = [ 'name', 'command', 'level', 'color' ]
	list_filter = [ 'level' ]

class IRCActionAdmin(VersionAdmin):
	# list
	list_display = [ 'datetime', 'user', 'command', 'target', 'args', 'performed' ]
	list_filter = [ 'user', 'command', 'target' ]

	# add/edit form
	exclude = [ 'performed' ]
	readonly_fields = []

	def get_readonly_fields(self, request, obj=None):
		if obj:
			return self.readonly_fields + ['command', 'target', 'args']
		return self.readonly_fields

	# only allow users to issue commands that are allowed for their userlevel
	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "command":
			try:
				kwargs['queryset'] = IRCCommand.objects.filter(level__lte=request.user.profile.irc_level)
				return db_field.formfield(**kwargs)
			except:
				pass

	# enforce User
	def save_model(self, request, obj, form, change):
		if getattr(obj, 'user', None) is None:
			obj.user = request.user
		obj.save()

admin.site.register(IRCAutoMode)
admin.site.register(IRCUser, IRCUserAdmin)
admin.site.register(IRCHost, IRCHostAdmin)
admin.site.register(IRCCommand, IRCCommandAdmin)
admin.site.register(IRCAction, IRCActionAdmin)

# User.Profile
admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
	model = UserProfile
	fk_name = 'user'

class UserProfileAdmin(UserAdmin):
	inlines = [ UserProfileInline ]

admin.site.register(User, UserProfileAdmin)
