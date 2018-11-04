from distutils.core import setup

setup(
    name='autoblob',
    version='0.1',
    description='Automatic blob loading for CLE',
    packages=['autoblob'],
    install_requires=[
        'cle',
        'archinfo',
    ],
)
