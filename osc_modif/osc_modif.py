#!/usr/bin/env python3
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
from modules import OsmSax

###########################################################################

def osc_modif(config, options):

    if options.poly:
        from modules import OsmGeom
        f = open(options.poly, "r")
        name = f.readline().strip()
        poly = OsmGeom.read_multipolygon(f)
        poly_buffered = poly.buffer(0.1, 8)
        f.close()
    else:
        poly = None

    try:
        from modules.OsmBin import OsmBin
        if not hasattr(options, "osmbin_path"):
            options.osmbin_path = "/data/work/osmbin/data/"
        reader = OsmBin(options.osmbin_path)
    except IOError:
        from modules import OsmOsis
        reader = OsmOsis.OsmOsis(config.dbs, config.dbp)

    in_osc = OsmSax.OscSaxReader(options.source)
    if options.position_only:
        out_osc = OsmSax.OscPositionSaxWriter(options.dest, "UTF-8", reader)
    elif poly:
        out_osc = OsmSax.OscFilterSaxWriter(options.dest, "UTF-8", reader, OsmGeom.check_intersection, poly, poly_buffered)
    elif options.bbox:
        out_osc = OsmSax.OscBBoxSaxWriter(options.dest, "UTF-8", reader)
    else:
#        out_osc = OsmSax.OscSaxWriter(options.dest, "UTF-8", reader)
        out_osc = OsmSax.OscSaxWriter(options.dest, "UTF-8")

    in_osc.CopyTo(out_osc)
    del in_osc
    del out_osc
    del reader


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
    parser.add_option("--bbox", dest="bbox", action="store_true",
                      help="Add bounding-box to ways and relations")
    (options, args) = parser.parse_args()

    osc_modif(config, options)

###########################################################################
import unittest

class Test(unittest.TestCase):

    def setUp(self):
        import os
        import shutil
        from modules import OsmBin
        shutil.rmtree("tmp-osmbin/", True)
        OsmBin.InitFolder("tmp-osmbin/")
        self.osmbin = OsmBin.OsmBin("tmp-osmbin/", "w")
        self.osmbin.Import("tests/000.osm")
        if not os.path.exists("tests/out"):
            os.makedirs("tests/out")
        del self.osmbin

    def tearDown(self):
        import shutil
        from modules import OsmBin
        self.osmbin = OsmBin.OsmBin("tmp-osmbin/", "w")
        del self.osmbin
        shutil.rmtree("tmp-osmbin/")

    def compare_files(self, a, b):
        import filecmp
        return filecmp.cmp(a, b)

    def test(self):
        class osc_modif_options:
            source = "tests/001.osc"
            dest = "tests/out/001.bbox.osc"
            poly = False
            bbox = True
            position_only = False
            osmbin_path = "tmp-osmbin/"
        osc_modif(None, osc_modif_options)

        assert self.compare_files("tests/results/001.bbox.osc", "tests/out/001.bbox.osc")

        class osc_modif_options:
            source = "tests/results/001.bbox.osc"
            dest = "tests/out/001.poly.osc"
            poly = "tests/polygon.poly"
            position_only = False
            osmbin_path = "tmp-osmbin/"
        osc_modif(None, osc_modif_options)

        assert self.compare_files("tests/results/001.poly.osc", "tests/out/001.poly.osc")
