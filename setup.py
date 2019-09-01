from setuptools import setup

setup(
    name='gencore_app',
    version='1.0',
    packages=['gencore_app', 'gencore_app.commands', 'gencore_app.utils'],
    include_package_data=True,
    install_requires=[
        'click',
        'apscheduler',
    ],
    entry_points='''
        [console_scripts]
        gencore_app=gencore_app.cli:cli
    ''',
)
