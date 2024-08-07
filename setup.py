import os
from setuptools import setup

README = """
See the README on `GitHub
<https://github.com/uw-it-aca/uw-django-saml2>`_.
"""
version_path = 'uw_saml/VERSION'
VERSION = open(os.path.join(os.path.dirname(__file__), version_path)).read()
VERSION = VERSION.replace("\n", "")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

url = 'https://github.com/uw-it-aca/uw-django-saml2'
setup(
    name='uw-django-saml2',
    version=VERSION,
    packages=['uw_saml'],
    author="UW-IT T&LS",
    author_email="aca-it@uw.edu",
    include_package_data=True,
    install_requires=[
        'django>=3.2,<5',
        'python3-saml~=1.16',
        'mock'
    ],
    license='Apache License, Version 2.0',
    description=('Django wrapper for python3-saml'),
    long_description=README,
    url=url,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
