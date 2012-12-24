test:
	python manage.py test --settings=test_app.test_settings tests
test_system:
	python manage.py test --settings=test_app.test_settings tests.system