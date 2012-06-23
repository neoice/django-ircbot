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
	inlines = [IRCHostInline]

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
	list_display = [ 'name', 'command' ]

class IRCActionAdmin(VersionAdmin):
	list_display = [ 'datetime', 'user', 'command', 'args', 'performed' ]
	exclude = [ 'performed' ]

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "command":
			try:
				ircuser = IRCUser.objects.get(user=request.user)
				kwargs['queryset'] = IRCCommand.objects.filter(level__lte=ircuser.level)
				return db_field.formfield(**kwargs)
			except:
				pass

	def save_model(self, request, obj, form, change):
		if getattr(obj, 'user', None) is None:
			obj.user = request.user
		obj.save()


admin.site.register(IRCAutoMode)
admin.site.register(IRCUser, IRCUserAdmin)
admin.site.register(IRCHost, IRCHostAdmin)
admin.site.register(IRCCommand, IRCCommandAdmin)
admin.site.register(IRCAction, IRCActionAdmin)
