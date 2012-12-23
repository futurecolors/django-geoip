test:
	`which django-admin.py` test --settings=test_app.test_settings tests
test_more:
    `which django-admin.py` test --settings=test_app.test_settings tests.system