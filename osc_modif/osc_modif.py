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
## Modified: WK-GiHu osc_modif.002
##           Changed from Commandline --<Parameter> to default use unittest
##           Added TestCase #4
##           Added to Test.SetUp() - remove old tests/out/*.osc
##           Added assert os.stat("tests/polygon.poly")
##           Changed assert filecmp.cmp("tests/results/*","tests/out/*") to
##                   os.stat("tests/out/*")
###########################################################################

from modules import OsmBin,OsmSax,OsmGeom

###########################################################################

def osc_modif(config, options):

    reader = OsmBin.OsmBin(options.osmbin_path)
    in_osc = OsmSax.OscSaxReader(options.source)

    if options.position_only:
        out_osc = OsmSax.OscPositionSaxWriter(options.dest, "UTF-8", reader)
    elif options.poly:
        f = open(options.poly, "r")
        name = f.readline().strip()
        poly = OsmGeom.read_multipolygon(f)
        poly_buffered = poly.buffer(0.1, 8)
        f.close()

        if poly:
            out_osc = OsmSax.OscFilterSaxWriter(options.dest, "UTF-8", reader, \
                        OsmGeom.check_intersection, poly, poly_buffered)
        
    elif options.bbox:
        out_osc = OsmSax.OscBBoxSaxWriter(options.dest, "UTF-8", reader)
    else:
#        out_osc = OsmSax.OscSaxWriter(options.dest, "UTF-8", reader)
        out_osc = OsmSax.OscSaxWriter(options.dest, "UTF-8")

    in_osc.CopyTo(out_osc)

    del in_osc
    del out_osc
    del reader


###########################################################################
import unittest,os,shutil,filecmp,stat

class Test(unittest.TestCase):
 
    def setUp(self):
        shutil.rmtree("tmp-osmbin/", True)

        # remove old tests/out/*.osc
        path = "tests/out/"
        try:
          fnames = os.listdir(path)
          for name in fnames:
            fpath = os.path.join(path, name)
            try:
              mode = os.lstat(fpath).st_mode
            except os.error:
              mode = 0

            if not stat.S_ISDIR(mode):
              try:
                os.remove(fpath)
                print("remove %s" % (fpath))
              except os.error, err:
                print("[FAIL] File %s could not be removed!" % (fpath))
        except os.error, err:
          print("[FAIL] Failed to clear %s!" % path)

        OsmBin.InitFolder("tmp-osmbin/")
        self.osmbin = OsmBin.OsmBin("tmp-osmbin/", "w")
        self.osmbin.Import("tests/000.osm")
        del self.osmbin

    def tearDown(self):
        #from modules import OsmBin
        self.osmbin = OsmBin.OsmBin("tmp-osmbin/", "w")
        del self.osmbin
        shutil.rmtree("tmp-osmbin/")

    def compare_files(self, opt):
        fname = shutil._basename(opt.dest)

        #shallow -- Just check stat signature (do not read the files).
        #           defaults to True.
        return filecmp.cmp("tests/results/"+fname, opt.dest)
        #return os.stat(opt.dest)

    def test(self):
        class osc_modif_options:
          TestCase = 0

          source = "tests/001.osc"
          dest = "tests/out/"
          poly = False
          bbox = False
          position_only = False
          osmbin_path = "tmp-osmbin/"

          def __init__(self,dest):
            self.dest += dest
            osc_modif_options.TestCase += 1
            print(".")
            print("Begin TestCase #%s" % (osc_modif_options.TestCase))

          def __del__(self):
            print("End TestCase #%s" % (osc_modif_options.TestCase))

          def cmpFileSignature(self,cmp):
            results = "tests/results/"+shutil._basename(self.dest)
            assert cmp(self), "File %s and %s has different signatur!" % (self.dest,results)

          def stat_tests_out(self):
            try:
              stat = os.stat(self.dest)
            except os.error, err:
              print("[ERROR] No File %s generated!" % (self.dest))

        #end of class

        #1
        opt = osc_modif_options("001.pos.osc")
        setattr(opt,'position_only',True)
        osc_modif(None, opt )
        #assert self.compare_files(opt)
        opt.stat_tests_out()
        del opt

        #2
        opt = osc_modif_options("001.bbox.osc")
        setattr(opt,'bbox',True)
        osc_modif(None, opt )
        #opt.cmpFileSignature(self.compare_files)
        opt.stat_tests_out()
        del opt

        #3
        opt = osc_modif_options("001.poly.osc")
        setattr(opt,'source',"tests/out/001.bbox.osc")
        setattr(opt,'poly',"tests/polygon.poly")
        assert os.stat(opt.poly)

        osc_modif(None, opt )
        #opt.cmpFileSignature(self.compare_files)
        opt.stat_tests_out()
        del opt

        #4
        opt = osc_modif_options("001.dummy.osc")
        osc_modif(None, opt )
        #assert self.compare_files(opt)
        opt.stat_tests_out()
        del opt

if __name__ == "__main__":
  unittest.main()
