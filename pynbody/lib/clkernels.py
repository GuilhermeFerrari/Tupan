#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""


from __future__ import print_function
import os
import numpy as np
import pyopencl as cl

from ggf84decor import (selftimer, addmethod)


__all__ = ['CLKernel', 'cl_p2p_acc', 'cl_p2p_phi']


path = os.path.dirname(__file__)



IUNROLL = 1#3                 # unroll for i-particles
JUNROLL = 24#16#64                # unroll for j-particles
BLOCK_SIZE = (192, 1, 1)#(256, 1, 1)#(128, 1, 1)
ENABLE_FAST_MATH = False
ENABLE_DOUBLE_PRECISION = True


fp_type = np.float32
if ENABLE_DOUBLE_PRECISION:
    fp_type = np.float64

dtype = np.dtype(fp_type)


class CLKernel(object):
    """
    This class serves as an abstraction layer to manage CL kernels.
    """

    def __init__(self, fname, options=' '):
        """
        Setup a kernel from the *.cl source file.
        """
        def get_from(source, pattern):
            for line in source.splitlines():
                if pattern in line:
                    return line.split()[-1]

        # Read the source program and the output shape.
        self._name = (os.path.split(fname)[1]).split('.')[0]
        with open(fname, 'r') as fobj:
            self._source = fobj.read()
            self._output_shape = get_from(self._source, 'Output shape')

        # Gets the count of flops from the core function.
        fname = fname.replace('.cl', '_core.h')
        with open(fname, 'r') as fobj:
            core_src = fobj.read()
            self._flops = int(get_from(core_src, 'Total flop count'))

        if ENABLE_DOUBLE_PRECISION:
            options += ' -D DOUBLE'
        if ENABLE_FAST_MATH:
            options += ' -cl-fast-relaxed-math'

        self._options = options

        self._ctx = None
        self._queue = None
        self._kernel = None
        self.is_available = False


    def build_kernel(self):
        """
        Builds CL kernels from source.
        """
        print("Building CL kernel '{0}'...".format(self._name))
        self._ctx = cl.create_some_context()
        self._queue = cl.CommandQueue(self._ctx)
        prog = cl.Program(self._ctx, self._source).build(options=self._options)
        self._kernel = getattr(prog, self._name)
        self.is_available = True
        print("Building CL kernel '{0}'... done.\n".format(self._name))


    def has_built(self):
        if self._kernel is None:
            return False
        return True


    @selftimer
    def _call_kernel(self, queue, dev_args):
        """
        Calls a kernel on a CL device.
        """
        self._kernel(queue, *dev_args).wait()


    def _kernel_manager(self, global_size, local_size, inputargs,
                        destshape, local_mem_size, gflops_count):
        """
        Manages a kernel call on a CL device.
        """
        mf = cl.mem_flags
        dev_args = [global_size, local_size]
        for item in inputargs:
            if isinstance(item, np.ndarray):
                dev_args.append(cl.Buffer(
                                self._ctx, mf.READ_ONLY | mf.COPY_HOST_PTR,
                                hostbuf=item))
            else:
                dev_args.append(item)

        destsize = reduce(lambda x, y: x * y, destshape) * dtype.itemsize
        dev_dest = cl.Buffer(self._ctx, mf.WRITE_ONLY, size=destsize)
        dev_args.append(dev_dest)

        for size in local_mem_size:
            dev_args.append(cl.LocalMemory(size))

        self._call_kernel(self._queue, dev_args)

#        elapsed = self._call_kernel.selftimer.elapsed
#        print('Execution time of CL kernel: {0:g} s'.format(elapsed))
#        print('CL kernel Gflops/s: {0:g}'.format(gflops_count/elapsed))

        dest = np.empty(destshape, dtype=dtype)

        cl.enqueue_read_buffer(self._queue, dev_dest, dest).wait()

        return dest


    def run(self, bi, bj):
        """
        Runs the calculation on a CL device.
        """

        ni = len(bi)
        nj = len(bj)

        local_size = BLOCK_SIZE
        global_size = (ni + IUNROLL * local_size[0] - 1)
        global_size //= IUNROLL * local_size[0]
        global_size *= local_size[0]
        global_size = (global_size, 1, 1)

#        print('-'*25)
#        print('lengths: ', (ni, nj))
#        print('unroll: ', IUNROLL)
#        print('local_size: ', local_size)
#        print('global_size: ', global_size)
#        print('diff: ', IUNROLL * global_size[0] - ni)

        iposeps2 = np.vstack((bi.pos.T, bi.eps2)).T.copy().astype(fp_type)
        imass = bi.mass.copy().astype(fp_type)
        jposeps2 = np.vstack((bj.pos.T, bj.eps2)).T.copy().astype(fp_type)
        jmass = bj.mass.copy().astype(fp_type)

        inputargs = (np.uint32(ni), np.uint32(nj),
                     iposeps2, imass, jposeps2, jmass)
        destshape = eval(self._output_shape.format(ni=ni))
        mem_size = reduce(lambda x, y: x * y, local_size) * dtype.itemsize
        local_mem_size = (4*mem_size, mem_size)
        gflops_count = self._flops * ni * nj * 1.0e-9

        dest = self._kernel_manager(global_size, local_size, inputargs,
                                    destshape, local_mem_size, gflops_count)

#        elapsed = self._kernel_manager.selftimer.elapsed
#        print('Total kernel_manager time: {0:g} s'.format(elapsed))
#        print('kernel_manager Gflops/s: {0:g}'.format(gflops_count/elapsed))

        return dest


    def print_profile(self, ni, nj):
        elapsed = self.run.selftimer.elapsed
        gflops_count = self._flops * ni * nj * 1.0e-9
        print('--  '*3)
        print('Total kernel-run time: {0:g} s'.format(elapsed))
        print('kernel-run Gflops/s: {0:g}'.format(gflops_count/elapsed))




options = ' -I {path}'.format(path=os.path.join(path, 'gravity'))
options += ' -D IUNROLL={iunroll}'.format(iunroll=IUNROLL)
options += ' -D JUNROLL={junroll}'.format(junroll=JUNROLL)


fname = os.path.join(path, 'gravity', 'p2p_phi_kernel.cl')
cl_p2p_phi = CLKernel(fname, options)
fname = os.path.join(path, 'gravity', 'p2p_acc_kernel.cl')
cl_p2p_acc = CLKernel(fname, options)
#fname = os.path.join(path, 'gravity', 'p2p_acc_kernel_gpugems3.cl')
#cl_p2p_acc_gpugems3 = CLKernel(fname, options)





#@addmethod(clkernel.cl_p2p_acc_gpugems3)
#@selftimer
#def print_name(self):
#    """doc of print_name"""
#    print('*** name: ', self._name, self.flops, '***')

#clkernel.cl_p2p_acc_gpugems3.print_name()






########## end of file ##########
