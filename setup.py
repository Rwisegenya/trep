#!/usr/bin/python

import subprocess
from distutils.util import convert_path
from distutils.core import setup
from distutils.extension import Extension
from distutils.command.sdist import sdist as _sdist
import numpy

include_dirs = [
    'src/_trep',
    numpy.get_include()  
    ]
cflags=[]
ldflags=[]
define_macros=[]

# Fast indexing results in significant speed ups for second
# derivatives.  Turning it off will force fast index accesses to use
# the normal indexing functions where the array can be tested for the
# correct dimensions for debugging and development.
define_macros += [("TREP_FAST_INDEXING", None)]

_trep = Extension('trep._trep',
                  include_dirs=include_dirs,
                  define_macros=define_macros,
                  extra_compile_args=cflags,
                  extra_link_args=ldflags,
                  sources = [
                      'src/_trep/midpointvi.c',
                      'src/_trep/system.c',
                      'src/_trep/math-code.c',
                      'src/_trep/frame.c',
                      'src/_trep/_trep.c',
                      'src/_trep/config.c',
                      'src/_trep/potential.c',
                      'src/_trep/force.c',
                      'src/_trep/input.c',
                      'src/_trep/constraint.c',
                      'src/_trep/frametransform.c',
                      'src/_trep/spline.c',
                      'src/_trep/framesequence.c',
                      
                      # Constraints
                      'src/_trep/constraints/distance.c',
                      'src/_trep/constraints/point.c',
                      
                      # Potentials
                      'src/_trep/potentials/gravity.c',
                      'src/_trep/potentials/linearspring.c',
                      'src/_trep/potentials/configspring.c',
                      'src/_trep/potentials/nonlinear_config_spring.c',
                      
                      # Forces
                      'src/_trep/forces/damping.c',
                      'src/_trep/forces/jointforce.c',
                      'src/_trep/forces/bodywrench.c',
                      'src/_trep/forces/hybridwrench.c', 
                      'src/_trep/forces/spatialwrench.c',
                      ],
                  depends=[
                      'src/_trep/trep.h'
                      ])

## _polyobject = Extension('_polyobject',
##                     extra_compile_args=[],
##                     extra_link_args=['-lGL'],
##                     include_dirs = ['/usr/local/include'],
##                     sources = ['src/newvisual/_polyobject.c'])


VERSION_PY = """
# This file was generated by setup.py

__version__ = '%s'
"""

def update_version_file():
    try:
        version_git = get_version_from_git()
        version_file = get_version_from_file()
        if version_git == version_file:
            return
    except (GitDescribeError, IOError):
        pass

    version = get_version()
    f = open(convert_path("src/__version__.py"), "wt")
    f.write(VERSION_PY % version)
    f.close()
    return version

class GitDescribeError(StandardError): pass


def get_version_from_git():
    try:
        p = subprocess.Popen(["git", "describe", "--dirty", "--always"],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    except EnvironmentError as e:
        raise GitDescribeError(e)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise GitDescribeError("git describe failed: '%s'" % stderr)
    return stdout.strip()


def get_version_from_file():
    glob = {'__builtins__' : __builtins__ }
    execfile('src/__version__.py', glob)
    return glob['__version__']


def get_version():
    try:
        return get_version_from_git()
    except GitDescribeError:
        pass
    try:
        return get_version_from_file()
    except IOError:
        pass
    return '<unknown>'


update_version_file()

cmd_class = {}
cmd_options = {}

################################################################################
# Sphinx support

# Try to add support to build the documentation if Sphinx is
# installed.
try:
    from sphinx.setup_command import BuildDoc
    cmd_class['build_sphinx'] = BuildDoc
    cmd_options['build_sphinx'] = {
        'version' : ('setup.py', get_version()),
        'release' : ('setup.py', '')
        }
    # See docstring for BuildDoc on how to set default options here.
except ImportError:
    pass


################################################################################


setup (name = 'trep',
       version = get_version(),
       description = 'trep is used to simulate mechanical systems.',
       author = ['Elliot Johnson'],
       author_email = 'elliot.r.johnson@gmail.com',
       url = 'http://trep.googlecode.com/',
       package_dir = {'' : 'src', 'trep': 'src'},
       packages=['trep',
                 'trep.constraints',
                 'trep.potentials',
                 'trep.forces',
                 'trep.visual',
                 'trep.puppets',
                 'trep.discopt'
                 ],
       ext_modules = [_trep,
                      #_polyobject
                      ],
       cmdclass=cmd_class,
       command_options=cmd_options)
