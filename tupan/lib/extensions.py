# -*- coding: utf-8 -*-
#

"""
This module implements highlevel interfaces for C/CL-extensions.
"""

from __future__ import print_function, division
import logging
from ..config import options


LOGGER = logging.getLogger(__name__)


def pn_struct(pn):
    order = pn['order']
    clight = pn['clight']
    d = {'order': order}
    for i in range(1, 8):
        d['inv'+str(i)] = clight**(-i)
    return d


class AbstractExtension(object):
    """

    """
    def __init__(self, name, backend):
        if backend == 'C':
            from .backend_cffi import drv
        elif backend == 'CL':
            from .backend_opencl import drv
        else:
            msg = "invalid backend: '{}' (choose from 'C', 'CL')"
            raise ValueError(msg.format(backend))
        self.kernel = drv.get_kernel(name)

    def set_args(self, ips, jps, **kwargs):
        raise NotImplementedError

    def run(self):
        return self.kernel.run()

    def map_buffers(self, *args, **kwargs):
        return self.kernel.map_buffers(*args, **kwargs)

    def __call__(self, ips, jps, **kwargs):
        self.set_args(ips, jps, **kwargs)
        self.run()
        self.map_buffers()
        return ips, jps


class Phi(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'phi_kernel'
        super(Phi, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        p = 1
        inpargs = (ips.n, ips.mass, ips.eps2, ips.rdot[:p],
                   jps.n, jps.mass, jps.eps2, jps.rdot[:p])

        outargs = (ips.phi,)

        self.kernel.set_args(inpargs, outargs)


class Phi_rectangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'phi_kernel_rectangle'
        super(Phi_rectangle, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        p = 1
        inpargs = (ips.n, ips.mass, ips.eps2, ips.rdot[:p],
                   jps.n, jps.mass, jps.eps2, jps.rdot[:p])

        outargs = (ips.phi, jps.phi)

        self.kernel.set_args(inpargs, outargs)


class Phi_triangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'phi_kernel_triangle'
        super(Phi_triangle, self).__init__(name, backend)

    def set_args(self, ips, jps=None, **kwargs):
        p = 1
        inpargs = (ips.n, ips.mass, ips.eps2, ips.rdot[:p])

        outargs = (ips.phi,)

        self.kernel.set_args(inpargs, outargs)


class Acc(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'acc_kernel'
        super(Acc, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        p = 1
        inpargs = (ips.n, ips.mass, ips.eps2, ips.rdot[:p],
                   jps.n, jps.mass, jps.eps2, jps.rdot[:p])

        outargs = (ips.rdot[2:2+p],)

        self.kernel.set_args(inpargs, outargs)


class Acc_rectangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'acc_kernel_rectangle'
        super(Acc_rectangle, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        p = 1
        inpargs = (ips.n, ips.mass, ips.eps2, ips.rdot[:p],
                   jps.n, jps.mass, jps.eps2, jps.rdot[:p])

        outargs = (ips.rdot[2:2+p], jps.rdot[2:2+p])

        self.kernel.set_args(inpargs, outargs)


class Acc_triangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'acc_kernel_triangle'
        super(Acc_triangle, self).__init__(name, backend)

    def set_args(self, ips, jps=None, **kwargs):
        p = 1
        inpargs = (ips.n, ips.mass, ips.eps2, ips.rdot[:p])

        outargs = (ips.rdot[2:2+p],)

        self.kernel.set_args(inpargs, outargs)


class AccJrk(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'acc_jrk_kernel'
        super(AccJrk, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        p = 2
        inpargs = (ips.n, ips.mass, ips.eps2, ips.rdot[:p],
                   jps.n, jps.mass, jps.eps2, jps.rdot[:p])

        outargs = (ips.rdot[2:2+p],)

        self.kernel.set_args(inpargs, outargs)


class AccJrk_rectangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'acc_jrk_kernel_rectangle'
        super(AccJrk_rectangle, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        p = 2
        inpargs = (ips.n, ips.mass, ips.eps2, ips.rdot[:p],
                   jps.n, jps.mass, jps.eps2, jps.rdot[:p])

        outargs = (ips.rdot[2:2+p], jps.rdot[2:2+p])

        self.kernel.set_args(inpargs, outargs)


class AccJrk_triangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'acc_jrk_kernel_triangle'
        super(AccJrk_triangle, self).__init__(name, backend)

    def set_args(self, ips, jps=None, **kwargs):
        p = 2
        inpargs = (ips.n, ips.mass, ips.eps2, ips.rdot[:p])

        outargs = (ips.rdot[2:2+p],)

        self.kernel.set_args(inpargs, outargs)


class SnpCrk(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'snp_crk_kernel'
        super(SnpCrk, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        p = 4
        jps = jps.copy()
        inpargs = (ips.n, ips.mass, ips.eps2, ips.rdot[:p],
                   jps.n, jps.mass, jps.eps2, jps.rdot[:p])

        outargs = (ips.rdot[2:2+p],)

        self.kernel.set_args(inpargs, outargs)


class SnpCrk_rectangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'snp_crk_kernel_rectangle'
        super(SnpCrk_rectangle, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        p = 4
        inpargs = (ips.n, ips.mass, ips.eps2, ips.rdot[:p],
                   jps.n, jps.mass, jps.eps2, jps.rdot[:p])

        outargs = (ips.rdot[2:2+p], jps.rdot[2:2+p])

        self.kernel.set_args(inpargs, outargs)


class SnpCrk_triangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'snp_crk_kernel_triangle'
        super(SnpCrk_triangle, self).__init__(name, backend)

    def set_args(self, ips, jps=None, **kwargs):
        p = 4
        inpargs = (ips.n, ips.mass, ips.eps2, ips.rdot[:p])

        outargs = (ips.rdot[2:2+p],)

        self.kernel.set_args(inpargs, outargs)


class Tstep(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'tstep_kernel'
        super(Tstep, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        p = 2
        inpargs = (ips.n, ips.mass, ips.eps2, ips.rdot[:p],
                   jps.n, jps.mass, jps.eps2, jps.rdot[:p],
                   kwargs['eta'])

        outargs = (ips.tstep, ips.tstep_sum)

        self.kernel.set_args(inpargs, outargs)


class Tstep_rectangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'tstep_kernel_rectangle'
        super(Tstep_rectangle, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        p = 2
        inpargs = (ips.n, ips.mass, ips.eps2, ips.rdot[:p],
                   jps.n, jps.mass, jps.eps2, jps.rdot[:p],
                   kwargs['eta'])

        outargs = (ips.tstep, ips.tstep_sum,
                   jps.tstep, jps.tstep_sum)

        self.kernel.set_args(inpargs, outargs)


class Tstep_triangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'tstep_kernel_triangle'
        super(Tstep_triangle, self).__init__(name, backend)

    def set_args(self, ips, jps=None, **kwargs):
        p = 2
        inpargs = (ips.n, ips.mass, ips.eps2, ips.rdot[:p],
                   kwargs['eta'])

        outargs = (ips.tstep, ips.tstep_sum)

        self.kernel.set_args(inpargs, outargs)


class PNAcc(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'pnacc_kernel'
        super(PNAcc, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        try:
            clight = self.clight
        except AttributeError:
            pn = pn_struct(kwargs['pn'])
            clight = self.kernel.make_struct('CLIGHT', **pn)
            self.clight = clight

        p = 2
        inpargs = (ips.n, ips.mass, ips.eps2, ips.rdot[:p],
                   jps.n, jps.mass, jps.eps2, jps.rdot[:p],
                   clight)

        outargs = (ips.pnacc,)

        self.kernel.set_args(inpargs, outargs)


class PNAcc_rectangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'pnacc_kernel_rectangle'
        super(PNAcc_rectangle, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        try:
            clight = self.clight
        except AttributeError:
            pn = pn_struct(kwargs['pn'])
            clight = self.kernel.make_struct('CLIGHT', **pn)
            self.clight = clight

        p = 2
        inpargs = (ips.n, ips.mass, ips.eps2, ips.rdot[:p],
                   jps.n, jps.mass, jps.eps2, jps.rdot[:p],
                   clight)

        outargs = (ips.pnacc, jps.pnacc)

        self.kernel.set_args(inpargs, outargs)


class PNAcc_triangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'pnacc_kernel_triangle'
        super(PNAcc_triangle, self).__init__(name, backend)

    def set_args(self, ips, jps=None, **kwargs):
        try:
            clight = self.clight
        except AttributeError:
            pn = pn_struct(kwargs['pn'])
            clight = self.kernel.make_struct('CLIGHT', **pn)
            self.clight = clight

        p = 2
        inpargs = (ips.n, ips.mass, ips.eps2, ips.rdot[:p],
                   clight)

        outargs = (ips.pnacc,)

        self.kernel.set_args(inpargs, outargs)


class Sakura(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'sakura_kernel'
        super(Sakura, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        if not hasattr(ips, 'dpos'):
            ips.register_attribute('dpos', '{nd}, {nb}', 'real_t')
        if not hasattr(ips, 'dvel'):
            ips.register_attribute('dvel', '{nd}, {nb}', 'real_t')

        inpargs = (ips.n,
                   ips.mass, ips.rdot[0][0], ips.rdot[0][1], ips.rdot[0][2],
                   ips.eps2, ips.rdot[1][0], ips.rdot[1][1], ips.rdot[1][2],
                   jps.n,
                   jps.mass, jps.rdot[0][0], jps.rdot[0][1], jps.rdot[0][2],
                   jps.eps2, jps.rdot[1][0], jps.rdot[1][1], jps.rdot[1][2],
                   kwargs['dt'], kwargs['flag'])

        outargs = (ips.dpos[0], ips.dpos[1], ips.dpos[2],
                   ips.dvel[0], ips.dvel[1], ips.dvel[2])

        self.kernel.set_args(inpargs, outargs)


class Sakura_rectangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'sakura_kernel_rectangle'
        super(Sakura_rectangle, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        if not hasattr(ips, 'dpos'):
            ips.register_attribute('dpos', '{nd}, {nb}', 'real_t')
        if not hasattr(ips, 'dvel'):
            ips.register_attribute('dvel', '{nd}, {nb}', 'real_t')

        if not hasattr(jps, 'dpos'):
            jps.register_attribute('dpos', '{nd}, {nb}', 'real_t')
        if not hasattr(jps, 'dvel'):
            jps.register_attribute('dvel', '{nd}, {nb}', 'real_t')

        inpargs = (ips.n,
                   ips.mass, ips.rdot[0][0], ips.rdot[0][1], ips.rdot[0][2],
                   ips.eps2, ips.rdot[1][0], ips.rdot[1][1], ips.rdot[1][2],
                   jps.n,
                   jps.mass, jps.rdot[0][0], jps.rdot[0][1], jps.rdot[0][2],
                   jps.eps2, jps.rdot[1][0], jps.rdot[1][1], jps.rdot[1][2],
                   kwargs['dt'], kwargs['flag'])

        outargs = (ips.dpos[0], ips.dpos[1], ips.dpos[2],
                   ips.dvel[0], ips.dvel[1], ips.dvel[2],
                   jps.dpos[0], jps.dpos[1], jps.dpos[2],
                   jps.dvel[0], jps.dvel[1], jps.dvel[2])

        self.kernel.set_args(inpargs, outargs)


class Sakura_triangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'sakura_kernel_triangle'
        super(Sakura_triangle, self).__init__(name, backend)

    def set_args(self, ips, jps=None, **kwargs):
        if not hasattr(ips, 'dpos'):
            ips.register_attribute('dpos', '{nd}, {nb}', 'real_t')
        if not hasattr(ips, 'dvel'):
            ips.register_attribute('dvel', '{nd}, {nb}', 'real_t')

        inpargs = (ips.n,
                   ips.mass, ips.rdot[0][0], ips.rdot[0][1], ips.rdot[0][2],
                   ips.eps2, ips.rdot[1][0], ips.rdot[1][1], ips.rdot[1][2],
                   kwargs['dt'], kwargs['flag'])

        outargs = (ips.dpos[0], ips.dpos[1], ips.dpos[2],
                   ips.dvel[0], ips.dvel[1], ips.dvel[2])

        self.kernel.set_args(inpargs, outargs)


class NregX(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'nreg_Xkernel'
        super(NregX, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        if not hasattr(ips, 'mr'):
            ips.register_attribute('mr', '{nd}, {nb}', 'real_t')
        if not hasattr(ips, 'u'):
            ips.register_attribute('u', '{nb}', 'real_t')

        inpargs = (ips.n,
                   ips.mass, ips.rdot[0][0], ips.rdot[0][1], ips.rdot[0][2],
                   ips.eps2, ips.rdot[1][0], ips.rdot[1][1], ips.rdot[1][2],
                   jps.n,
                   jps.mass, jps.rdot[0][0], jps.rdot[0][1], jps.rdot[0][2],
                   jps.eps2, jps.rdot[1][0], jps.rdot[1][1], jps.rdot[1][2],
                   kwargs['dt'])

        outargs = (ips.mr[0], ips.mr[1], ips.mr[2],
                   ips.rdot[2][0], ips.rdot[2][1], ips.rdot[2][2],
                   ips.u)

        self.kernel.set_args(inpargs, outargs)


class NregX_rectangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'nreg_Xkernel_rectangle'
        super(NregX_rectangle, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        if not hasattr(ips, 'mr'):
            ips.register_attribute('mr', '{nd}, {nb}', 'real_t')
        if not hasattr(ips, 'u'):
            ips.register_attribute('u', '{nb}', 'real_t')

        if not hasattr(jps, 'mr'):
            jps.register_attribute('mr', '{nd}, {nb}', 'real_t')
        if not hasattr(jps, 'u'):
            jps.register_attribute('u', '{nb}', 'real_t')

        inpargs = (ips.n,
                   ips.mass, ips.rdot[0][0], ips.rdot[0][1], ips.rdot[0][2],
                   ips.eps2, ips.rdot[1][0], ips.rdot[1][1], ips.rdot[1][2],
                   jps.n,
                   jps.mass, jps.rdot[0][0], jps.rdot[0][1], jps.rdot[0][2],
                   jps.eps2, jps.rdot[1][0], jps.rdot[1][1], jps.rdot[1][2],
                   kwargs['dt'])

        outargs = (ips.mr[0], ips.mr[1], ips.mr[2],
                   ips.rdot[2][0], ips.rdot[2][1], ips.rdot[2][2],
                   ips.u,
                   jps.mr[0], jps.mr[1], jps.mr[2],
                   jps.rdot[2][0], jps.rdot[2][1], jps.rdot[2][2],
                   jps.u)

        self.kernel.set_args(inpargs, outargs)


class NregX_triangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'nreg_Xkernel_triangle'
        super(NregX_triangle, self).__init__(name, backend)

    def set_args(self, ips, jps=None, **kwargs):
        if not hasattr(ips, 'mr'):
            ips.register_attribute('mr', '{nd}, {nb}', 'real_t')
        if not hasattr(ips, 'u'):
            ips.register_attribute('u', '{nb}', 'real_t')

        inpargs = (ips.n,
                   ips.mass, ips.rdot[0][0], ips.rdot[0][1], ips.rdot[0][2],
                   ips.eps2, ips.rdot[1][0], ips.rdot[1][1], ips.rdot[1][2],
                   kwargs['dt'])

        outargs = (ips.mr[0], ips.mr[1], ips.mr[2],
                   ips.rdot[2][0], ips.rdot[2][1], ips.rdot[2][2],
                   ips.u)

        self.kernel.set_args(inpargs, outargs)


class NregV(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'nreg_Vkernel'
        super(NregV, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        if not hasattr(ips, 'mv'):
            ips.register_attribute('mv', '{nd}, {nb}', 'real_t')
        if not hasattr(ips, 'mk'):
            ips.register_attribute('mk', '{nb}', 'real_t')

        inpargs = (ips.n,
                   ips.mass, ips.rdot[1][0], ips.rdot[1][1], ips.rdot[1][2],
                   ips.rdot[2][0], ips.rdot[2][1], ips.rdot[2][2],
                   jps.n,
                   jps.mass, jps.rdot[1][0], jps.rdot[1][1], jps.rdot[1][2],
                   jps.rdot[2][0], jps.rdot[2][1], jps.rdot[2][2],
                   kwargs['dt'])

        outargs = (ips.mv[0], ips.mv[1], ips.mv[2], ips.mk)

        self.kernel.set_args(inpargs, outargs)


class NregV_rectangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'nreg_Vkernel_rectangle'
        super(NregV_rectangle, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        if not hasattr(ips, 'mv'):
            ips.register_attribute('mv', '{nd}, {nb}', 'real_t')
        if not hasattr(ips, 'mk'):
            ips.register_attribute('mk', '{nb}', 'real_t')

        if not hasattr(jps, 'mv'):
            jps.register_attribute('mv', '{nd}, {nb}', 'real_t')
        if not hasattr(jps, 'mk'):
            jps.register_attribute('mk', '{nb}', 'real_t')

        inpargs = (ips.n,
                   ips.mass, ips.rdot[1][0], ips.rdot[1][1], ips.rdot[1][2],
                   ips.rdot[2][0], ips.rdot[2][1], ips.rdot[2][2],
                   jps.n,
                   jps.mass, jps.rdot[1][0], jps.rdot[1][1], jps.rdot[1][2],
                   jps.rdot[2][0], jps.rdot[2][1], jps.rdot[2][2],
                   kwargs['dt'])

        outargs = (ips.mv[0], ips.mv[1], ips.mv[2], ips.mk,
                   jps.mv[0], jps.mv[1], jps.mv[2], jps.mk)

        self.kernel.set_args(inpargs, outargs)


class NregV_triangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        name = 'nreg_Vkernel_triangle'
        super(NregV_triangle, self).__init__(name, backend)

    def set_args(self, ips, jps=None, **kwargs):
        if not hasattr(ips, 'mv'):
            ips.register_attribute('mv', '{nd}, {nb}', 'real_t')
        if not hasattr(ips, 'mk'):
            ips.register_attribute('mk', '{nb}', 'real_t')

        inpargs = (ips.n,
                   ips.mass, ips.rdot[1][0], ips.rdot[1][1], ips.rdot[1][2],
                   ips.rdot[2][0], ips.rdot[2][1], ips.rdot[2][2],
                   kwargs['dt'])

        outargs = (ips.mv[0], ips.mv[1], ips.mv[2], ips.mk)

        self.kernel.set_args(inpargs, outargs)


class Kepler(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        if backend == 'CL':    # No need for CL support.
            backend = 'C'      # C is fast enough!

        name = 'kepler_solver_kernel'
        super(Kepler, self).__init__(name, backend)

    def set_args(self, ips, jps, **kwargs):
        inpargs = (ips.n,
                   ips.mass, ips.rdot[0][0], ips.rdot[0][1], ips.rdot[0][2],
                   ips.eps2, ips.rdot[1][0], ips.rdot[1][1], ips.rdot[1][2],
                   jps.n,
                   jps.mass, jps.rdot[0][0], jps.rdot[0][1], jps.rdot[0][2],
                   jps.eps2, jps.rdot[1][0], jps.rdot[1][1], jps.rdot[1][2],
                   kwargs['dt'])

        outargs = (ips.rdot[0][0], ips.rdot[0][1], ips.rdot[0][2],
                   ips.rdot[1][0], ips.rdot[1][1], ips.rdot[1][2],
                   jps.rdot[0][0], jps.rdot[0][1], jps.rdot[0][2],
                   jps.rdot[1][0], jps.rdot[1][1], jps.rdot[1][2])

        self.kernel.set_args(inpargs, outargs)


def get_kernel(name, backend=options.backend):
    kernel = globals()[name](backend)

    def func(ips, jps, **kwargs):
        if ips != jps:
            kernel(jps, ips, **kwargs)
        return kernel(ips, jps, **kwargs)

    if backend == 'C' and name not in ('Kepler',):
        kernel_r = globals()[name+'_rectangle'](backend)
        kernel_t = globals()[name+'_triangle'](backend)

        def c_func(ips, jps, **kwargs):
            if ips != jps:
                return kernel_r(ips, jps, **kwargs)
            return kernel_t(ips, ips, **kwargs)

        return c_func

    return func


# -- End of File --
