#!/usr/bin/env python

# WSGI-style path setup
import os,sys
sys.path.append("/home/ecanada/django")
sys.path.append("/home/ecanada/django/ircbot_app")
os.environ["DJANGO_SETTINGS_MODULE"] = "ircbot_app.settings"

# django
from ircbot.models import IRCUser, IRCHost, IRCCommand, IRCAction

# irc
from ircutils import bot, format, start_all

# python
import ConfigParser
from threading import Timer
from time import sleep

class DjangoBot(bot.SimpleBot):
	def on_any(self, event):
		disconnected = False

	### events ###
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

	def on_join(self, event):
		users = IRCUser.objects.filter(irchost__hostname=event.host)

		if users:
			user = users[0]
			if user.automode:
				c = user.automode.command.command.split()
				self.execute( str(c[0]), str(event.target), str(c[1]), str(event.source) )

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

	disconnected = True
	def bot_poll():
		while True:
			# PING/PONG occurs every 60s, so I thought 120 would
			# be plenty, but it didn't seem to work.
			sleep(180)
			disconnected = True

			if disconnected:
				bot.connect( configs['SERVER'] )
				bot.start()


	poller = Timer(5.0, bot_poll)
	poller.start()

	bot = DjangoBot( configs['NICK'] )
	bot.connect( configs['SERVER'] )
	bot.start()
