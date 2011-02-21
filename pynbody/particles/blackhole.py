#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

from __future__ import print_function
import math
import numpy as np


class BlackHoles(object):
    """A base class for BH-type particles"""

    def __init__(self):
        self.dtype = [('index', 'u8'), ('step_number', 'u8'),
                      ('step_density', 'f8'), ('time', 'f8'),
                      ('mass', 'f8'), ('eps2', 'f8'), ('pot', 'f8'),
                      ('pos', '3f8'), ('vel', '3f8'), ('acc', '3f8'),
                      ('spin', '3f8')]

        self.index = np.array([], dtype='u8')
        self.step_number = np.array([], dtype='u8')
        self.step_density = np.array([], dtype='f8')
        self.time = np.array([], dtype='f8')
        self.mass = np.array([], dtype='f8')
        self.eps2 = np.array([], dtype='f8')
        self.pot = np.array([], dtype='f8')
        self.pos = np.array([], dtype='3f8')
        self.vel = np.array([], dtype='3f8')
        self.acc = np.array([], dtype='3f8')
        self.spin = np.array([], dtype='3f8')

        # total mass
        self.total_mass = 0.0


    def from_cmpd_struct(self, _array):
        for attr in dict(self.dtype).keys():
            setattr(self, attr, _array[attr])

    def to_cmpd_struct(self):
        _array = np.empty(len(self), dtype=self.dtype)
        for attr in dict(self.dtype).keys():
            _array[attr] = getattr(self, attr)
        return _array

    def __repr__(self):
        return '{array}'.format(array=self.to_cmpd_struct())

    def __iter__(self):
        return iter(self.to_cmpd_struct())

    def __len__(self):
        return len(self.index)

    def __reversed__(self):
        return reversed(self.to_cmpd_struct())

    def fromlist(self, data):
        self.from_cmpd_struct(np.asarray(data, dtype=self.dtype))
        self.total_mass = np.sum(self.mass)



########## end of file ##########
