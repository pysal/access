from setuptools import setup, find_packages
from distutils.command.build_py import build_py
import versioneer


with open("README.md", "r") as fh:
    long_description = fh.read()


def _get_requirements_from_files(groups_files):
    groups_reqlist = {}

    for k, v in groups_files.items():
        with open(v, "r") as f:
            pkg_list = f.read().splitlines()
        groups_reqlist[k] = pkg_list

    return groups_reqlist


def setup_package():

    _groups_files = {
        "base": "requirements.txt",  # basic requirements
        "tests": "requirements_tests.txt",  # requirements for tests
        "docs": "requirements_docs.txt",  # requirements for building docs
    }
    reqs = _get_requirements_from_files(_groups_files)
    install_reqs = reqs.pop("base")
    extras_reqs = reqs

    setup(
        name="access",  # name of package
        version=versioneer.get_version(),
        cmdclass=versioneer.get_cmdclass({"build_py": build_py}),
        description="Calculate spatial accessibility metrics.",  # short <80chr description
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://access.readthedocs.io/en/latest/",  # github repo
        maintainer="James Saxon",
        maintainer_email="jsaxon@uchicago.edu",
        keywords="spatial statistics access",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Science/Research",
            "Intended Audience :: Developers",
            "Intended Audience :: Education",
            "Topic :: Scientific/Engineering",
            "Topic :: Scientific/Engineering :: GIS",
            "License :: OSI Approved :: BSD License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
        ],
        license="3-Clause BSD",
        packages=find_packages(),
        install_requires=install_reqs,
        extras_require=extras_reqs,
        zip_safe=False,
    )


if __name__ == "__main__":

    setup_package()
