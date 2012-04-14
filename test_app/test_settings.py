import django

if django.VERSION[:2] >= (1, 3):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        },
    }
else:
    DATABASE_ENGINE = 'sqlite3'

SECRET_KEY = '_'
ROOT_URLCONF = 'test_app.urls'
INSTALLED_APPS = ('django_nose', 'django_geoip', 'test_app')
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'