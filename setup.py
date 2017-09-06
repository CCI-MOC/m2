from setuptools import setup, find_packages

setup(
    name='ims',
    version='0.3',
    install_requires=["pyro4==4.41", "requests", "flask", "sqlalchemy>=1.0.13",
                      "click", "prettytable", "sh"],
    packages=find_packages(),
    scripts=['scripts/einstein_server', 'scripts/picasso_server'],
    include_package_data=True,
    package_data={'ims': ['*.temp']},
    entry_points={
        'console_scripts': [
            'bmi = ims.cli.cli:cli'
        ]
    })
