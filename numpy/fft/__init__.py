from __future__ import division, absolute_import, print_function

# To get sub-modules
from .info import __doc__

from .fftpack import *
from .helper import *

from numpy._pytesttester import PytestTester
test = PytestTester(__name__)
del PytestTester


try:
    import warnings
    with warnings.catch_warnings():
        # Filter out harmless Cython warnings coming from mkl_fft
        warnings.filterwarnings("ignore", message="numpy.dtype size changed")
        warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
        warnings.filterwarnings("ignore", message="numpy.ndarray size changed")
        import mkl_fft._numpy_fft as _nfft
        patch_fft = True
        __patched_functions__ = _nfft.__all__
except ImportError:
    patch_fft = False

if patch_fft:
    _restore_dict = {}
    import sys

    def register_func(name, func):
        if name not in __patched_functions__:
            raise ValueError("%s not an mkl_fft function." % name)
        f = sys._getframe(0).f_globals
        _restore_dict[name] = f[name]
        f[name] = func

    def restore_func(name):
        if name not in __patched_functions__:
            raise ValueError("%s not an mkl_fft function." % name)
        try:
            val = _restore_dict[name]
        except KeyError:
            print('failed to restore')
            return
        else:
            print('found and restoring...')
            sys._getframe(0).f_globals[name] = val

    def restore_all():
        for name in _restore_dict.keys():
            restore_func(name)

    for f in __patched_functions__:
        register_func(f, getattr(_nfft, f))
    del _nfft

del patch_fft
