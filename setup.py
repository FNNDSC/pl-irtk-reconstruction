from os import path
from setuptools import setup

with open(path.join(path.dirname(path.abspath(__file__)), 'README.md')) as f:
    readme = f.read()

setup(
    name             = 'irtkrecon',
    version          = '1.0.3',
    description      = 'Fetal brain MRI Reconstruction',
    long_description = readme,
    author           = 'FNNDSC',
    author_email     = 'dev@babyMRI.org',
    url              = 'https://github.com/FNNDSC/pl-irtk-reconstruction#readme',
    packages         = ['irtkrecon'],
    install_requires = ['chrisapp~=3.0.0rc2'],
    license          = 'GPLv2',
    zip_safe         = False,
    python_requires  = '>=3.7',
    entry_points     = {
        'console_scripts': [
            'irtkrecon = irtkrecon.__main__:main'
            ]
        }
)
