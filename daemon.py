#!/usr/bin/env python

# WSGI-style path setup
import os,sys
sys.path.append("/home/ecanada/django")
sys.path.append("/home/ecanada/django/ircbot_app")
os.environ["DJANGO_SETTINGS_MODULE"] = "ircbot_app.settings"

# django
from django.contrib.auth.models import User
from ircbot.models import IRCHost, IRCCommand, IRCAction

# irc
from ircutils import bot, format, start_all

# python
import ConfigParser
from datetime import datetime, timedelta
from threading import Timer
from time import sleep

class DjangoBot(bot.SimpleBot):
	last_event = datetime.now()

	def process_queue(self, event):
		actions = IRCAction.objects.filter(performed=False)
		for each in actions:
			c = each.command.command.split()
			if c[0] == "MODE":
				self.execute( str(c[0]), str(event.target), str(c[1]), str(each.target) )
			else:
				if each.args:
					if each.command.color:
						output = format.color( str(each.args), format.RED )
					else:
						output = str(each.args)
				if each.target and each.args:
					self.execute( str(c[0]), str(event.target), str(each.target), trailing=output )
				elif each.target:
					self.execute( str(c[0]), str(event.target), str(each.target) )
				else:
					self.execute( str(c[0]), str(event.target), trailing=output )

			each.performed = True
			each.save()

	def process_chat_command(self, event):
		#TODO: replace filter() with get() ??
		user = User.objects.filter(userprofile__vhosts__hostname=event.host)[0]

		if user:
			msg = event.params[0]

			#TODO: actually handle some exceptions here.
			try:
				if msg[0] == "!":
					chat_command = msg.split()[0]
					target = msg.split()[1]
					#TODO: replace filter() with get() ??
					cmd = IRCCommand.objects.filter(chat_command=chat_command)[0]

					if user.userprofile.level >= cmd.level:
						new_action = IRCAction()
						new_action.command = cmd
						new_action.user = user
						new_action.target = target
						new_action.args = ''
						new_action.comment = "issued via msg: " + str(event.params[0])
						new_action.performed = False
						new_action.save()
						self.process_queue(event)
					else:
						self.send_message(event.source, "permission denied")
			except:
				pass


	### events ###
	def on_any(self, event):
		self.process_queue(event)
		self.last_event = datetime.now()

	#TODO: support IRCChannels
	def on_welcome(self, event):
		self.join( configs['CHANNEL'] )

		if configs['NICKSERV']:
			self.identify( configs['NS_PASS'] )

	def on_ctcp_version(self, event):
		self.send_ctcp_reply(event.source, "VERSION", ["DjangoBot v0"])

	# auto-rejoin
	# TODO: multi-channel support?
	def on_kick(self, event):
		if event.params[0] == self.nickname:
			self.join( configs['CHANNEL'] )

	#TODO: remove core logic from event handler
	def on_message(self, event):
		self.process_chat_command(event)

	#TODO: fix automodes
	#def on_join(self, event):
	#	users = IRCUser.objects.filter(irchost__hostname=event.host)

	#	if users:
	#		user = users[0]
	#		if user.automode:
	#			c = user.automode.command.command.split()
	#			self.execute( str(c[0]), str(event.target), str(c[1]), str(event.source) )

def config_parsing():
	# open config file
	try:
		config = ConfigParser.ConfigParser()
		config.read('bot.cfg')
	except:
		print "configuration file could not be opened!"
		print sys.exc_info()
		sys.exit(1)

	# read configuration settings
	configs = {}
	try:
	# database
		configs['NICK'] = config.get('irc', 'nick')
		configs['SERVER'] = config.get('irc', 'server')
		configs['CHANNEL'] = config.get('irc', 'channel')
		configs['NICKSERV'] = config.get('irc', 'nickserv')
		configs['NS_PASS'] = config.get('irc', 'ns_pass')
	except:
		print "invalid or incomplete configuration data provided."
		print sys.exc_info()
		sys.exit(1)

	return configs


if __name__ == "__main__":
	configs = config_parsing()

	timeout = timedelta(0, 180)
	def bot_poll():
		while True:
			sleep(30)
			time_since_last = datetime.now() - bot.last_event

			if ( time_since_last > timeout):
				print "we look disconnected!"
				bot.disconnect()
				bot.connect( configs['SERVER'] )
				bot.start()


	poller = Timer(15.0, bot_poll)
	poller.start()

	bot = DjangoBot( configs['NICK'] )
	bot.connect( configs['SERVER'] )
	bot.start()
