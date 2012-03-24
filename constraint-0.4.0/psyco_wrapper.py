# pylint: disable-msg=W0232
# (c) 2002-2004 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307
# USA.

"""Provides an psyobj class regardless of the availability of psyco"""

import os

try:
    if "NO_PSYCO" in os.environ:
        raise ImportError()
    from psyco.classes import psyobj as Psyobj # pylint: disable-msg=W0611
except ImportError:

    class Psyobj:
        pass

    if hasattr(os,'uname') and os.uname()[-1] == 'x86_64':
        pass # psyco only available for 32bits platforms
    else:
        from warnings import warn
        warn("Psyco could not be loaded."
             " Psyco is a Python just in time compiler available at http://psyco.sf.net"
             " Installing it will enhance the performance of logilab.constraint",
             stacklevel=2)


