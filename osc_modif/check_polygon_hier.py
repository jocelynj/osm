#! /usr/bin/env python3

import filecmp
import os
import shapely.ops
from modules import OsmGeom

polygon_dir = "polygons"

def read_polygon(f_name):
  with open(f_name, "r") as f:
    name = f.readline().strip()
    return OsmGeom.read_multipolygon(f)

def write_polygon(f_name, geom):
  os.makedirs(os.path.dirname(f_name), exist_ok=True)
  with open(f_name, "w") as f:
    return OsmGeom.write_multipolygon(f, geom)


def check_region(region_name):
  """ Check polygons in a given region
  """
  region_dir = os.path.join(polygon_dir, region_name)
  if not os.path.isdir(region_dir):
    raise Exception("Path '%s' doesn't exists" % region_dir)

  region_poly = read_polygon(region_dir + ".poly")

  tweak_country_poly = [region_poly]
  regenerate = False

  # firstly check sub-regions
  for name in os.listdir(region_dir):
    country_name = os.path.join(region_name, name)
    country_dir = os.path.join(polygon_dir, country_name)
    if os.path.isdir(country_dir):
      # New region to check
      check_region(country_name)

  # secondly check all .poly files
  for name in os.listdir(region_dir):
    country_name = os.path.join(region_name, name)
    country_dir = os.path.join(polygon_dir, country_name)
    if os.path.isdir(country_dir):
      continue

    country_poly = read_polygon(country_dir)
    tweak_country_poly.append(country_poly)

    if not region_poly.contains(country_poly):
      regenerate = True

  if regenerate:
    print(region_name)
    new_region_poly = shapely.ops.unary_union(tweak_country_poly).simplify(tolerance=0.001)
    write_polygon(region_dir + "_new.poly", new_region_poly.wkt)
    print("  old area = %f" % region_poly.area)
    print("  new area = %f" % new_region_poly.area)
    write_polygon("diff/" + region_name + "_diff.poly", new_region_poly.symmetric_difference(region_poly).wkt)


if __name__ == '__main__':

  import argparse

  parser = argparse.ArgumentParser(description="Check polygon hierarchical inclusion")
  parser.add_argument("--region", dest="regions", action="store", nargs="+",
                      help="Get list of region to check")
  args = parser.parse_args()

  if args.regions:
    for region in args.regions:
      check_region(region)
