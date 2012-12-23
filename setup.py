from os import path
import codecs
from setuptools import setup, find_packages

read = lambda filepath: codecs.open(filepath, 'r', 'utf-8').read()


setup(
    name='django-geoip',
    version='0.3dev',
    author='Ilya Baryshev',
    author_email='baryshev@gmail.com',
    packages=find_packages(exclude="tests"),
    url='https://github.com/futurecolors/django-geoip',
    license='MIT',
    description="App to figure out where your visitors are from by their IP address.",
    long_description=read(path.join(path.dirname(__file__), 'README.rst')),
    dependency_links=[
        'https://github.com/rafales/django-appconf/archive/feature/py3-support.zip#egg=django-appconf',
        'https://github.com/coagulant/progressbar-python3/archive/master.zip#egg=progressbar',
    ],
    install_requires=[
        'django-appconf==0.5',
        'progressbar==2.3',
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)