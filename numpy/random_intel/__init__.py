import warnings
try:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="numpy.ndarray size changed")
        from mkl_random import *
except ImportError as e:
    warnings.warn("mkl_random not found. Install it with 'conda instal -c intel mkl_random', or get it from 'http://github.com/IntelPython/mkl_random'", stacklevel=2)
