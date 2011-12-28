#!/usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Jocelyn Jaubert                 2011                       ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, either version 3 of the License, or     ##
## (at your option) any later version.                                   ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
##                                                                       ##
###########################################################################

import sys, re, urllib, time
from pyPgSQL import PgSQL
from modules import OsmSax

###########################################################################

def osc_modif(config, options):

    if options.poly:
        from modules import OsmGeom
        f = open(options.poly, "r")
        name = f.readline().strip()
        poly = OsmGeom.read_multipolygon(f)
        f.close()
    else:
        poly = None

    try:
        from modules.OsmBin import OsmBin
        reader = OsmBin("/data/work/osmbin/data")
    except IOError:
        from modules import OsmOsis
        reader = OsmOsis.OsmOsis(config.dbs, config.dbp)

    in_osc = OsmSax.OscSaxReader(options.source)
    if options.position_only:
        out_osc = OsmSax.OscPositionSaxWriter(options.dest, "UTF-8", reader)
    elif poly:
        out_osc = OsmSax.OscFilterSaxWriter(options.dest, "UTF-8", reader, poly, OsmGeom.check_intersection)
    else:
#        out_osc = OsmSax.OscSaxWriter(options.dest, "UTF-8", reader)
        out_osc = OsmSax.OscSaxWriter(options.dest, "UTF-8")

    in_osc.CopyTo(out_osc)


if __name__ == "__main__":

    class template_config:

        db_base     = "osm"
        db_user     = ""
        db_password = ""
        db_schema   = "osmosis"

        def init(self):
            self.db_string = "dbname=%s user=%s password=%s"%(self.db_base, self.db_user, self.db_password)

    config = template_config()
    config.init()

    config.dbs = config.db_string
    config.dbp = "osmosis"

    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("--source", dest="source", action="store",
                      help="Osc source file")
    parser.add_option("--dest", dest="dest", action="store",
                      help="Osc destination file")
    parser.add_option("--position-only", dest="position_only", action="store_true",
                      help="Only report positions")
    parser.add_option("--poly", dest="poly", action="store",
                      help="Polygon to use to limit changes")
    (options, args) = parser.parse_args()

    osc_modif(config, options)
