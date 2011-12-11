from django.core.management import execute_manager
import sys
from tests import settings

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv += ['test', 'tests']
    execute_manager(settings)
else:
    from django.test.simple import DjangoTestSuiteRunner
    failures = DjangoTestSuiteRunner().run_tests(['tests',])
    if failures:
        sys.exit(failures)