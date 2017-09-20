# -*- coding: utf-8 -*-
#

"""
This module implements highlevel interfaces for C/CL-extensions.
"""

import logging
from ..config import cli


LOGGER = logging.getLogger(__name__)


class Phi(object):
    """

    """
    name = 'phi_kernel'

    def set_consts(self):
        return []

    def set_bufs(self, ps, nforce=1):
        to_int = self.to_int
        to_buf = self.to_buf
        ps.phi[...] = 0
        return [
            to_int(ps.n),
            to_buf(ps.data['mass']),
            to_buf(ps.data['eps2']),
            to_buf(ps.data['rdot']),
            to_buf(ps.data['phi']),
        ]

    def map_bufs(self, bufs, ps, nforce=1):
        self.map_buf(ps.data['mass'])
        self.map_buf(ps.data['eps2'])
        self.map_buf(ps.data['rdot'])
        self.map_buf(ps.data['phi'])
        self.sync()


class Acc(object):
    """

    """
    name = 'acc_kernel'

    def set_consts(self):
        return []

    def set_bufs(self, ps, nforce=1):
        to_int = self.to_int
        to_buf = self.to_buf
        ps.fdot[:nforce] = 0
        return [
            to_int(ps.n),
            to_buf(ps.data['mass']),
            to_buf(ps.data['eps2']),
            to_buf(ps.data['rdot']),
            to_buf(ps.data['fdot']),
        ]

    def map_bufs(self, bufs, ps, nforce=1):
        self.map_buf(ps.data['mass'])
        self.map_buf(ps.data['eps2'])
        self.map_buf(ps.data['rdot'])
        self.map_buf(ps.data['fdot'])
        self.sync()


class Acc_Jrk(Acc):
    """

    """
    name = 'acc_jrk_kernel'


class Snp_Crk(Acc):
    """

    """
    name = 'snp_crk_kernel'


class Tstep(object):
    """

    """
    name = 'tstep_kernel'

    def set_consts(self, eta=None):
        return [
            self.to_real(eta),
        ]

    def set_bufs(self, ps, nforce=2):
        to_int = self.to_int
        to_buf = self.to_buf
        ps.tstep[...] = 0
        ps.tstep_sum[...] = 0
        return [
            to_int(ps.n),
            to_buf(ps.data['mass']),
            to_buf(ps.data['eps2']),
            to_buf(ps.data['rdot']),
            to_buf(ps.data['tstep']),
            to_buf(ps.data['tstep_sum']),
        ]

    def map_bufs(self, bufs, ps, nforce=2):
        self.map_buf(ps.data['mass'])
        self.map_buf(ps.data['eps2'])
        self.map_buf(ps.data['rdot'])
        self.map_buf(ps.data['tstep'])
        self.map_buf(ps.data['tstep_sum'])
        self.sync()


class PNAcc(object):
    """

    """
    name = 'pnacc_kernel'

    def set_consts(self, order=None, clight=None):
        return [
            self.to_int(order),
            self.to_real(clight),
        ]

    def set_bufs(self, ps, nforce=2):
        to_int = self.to_int
        to_buf = self.to_buf
        ps.pnacc[...] = 0
        return [
            to_int(ps.n),
            to_buf(ps.data['mass']),
            to_buf(ps.data['eps2']),
            to_buf(ps.data['rdot']),
            to_buf(ps.data['pnacc']),
        ]

    def map_bufs(self, bufs, ps, nforce=1):
        self.map_buf(ps.data['mass'])
        self.map_buf(ps.data['eps2'])
        self.map_buf(ps.data['rdot'])
        self.map_buf(ps.data['pnacc'])
        self.sync()


class Sakura(object):
    """

    """
    name = 'sakura_kernel'

    def set_consts(self, dt=None, flag=None):
        return [
            self.to_real(dt),
            self.to_int(flag),
        ]

    def set_bufs(self, ps, nforce=2):
        to_int = self.to_int
        to_buf = self.to_buf
        ps.drdot[...] = 0
        return [
            to_int(ps.n),
            to_buf(ps.data['mass']),
            to_buf(ps.data['eps2']),
            to_buf(ps.data['rdot']),
            to_buf(ps.data['drdot']),
        ]

    def map_bufs(self, bufs, ps, nforce=1):
        self.map_buf(ps.data['mass'])
        self.map_buf(ps.data['eps2'])
        self.map_buf(ps.data['rdot'])
        self.map_buf(ps.data['drdot'])
        self.sync()


class Kepler(object):
    """

    """
    name = 'kepler_solver_kernel'

    def set_consts(self, dt=None):
        return [
            self.to_real(dt),
        ]

    def set_bufs(self, ps, nforce=2):
        to_int = self.to_int
        to_buf = self.to_buf
        return [
            to_int(ps.n),
            to_buf(ps.mass),
            to_buf(ps.eps2),
            to_buf(ps.rdot[0][0]),
            to_buf(ps.rdot[0][1]),
            to_buf(ps.rdot[0][2]),
            to_buf(ps.rdot[1][0]),
            to_buf(ps.rdot[1][1]),
            to_buf(ps.rdot[1][2]),
        ]

    def map_bufs(self, bufs, ps, nforce=2):
        self.map_buf(ps.rdot[0][0])
        self.map_buf(ps.rdot[0][1])
        self.map_buf(ps.rdot[0][2])
        self.map_buf(ps.rdot[1][0])
        self.map_buf(ps.rdot[1][1])
        self.map_buf(ps.rdot[1][2])


def make_extension(name, backend=cli.backend):
    if backend == 'C':
        from .backend_cffi import CKernel as Kernel
    elif backend == 'CL':
        from .backend_opencl import CLKernel as Kernel
    else:
        msg = f"Invalid backend: '{backend}'. Choices are: ('C', 'CL')"
        raise ValueError(msg)

    cls = globals()[name]
    Extension = type(name, (cls, Kernel), {})
    return Extension(cls.name)


class ArrayWrapper(object):
    """

    """
    def __init__(self, ary):
        self.buf = None
        self.ary = ary
        self.shape = ary.shape
        self.dtype = ary.dtype

    def __getstate__(self):
        return (self.ary, self.shape, self.dtype)  # buf can not be pickled!

    def __setstate__(self, state):
        self.ary, self.shape, self.dtype = state
        self.buf = None


# -- End of File --
