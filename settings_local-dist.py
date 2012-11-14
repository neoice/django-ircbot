DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.mysql',
		'NAME': '', 
		'USER': '',
		'PASSWORD': '', 
	},
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/home/username/public_html/static/django-media/'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # TODO: port this to be inside django app
    '/home/username/django/templates/'
)
