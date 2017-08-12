# -*- coding: utf-8 -*-

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound as error:
   # package is not installed
   __version__ = "GIT_NOT_FOUND"