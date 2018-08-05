from setuptools import setup
import os.path
from distutils.command.build_py import build_py

Major = 1
Feature = 0
Bug = 0
# dev could be removed
version = '%d.%d.%d' % (Major, Feature, Bug) + 'dev'

def _get_requirements_from_files(groups_files):
    groups_reqlist = {}

    for k,v in groups_files.items():
        with open(v, 'r') as f:
            pkg_list = f.read().splitlines()
        groups_reqlist[k] = pkg_list

    return groups_reqlist

def setup_package():

    _groups_files = {
        'base': 'requirements.txt', #basic requirements
        'tests': 'requirements_tests.txt', #requirements for tests
        'docs': 'requirements_docs.txt' #requirements for building docs
    }
    reqs = _get_requirements_from_files(_groups_files)
    install_reqs = reqs.pop('base')
    extras_reqs = reqs

    setup(name='', #name of package
          version=version,
          description='', #short <80chr description
          url='', #github repo
          maintainer='',
          maintainer_email='',
          test_suite = 'nose.collector',
          tests_require=['nose'],
          keywords='spatial statistics',
          classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Science/Research',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: GIS',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6'
            ],
          license='3-Clause BSD',
          packages=[], #add your package name here as a string
          install_requires=install_reqs,
          extras_require=extras_reqs,
          zip_safe=False,
          cmdclass = {'build.py':build_py})

if __name__ == '__main__':
    setup_package()
