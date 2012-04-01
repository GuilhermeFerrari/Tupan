#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""


from . import block
from . import leapfrog


class Integrator(object):
    """

    """
    PROVIDED_METHODS = ['leapfrog', 'blockstep']

    def __init__(self, eta, time, particles, method="leapfrog", **kwargs):
        import logging
        logger = logging.getLogger(__name__)

        self.integrator = None
        if method == "leapfrog":
            logger.info("Using 'leapfrog' integrator.")
            self.integrator = leapfrog.LeapFrog(eta, time, particles)
        elif method == "blockstep":
            logger.info("Using 'blockstep' integrator.")
            self.integrator = leapfrog.BlockStep(eta, time, particles)
        else:
            logger.critical("Unexpected integrator method: '%s'. Provided methods: %s",
                            method, str(self.PROVIDED_METHODS))


    def step(self):
        self.integrator.step()

    @property
    def tstep(self):
        return self.integrator.tstep

    @property
    def current_time(self):
        return self.integrator.time

    @property
    def particles(self):
        return self.integrator.particles


########## end of file ##########
