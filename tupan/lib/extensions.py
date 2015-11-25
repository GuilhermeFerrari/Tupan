# -*- coding: utf-8 -*-
#

"""
This module implements highlevel interfaces for C/CL-extensions.
"""

from __future__ import print_function, division
import logging
from ..config import options
from .utils.timing import timings, bind_all


LOGGER = logging.getLogger(__name__)


@bind_all(timings)
class PN(object):
    """This class holds the values of the PN parameters.

    """
    def __init__(self, order=0, clight='inf'):
        self.order = int(order)
        clight = float(clight)
        for i in range(1, 8):
            setattr(self, 'inv'+str(i), clight**(-i))


pn = PN()


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

    def map_buffers(self, *args, **kwargs):
        return self.kernel.map_buffers(*args, **kwargs)

    def __call__(self, ips, jps, **kwargs):
        self.set_args(ips, jps, **kwargs)
        self.kernel.run()
        return self.map_buffers()


@bind_all(timings)
class Phi(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(Phi, self).__init__('phi_kernel', backend)

    def set_args(self, ips, jps, **kwargs):
        inpargs = (ips.n,
                   ips.mass, ips.pos[0], ips.pos[1], ips.pos[2],
                   ips.eps2,
                   jps.n,
                   jps.mass, jps.pos[0], jps.pos[1], jps.pos[2],
                   jps.eps2)

        outargs = (ips.phi,)

        self.kernel.set_args(inpargs, outargs)


@bind_all(timings)
class Acc(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(Acc, self).__init__('acc_kernel', backend)

    def set_args(self, ips, jps, **kwargs):
        inpargs = (ips.n,
                   ips.mass, ips.pos[0], ips.pos[1], ips.pos[2],
                   ips.eps2,
                   jps.n,
                   jps.mass, jps.pos[0], jps.pos[1], jps.pos[2],
                   jps.eps2)

        outargs = (ips.acc[0], ips.acc[1], ips.acc[2])

        self.kernel.set_args(inpargs, outargs)


@bind_all(timings)
class Acc_rectangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(Acc_rectangle, self).__init__('acc_kernel_rectangle', backend)

    def set_args(self, ips, jps, **kwargs):
        inpargs = (ips.n,
                   ips.mass, ips.pos[0], ips.pos[1], ips.pos[2],
                   ips.eps2,
                   jps.n,
                   jps.mass, jps.pos[0], jps.pos[1], jps.pos[2],
                   jps.eps2)

        outargs = (ips.acc[0], ips.acc[1], ips.acc[2],
                   jps.acc[0], jps.acc[1], jps.acc[2])

        self.kernel.set_args(inpargs, outargs)


@bind_all(timings)
class Acc_triangle(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(Acc_triangle, self).__init__('acc_kernel_triangle', backend)

    def set_args(self, ips, jps=None, **kwargs):
        inpargs = (ips.n,
                   ips.mass, ips.pos[0], ips.pos[1], ips.pos[2],
                   ips.eps2)

        outargs = (ips.acc[0], ips.acc[1], ips.acc[2])

        self.kernel.set_args(inpargs, outargs)


@bind_all(timings)
class AccJrk(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(AccJrk, self).__init__('acc_jrk_kernel', backend)

    def set_args(self, ips, jps, **kwargs):
        inpargs = (ips.n,
                   ips.mass, ips.pos[0], ips.pos[1], ips.pos[2],
                   ips.eps2, ips.vel[0], ips.vel[1], ips.vel[2],
                   jps.n,
                   jps.mass, jps.pos[0], jps.pos[1], jps.pos[2],
                   jps.eps2, jps.vel[0], jps.vel[1], jps.vel[2])

        outargs = (ips.acc[0], ips.acc[1], ips.acc[2],
                   ips.jrk[0], ips.jrk[1], ips.jrk[2])

        self.kernel.set_args(inpargs, outargs)


@bind_all(timings)
class SnpCrk(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(SnpCrk, self).__init__('snp_crk_kernel', backend)

    def set_args(self, ips, jps, **kwargs):
        inpargs = (ips.n,
                   ips.mass, ips.pos[0], ips.pos[1], ips.pos[2],
                   ips.eps2, ips.vel[0], ips.vel[1], ips.vel[2],
                   ips.acc[0], ips.acc[1], ips.acc[2],
                   ips.jrk[0], ips.jrk[1], ips.jrk[2],
                   jps.n,
                   jps.mass, jps.pos[0], jps.pos[1], jps.pos[2],
                   jps.eps2, jps.vel[0], jps.vel[1], jps.vel[2],
                   jps.acc[0], jps.acc[1], jps.acc[2],
                   jps.jrk[0], jps.jrk[1], jps.jrk[2])

        outargs = (ips.snp[0], ips.snp[1], ips.snp[2],
                   ips.crk[0], ips.crk[1], ips.crk[2])

        self.kernel.set_args(inpargs, outargs)


@bind_all(timings)
class Tstep(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(Tstep, self).__init__('tstep_kernel', backend)

    def set_args(self, ips, jps, **kwargs):
        inpargs = (ips.n,
                   ips.mass, ips.pos[0], ips.pos[1], ips.pos[2],
                   ips.eps2, ips.vel[0], ips.vel[1], ips.vel[2],
                   jps.n,
                   jps.mass, jps.pos[0], jps.pos[1], jps.pos[2],
                   jps.eps2, jps.vel[0], jps.vel[1], jps.vel[2],
                   kwargs['eta'])

        outargs = (ips.tstep, ips.tstepij)

        self.kernel.set_args(inpargs, outargs)


@bind_all(timings)
class PNAcc(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(PNAcc, self).__init__('pnacc_kernel', backend)
        self.clight = None

    def set_args(self, ips, jps, **kwargs):
        if self.clight is None:
            self.clight = self.kernel.make_struct('CLIGHT', **vars(pn))

        if kwargs['use_auxvel']:
            inpargs = (ips.n,
                       ips.mass, ips.pos[0], ips.pos[1], ips.pos[2],
                       ips.eps2, ips.wel[0], ips.wel[1], ips.wel[2],
                       jps.n,
                       jps.mass, jps.pos[0], jps.pos[1], jps.pos[2],
                       jps.eps2, jps.wel[0], jps.wel[1], jps.wel[2],
                       self.clight)
        else:
            inpargs = (ips.n,
                       ips.mass, ips.pos[0], ips.pos[1], ips.pos[2],
                       ips.eps2, ips.vel[0], ips.vel[1], ips.vel[2],
                       jps.n,
                       jps.mass, jps.pos[0], jps.pos[1], jps.pos[2],
                       jps.eps2, jps.vel[0], jps.vel[1], jps.vel[2],
                       self.clight)

        outargs = (ips.pnacc[0], ips.pnacc[1], ips.pnacc[2])

        self.kernel.set_args(inpargs, outargs)


@bind_all(timings)
class Sakura(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(Sakura, self).__init__('sakura_kernel', backend)

    def set_args(self, ips, jps, **kwargs):
        if not hasattr(ips, 'dpos'):
            ips.register_attribute('dpos', '3, {n}', 'real_t')
        if not hasattr(ips, 'dvel'):
            ips.register_attribute('dvel', '3, {n}', 'real_t')

        inpargs = (ips.n,
                   ips.mass, ips.pos[0], ips.pos[1], ips.pos[2],
                   ips.eps2, ips.vel[0], ips.vel[1], ips.vel[2],
                   jps.n,
                   jps.mass, jps.pos[0], jps.pos[1], jps.pos[2],
                   jps.eps2, jps.vel[0], jps.vel[1], jps.vel[2],
                   kwargs['dt'], kwargs['flag'])

        outargs = (ips.dpos[0], ips.dpos[1], ips.dpos[2],
                   ips.dvel[0], ips.dvel[1], ips.dvel[2])

        self.kernel.set_args(inpargs, outargs)


@bind_all(timings)
class NregX(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(NregX, self).__init__('nreg_Xkernel', backend)

    def set_args(self, ips, jps, **kwargs):
        if not hasattr(ips, 'mr'):
            ips.register_attribute('mr', '3, {n}', 'real_t')
        if not hasattr(ips, 'u'):
            ips.register_attribute('u', '{n}', 'real_t')

        inpargs = (ips.n,
                   ips.mass, ips.pos[0], ips.pos[1], ips.pos[2],
                   ips.eps2, ips.vel[0], ips.vel[1], ips.vel[2],
                   jps.n,
                   jps.mass, jps.pos[0], jps.pos[1], jps.pos[2],
                   jps.eps2, jps.vel[0], jps.vel[1], jps.vel[2],
                   kwargs['dt'])

        outargs = (ips.mr[0], ips.mr[1], ips.mr[2],
                   ips.acc[0], ips.acc[1], ips.acc[2],
                   ips.u)

        self.kernel.set_args(inpargs, outargs)


@bind_all(timings)
class NregV(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):
        super(NregV, self).__init__('nreg_Vkernel', backend)

    def set_args(self, ips, jps, **kwargs):
        if not hasattr(ips, 'mv'):
            ips.register_attribute('mv', '3, {n}', 'real_t')
        if not hasattr(ips, 'mk'):
            ips.register_attribute('mk', '{n}', 'real_t')

        inpargs = (ips.n,
                   ips.mass, ips.vel[0], ips.vel[1], ips.vel[2],
                   ips.acc[0], ips.acc[1], ips.acc[2],
                   jps.n,
                   jps.mass, jps.vel[0], jps.vel[1], jps.vel[2],
                   jps.acc[0], jps.acc[1], jps.acc[2],
                   kwargs['dt'])

        outargs = (ips.mv[0], ips.mv[1], ips.mv[2], ips.mk)

        self.kernel.set_args(inpargs, outargs)


@bind_all(timings)
class Kepler(AbstractExtension):
    """

    """
    def __init__(self, backend=options.backend):

        if backend == 'CL':    # No need for CL support.
            backend = 'C'      # C is fast enough!

        super(Kepler, self).__init__('kepler_solver_kernel', backend)

    def set_args(self, ips, jps, **kwargs):
        inpargs = (ips.n,
                   ips.mass, ips.pos[0], ips.pos[1], ips.pos[2],
                   ips.eps2, ips.vel[0], ips.vel[1], ips.vel[2],
                   jps.n,
                   jps.mass, jps.pos[0], jps.pos[1], jps.pos[2],
                   jps.eps2, jps.vel[0], jps.vel[1], jps.vel[2],
                   kwargs['dt'])

        outargs = (ips.pos[0], ips.pos[1], ips.pos[2],
                   ips.vel[0], ips.vel[1], ips.vel[2],
                   jps.pos[0], jps.pos[1], jps.pos[2],
                   jps.vel[0], jps.vel[1], jps.vel[2])

        self.kernel.set_args(inpargs, outargs)


def get_kernel(name, backend=options.backend):
    kernel = globals()[name](backend)

    def func(ips, jps, **kwargs):
        kernel(ips, jps, **kwargs)
        if ips != jps:
            kernel(jps, ips, **kwargs)

    if name == 'Acc' and backend == 'C':
        kernel_r = Acc_rectangle(backend)
        kernel_t = Acc_triangle(backend)

        def c_func(ips, jps, **kwargs):
            if ips != jps:
                kernel_r(jps, ips, **kwargs)
            else:
                kernel_t(ips, jps, **kwargs)

        return c_func

    return func


# -- End of File --
