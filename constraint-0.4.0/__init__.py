"""
Constraint Satisfaction Problem (CSP) Solver in Python.

:copyright:
  2000-2008 `LOGILAB S.A. <http://www.logilab.fr>`_ (Paris, FRANCE),
  all rights reserved.

:contact:
  http://www.logilab.org/project/logilab-constraint --
  mailto:python-projects@logilab.org

:license:
  `General Public License version 2
  <http://www.gnu.org/licenses/old-licenses/gpl-2.0.html>`_
"""

from logilab.constraint.__pkginfo__ import version as __version__
from logilab.constraint.propagation import Repository, Solver
from logilab.constraint.distributors import DefaultDistributor
from logilab.constraint import fd
from logilab.constraint import fi
__all__ = ['Repository', 'Solver', 'DefaultDistributor', 'fd', 'fi']
