#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

from __future__ import print_function
import math
import numpy as np
from collections import namedtuple
from pynbody.particles.pbase import Pbase
from pynbody.lib import gravity
try:
    from pynbody.lib.kernels import clkernel
    HAVE_CL = True
#    raise
except Exception as e:
    HAVE_CL = False
    print(e)
    print('Doing calculations without OpenCL...')



fields = [('index', 'u8'), ('mass', 'f8'), ('eps2', 'f8'),   # eps2 -> radius
          ('phi', 'f8'), ('stepdens', '2f8'), ('pos', '3f8'),
          ('vel', '3f8'), ('acc', '3f8')]
#dtype = fields
dtype = {'names': [n for (n, f) in fields], 'formats': [f for (n, f) in fields]}


class Body(Pbase):
    """
    A base class for Body-type particles.
    """

    def __init__(self, numobjs=0):
        Pbase.__init__(self, numobjs, dtype)


    def get_total_mass(self):
        return np.sum(self.mass)


    # Center-of-Mass methods

    def get_center_of_mass_pos(self):
        """
        Get the center-of-mass position.
        """
        return (self.mass * self.pos.T).sum(1) / self.get_total_mass()

    def get_center_of_mass_vel(self):
        """
        Get the center-of-mass velocity.
        """
        return (self.mass * self.vel.T).sum(1) / self.get_total_mass()

    def reset_center_of_mass(self):
        """
        Reset the center-of-mass to origin.
        """
        self.pos -= self.get_center_of_mass_pos()
        self.vel -= self.get_center_of_mass_vel()


    # Momentum methods

    def get_linmom(self):
        """
        Get the individual linear momentum.
        """
        return (self.mass * self.vel.T).T

    def get_angmom(self):
        """
        Get the individual angular momentum.
        """
        return (self.mass * np.cross(self.pos, self.vel).T).T

    def get_total_linmom(self):
        """
        Get the total linear momentum.
        """
        return self.get_linmom().sum(0)

    def get_total_angmom(self):
        """
        Get the total angular momentum.
        """
        return self.get_angmom().sum(0)


    # Energy methods

    def get_ekin(self):
        """
        Get the individual kinetic energy in the center-of-mass frame.
        """
        vcm = self.get_center_of_mass_vel()
        return 0.5 * self.mass * ((self.vel - vcm)**2).sum(1)

    def get_epot(self):
        """
        Get the individual potential energy.
        """
        return self.mass * self.phi

    def get_energies(self):
        """
        Get the individual energies 'kin', 'pot', 'tot', 'vir'.
        """
        ekin = self.get_ekin()
        epot = self.get_epot()
        etot = ekin + epot
        Energies = namedtuple('Energies', ['kin', 'pot', 'tot', 'vir'])
        energies = Energies(ekin, epot, etot, 2*ekin+epot)
        return energies

    def get_total_ekin(self):
        """
        Get the total kinetic energy.
        """
        return np.sum(self.get_ekin())

    def get_total_epot(self):
        """
        Get the total potential energy.
        """
        return 0.5 * np.sum(self.get_epot())

    def get_total_energies(self):
        """
        Get the total energies 'kin', 'pot', 'tot', 'vir'.
        """
        ekin = self.get_total_ekin()
        epot = self.get_total_epot()
        etot = ekin + epot
        TotEnergies = namedtuple('TotEnergies', ['kin', 'pot', 'tot', 'vir'])
        totenergies = TotEnergies(ekin, epot, etot, 2*ekin+epot)
        return totenergies


    # Evolve methods

    def drift(self, tau):
        self.pos += tau * self.vel

    def kick(self, tau):
        self.vel += tau * self.acc


    # Gravity methods

    def set_phi(self, objs):
        """
        Set the individual gravitational potential due to other bodies.
        """
        # double python's for
        def p2p_pot_pyrun_(self, objs):  # 512:5.48938   1024:22.4172
            _phi = []
            for bi in self:
                iphi = 0.0
                for bj in objs:
                    if bi['index'] != bj['index']:
                        dpos = bi['pos'] - bj['pos']
                        eps2 = bi['eps2'] + bj['eps2']
                        ds2 = np.dot(dpos, dpos) + eps2
                        iphi -= bj['mass'] / math.sqrt(ds2)
                _phi.append(iphi)
            return np.asarray(_phi)

        # python's for plus numpy
        def p2p_pot_pyrun(self, objs):  # 512:0.51603   1024:1.74731
            _phi = np.empty_like(self.phi)
            for (i, bi) in zip(range(len(self)), self):
                bj = objs[np.where(objs.index != bi['index'])]
                dpos = bi['pos'] - bj.pos
                eps2 = bi['eps2'] + bj.eps2
                ds2 = np.square(dpos).sum(1) + eps2
                _phi[i] = -np.sum(bj.mass / np.sqrt(ds2))
            return _phi

        if HAVE_CL:
            _phi = clkernel.p2p_pot.run(self, objs)
#            clkernel.p2p_pot.print_profile(len(self), len(objs))
        else:
            _phi = p2p_pot_pyrun(self, objs)

#        print(_phi)

        self.phi[:] = _phi


    def set_acc(self, objs):
        """
        Set the individual acceleration due to other bodies.
        """
        # double python's for
        def p2p_acc_pyrun_(self, objs): # 512:13.6872   1024:53.6422
            _acc = []
            for bi in self:
                iacc = np.zeros(4, dtype=np.float64)
                for bj in objs:
                    if bi['index'] != bj['index']:
                        dpos = bi['pos'] - bj['pos']
                        eps2 = bi['eps2'] + bj['eps2']
                        dvel = bi['vel'] - bj['vel']
                        M = bi['mass'] + bj['mass']
                        ds2 = np.dot(dpos, dpos) + eps2
                        dv2 = np.dot(dvel, dvel)
                        rinv = math.sqrt(1.0 / ds2)
                        r3inv = rinv * rinv
                        e = 0.5*dv2 + M*rinv
                        iacc[3] += e * r3inv
                        r3inv *= bj['mass'] * rinv
                        iacc[0:3] -= r3inv * dpos
                _acc.append(iacc)
            return np.asarray(_acc)

        # python's for plus numpy
        def p2p_acc_pyrun(self, objs):  # 512:0.598859   1024:1.97784
            _acc = np.empty((len(self.acc),4))
            for (i, bi) in zip(range(len(self)), self):
                bj = objs[np.where(objs.index != bi['index'])]
                dpos = bi['pos'] - bj.pos
                eps2 = bi['eps2'] + bj.eps2
                dvel = bi['vel'] - bj.vel
                M = bi['mass'] + bj.mass
                ds2 = np.square(dpos).sum(1) + eps2
                dv2 = np.square(dvel).sum(1)
                rinv = np.sqrt(1.0 / ds2)
                r3inv = rinv * rinv
                e = 0.5*dv2 + M*rinv
                _acc[i][3] = np.sum(e * r3inv)
                r3inv *= bj.mass * rinv
                _acc[i][:3] = -(r3inv * dpos.T).sum(1)
            return _acc

#        if HAVE_CL:
#            _acc = clkernel.p2p_acc.run(self, objs)
##            clkernel.p2p_acc.print_profile(len(self), len(objs))
#        else:
#            _acc = p2p_acc_pyrun(self, objs)

        _acc = gravity.get_acc(self, objs)

#        print('acc - '*10)
#        print(_acc)

        self.acc[:] = _acc[:,:3]
        self.stepdens[:,0] = np.sqrt(_acc[:,3]/(len(objs)-1))




########## end of file ##########
