#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""


from __future__ import (print_function, division)
import sys
import math
import logging
import numpy as np
from ..particles import System
from ..lib.utils.timing import decallmethods, timings


__all__ = ['Plummer']

logger = logging.getLogger(__name__)


def scale_mass(p, m_scale):
    p.mass *= m_scale

def scale_pos(p, r_scale):
    p.x *= r_scale
    p.y *= r_scale
    p.z *= r_scale

def scale_vel(p, v_scale):
    p.vx *= v_scale
    p.vy *= v_scale
    p.vz *= v_scale

def scale_to_virial(particles, ke, pe, te):
    scale_vel(particles, math.sqrt(-0.5*pe/ke))
    ke = -0.5 * pe
    te = ke + pe
    scale_pos(particles, -te / 0.25)
    pe = particles.potential_energy
    scale_vel(particles, math.sqrt(0.5 * abs(pe / te)))


def scale_to_nbody_units(particles):
#    scale_mass(particles["star"], 1.0/particles["star"].get_mass())
#    particles["star"].set_phi(particles)

    ke = particles.kinetic_energy
    pe = particles.potential_energy
    te = ke + pe
    ve = ke + te
    print(ke, pe, te, ve)

    scale_to_virial(particles, ke, pe, te)

    ke = particles.kinetic_energy
    pe = particles.potential_energy
    te = ke + pe
    ve = ke + te
    print(ke, pe, te, ve)



@decallmethods(timings)
class Plummer(object):
    """  """

    def __init__(self, num, imf, mfrac=0.999, eps=0.0, eps_parametrization=0, seed=None):
        self.num = num
        self.imf = imf
        self.mfrac = mfrac
        self.eps2 = eps*eps
        self.eps_parametrization = eps_parametrization
        self.particles = System(nstars=num)
        np.random.seed(seed)

    def set_eps2(self, mass):
        n = self.num
        if self.eps_parametrization == 0:       # eps2 ~ cte
            eps2 = np.ones(n)
        elif self.eps_parametrization == 1:     # eps2 ~ m^2 ~ 1/n^2 if m ~ 1/n
            eps2 = mass**2
        elif self.eps_parametrization == 2:     # eps2 ~ m/n ~ 1/n^2 if m ~ 1/n
            eps2 = mass / n
        elif self.eps_parametrization == 3:     # eps2 ~ (m/n^2)^(2/3) ~ 1/n^2 if m ~ 1/n
            eps2 = (mass / n**2)**(2.0/3)
        elif self.eps_parametrization == 4:     # eps2 ~ (1/(m*n^2))^2 ~ 1/n^2 if m ~ 1/n
            eps2 = (1.0 / (mass * n**2))**2
        else:
            logger.critical("Unexpected value for eps_parametrization: %d.", self.eps_parametrization)
            raise ValueError("Unexpected value for eps_parametrization: {}.".format(self.eps_parametrization))

        # normalizes by the provided scale of eps2
        eps2 *= self.eps2 / np.mean(eps2)

        # return half of real value in order to avoid to do this in force loop.
        return eps2/2


    def set_pos(self, irand):
        n = self.num
        mfrac = self.mfrac
        mrand = (irand + np.random.random(n)) * mfrac / n
        radius = 1.0 / np.sqrt(np.power(mrand, -2.0/3.0) - 1.0)
        theta = np.arccos(np.random.uniform(-1.0, 1.0, size=n))
        phi = np.random.uniform(0.0, 2.0 * np.pi, size=n)
        rx = radius * np.sin(theta) * np.cos(phi)
        ry = radius * np.sin(theta) * np.sin(phi)
        rz = radius * np.cos(theta)
        return (rx, ry, rz)


    def set_vel(self, pot):
        count = 0
        n = self.num
        rnd = np.empty(n)
        while count < n:
            r1 = np.random.random()
            r2 = np.random.random()
            if (r2 < r1):
                rnd[count] = r2
                count += 1
        velocity = np.sqrt(-2 * rnd * pot)
        theta = np.arccos(np.random.uniform(-1.0, 1.0, size=n))
        phi = np.random.uniform(0.0, 2.0 * np.pi, size=n)
        vx = velocity * np.sin(theta) * np.cos(phi)
        vy = velocity * np.sin(theta) * np.sin(phi)
        vz = velocity * np.cos(theta)
        return (vx, vy, vz)


    def set_bodies(self):
        """  """
        n = self.num
        ilist = np.arange(n)

        # set index
        self.particles.id = ilist

        srand = np.random.get_state()

        # set mass
        self.particles.mass = self.imf.sample(n)
        self.particles.mass /= self.particles.total_mass

        # set eps2
        self.particles.eps2 = self.set_eps2(self.particles.mass)

        np.random.set_state(srand)

        # set pos
        pos = self.set_pos(np.random.permutation(ilist))
        self.particles.x = pos[0]
        self.particles.y = pos[1]
        self.particles.z = pos[2]

        # set vel
        vel = self.set_vel(self.particles.get_phi(self.particles))
        self.particles.vx = vel[0]
        self.particles.vy = vel[1]
        self.particles.vz = vel[2]


    def make_plummer(self):
        self.set_bodies()
        self.particles.move_to_center()
        scale_to_nbody_units(self.particles)







    def show(self, nbins=32):
        from scipy import optimize
        import matplotlib.pyplot as plt
        from matplotlib.patches import Circle

        mass = self.imf._mtot * self.particles.mass.copy()

        ###################################

        (hist, bins) = np.histogram(np.log10(mass), bins=nbins)
        linbins = np.power(10.0, bins)
        where_gt_zero = np.where(hist > 0)

        fitfunc = lambda k, m: k * self.imf.func(m)
        errfunc = lambda k, m, y: fitfunc(k, m)[where_gt_zero] - y[where_gt_zero]
        k0 = 1.0
        k1, success = optimize.leastsq(errfunc, k0, args=(linbins[:-1], hist))
        x = np.logspace(np.log10(self.imf.min_mlow),
                        np.log10(self.imf.max_mhigh),
                        num=128, base=10.0)
        y = fitfunc(k1, x)

        ###################################
        # IMF plot

        fig = plt.figure(figsize=(13.5, 6))
        ax1 = fig.add_subplot(1,2,1)
        ax1.plot(bins[where_gt_zero], np.log10(hist[where_gt_zero]),
                 'bo', label='IMF sample')
        ax1.plot(np.log10(x), np.log10(y), 'r--',
                 label='IMF distribution', linewidth=1.5)
        ax1.grid(True)
        ax1.set_xlabel(r'$\log_{10}(m)$', fontsize=18)
        ax1.set_ylabel(r'$\log_{10}(dN/d\log_{10}(m))$', fontsize=18)
        ax1.legend(loc='lower left', shadow=True,
                   fancybox=True, borderaxespad=0.75)

        ###################################

        b = self.particles
        n = b.n
        x = b.x
        y = b.y
        radius = 2 * n * b.mass
        color = n * b.mass

        ###################################
        # Scatter plot

        ax2 = fig.add_subplot(1,2,2)
#        ax.set_axis_bgcolor('0.75')
        ax2.scatter(x, y, c=color, s=radius, cmap='gist_rainbow',
                    alpha=0.75, label=r'$Stars$')
        circle = Circle((0, 0), 1, facecolor='none',
                        edgecolor=(1,0.25,0), linewidth=1.5, label=r'$R_{Vir}$')
        ax2.add_patch(circle)

        ax2.set_xlim(-4, +4)
        ax2.set_ylim(-4, +4)

        ax2.set_xlabel(r'$x$', fontsize=18)
        ax2.set_ylabel(r'$y$', fontsize=18)
        ax2.legend(loc='upper right', shadow=True,
                   fancybox=True, borderaxespad=0.75)

        ###################################
        # Show
        plt.savefig('show.png', bbox_inches="tight")
#        plt.savefig('show.pdf', bbox_inches="tight")
        plt.show()
        plt.close()



########## end of file ##########
