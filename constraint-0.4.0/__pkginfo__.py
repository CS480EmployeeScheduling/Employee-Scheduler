# pylint: disable-msg=W0622
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
"""Copyright (c) 2001-2006 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr  
"""

modname = 'constraint'
distname = 'logilab-constraint'

numversion = (0, 4, 0)
version = '.'.join(map(str, numversion))
pyversions = ('2.3', '2.4')

license = 'GPL'
copyright = '''Copyright (c) 2001-2006 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

short_desc = "constraints satisfaction solver in Python"

long_desc = """Extensible constraint satisfaction problem solver written in pure
Python, using constraint propagation algorithms. The
logilab.constraint module provides finite domains with arbitrary
values, finite interval domains, and constraints which can be applied
to variables linked to these domains.
"""

author = "Alexandre Fayolle"
author_email = "alexandre.fayolle@logilab.fr"

web = "http://www.logilab.org/projects/%s" % modname
ftp = "ftp://ftp.logilab.org/pub/%s/" % modname
mailinglist = "http://lists.logilab.org/mailman/listinfo/python-logic/"

subpackage_of = 'logilab'
debian_name = 'constraint'
debian_maintainer_email = 'afayolle@debian.org'
