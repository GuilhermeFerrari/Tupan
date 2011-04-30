#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""


from __future__ import print_function
import os
import time
import numpy as np
import pyopencl as cl

from pynbody.lib.decorators import (selftimer, addmethod)

path = os.path.dirname(__file__)



IUNROLL = 3                 # unroll for i-particles
JUNROLL = 64                # unroll for j-particles
BLOCK_SIZE = (128, 1, 1)
ENABLE_FAST_MATH = True
ENABLE_DOUBLE_PRECISION = True


fp_type = np.float32
if ENABLE_DOUBLE_PRECISION:
    fp_type = np.float64

dtype = np.dtype(fp_type)


ctx = cl.create_some_context()
_properties = cl.command_queue_properties.PROFILING_ENABLE
queue = cl.CommandQueue(ctx, properties=_properties)


@selftimer
class Kernels(object):
    """
    This class serves as an abstraction layer to manage CL kernels.
    """

    def __init__(self, fname, options=' '):
        """
        Setup a kernel from .cl source file.
        """
        def get_from(source, pattern):
            for line in source.splitlines():
                if pattern in line:
                    return line.split()[-1]
        self.name = fname.split('.')[0]
        fname = os.path.join(path, fname)
        with open(fname, 'r') as f:
            self.source = f.read()
            self.flops = int(get_from(self.source, 'Total flop count'))
            self.output_shape = get_from(self.source, 'Output shape')
            if ENABLE_DOUBLE_PRECISION:
                options += ' -D DOUBLE'
            if ENABLE_FAST_MATH:
                options += ' -cl-fast-relaxed-math'
            prog = cl.Program(ctx, self.source).build(options=options)
            self.kernel = getattr(prog, self.name)

    @selftimer
    def call_kernel(self, queue, dev_args):
        """
        Call a kernel on a CL device.
        """
        self.kernel(queue, *dev_args).wait()

    @selftimer
    def kernel_manager(self, global_size, local_size, inputargs,
                       destshape, local_mem_size, gflops_count):
        """
        Manages a kernel call on a CL device.
        """
        mf = cl.mem_flags
        dev_args = [global_size, local_size]
        for item in inputargs:
            if isinstance(item, np.ndarray):
                dev_args.append(cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR,
                                hostbuf=item))
            else:
                dev_args.append(item)

        destsize = reduce(lambda x, y: x * y, destshape) * dtype.itemsize
        dev_dest = cl.Buffer(ctx, mf.WRITE_ONLY, size=destsize)
        dev_args.append(dev_dest)

        for size in local_mem_size:
            dev_args.append(cl.LocalMemory(size))

        self.call_kernel(queue, dev_args)

#        elapsed = self.call_kernel.selftimer.elapsed
#        print('Execution time of CL kernel: {0:g} s'.format(elapsed))
#        print('CL kernel Gflops/s: {0:g}'.format(gflops_count/elapsed))

        dest = np.empty(destshape, dtype=dtype)

        cl.enqueue_read_buffer(queue, dev_dest, dest).wait()

        return dest

    @selftimer
    def run(self, bi, bj):
        """
        Runs the calculation on a CL device.
        """

        ni = len(bi)
        nj = len(bj)

        local_size = BLOCK_SIZE
        global_size = (nj + IUNROLL * local_size[0] - 1)
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
        ivelmass = np.vstack((bi.vel.T, bi.mass)).T.copy().astype(fp_type)
        jposeps2 = np.vstack((bj.pos.T, bj.eps2)).T.copy().astype(fp_type)
        jvelmass = np.vstack((bj.vel.T, bj.mass)).T.copy().astype(fp_type)

        inputargs = (np.uint32(ni), np.uint32(nj),
                     iposeps2, ivelmass, jposeps2, jvelmass)
        destshape = eval(self.output_shape.format(ni=ni))
        mem_size = reduce(lambda x, y: x * y, local_size) * dtype.itemsize
        local_mem_size = (4*mem_size, 4*mem_size)
        gflops_count = self.flops * ni * nj * 1.0e-9

        dest = self.kernel_manager(global_size, local_size, inputargs,
                                   destshape, local_mem_size, gflops_count)

#        elapsed = self.kernel_manager.selftimer.elapsed
#        print('Total kernel_manager time: {0:g} s'.format(elapsed))
#        print('kernel_manager Gflops/s: {0:g}'.format(gflops_count/elapsed))

        return dest





options = '-D IUNROLL={iunroll} -D JUNROLL={junroll}'.format(iunroll=IUNROLL,
                                                             junroll=JUNROLL)

# setup the potential kernel
p2p_pot_kernel = Kernels('p2p_pot_kernel.cl', options)

# setup the acceleration kernel
p2p_acc_kernel = Kernels('p2p_acc_kernel.cl', options)
#p2p_acc_kernel = Kernels('p2p_acc_kernel_gpugems3.cl', options)

# setup the acceleration kernel (gpugems3)
p2p_acc_kernel_gpugems3 = Kernels('p2p_acc_kernel_gpugems3.cl', options)



@addmethod(p2p_acc_kernel_gpugems3)
@selftimer
def print_name(self):
    """doc of print_name"""
    print('*** name: ', self.name, self.flops, '***')

#p2p_acc_kernel_gpugems3.print_name()


########## end of file ##########
