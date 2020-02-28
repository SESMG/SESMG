""" Distributor init file

Distributors: you can add custom code here to support particular distributions
of numpy.

For example, this is a good place to put any checks for hardware requirements.

The numpy standard source distribution will not put code in this file, so you
can safely replace this file with your own version.
"""
import sys

class RTLD_for_MKL():
    def __init__(self):
        self.saved_rtld = None

    def __enter__(self):
        import ctypes
        try:
            self.saved_rtld = sys.getdlopenflags()
            # python loads libraries with RTLD_LOCAL, but MKL requires RTLD_GLOBAL
            # pre-load MKL with RTLD_GLOBAL before loading the native extension
            sys.setdlopenflags(self.saved_rtld | ctypes.RTLD_GLOBAL)
        except AttributeError:
            pass
        del ctypes

    def __exit__(self, *args):
        if self.saved_rtld:
            sys.setdlopenflags(self.saved_rtld)
            self.saved_rtld = None

with RTLD_for_MKL():
    from . import _mklinit

del RTLD_for_MKL
del sys
