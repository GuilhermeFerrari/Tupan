#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module implements a minimal class for gravitational interactions
between particles in Newtonian and post-Newtonian approach.
"""


import numpy as np
from .extensions import kernels
from .utils.timing import decallmethods, timings
from .utils.dtype import *


__all__ = ["Phi", "phi",
           "Acc", "acc",
           "Tstep", "tstep",
           "PNAcc", "pnacc",
           "AccJerk", "acc_jerk"]


@decallmethods(timings)
class Clight(object):
    """
    This class holds the PN-order and some inverse powers of clight.
    """
    def __init__(self, pn_order, clight):
        self.pn_order = int(pn_order)
        self.inv1 = 1.0/float(clight)
        self.inv2 = self.inv1**2
        self.inv3 = self.inv1**3
        self.inv4 = self.inv1**4
        self.inv5 = self.inv1**5
        self.inv6 = self.inv1**6
        self.inv7 = self.inv1**7



@decallmethods(timings)
class Phi(object):
    """

    """
    def __init__(self, libgrav):
        self.kernel = libgrav.p2p_phi_kernel
        self.kernel.local_size = 512
        self.phi = np.zeros(0, dtype=REAL)
        self.max_output_size = 0

        self.kernel.set_local_memory(19, 1)
        self.kernel.set_local_memory(20, 1)
        self.kernel.set_local_memory(21, 1)
        self.kernel.set_local_memory(22, 1)
        self.kernel.set_local_memory(23, 1)
        self.kernel.set_local_memory(24, 1)
        self.kernel.set_local_memory(25, 1)
        self.kernel.set_local_memory(26, 1)


    def set_args(self, iobj, jobj):
        ni = iobj.n
        nj = jobj.n

        if ni > self.max_output_size:
            self.phi = np.zeros(ni, dtype=REAL)
            self.max_output_size = ni

        self.kernel.global_size = ni
        self.kernel.set_int(0, ni)
        self.kernel.set_input_buffer(1, iobj.x)
        self.kernel.set_input_buffer(2, iobj.y)
        self.kernel.set_input_buffer(3, iobj.z)
        self.kernel.set_input_buffer(4, iobj.mass)
        self.kernel.set_input_buffer(5, iobj.vx)
        self.kernel.set_input_buffer(6, iobj.vy)
        self.kernel.set_input_buffer(7, iobj.vz)
        self.kernel.set_input_buffer(8, iobj.eps2)
        self.kernel.set_int(9, nj)
        self.kernel.set_input_buffer(10, jobj.x)
        self.kernel.set_input_buffer(11, jobj.y)
        self.kernel.set_input_buffer(12, jobj.z)
        self.kernel.set_input_buffer(13, jobj.mass)
        self.kernel.set_input_buffer(14, jobj.vx)
        self.kernel.set_input_buffer(15, jobj.vy)
        self.kernel.set_input_buffer(16, jobj.vz)
        self.kernel.set_input_buffer(17, jobj.eps2)
        self.kernel.set_output_buffer(18, self.phi[:ni])


    def run(self):
        self.kernel.run()


    def get_result(self):
        return self.kernel.get_result()[0]



@decallmethods(timings)
class Acc(object):
    """

    """
    def __init__(self, libgrav):
        self.kernel = libgrav.p2p_acc_kernel
        self.kernel.local_size = 512
        self.ax = np.zeros(0, dtype=REAL)
        self.ay = np.zeros(0, dtype=REAL)
        self.az = np.zeros(0, dtype=REAL)
        self.max_output_size = 0

        self.kernel.set_local_memory(21, 1)
        self.kernel.set_local_memory(22, 1)
        self.kernel.set_local_memory(23, 1)
        self.kernel.set_local_memory(24, 1)
        self.kernel.set_local_memory(25, 1)
        self.kernel.set_local_memory(26, 1)
        self.kernel.set_local_memory(27, 1)
        self.kernel.set_local_memory(28, 1)


    def set_args(self, iobj, jobj):
        ni = iobj.n
        nj = jobj.n

        if ni > self.max_output_size:
            self.ax = np.zeros(ni, dtype=REAL)
            self.ay = np.zeros(ni, dtype=REAL)
            self.az = np.zeros(ni, dtype=REAL)
            self.max_output_size = ni

        self.kernel.global_size = ni
        self.kernel.set_int(0, ni)
        self.kernel.set_input_buffer(1, iobj.x)
        self.kernel.set_input_buffer(2, iobj.y)
        self.kernel.set_input_buffer(3, iobj.z)
        self.kernel.set_input_buffer(4, iobj.mass)
        self.kernel.set_input_buffer(5, iobj.vx)
        self.kernel.set_input_buffer(6, iobj.vy)
        self.kernel.set_input_buffer(7, iobj.vz)
        self.kernel.set_input_buffer(8, iobj.eps2)
        self.kernel.set_int(9, nj)
        self.kernel.set_input_buffer(10, jobj.x)
        self.kernel.set_input_buffer(11, jobj.y)
        self.kernel.set_input_buffer(12, jobj.z)
        self.kernel.set_input_buffer(13, jobj.mass)
        self.kernel.set_input_buffer(14, jobj.vx)
        self.kernel.set_input_buffer(15, jobj.vy)
        self.kernel.set_input_buffer(16, jobj.vz)
        self.kernel.set_input_buffer(17, jobj.eps2)
        self.kernel.set_output_buffer(18, self.ax[:ni])
        self.kernel.set_output_buffer(19, self.ay[:ni])
        self.kernel.set_output_buffer(20, self.az[:ni])


    def run(self):
        self.kernel.run()


    def get_result(self):
        return self.kernel.get_result()



@decallmethods(timings)
class AccJerk(object):
    """

    """
    def __init__(self, libgrav):
        self.kernel = libgrav.p2p_acc_jerk_kernel
        self.kernel.local_size = 512
        self.ax = np.zeros(0, dtype=REAL)
        self.ay = np.zeros(0, dtype=REAL)
        self.az = np.zeros(0, dtype=REAL)
        self.jx = np.zeros(0, dtype=REAL)
        self.jy = np.zeros(0, dtype=REAL)
        self.jz = np.zeros(0, dtype=REAL)
        self.max_output_size = 0

        self.kernel.set_local_memory(24, 1)
        self.kernel.set_local_memory(25, 1)
        self.kernel.set_local_memory(26, 1)
        self.kernel.set_local_memory(27, 1)
        self.kernel.set_local_memory(28, 1)
        self.kernel.set_local_memory(29, 1)
        self.kernel.set_local_memory(30, 1)
        self.kernel.set_local_memory(31, 1)


    def set_args(self, iobj, jobj):
        ni = iobj.n
        nj = jobj.n

        if ni > self.max_output_size:
            self.ax = np.zeros(ni, dtype=REAL)
            self.ay = np.zeros(ni, dtype=REAL)
            self.az = np.zeros(ni, dtype=REAL)
            self.jx = np.zeros(ni, dtype=REAL)
            self.jy = np.zeros(ni, dtype=REAL)
            self.jz = np.zeros(ni, dtype=REAL)
            self.max_output_size = ni

        self.kernel.global_size = ni
        self.kernel.set_int(0, ni)
        self.kernel.set_input_buffer(1, iobj.x)
        self.kernel.set_input_buffer(2, iobj.y)
        self.kernel.set_input_buffer(3, iobj.z)
        self.kernel.set_input_buffer(4, iobj.mass)
        self.kernel.set_input_buffer(5, iobj.vx)
        self.kernel.set_input_buffer(6, iobj.vy)
        self.kernel.set_input_buffer(7, iobj.vz)
        self.kernel.set_input_buffer(8, iobj.eps2)
        self.kernel.set_int(9, nj)
        self.kernel.set_input_buffer(10, jobj.x)
        self.kernel.set_input_buffer(11, jobj.y)
        self.kernel.set_input_buffer(12, jobj.z)
        self.kernel.set_input_buffer(13, jobj.mass)
        self.kernel.set_input_buffer(14, jobj.vx)
        self.kernel.set_input_buffer(15, jobj.vy)
        self.kernel.set_input_buffer(16, jobj.vz)
        self.kernel.set_input_buffer(17, jobj.eps2)
        self.kernel.set_output_buffer(18, self.ax[:ni])
        self.kernel.set_output_buffer(19, self.ay[:ni])
        self.kernel.set_output_buffer(20, self.az[:ni])
        self.kernel.set_output_buffer(21, self.jx[:ni])
        self.kernel.set_output_buffer(22, self.jy[:ni])
        self.kernel.set_output_buffer(23, self.jz[:ni])


    def run(self):
        self.kernel.run()


    def get_result(self):
        return self.kernel.get_result()



@decallmethods(timings)
class Tstep(object):
    """

    """
    def __init__(self, libgrav):
        self.kernel = libgrav.p2p_tstep_kernel
        self.kernel.local_size = 512
        self.tstep = np.zeros(0, dtype=REAL)
        self.max_output_size = 0

        self.kernel.set_local_memory(20, 1)
        self.kernel.set_local_memory(21, 1)
        self.kernel.set_local_memory(22, 1)
        self.kernel.set_local_memory(23, 1)
        self.kernel.set_local_memory(24, 1)
        self.kernel.set_local_memory(25, 1)
        self.kernel.set_local_memory(26, 1)
        self.kernel.set_local_memory(27, 1)


    def set_args(self, iobj, jobj, eta):
        ni = iobj.n
        nj = jobj.n

        if ni > self.max_output_size:
            self.tstep = np.zeros(ni, dtype=REAL)
            self.max_output_size = ni

        self.kernel.global_size = ni
        self.kernel.set_int(0, ni)
        self.kernel.set_input_buffer(1, iobj.x)
        self.kernel.set_input_buffer(2, iobj.y)
        self.kernel.set_input_buffer(3, iobj.z)
        self.kernel.set_input_buffer(4, iobj.mass)
        self.kernel.set_input_buffer(5, iobj.vx)
        self.kernel.set_input_buffer(6, iobj.vy)
        self.kernel.set_input_buffer(7, iobj.vz)
        self.kernel.set_input_buffer(8, iobj.eps2)
        self.kernel.set_int(9, nj)
        self.kernel.set_input_buffer(10, jobj.x)
        self.kernel.set_input_buffer(11, jobj.y)
        self.kernel.set_input_buffer(12, jobj.z)
        self.kernel.set_input_buffer(13, jobj.mass)
        self.kernel.set_input_buffer(14, jobj.vx)
        self.kernel.set_input_buffer(15, jobj.vy)
        self.kernel.set_input_buffer(16, jobj.vz)
        self.kernel.set_input_buffer(17, jobj.eps2)
        self.kernel.set_float(18, eta)
        self.kernel.set_output_buffer(19, self.tstep[:ni])


    def run(self):
        self.kernel.run()


    def get_result(self):
        return self.kernel.get_result()[0]



@decallmethods(timings)
class PNAcc(object):
    """

    """
    def __init__(self, libgrav):
        self.kernel = libgrav.p2p_pnacc_kernel
        self.kernel.local_size = 512
        self.pnax = np.zeros(0, dtype=REAL)
        self.pnay = np.zeros(0, dtype=REAL)
        self.pnaz = np.zeros(0, dtype=REAL)
        self.max_output_size = 0

        self.kernel.set_local_memory(29, 1)
        self.kernel.set_local_memory(30, 1)
        self.kernel.set_local_memory(31, 1)
        self.kernel.set_local_memory(32, 1)
        self.kernel.set_local_memory(33, 1)
        self.kernel.set_local_memory(34, 1)
        self.kernel.set_local_memory(35, 1)
        self.kernel.set_local_memory(36, 1)


    def set_args(self, iobj, jobj, pn_order, clight):
        ni = iobj.n
        nj = jobj.n

        clight = Clight(pn_order, clight)

        if ni > self.max_output_size:
            self.pnax = np.zeros(ni, dtype=REAL)
            self.pnay = np.zeros(ni, dtype=REAL)
            self.pnaz = np.zeros(ni, dtype=REAL)
            self.max_output_size = ni

        self.kernel.global_size = ni
        self.kernel.set_int(0, ni)
        self.kernel.set_input_buffer(1, iobj.x)
        self.kernel.set_input_buffer(2, iobj.y)
        self.kernel.set_input_buffer(3, iobj.z)
        self.kernel.set_input_buffer(4, iobj.mass)
        self.kernel.set_input_buffer(5, iobj.vx)
        self.kernel.set_input_buffer(6, iobj.vy)
        self.kernel.set_input_buffer(7, iobj.vz)
        self.kernel.set_input_buffer(8, iobj.eps2)
        self.kernel.set_int(9, nj)
        self.kernel.set_input_buffer(10, jobj.x)
        self.kernel.set_input_buffer(11, jobj.y)
        self.kernel.set_input_buffer(12, jobj.z)
        self.kernel.set_input_buffer(13, jobj.mass)
        self.kernel.set_input_buffer(14, jobj.vx)
        self.kernel.set_input_buffer(15, jobj.vy)
        self.kernel.set_input_buffer(16, jobj.vz)
        self.kernel.set_input_buffer(17, jobj.eps2)
        self.kernel.set_int(18, clight.pn_order)
        self.kernel.set_float(19, clight.inv1)
        self.kernel.set_float(20, clight.inv2)
        self.kernel.set_float(21, clight.inv3)
        self.kernel.set_float(22, clight.inv4)
        self.kernel.set_float(23, clight.inv5)
        self.kernel.set_float(24, clight.inv6)
        self.kernel.set_float(25, clight.inv7)
        self.kernel.set_output_buffer(26, self.pnax[:ni])
        self.kernel.set_output_buffer(27, self.pnay[:ni])
        self.kernel.set_output_buffer(28, self.pnaz[:ni])


    def run(self):
        self.kernel.run()


    def get_result(self):
        return self.kernel.get_result()













@decallmethods(timings)
class Acc2(object):
    """

    """
    def __init__(self):
        import os
        import ctypes

        dirname = os.path.dirname(__file__)
        path = os.path.abspath(dirname)
        self.get_acc = np.ctypeslib.load_library("libtupan_dp", path).main_p2p_acc_kernel

        self.get_acc.restype = None
        self.get_acc.argtypes = [ctypes.c_uint,
                                 np.ctypeslib.ndpointer(),
                                 np.ctypeslib.ndpointer(),
                                 np.ctypeslib.ndpointer(),
                                 np.ctypeslib.ndpointer(),
                                 np.ctypeslib.ndpointer(),
                                 np.ctypeslib.ndpointer(),
                                 np.ctypeslib.ndpointer(),
                                 np.ctypeslib.ndpointer(),
                                 ctypes.c_uint,
                                 np.ctypeslib.ndpointer(),
                                 np.ctypeslib.ndpointer(),
                                 np.ctypeslib.ndpointer(),
                                 np.ctypeslib.ndpointer(),
                                 np.ctypeslib.ndpointer(),
                                 np.ctypeslib.ndpointer(),
                                 np.ctypeslib.ndpointer(),
                                 np.ctypeslib.ndpointer(),
                                 #
                                 np.ctypeslib.ndpointer(),
                                 np.ctypeslib.ndpointer(),
                                 np.ctypeslib.ndpointer(),
                                ]

        self.args = None

        self.ax = np.zeros(0, dtype=REAL)
        self.ay = np.zeros(0, dtype=REAL)
        self.az = np.zeros(0, dtype=REAL)
        self.max_output_size = 0


    def set_args(self, iobj, jobj):
        ni = iobj.n
        nj = jobj.n

        if ni > self.max_output_size:
            self.ax = np.zeros(ni, dtype=REAL)
            self.ay = np.zeros(ni, dtype=REAL)
            self.az = np.zeros(ni, dtype=REAL)
            self.max_output_size = ni

        self.args = (ni,
                     iobj.x, iobj.y, iobj.z, iobj.mass,
                     iobj.vx, iobj.vy, iobj.vz, iobj.eps2,
                     nj,
                     jobj.x, jobj.y, jobj.z, jobj.mass,
                     jobj.vx, jobj.vy, jobj.vz, jobj.eps2,
                     self.ax, self.ay, self.az,
                    )

    def run(self):
        args = self.args
        self.get_acc(*args)


    def get_result(self):
        ni = self.args[0]
        return [self.ax[:ni], self.ay[:ni], self.az[:ni]]







#acc = Acc2()











phi = Phi(kernels)
acc = Acc(kernels)
acc_jerk = AccJerk(kernels)
tstep = Tstep(kernels)
pnacc = PNAcc(kernels)


########## end of file ##########
