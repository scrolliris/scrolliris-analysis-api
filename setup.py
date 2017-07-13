"""Setup Script.
"""
import os

from setuptools import setup, find_packages

# pylint: disable=invalid-name
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, *('doc', 'README.rst'))) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGELOG')) as f:
    CHANGELOG = f.read()

requires = [
    'colorlog',
    'Paste',
    'PasteScript',
    'python-dotenv',
    'pyramid',
    'pyramid_assetviews',
    'pyramid_mako',
]

development_requires = [
    'flake8',
    'pylint',
    'waitress',
]

testing_requires = [
    'pytest',
    'pytest-cov',
    'WebTest',
]

production_requires = [
    'CherryPy',
]

setup(
    name='scythia',
    version='0.1',
    description='',
    long_description=README + '\n\n' + CHANGELOG,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='',
    author_email='',
    url='',
    keywords='web wsgi pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'development': development_requires,
        'testing': testing_requires,
        'production': production_requires,
    },
    install_requires=requires,
    message_extractors={'scythia': [
        ('**.py', 'python', None),
        ('static/**', 'ignore', None),
    ]},
    entry_points="""\
    [paste.app_factory]
    main = scythia:main
    [console_scripts]
    scythia_pserve = scythia.scripts.pserve:main
    scythia_pstart = scythia.scripts.pstart:main
    """,
)
