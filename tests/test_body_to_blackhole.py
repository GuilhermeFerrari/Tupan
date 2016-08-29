# -*- coding: utf-8 -*-
#

"""
TODO.
"""

from __future__ import print_function


if __name__ == "__main__":
    from tupan.ics.plummer import make_plummer
    from tupan.io.hdf5io import HDF5IO

    n = 256
    eps = 4.0/n

#    imf = ("equalmass",)
#    imf = ("salpeter1955", 0.5, 120.0)
    imf = ("parravano2011", 0.075, 120.0)
#    imf = ("padoan2007", 0.075, 120.0)

    ps = make_plummer(n, eps, imf, seed=1)

    fname = ("plummer" + str(n).zfill(5) + '-' +
             '_'.join(str(i) for i in imf))

    with HDF5IO(fname, 'w') as fid:
        fid.dump_snap(ps)

#    from tupan.ics.fewbody import make_figure83
    from tupan.ics.fewbody import make_pythagorean
    from tupan.particles.blackhole import Blackhole
#    bh = make_figure83().members.body.astype(Blackhole)
    bh = make_pythagorean().members.body.astype(Blackhole)
    bh.dynrescale_total_mass(0.5)
    ps.dynrescale_total_mass(0.5)
    members = ps.members
    members[bh.name] = bh
    ps.update_members(**members)
    ps.reset_pid()
    ps.to_nbody_units()
    nbh = ps.members.blackhole.n

    fname = ("plummer" + str(n).zfill(5) + '-' +
             '_'.join(str(i) for i in imf) +
             '-' + str(nbh) + 'bh')

    with HDF5IO(fname, 'w') as fid:
        fid.dump_snap(ps)

    from tupan.animation import GLviewer
    with GLviewer() as viewer:
        viewer.show_event(ps)


# -- End of File --
