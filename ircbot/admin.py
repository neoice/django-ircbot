from django.contrib import admin
from django.contrib.auth.models import User
from django import forms

from ircbot.models import IRCUser, IRCHost, IRCCommand, IRCAction, IRCAutoMode

from reversion.admin import VersionAdmin

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
				ircuser = IRCUser.objects.get(user=request.user)
				kwargs['queryset'] = IRCAutoMode.objects.filter(command__level__lte=ircuser.level)
				return db_field.formfield(**kwargs)
			except:
				pass

class IRCCommandAdmin(VersionAdmin):
	list_display = [ 'name', 'command', 'level', 'color' ]
	list_filter = [ 'level' ]

class IRCActionAdmin(VersionAdmin):
	# list
	list_display = [ 'datetime', 'user', 'command', 'args', 'performed' ]
	list_filter = [ 'user' ]

	# add/edit form
	exclude = [ 'performed' ]

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "command":
			try:
				ircuser = IRCUser.objects.get(user=request.user)
				kwargs['queryset'] = IRCCommand.objects.filter(level__lte=ircuser.level)
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
