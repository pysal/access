"""
:mod:`access` --- Accessibility Metrics
=================================================
"""

import contextlib
from importlib.metadata import PackageNotFoundError, version

from .access import Access
from .datasets import Datasets

with contextlib.suppress(PackageNotFoundError):
    __version__ = version("access")