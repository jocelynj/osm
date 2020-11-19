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

import lockfile
import os
import shutil
import subprocess
import sys

# configuration
osmosis_bin = "/usr/bin/osmosis"
osmium_bin = "/usr/bin/osmium"
work_path = "/data/work/osmbin/"
work_diffs_path = os.path.join(work_path, "replication", "diffs")
merge_diffs_path = os.path.join(work_diffs_path, "merge")
type_replicate = "minute"
lock_file = os.path.join(work_path, "merge.lock")

work_pbfs_path = os.path.join(work_path, "extracts")
merge_pbfs_path = os.path.join(work_pbfs_path, "merge")

###########################################################################

def update_hardlink(src, dst):
  if os.path.exists(dst):
    os.remove(dst)
  os.link(src, dst)

def update_symlink(src, dst):
  if os.path.exists(dst) and not os.path.islink(dst):
    raise Exception("File '%s' is not a symbolic link" % dst)
  if os.path.exists(dst):
    os.remove(dst)
  try:
    os.symlink(src, dst)
  except:
    print("FAIL on update_symlink(%s, %s)" % (src, dst))
    raise

# get local sequence number
def get_sequence_num(f):
  for line in f:
    (key, sep, value) = line.partition("=")
    if key.strip() == "sequenceNumber":
      return int(value)

###########################################################################

def merge(filename, use_osmium):

  # get lock
  if not os.path.exists(work_path):
    os.makedirs(work_path)
  lock = lockfile.FileLock(lock_file)
  lock.acquire(timeout=0)

  diff_list = []
  f = open(filename, "r")
  for line in f:
    if len(line) > 4:
      diff_list.append(line.strip())
  f.close()

  # get first sequence number
  try:
    f = open(os.path.join(merge_diffs_path, filename, type_replicate, "state.txt"))
    begin_sequence = get_sequence_num(f)
    f.close()
  except:
    begin_sequence = 0

  # get last sequence number
  end_sequence = sys.maxsize
  for d in diff_list:
    f = open(os.path.join(work_diffs_path, d, type_replicate, "state.txt"))
    end_sequence = min(end_sequence, get_sequence_num(f))
    f.close()

  if end_sequence == sys.maxsize:
    lock.release()
    return

  if begin_sequence == 0:
    begin_sequence = end_sequence - 2

  for i in range(begin_sequence + 1, end_sequence + 1):
    num = "%03d/%03d/%03d" % (i // (1000 * 1000), (i // 1000) % 1000, i % 1000)
    merge_num(filename, diff_list, num, use_osmium)

  # free lock
  sys.stdout.flush()
  lock.release()


def merge_num(dest, diff_list, num, use_osmium):

  print(num)

  if use_osmium:
    cmd = [osmium_bin, "merge-changes", "--no-progress", "--simplify", "--overwrite"]
    for (n, d) in enumerate(diff_list):
      cmd += [os.path.join(work_diffs_path, d, type_replicate, num) + ".osc.gz"]

    dest_diff = os.path.join(merge_diffs_path, dest, type_replicate, num) + ".osc.gz"
    cmd += ["-o", dest_diff]

  else:
    cmd = [osmosis_bin]
    for (n, d) in enumerate(diff_list):
      cmd += ["--read-xml-change", os.path.join(work_diffs_path, d, type_replicate, num) + ".osc.gz"]
      if n != 0:
        cmd += ["--merge-change", "--buffer-change"]

    dest_diff = os.path.join(merge_diffs_path, dest, type_replicate, num) + ".osc.gz"
    cmd += ["--write-xml-change", dest_diff]

  dest_path = os.path.dirname(dest_diff)
  if not os.path.exists(dest_path):
    os.makedirs(dest_path)

  subprocess.check_call(cmd)
  new_state = os.path.join(merge_diffs_path, dest, type_replicate, num) + ".state.txt"
  update_hardlink(os.path.join(work_diffs_path, d, type_replicate, num) + ".state.txt", new_state)

  update_symlink(new_state, os.path.join(merge_diffs_path, dest, type_replicate, "state.txt"))

def merge_pbf(filename, use_osmium):

  # get lock
  if not os.path.exists(work_path):
    os.makedirs(work_path)
  lock = lockfile.FileLock(lock_file)
  lock.acquire(timeout=0)

  pbf_list = []
  f = open(filename, "r")
  for line in f:
    if len(line) > 4:
      pbf_list.append(line.strip())
  f.close()

  dest = filename

  if use_osmium:
    cmd = [osmium_bin, "merge", "--overwrite"]
    for (n, d) in enumerate(pbf_list):
      cmd += [os.path.join(work_pbfs_path, d, os.path.basename(d) + ".osm.pbf")]

    dest_pbf = os.path.join(merge_pbfs_path, dest, os.path.basename(dest) + ".osm.pbf")
    cmd += ["-o", dest_pbf]

    orig_state = os.path.join(work_pbfs_path, d, "state.txt")
    with open(orig_state) as f:
      for line in f:
        (key, sep, value) = line.partition("=")
        if key.strip() == "timestamp":
          state_timestamp = value.replace("\\:", ":")
        if key.strip() == "sequenceNumber":
          state_sequencenum = value

    repl_base_url = "http://download.openstreetmap.fr/replication/%s/minute" % os.path.join("merge", dest)

    cmd += ["--output-header=osmosis_replication_timestamp=%s" % state_timestamp]
    cmd += ["--output-header=osmosis_replication_sequence_number=%s" % state_sequencenum]
    cmd += ["--output-header=osmosis_replication_base_url=%s" % repl_base_url]

  else:
    cmd = [osmosis_bin]
    for (n, d) in enumerate(pbf_list):
      cmd += ["--read-pbf", os.path.join(work_pbfs_path, d, os.path.basename(d) + ".osm.pbf")]
      if n != 0:
        cmd += ["--merge", "--buffer"]

    dest_pbf = os.path.join(merge_pbfs_path, dest, os.path.basename(dest) + ".osm.pbf")
    cmd += ["--write-pbf", dest_pbf]

  dest_path = os.path.dirname(dest_pbf)
  if not os.path.exists(dest_path):
    os.makedirs(dest_path)

  subprocess.check_call(cmd)
  new_state = os.path.join(merge_pbfs_path, dest, "state.txt")
  shutil.copy2(os.path.join(work_pbfs_path, d, "state.txt"), new_state)

  # free lock
  sys.stdout.flush()
  lock.release()

###########################################################################

if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser(description="Generate pbf/diff files for merge")
  parser.add_argument("--osmium", dest="osmium", action="store_true", default=False,
                      help="Use osmium instead of osmosis")
  parser.add_argument("--pbf", action="store_true", default=False,
                      help="Generate pbf files instead of diff")
  parser.add_argument("--country", dest="country", action="store", nargs="+",
                      help="Limit to a country")
  args = parser.parse_args()

  countries = None
  if args.pbf:
    pbf = True
  else:
    pbf = False

  if args.country:
    countries = args.country

  os.chdir("merge")
  for (r,d,files) in os.walk("."):
    for f in files:
      if countries and f not in countries:
        continue
      print(f)
      if pbf:
        merge_pbf(os.path.join(r, f), args.osmium)
      else:
        merge(os.path.join(r, f), args.osmium)
