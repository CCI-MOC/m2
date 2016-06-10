import sys

from setuptools import setup

args = sys.argv

picasso_install_requires = ["pyro4", "requests","flask"]
einstein_install_requires = ["sqlalchemy>=1.0.13", "requests", "Pyro4"]
picasso_packages = ['ims.common','ims.picasso','ims.rpc.client']
einstein_packages = ['ims.einstein', 'ims.database',
                     'ims.exception', 'ims.rpc.server','ims.common']

install_requires = []
packages = []

if args[1] == 'install':
    if args[2] == 'einstein':
        install_requires = einstein_install_requires
        packages = einstein_packages
    elif args[2] == 'picasso':
        install_requires = picasso_install_requires
        packages = picasso_packages
    elif args[2] == 'einstein+picasso':
        install_requires = list(
            set(einstein_install_requires + picasso_install_requires))
        packages = list(set(einstein_packages + picasso_packages))
    else:
        print "Invalid Argument"
        sys.exit()

    sys.argv.pop()

setup(
    name='ims',
    version='0.2',
    install_requires=install_requires,
    packages=packages,
    url='',
    license='',
    author='chemistry_sourabh',
    author_email='',
    description=''
)
