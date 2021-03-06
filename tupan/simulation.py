# -*- coding: utf-8 -*-
#

"""
TODO.
"""


from __future__ import print_function
import sys
import math
import pickle
import argparse
import logging
from pprint import pprint
from .io import IO
from .integrator import Integrator
from .analysis.glviewer import GLviewer
from .lib.utils.timing import decallmethods, timings, Timer


logger = logging.getLogger(__name__)


__all__ = ['Simulation']


@timings
def myprint(data, fname, fmode):
    if fname == '<stdout>':
        print(data, file=sys.stdout)
    elif fname == '<stderr>':
        print(data, file=sys.stderr)
    else:
        with open(fname, fmode) as fobj:
            print(data, file=fobj)


@decallmethods(timings)
class Diagnostic(object):
    """

    """
    def __init__(self, fname, time, ps, report_freq=4, pn_order=0):
        self.fname = fname
        self.time = time
        self.report_freq = report_freq
        self.include_pn_corrections = True if pn_order else False
        self.nreport = 0
        self.is_initialized = False

    def initialize(self, ps):
        self.ke0 = ps.kinetic_energy
        self.pe0 = ps.potential_energy
        self.te0 = self.ke0 + self.pe0

        self.com_r0 = ps.com_r
        self.com_v0 = ps.com_v
        self.lmom0 = ps.linear_momentum
        self.amom0 = ps.angular_momentum

        self.count = 0
        self.ceerr = 0.0

        self.timer = Timer()
        self.timer.start()

        self.print_header()

        self.is_initialized = True

    def __repr__(self):
        return '{0}'.format(self.__dict__)

    def print_header(self):
        fmt = '{0:13s} {1:10s} '\
              '{2:10s} {3:10s} {4:15s} '\
              '{5:10s} {6:10s} {7:10s} '\
              '{8:10s} {9:10s} {10:10s} '\
              '{11:10s} {12:13s}'
        myprint(fmt.format('#00:time', '#01:dtime',
                           '#02:ke', '#03:pe', '#04:te',
                           '#05:virial', '#06:eerr', '#07:geerr',
                           '#08:com_r', '#09:com_v', '#10:lmom',
                           '#11:amom', '#12:wct'),
                self.fname, 'w')

    def diagnostic_report(self, ps):
        if not self.is_initialized:
            self.initialize(ps)
        t_curr = ps.t_curr
        if self.nreport % self.report_freq == 0:
            self.print_diagnostic(t_curr, t_curr - self.time, ps)
        self.nreport += 1

    def print_diagnostic(self, time, dtime, ps):
        self.time = time

        ke = ps.kinetic_energy
        pe = ps.potential_energy
        te = ke + pe
        virial = ps.virial_energy

        com_r = ps.com_r
        com_v = ps.com_v
        lmom = ps.linear_momentum
        amom = ps.angular_momentum

        eerr = (te-self.te0)/(-pe)
        self.count += 1
        self.ceerr += eerr**2
        geerr = math.sqrt(self.ceerr / self.count)
        com_dr = (((com_r-self.com_r0)**2).sum())**0.5
        com_dv = (((com_v-self.com_v0)**2).sum())**0.5
        dLmom = (((lmom-self.lmom0)**2).sum())**0.5
        dAmom = (((amom-self.amom0)**2).sum())**0.5

        fmt = '{time:< 13.6e} {dtime:< 10.3e} '\
              '{ke:< 10.3e} {pe:< 10.3e} {te:< 15.8e} '\
              '{virial:< 10.3e} {eerr:< 10.3e} {geerr:< 10.3e} '\
              '{com_r:< 10.3e} {com_v:< 10.3e} {lmom:< 10.3e} '\
              '{amom:< 10.3e} {wct:< 13.6e}'
        myprint(fmt.format(time=time, dtime=dtime,
                           ke=ke, pe=pe,
                           te=te, virial=virial,
                           eerr=eerr, geerr=geerr, com_r=com_dr,
                           com_v=com_dv, lmom=dLmom, amom=dAmom,
                           wct=self.timer.elapsed()),
                self.fname, 'a')


@decallmethods(timings)
class Simulation(object):
    """
    The Simulation class is the top level class for N-body simulations.
    """
    def __init__(self, args, viewer):
        self.args = args
        self.viewer = viewer

        print("#" * 40, file=sys.stderr)
        pprint(args.__dict__, stream=sys.stderr)
        print("#" * 40, file=sys.stderr)

        # Read the initial conditions
        fname = self.args.input_file
        ps = IO(fname, 'r').load_snapshot()

        # Initializes output file
        fname = self.args.output_file
        self.io = IO(fname, 'a') if fname else None

        # Initializes the diagnostic report of the simulation
        self.dia = Diagnostic(self.args.log_file,
                              self.args.t_begin,
                              ps,
                              report_freq=self.args.report_freq,
                              pn_order=self.args.pn_order,
                              )

        # Initializes the integrator
        self.integrator = Integrator(self.args.eta,
                                     self.args.t_begin,
                                     ps,
                                     method=self.args.meth,
                                     pn_order=self.args.pn_order,
                                     clight=self.args.clight,
                                     reporter=self.dia,
                                     viewer=self.viewer,
                                     dumpper=self.io,
                                     dump_freq=self.args.dump_freq,
                                     gl_freq=self.args.gl_freq,
                                     )

        # Initializes some counters
        self.res_steps = 0

    def dump_restart_file(self):
        if sys.version_info >= (2, 7):
            with open(self.args.restart_file, 'wb') as fobj:
                pickle.dump(self, fobj, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            fobj = open(self.args.restart_file, 'wb')
            pickle.dump(self, fobj, protocol=pickle.HIGHEST_PROTOCOL)
            fobj.close()

    def evolve(self):
        """

        """
        while (abs(self.integrator.time) < self.args.t_end):
            # evolve a single time-step
            self.integrator.evolve_step(self.args.t_end)

            # dump restart file
            if self.res_steps % self.args.restart_freq == 0:
                self.dump_restart_file()
            self.res_steps += 1

        # Finalize the integrator
        self.integrator.finalize(self.args.t_end)


# ------------------------------------------------------------------------


def _main_newrun(args):
    if args.log_file == sys.stdout:
        args.log_file = sys.stdout.name

    if args.debug_file == sys.stderr:
        args.debug_file = sys.stderr.name

    # ------------------------------------------------------------------------

    viewer = GLviewer() if args.view else None
    mysim = Simulation(args, viewer)
    mysim.evolve()
    return 0


def _main_restart(args):
    if sys.version_info >= (2, 7):
        with open(args.restart_file, "rb") as fobj:
            mysim = pickle.load(fobj)
    else:
        fobj = open(args.restart_file, "rb")
        mysim = pickle.load(fobj)
        fobj.close()

    # update args
    mysim.args.t_end = args.t_end
    if not args.eta is None:
        mysim.integrator._meth.eta = args.eta

    mysim.evolve()
    return 0


def parse_args():
    """Here we process the command line arguments to run a new N-body
    simulation or restart from a previous run.
    """

    # create the parser
    parser = argparse.ArgumentParser(
        description="A Python Toolkit for Astrophysical N-Body Simulations."
    )
    subparser = parser.add_subparsers(
        help="Consult specific help for details."
    )

    # -------------------------------------------------------------------------
    # add subparser newrun
    newrun = subparser.add_parser(
        "newrun",
        description="Performs a new N-body simulation."
    )
    # add the arguments to newrun
    newrun.add_argument(
        "-i", "--input_file",
        type=str,
        default=None,
        required=True,
        help="The name of the initial conditions file which must be read "
             "from. The file format, if supported, is automatically "
             "discovered (type: str, default: None)."
    )
    newrun.add_argument(
        "-m", "--meth",
        type=str,
        default=None,
        required=True,
        choices=Integrator.PROVIDED_METHODS,
        help="Integration method name (type: str, default: None)."
    )
    newrun.add_argument(
        "-e", "--eta",
        type=float,
        default=None,
        required=True,
        help="Parameter for time step determination "
             "(type: float, default: None)."
    )
    newrun.add_argument(
        "-t", "--t_end",
        type=float,
        default=None,
        required=True,
        help="Time to end the simulation (type: float, default: None)."
    )
    newrun.add_argument(
        "-o", "--output_file",
        type=str,
        default='',
        # choices=IO.PROVIDED_FORMATS,
        help="The name of the output file to store the simulation data "
             "(type: str, default: '')."
    )
    newrun.add_argument(
        "--t_begin",
        type=float,
        default=0.0,
        help="Time to begin the simulation (type: float, default: 0.0)."
    )
    newrun.add_argument(
        "--pn_order",
        type=int,
        default=0,
        choices=[0, 2, 4, 5, 6, 7],
        help="Order of the Post-Newtonian corrections "
             "(type: int, default: 0)."
    )
    newrun.add_argument(
        "--clight",
        type=float,
        default=None,
        help="Speed of light value to use in Post-Newtonian corrections "
             "(type: int, default: None)."
    )
    newrun.add_argument(
        "--log_file",
        type=str,
        default=sys.stdout,
        help="File name where log messages should be written "
             "(type: str, default: sys.stdout)."
    )
    newrun.add_argument(
        "-r", "--report_freq",
        type=int,
        default=4,
        help="Number of time-steps between diagnostic reports of the "
             "simulation (type: int, default: 4)."
    )
    newrun.add_argument(
        "-d", "--dump_freq",
        type=int,
        default=16,
        help="Number of time-steps between dump of snapshots "
             "(type: int, default: 16)."
    )
    newrun.add_argument(
        "--restart_freq",
        type=int,
        default=128,
        help="Number of time-steps between rewrites of the restart file "
             "(type: int, default: 128)."
    )
    newrun.add_argument(
        "--use_cl",
        action="store_true",
        help="Enable OpenCL support."
    )
    newrun.add_argument(
        "--use_sp",
        action="store_true",
        help="Enforce the use of single precision in extension modules."
    )
    newrun.add_argument(
        "--view",
        action="store_true",
        help="Enable visualization of the simulation in real time."
    )
    newrun.add_argument(
        "-g", "--gl_freq",
        type=int,
        default=1,
        help="Number of time-steps between GLviewer events "
             "(type: int, default: 1)."
    )
    newrun.add_argument(
        "--profile",
        action="store_true",
        help="Enable execution profile."
    )
    newrun.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug messages."
    )
    newrun.add_argument(
        "--debug_file",
        type=str,
        default=sys.stderr,
        help="File name where error messages should be written "
             "(type: str, default: sys.stderr)."
    )
    newrun.add_argument(
        "--restart_file",
        type=str,
        default="restart.pkl",
        help="The name of the restart file which must be read from "
             "(type: str, default: 'restart.pkl')."
    )
    newrun.set_defaults(func=_main_newrun)

    # -------------------------------------------------------------------------
    # add subparser restart
    restart = subparser.add_parser(
        "restart",
        description="Restart a simulation from a previous run."
    )
    # add the arguments to restart
    restart.add_argument(
        "-t", "--t_end",
        type=float,
        default=None,
        required=True,
        help="Time to end the simulation (type: float, default: None)."
    )
    restart.add_argument(
        "-e", "--eta",
        type=float,
        default=None,
        help="Parameter for time step determination "
             "(type: float, default: obtained from the restart file)."
    )
    restart.add_argument(
        "--restart_file",
        type=str,
        default="restart.pkl",
        help="The name of the restart file which must be read from "
             "(type: str, default: 'restart.pkl')."
    )
    restart.set_defaults(func=_main_restart)

    # ------------------------------------------------------------------------
    return parser.parse_args()


def main():
    """The top-level main function of tupan.

    .. note:: You shouldn't be able to call this function from a ipython
        session. Instead you must call tupan's script directly from a unix
        shell.
    """
    args = parse_args()
    args.func(args)


########## end of file ##########
