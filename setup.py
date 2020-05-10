from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ansilog',
    version='1.6',
    description="Smart and colorful solution for logging, "
                "output, and basic terminal control.",
    long_description=long_description,

    url='https://github.com/lainproliant/ansilog',

    author='Lain Supe (lainproliant)',
    author_email='lainproliant@gmail.com',

    license='BSD',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8'
    ],

    keywords='ANSI CLI terminal color colour',

    packages=['ansilog'],
    install_requires=[],
    extras_require={},
    package_data={'ansilog': ["LICENSE"]},
    entry_points={'console_scripts': []},
)
