test:
	python manage.py test --settings=test_app.test_settings
test_system:
	python manage.py test --settings=test_app.test_settings tests.system
coverage:
	coverage run --source=django_geoip manage.py test && coverage report -m
sphinx:
	cd docs && sphinx-build -b html -d .build/doctrees . .build/html