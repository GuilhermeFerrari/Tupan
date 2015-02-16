# -*- coding: utf-8 -*-
#

"""This module implements the CFFI backend to call C-extensions.

"""


import os
import cffi
import ctypes
import logging
from ..config import options, get_cache_dir
from .utils.ctype import Ctype
from .utils.timing import timings, bind_all


LOGGER = logging.getLogger(__name__)

DIRNAME = os.path.dirname(__file__)
PATH = os.path.join(DIRNAME, 'src')


@bind_all(timings)
class CDriver(object):
    """

    """
    def __init__(self, fpwidth=options.fpwidth):
        self.fpwidth = fpwidth

        self._make_lib()

    def _make_lib(self):
        LOGGER.debug("Building '%s' C extension module.", self.fpwidth)

        fnames = ('phi_kernel.c',
                  'acc_kernel.c',
                  'acc_jerk_kernel.c',
                  'snap_crackle_kernel.c',
                  'tstep_kernel.c',
                  'pnacc_kernel.c',
                  'nreg_kernels.c',
                  'sakura_kernel.c',
                  'kepler_solver_kernel.c', )

        src = []
        with open(os.path.join(PATH, 'libtupan.h'), 'r') as fobj:
            src.append('typedef {} int_t;'.format(Ctype.c_int))
            src.append('typedef {} uint_t;'.format(Ctype.c_uint))
            src.append('typedef {} real_t;'.format(Ctype.c_real))
            src.append(fobj.read())
        source = '\n'.join(src)

        self.ffi = cffi.FFI()

        self.ffi.cdef(source)

        define_macros = []
        if self.fpwidth == 'fp64':
            define_macros.append(('CONFIG_USE_DOUBLE', 1))

        self.lib = self.ffi.verify(
            """
            #include "common.h"
            #include "libtupan.h"
            """,
            tmpdir=get_cache_dir(),
            define_macros=define_macros,
            include_dirs=[PATH],
            libraries=['m'],
            extra_compile_args=['-O3', '-std=c99', '-march=native'],
            sources=[os.path.join(PATH, fname) for fname in fnames],
        )

        LOGGER.debug('C extension module loaded.')

    def get_kernel(self, name):
        LOGGER.debug("Using '%s' function from 'C' backend.", name)
        kernel = getattr(self.lib, name)
        return CKernel(kernel)


drv = CDriver()


@bind_all(timings)
class CKernel(object):
    """

    """
    def __init__(self, kernel):
        self.kernel = kernel
        self.inptypes = None
        self.outtypes = None
        self.iarg = {}
        self.ibuf = {}
        self.oarg = {}
        self.obuf = {}

    def set_args(self, inpargs, outargs):
        bufs = []

        if self.inptypes is None:
            types = []
            for arg in inpargs:
                if isinstance(arg, int):
                    int_t = lambda x: x
                    uint_t = lambda x: x
                    types.append(int_t if arg < 0 else uint_t)
                elif isinstance(arg, float):
                    real_t = lambda x: x
                    types.append(real_t)
                else:
                    from_buffer = (ctypes.c_char * 0).from_buffer
                    addressof = ctypes.addressof
                    cast = drv.ffi.cast
                    iptr = lambda x: cast('void *', addressof(from_buffer(x)))
                    types.append(iptr)
            self.inptypes = types

        if self.outtypes is None:
            from_buffer = (ctypes.c_char * 0).from_buffer
            addressof = ctypes.addressof
            cast = drv.ffi.cast
            optr = lambda x: cast('void *', addressof(from_buffer(x)))
            self.outtypes = [optr for _ in outargs]

        # set inpargs
        for (i, argtype) in enumerate(self.inptypes):
            arg = inpargs[i]
            buf = argtype(arg)
            self.iarg[i] = arg
            self.ibuf[i] = buf
            bufs.append(buf)

        # set outargs
        for (i, argtype) in enumerate(self.outtypes):
            arg = outargs[i]
            buf = argtype(arg)
            self.oarg[i] = arg
            self.obuf[i] = buf
            bufs.append(buf)

        self.bufs = bufs

    def map_buffers(self):
        return list(self.oarg.values())

    def run(self):
        self.kernel(*self.bufs)


# -- End of File --
