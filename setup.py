import os
from setuptools import setup

README = """
See the README on `GitHub
<https://github.com/uw-it-aca/uw-django-saml2>`_.
"""

# The VERSION file is created by travis-ci, based on the tag name
version_path = 'uw_saml/VERSION'
VERSION = open(os.path.join(os.path.dirname(__file__), version_path)).read()
VERSION = VERSION.replace("\n", "")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

url = 'https://github.com/uw-it-aca/uw-django-saml2'
setup(
    name='UW-Django-SAML2',
    version=VERSION,
    packages=['uw_saml'],
    author="UW-IT AXDD",
    author_email="aca-it@uw.edu",
    include_package_data=True,
    install_requires=[
        'Django>=2.0,<2.3',
        'python3-saml>=1.6.0',
        'mock'
    ],
    license='Apache License, Version 2.0',
    description=('UW-Django-SAML2'),
    long_description=README,
    url=url,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
)
