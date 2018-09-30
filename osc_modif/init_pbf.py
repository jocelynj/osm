#!/usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Jocelyn Jaubert                 2016                       ##
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

import os
import urllib
import shutil
import subprocess

# configuration
osmosis_bin = "/data/project/osmbin/osmosis-0.43.1/bin/osmosis"
work_path = "/data/work/osmbin/"
work_pbfs_path = os.path.join(work_path, "extracts")

planet_url = "http://planet.openstreetmap.org/pbf/planet-latest.osm.pbf"
planet_file = os.path.join(work_pbfs_path, "planet-latest.osm.pbf")

###########################################################################

def init_pbf(dirpath, filenames, options):
  cmd = [osmosis_bin]
  print dirpath
  if dirpath == ".":
    orig_pbf = planet_file
  else:
    orig_pbf = os.path.join(work_pbfs_path, dirpath, os.path.basename(dirpath) + ".osm.pbf")
  need_launch = False
  country_dir = {}
  cmd += ["--read-pbf", orig_pbf]
  for f in filenames:
    country_dir[f] = os.path.join(work_pbfs_path, dirpath, f.split(".")[0])
    if not os.path.isdir(country_dir[f]):
      os.makedirs(country_dir[f])

    if options.country and f.split(".")[0] not in options.country:
      print f
      continue
    need_launch = True
    cmd += ["--tee", "--bounding-polygon", "completeRelations=yes", "file=%s" % os.path.join(dirpath, f)]
    cmd += ["--write-pbf", os.path.join(country_dir[f], ".".join(f.split(".")[:-1]) + ".osm.tmp.pbf")]

  cmd += ["--write-null"]

  if not need_launch:
    return

  # Create configuration.txt
  orig_configuration = os.path.join(os.path.dirname(planet_file), "configuration.txt")
  orig_lines = []
  with open(orig_configuration, "r") as src_f:
    for l in src_f:
      orig_lines.append(l)
  for f in filenames:
    dest_configuration = os.path.join(country_dir[f], "configuration.txt")
    with open(dest_configuration, "w") as dest_f:
      for line in orig_lines:
        l = line
        if "baseUrl" in line:
          l = "baseUrl=file://" + os.path.join(work_path, "replication", "diffs", dirpath, f.split(".")[0], "minute") + "\n"
        dest_f.write(l)

  if options.only_conf:
    return

  if not options.only_state:
    print cmd
    subprocess.check_call(cmd)

  for f in filenames:
    if options.country and f.split(".")[0] not in options.country:
      continue
    base_pbf = os.path.join(work_pbfs_path, dirpath, f.split(".")[0], ".".join(f.split(".")[:-1]))
    os.rename(base_pbf + ".osm.tmp.pbf", base_pbf + ".osm.pbf")

  # Create state.txt
  orig_state = os.path.join(os.path.dirname(orig_pbf), "state.txt")
  for f in filenames:
    dest_state = os.path.join(work_pbfs_path, dirpath, f.split(".")[0], "state.txt")
    shutil.copyfile(orig_state, dest_state)


###########################################################################

if __name__ == '__main__':

  import argparse

  parser = argparse.ArgumentParser(description="Initialise pbf files for extracts")
  parser.add_argument("--planet", dest="planet", action="store_true", default=False,
                      help="Download whole planet")
  parser.add_argument("--only-state", dest="only_state", action="store_true", default=False,
                      help="Update only state.txt file")
  parser.add_argument("--only-conf", dest="only_conf", action="store_true", default=False,
                      help="Update only configuration.txt file")
  parser.add_argument("--list-region", dest="list_region", action="store_true", default=False,
                      help="List available regions")
  parser.add_argument("--region", dest="region", action="store", nargs="+",
                      help="Limit to a region")
  parser.add_argument("--country", dest="country", action="store", nargs="+",
                      help="Limit to a country")
  args = parser.parse_args()

  if args.planet:
    (filename, headers) = urllib.urlretrieve(planet_url, planet_file)

  os.chdir("polygons")
  for (r,d,files) in os.walk("."):
    if args.list_region:
      print r[2:]
    elif not args.region or r[2:] in args.region:
      init_pbf(r, files, args)
