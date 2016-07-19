from setuptools import setup

setup(
    name='ims',
    version='0.2',
    install_requires=["sqlalchemy>=1.0.13", 'requests'],
    packages=['ims', 'ims.database', 'ims.exception'],
    url='',
    license='',
    author='chemistry_sourabh',
    author_email='',
    description=''
)
