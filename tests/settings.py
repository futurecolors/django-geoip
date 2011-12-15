import os

PROJECT_APPS = ('django_geoip', 'tests')
ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

try:
    import django_jenkins
    JENKINS_APP = ('django_jenkins',)
except ImportError:
    JENKINS_APP = tuple()

try:
    import south
    SOUTH_APP = ('south',)
except ImportError:
    SOUTH_APP = tuple()

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydatabase'
    }
}
INSTALLED_APPS = ('django.contrib.auth',
                 'django.contrib.contenttypes',
                 'django.contrib.sessions',
                 'django.contrib.admin',) + PROJECT_APPS + JENKINS_APP + SOUTH_APP
PROJECT_APPS = PROJECT_APPS
JENKINS_TASKS = (
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.django_tests',
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pylint',
)
PYLINT_RCFILE = os.path.join(ROOT_PATH, 'tests', 'pylint.rc')
ROOT_URLCONF = 'tests.urls'