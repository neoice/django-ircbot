# django
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django import forms

# history tracking
from reversion.admin import VersionAdmin

# models
from ircbot.models import IRCHost, IRCCommand, IRCAction, IRCAutoMode
from ircbot.models import UserProfile

class IRCHostAdmin(VersionAdmin):
	pass

class IRCHostInline(admin.TabularInline):
	model = IRCHost

class IRCCommandAdmin(VersionAdmin):
	list_display = [ 'name', 'command', 'chat_command', 'level', 'color' ]
	list_filter = [ 'level' ]

class IRCActionAdmin(VersionAdmin):
	# list
	list_display = [ 'datetime', 'user', 'command', 'target', 'args', 'comment', 'performed' ]
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
				kwargs['queryset'] = IRCCommand.objects.filter(level__lte=request.user.profile.level)
				return db_field.formfield(**kwargs)
			except:
				pass

	# enforce User
	def save_model(self, request, obj, form, change):
		if getattr(obj, 'user', None) is None:
			obj.user = request.user
		obj.save()

admin.site.register(IRCAutoMode)
admin.site.register(IRCHost, IRCHostAdmin)
admin.site.register(IRCCommand, IRCCommandAdmin)
admin.site.register(IRCAction, IRCActionAdmin)

# User.Profile
admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
	model = UserProfile
	fk_name = 'user'

class UserProfileAdmin(UserAdmin):
	list_display = [ 'username', 'email', 'is_staff', 'is_superuser', 'profile' ]
	list_filter = ['groups' ]

	readonly_fields = [ ]

	def get_readonly_fields(self, request, obj=None):
		if request.user.is_superuser:
			return self.readonly_fields
		else:
			return self.readonly_fields + [ 'is_superuser', 'user_permissions', 'last_login', 'date_joined', 'first_name', 'last_name' ]

	inlines = [ UserProfileInline, IRCHostInline ]

admin.site.register(User, UserProfileAdmin)
