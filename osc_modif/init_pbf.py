#!/usr/bin/env python3
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
osmosis_bin = "/usr/bin/osmosis"
osmium_bin = "/usr/bin/osmium"
osmium_config_file = "/tmp/osmium_config"
work_path = "/data/work/osmbin/"
work_pbfs_path = os.path.join(work_path, "extracts")
limit_country = 5

planet_url = "http://planet.openstreetmap.org/pbf/planet-latest.osm.pbf"
planet_file = os.path.join(work_pbfs_path, "planet-latest.osm.pbf")

###########################################################################

def init_pbf(dirpath, filenames, options):
  cmd = [osmosis_bin]
  print(dirpath)
  if dirpath == ".":
    orig_pbf = planet_file
  else:
    orig_pbf = os.path.join(work_pbfs_path, dirpath, os.path.basename(dirpath) + ".osm.pbf")
    if not os.path.isfile(orig_pbf):
      up = os.path.dirname(os.path.dirname(orig_pbf))
      orig_pbf = os.path.join(up, os.path.basename(up) + ".osm.pbf")
      print(orig_pbf)
  need_launch = False
  country_dir = {}
  pwd = os.getcwd()
  cmd += ["--read-pbf", orig_pbf]

  osmium_cmd  = [osmium_bin]
  osmium_cmd += ["extract", "--config", osmium_config_file, orig_pbf]
  osmium_config_begin  = '{\n'
  osmium_config_begin += '    "extracts": [\n'
  osmium_config_list = []
  for f in filenames:
    country_dir[f] = os.path.join(work_pbfs_path, dirpath, f.split(".")[0])
    if not os.path.isdir(country_dir[f]):
      os.makedirs(country_dir[f])

    if options.country and f.split(".")[0] not in options.country:
      continue
    print(f)
    need_launch = True
    dst_poly = os.path.join(pwd, dirpath, f)
    dst_pbf = os.path.join(country_dir[f], ".".join(f.split(".")[:-1]) + ".osm.tmp.pbf")
    try:
      os.remove(dst_pbf)
    except OSError:
      pass
    cmd += ["--tee", "--bounding-polygon", "completeWays=yes", "completeRelations=no", "cascadingRelations=no", "file=%s" % dst_poly]
    cmd += ["--write-pbf", dst_pbf]

    osmium_config  = '       {\n'
    osmium_config += '           "output": "%s",\n' % dst_pbf
    osmium_config += '           "output_format": "pbf",\n'
    osmium_config += '           "polygon": {\n'
    osmium_config += '               "file_name": "%s",\n' % dst_poly
    osmium_config += '               "file_type": "poly",\n'
    osmium_config += '           }\n'
    osmium_config += '       },\n'
    osmium_config_list.append(osmium_config)

  cmd += ["--write-null"]
  osmium_config_end  = '    ]\n'
  osmium_config_end += '}\n'

  if not need_launch:
    return

  # Create configuration.txt
  orig_configuration = "../configuration-planet.txt"
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
    if options.osmium:
      num_runs = max(1, (len(osmium_config_list) + 1) // limit_country)
      first = 0
      last = (len(osmium_config_list) // num_runs)
      for run in range(num_runs):
        if run == num_runs-1:
          last = len(osmium_config_list)

        print("  run %d with %d countries" % (run, last-first))
        osmium_config = "".join(osmium_config_list[first:last])
        with open(osmium_config_file, "w") as f:
          f.write(osmium_config_begin)
          f.write(osmium_config)
          f.write(osmium_config_end)
        print(osmium_cmd)
        subprocess.check_call(osmium_cmd)

        first = last
        last += len(osmium_config_list) // num_runs
    else:
      print(cmd)
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
  parser.add_argument("--osmium", dest="osmium", action="store_true", default=False,
                      help="Use osmium instead of osmosis")
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
    if r == ".":
      region = r
    else: # remove initial "./"
      region = r[2:]

    if args.list_region:
      print(region)
    elif not args.region or region in args.region:
      init_pbf(r, files, args)
