#!/usr/bin/env python
from __future__ import division, print_function


def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    from numpy.distutils.system_info import get_info

    defs = []
    libs = get_info('mkl').get('libraries', [])
    if any(['mkl_rt' in li for li in libs]):
        #libs += ['dl'] - by default on Linux
        defs += [('USING_MKL_RT', None)]

    config = Configuration('numpy', parent_package, top_path)
    config.add_extension('_mklinit',
                          sources=['_mklinitmodule.c'],
                          define_macros=defs,
                          extra_info=get_info('mkl'))
    config.add_subpackage('compat')
    config.add_subpackage('core')
    config.add_subpackage('distutils')
    config.add_subpackage('doc')
    config.add_subpackage('f2py')
    config.add_subpackage('fft')
    config.add_subpackage('lib')
    config.add_subpackage('linalg')
    config.add_subpackage('ma')
    config.add_subpackage('matrixlib')
    config.add_subpackage('polynomial')
    config.add_subpackage('random')
    config.add_subpackage('random_intel')
    config.add_subpackage('testing')
    config.add_data_dir('doc')
    config.add_data_dir('tests')
    config.make_config_py() # installs __config__.py
    return config


if __name__ == '__main__':
    print('This is the wrong setup.py file to run')
