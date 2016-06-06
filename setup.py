import os

from setuptools import setup, find_packages

from vindaloo.version import VERSION


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

with open(os.path.join(here, 'requirements/base.txt')) as f:
    REQUIRES = [l.strip() for l in f.readlines()]

with open(os.path.join(here, 'requirements/dev.txt')) as f:
    DEV_REQUIRES = [l.strip() for l in f.readlines()]


setup(
    name='vindaloo',
    version=VERSION,
    description='JSON API library for Pyramid',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: API',
    ],
    author='Rob van der Linde',
    author_email='robvdl@gmail.com',
    url='https://github.com/robvdl/vindaloo',
    keywords='json api pyramid sqlalchemy',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIRES,
    tests_require=DEV_REQUIRES,
    extras_require={'dev': DEV_REQUIRES},
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'vindaloo = vindaloo.cli:main',
        ],
        'pyramid.scaffold': [
            'vindaloo = vindaloo.scaffolds:VindalooTemplate'
        ]
    }

)
