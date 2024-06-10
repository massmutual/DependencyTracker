#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

from setuptools import setup
from distutils.command.build import build
from distutils.command.clean import clean
from distutils.command.sdist import sdist
from distutils.spawn import find_executable

with open('README') as readme_file:
    readme = readme_file.read()

requirements = ["py4j==0.10.1"]
setup_requirements = ["pytest-runner==2.9", "wheel"]
test_requirements = ["pytest==2.9.2", "coverage==4.1", "pytest-cov==2.3.0"]

exec(compile(open("py4jdbc/version.py").read(), "py4jdbc/version.py", 'exec'))
VERSION = __version__  # noqa
ASSEMBLY_JAR = "py4jdbc/scala/target/scala-2.10/py4jdbc-assembly-{0}.jar".format(__version__)


class jar_build(build):
    def run(self):
        """
        Compile the companion jar file.
        """

        if find_executable('sbt') is None:
            raise EnvironmentError("""

The executable "sbt" cannot be found.

Please install the "sbt" tool to build the companion jar file.
""")

        build.run(self)

        cwd = os.getcwd()
        os.chdir('py4jdbc/scala')
        subprocess.check_call('sbt assembly', shell=True)
        os.chdir(cwd)

class jar_clean(clean):
    def run(self):
        """
        Cleans the scala targets from the system.
        """
        clean.run(self)

        cwd = os.getcwd()
        os.chdir('py4jdbc/scala')
        subprocess.check_call('sbt clean', shell=True)
        os.chdir(cwd)


class my_sdist(sdist):
    def initialize_options(self, *args, **kwargs):
        here = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(here, "MANIFEST.in")
        with open(filename, 'w') as f:
            incld = "include {}\n"
            f.write(incld.format(ASSEMBLY_JAR))
        return super().initialize_options(*args, **kwargs)

setup(
    name='py4jdbc',
    version=VERSION,
    description="py4j JDBC wrapper",
    long_description=readme,
    author="Thom Neale",
    author_email='tneale@massmutual.com',
    url='https://github.com/massmutual/py4jdbc',
    packages=['py4jdbc', 'py4jdbc.exceptions'],
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords=['jdbc', 'dbapi', 'py4j'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    cmdclass={
        'build': jar_build,
        'clean': jar_clean,
        'sdist': my_sdist,
    },
    package_data={
        'py4jdbc': [
            'scala/build.sbt',
            'scala/LICENCE',
            'scala/project/assembly.sbt',
            'scala/src/main/scala/GatewayServer.scala'
        ]
    },
    data_files=[
        ('share/py4jdbc', [ASSEMBLY_JAR])
    ],
    setup_requires=setup_requirements
)
