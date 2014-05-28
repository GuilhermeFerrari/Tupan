# -*- coding: utf-8 -*-
#

"""
TODO.
"""


from __future__ import print_function
import numpy as np
from .body import Bodies
from .sph import Sphs
from .star import Stars
from .blackhole import Blackholes
from .base import AbstractNbodyMethods
from ..lib.utils.timing import timings, bind_all


__all__ = ['ParticleSystem']


@bind_all(timings)
class ParticleSystem(AbstractNbodyMethods):
    """
    This class holds the particle types in the simulation.
    """
    def __init__(self, nbodies=0, nstars=0, nbhs=0, nsphs=0, members=None):
        """
        Initializer.
        """
        init_ids = False
        if members is None:
            init_ids = True
            members = {cls.__name__.lower(): cls(n)
                       for (n, cls) in [(nbodies, Bodies),
                                        (nstars, Stars),
                                        (nbhs, Blackholes),
                                        (nsphs, Sphs)] if n}
        self.members = members
        self.n = len(self)
        if init_ids:
            if self.n:
                self.id[...] = range(self.n)

    def register_attribute(self, attr, sctype, doc=''):
        for member in self.members.values():
            member.register_attribute(attr, sctype, doc)

        super(ParticleSystem, self).register_attribute(attr, sctype, doc)

    #
    # miscellaneous methods
    #

    def __repr__(self):
        return repr(self.__dict__)

    def __str__(self):
        fmt = type(self).__name__+'(['
        if self.n:
            for member in self.members.values():
                fmt += '\n\t{0},'.format('\n\t'.join(str(member).split('\n')))
            fmt += '\n'
        fmt += '])'
        return fmt

    def __len__(self):
        return sum(len(member) for member in self.members.values())

    def append(self, obj):
        if obj.n:
            try:
                members = obj.members
            except AttributeError:
                members = dict([(type(obj).__name__.lower(), obj)])
            for (k, v) in members.items():
                try:
                    self.members[k].append(v)
                except KeyError:
                    self.members[k] = v.copy()
            self.n = len(self)
            for attr in list(self.__dict__):
                if attr not in ('n', 'members'):
                    delattr(self, attr)

    def __getitem__(self, slc):
        if isinstance(slc, np.ndarray):
            ns = 0
            nf = 0
            members = {}
            for (key, obj) in self.members.items():
                nf += obj.n
                members[key] = obj[slc[ns:nf]]
                ns += obj.n
            return type(self)(members=members)

        if isinstance(slc, int):
            if abs(slc) > self.n-1:
                raise IndexError(
                    'index {0} out of bounds 0<=index<{1}'.format(slc, self.n))
            if slc < 0:
                slc = self.n + slc
            i = slc
            members = {}
            for (key, obj) in self.members.items():
                if 0 <= i < obj.n:
                    members[key] = obj[i]
                i -= obj.n
            return type(self)(members=members)

        if isinstance(slc, slice):
            start = slc.start
            stop = slc.stop
            if start is None:
                start = 0
            if stop is None:
                stop = self.n
            if start < 0:
                start = self.n + start
            if stop < 0:
                stop = self.n + stop
            members = {}
            for (key, obj) in self.members.items():
                if stop >= 0 and start < obj.n:
                    members[key] = obj[start-obj.n:stop]
                start -= obj.n
                stop -= obj.n
            return type(self)(members=members)

    def __setitem__(self, slc, values):
        if isinstance(slc, np.ndarray):
            ns = 0
            nf = 0
            for (key, obj) in self.members.items():
                nf += obj.n
                obj[slc[ns:nf]] = values.members[key]
                ns += obj.n
            return

        if isinstance(slc, int):
            if abs(slc) > self.n-1:
                raise IndexError(
                    'index {0} out of bounds 0<=index<{1}'.format(slc, self.n))
            if slc < 0:
                slc = self.n + slc
            i = slc
            for (key, obj) in self.members.items():
                if 0 <= i < obj.n:
                    obj[i] = values.members[key]
                i -= obj.n
            return

        if isinstance(slc, slice):
            start = slc.start
            stop = slc.stop
            if start is None:
                start = 0
            if stop is None:
                stop = self.n
            if start < 0:
                start = self.n + start
            if stop < 0:
                stop = self.n + stop
            for (key, obj) in self.members.items():
                if stop >= 0 and start < obj.n:
                    obj[start-obj.n:stop] = values.members[key]
                start -= obj.n
                stop -= obj.n
            return


# -- End of File --