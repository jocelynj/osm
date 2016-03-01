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

import os, urllib, lockfile, shutil, time, dateutil.parser, dateutil.tz
import multiprocessing
import sys
import osc_modif
from modules import OsmBin
from modules import OsmSax

# configuration
skip_diff_generation = False
multiproc_enabled = True
work_path = "/data/work/osmbin/replication"
work_diffs_path = os.path.join(work_path, "diffs")
type_replicate = "minute"
#type_replicate = "day-replicate"
orig_diff_path = os.path.join(work_diffs_path, "planet", type_replicate)
bbox_diff_path = os.path.join(work_diffs_path, "bbox", type_replicate)

countries_param = {}
modif_diff_path = []
dependencies = {}

os.chdir("polygons")
for (r,d,files) in os.walk("."):
  for f in files:
     if f.endswith(".poly"):
        country_poly = os.path.join(r, f)
        p = os.path.join(r, f[:-len(".poly")])
        dependencies[p] = []
        for i in range(1, p.count("/")):
            father = "/".join(p.split("/")[:-i])
            if father in dependencies:
                dependencies[father] += [p]
                break
        country_diff = os.path.join(work_diffs_path, p, type_replicate)
        modif_diff_path.append(country_diff)
        countries_param[p] = (country_poly, country_diff)

# Find countries without any dependencies
top_countries = dependencies.keys()
for (k,v) in dependencies.iteritems():
  for c in v:
    if c in top_countries:
      top_countries.remove(c)

remote_diff_url = "http://planet.openstreetmap.org/replication/" + type_replicate
lock_file = os.path.join(work_path, "update.lock")

###########################################################################

def update_hardlink(src, dst):
  if os.path.exists(dst):
    os.remove(dst)
  os.link(src, dst)

def update_symlink(src, dst):
  if os.path.exists(dst) and not os.path.islink(dst):
    raise Exception, "File '%s' is not a symbolic link" % dst
  if os.path.exists(dst):
    os.remove(dst)
  try:
    os.symlink(src, dst)
  except:
    print "FAIL on update_symlink(%s, %s)" % (src, dst)
    raise

def generate_bbox_diff(orig_diff_path, file_location, file_date, modif_diff_path):

  orig_diff_file = os.path.join(orig_diff_path, file_location)
  modif_diff_file = os.path.join(modif_diff_path, file_location)

  class osc_modif_options:
    source = orig_diff_file + ".osc.gz"
    dest = modif_diff_file + "-tmp.osc.gz"
    poly = False
    bbox = True
    position_only = False

  # apply polygon
  print time.strftime("%H:%M:%S"), "  generate bbox"
  sys.stdout.flush()
  osc_modif.osc_modif(None, osc_modif_options)
  os.rename(modif_diff_file + "-tmp.osc.gz", modif_diff_file + ".osc.gz")
  os.utime(modif_diff_file + ".osc.gz", (file_date, file_date))
  update_hardlink(orig_diff_file + ".state.txt", modif_diff_file + ".state.txt")

  # update symbolic link to state.txt
  modif_state_file = os.path.join(modif_diff_path, "state.txt")
  update_symlink(modif_diff_file + ".state.txt", modif_state_file)
  os.utime(modif_state_file, (file_date, file_date))
  print time.strftime("%H:%M:%S"), "  finish bbox"
  sys.stdout.flush()


def generate_diff(orig_diff_path, file_location, file_date, modif_poly, modif_diff_path, country):

  orig_diff_file = os.path.join(orig_diff_path, file_location)
  modif_diff_file = os.path.join(modif_diff_path, file_location)

  class osc_modif_options:
    source = orig_diff_file + ".osc.gz"
    dest = modif_diff_file + "-tmp.osc.gz"
    poly = modif_poly
    position_only = False

  # apply polygon
#  print time.strftime("%H:%M:%S"), "  apply polygon", modif_poly
#  sys.stdout.flush()
  osc_modif.osc_modif(None, osc_modif_options)
  os.rename(modif_diff_file + "-tmp.osc.gz", modif_diff_file + ".osc.gz")
  os.utime(modif_diff_file + ".osc.gz", (file_date, file_date))
  update_hardlink(orig_diff_file + ".state.txt", modif_diff_file + ".state.txt")

  # update symbolic link to state.txt
  modif_state_file = os.path.join(modif_diff_path, "state.txt")
  update_symlink(modif_diff_file + ".state.txt", modif_state_file)
  os.utime(modif_state_file, (file_date, file_date))
  print time.strftime("%H:%M:%S"), "  finish polygon", modif_poly
#  sys.stdout.flush()

  return (country, file_location, file_date)

###########################################################################

def launch_dep_countries(res):

  global multiproc_enabled
  global pool
  global pool_jobs
  global lock_num_launched
  global num_launched

  if multiproc_enabled:
    lock_num_launched.acquire()

  for c in dependencies[res[0]]:
    country_param = countries_param[c]
    num_launched += 1
    if multiproc_enabled:
      pool_jobs.append(pool.apply_async(generate_diff,
                                        (countries_param[res[0]][1], res[1], res[2],
                                         country_param[0], country_param[1], c),
                                        callback=launch_dep_countries))
    else:
      new_res = generate_diff(countries_param[res[0]][1], res[1], res[2],
                              country_param[0], country_param[1], c)
      launch_dep_countries(new_res)

  num_launched -= 1
  if multiproc_enabled:
    lock_num_launched.release()


###########################################################################

def update(wanted_end_sequence=None):

  global pool
  global pool_jobs
  global lock_num_launched
  global num_launched

  # get lock
  if not os.path.exists(work_path):
    os.makedirs(work_path)
  lock = lockfile.FileLock(lock_file)
  lock.acquire(timeout=0)

  # get local sequence number
  def get_sequence_num(f):
    for line in f:
      (key, sep, value) = line.partition("=")
      if key.strip() == "sequenceNumber":
        return int(value)

  try:
    print os.path.join(orig_diff_path, "state.txt")
    f = open(os.path.join(orig_diff_path, "state.txt"), "r")
    begin_sequence = get_sequence_num(f)
    f.close()
  except IOError:
    begin_sequence = 0

  # get remote sequence number
  try:
    f = urllib.urlopen(os.path.join(remote_diff_url, "state.txt"), "r")
  except IOError:
    lock.release()
    raise
  end_sequence = min(begin_sequence + 10000, get_sequence_num(f))
  if wanted_end_sequence:
    end_sequence = min(end_sequence, wanted_end_sequence)
  f.close()

  try:
    begin_sequence = int(begin_sequence)
    end_sequence = int(end_sequence)
  except TypeError:
    lock.release()
    raise

  # download diffs, and apply the polygon on them
  for i in xrange(begin_sequence + 1, end_sequence + 1):
    print time.strftime("%H:%M:%S"), i
    for path in [orig_diff_path] + modif_diff_path + [bbox_diff_path]:
      tmp_path = os.path.join(path, "%03d/%03d" % (i // (1000 * 1000), (i // 1000) % 1000))
      if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)

    file_location = "%03d/%03d/%03d" % (i // (1000 * 1000), (i // 1000) % 1000, i % 1000)

    # download diff file
    print time.strftime("%H:%M:%S"), "  download diff"
    orig_diff_file = os.path.join(orig_diff_path, file_location)
    for ext in (".osc.gz", ".state.txt"):
      try:
        (filename, headers) = urllib.urlretrieve(os.path.join(remote_diff_url, file_location) + ext, orig_diff_file + ext)
      except IOError:
        lock.release()
        raise
      file_date = time.mktime(dateutil.parser.parse(headers["Last-Modified"]).astimezone(dateutil.tz.tzlocal()).timetuple())
      os.utime(orig_diff_file + ext, (file_date, file_date))

    if not skip_diff_generation:
      generate_bbox_diff(orig_diff_path, file_location, file_date, bbox_diff_path)

      if multiproc_enabled:
        lock_num_launched.acquire()

      for country in top_countries:
        country_param = countries_param[country]
        num_launched += 1
        if multiproc_enabled:
          pool_jobs.append(pool.apply_async(generate_diff,
                                            (bbox_diff_path, file_location, file_date,
                                             country_param[0], country_param[1], country),
                                            callback=launch_dep_countries))
        else:
          pool_jobs = generate_diff(bbox_diff_path, file_location, file_date,
                                    country_param[0], country_param[1], country)
          launch_dep_countries(pool_jobs)

      if multiproc_enabled:
        lock_num_launched.release()
        while True:
          lock_num_launched.acquire()
          local_num_launched = num_launched
          lock_num_launched.release()
          if local_num_launched == 0 and len(pool_jobs) == 0:
            break
          for r in pool_jobs:
            r.get()
            pool_jobs.remove(r)

      assert num_launched == 0

    # update osmbin
    print time.strftime("%H:%M:%S"), "  update osmbin"
    diff_read = OsmSax.OscSaxReader(orig_diff_file + ".osc.gz")
    o = OsmBin.OsmBin("/data/work/osmbin/data", "w")
    diff_read.CopyTo(o)
    del o
    del diff_read

    # update symbolic links to state.txt
    print time.strftime("%H:%M:%S"), "  update links to state.txt"
    update_symlink(orig_diff_file + ".state.txt", os.path.join(orig_diff_path, "state.txt"))
    os.utime(os.path.join(orig_diff_path, "state.txt"), (file_date, file_date))
    sys.stdout.flush()

  if multiproc_enabled:
    pool.close()
    pool.join()

  # free lock
  sys.stdout.flush()
  lock.release()

if __name__ == '__main__':
  if len(sys.argv) > 1 and sys.argv[1]=="--list":
    import pprint
    pprint.pprint(sorted(top_countries))
    pprint.pprint(dependencies)
    sys.exit(0)
  if len(sys.argv) > 1 and sys.argv[1]=="--end":
    wanted_end_sequence = int(sys.argv[2])
  else:
    wanted_end_sequence = None
  if multiproc_enabled:
    pool = multiprocessing.Pool(processes=8)
  lock_num_launched = multiprocessing.Lock()
  num_launched = 0
  pool_jobs = []

  update(wanted_end_sequence)
