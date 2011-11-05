import os
from django.core.management import execute_manager
import sys
from django.conf import settings

PROJECT_APPS = ('django_geoip', 'tests')
ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

try:
    import django_jenkins
    JENKINS_APP = ('django_jenkins',)
except ImportError:
    JENKINS_APP = tuple()

settings.configure(DEBUG = True,
                   DATABASE_ENGINE = 'sqlite3',
                   DATABASES = {
                        'default': {
                            'ENGINE': 'django.db.backends.sqlite3',
                            }
                   },
                   INSTALLED_APPS = ('django.contrib.auth',
                                     'django.contrib.contenttypes',
                                     'django.contrib.sessions',
                                     'django.contrib.admin',) + PROJECT_APPS + JENKINS_APP,
                   PROJECT_APPS = PROJECT_APPS,
                   JENKINS_TASKS = (
                        'django_jenkins.tasks.with_coverage',
                        'django_jenkins.tasks.django_tests',
                        'django_jenkins.tasks.run_pep8',
                        'django_jenkins.tasks.run_pylint',
                   ),
                   PYLINT_RCFILE = os.path.join(ROOT_PATH, 'tests', 'pylint.rc'),
                   ROOT_URLCONF = 'tests.urls'
)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv += ['test', 'tests']
    execute_manager(settings)
else:
    from django.test.simple import DjangoTestSuiteRunner
    failures = DjangoTestSuiteRunner().run_tests(['tests',])
    if failures:
        sys.exit(failures)