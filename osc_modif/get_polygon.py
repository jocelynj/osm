#! /usr/bin/python3

import fileinput
import lxml
import lxml.html
import os
import requests
import sys

main_url = "http://polygons.openstreetmap.fr/"
relation_generation_url = main_url + "index.py"
polygon_union_url = main_url + "get_poly.py"

def generate_poly(country_name, polygon_id):
  print("  ", country_name, polygon_id)

  out_file = os.path.join("generated-polygons", country_name + ".poly")
  if os.path.exists(out_file):
    return

  if "/" in country_name:
    dir_name = os.path.join("generated-polygons", os.path.dirname(country_name))
    if not os.path.exists(dir_name):
      os.makedirs(dir_name)

  # generate relation boundary
  r = requests.get(relation_generation_url, params={"id": polygon_id})
  parser = lxml.html.HTMLParser(encoding='UTF-8')
  p = lxml.html.fromstring(r.text, parser=parser)

  print(relation_generation_url + "?id=" + str(polygon_id))

  try:
    form = p.forms[1]
    x = form.inputs["x"].value
    y = form.inputs["y"].value
    z = form.inputs["z"].value
  except:
    print("    * ERROR * ")
    return

  if not ("%s-%s-%s" % (x, y, z)) in r.text:
    r = requests.post(relation_generation_url, params={"id": polygon_id}, data={"x": x, "y": y, "z": z})

  r = requests.get(polygon_union_url, params={"id": polygon_id,
                                              "params": "%s-%s-%s" % (x,y,z)})

  out_file = os.path.join("generated-polygons", country_name + ".poly")
  with open(out_file, "wb") as text_file:
    text_file.write(r.content)

if __name__ == '__main__':

  import argparse

  parser = argparse.ArgumentParser(description="Initialise polygon files from %s" % main_url)
  parser.add_argument("--file", dest="file", action="store",
                      help="Get list of extracts to generate - format 'name rel_id' per line")
  parser.add_argument("--region", dest="region", action="store", nargs="+",
                      help="Get list of regin to generate - rel_id from osmose backend")
  args = parser.parse_args()

  if args.file:
    with open(args.file) as f:
      for line in f.readlines():
        (country_name, polygon_id) = line.split()
        generate_poly(country_name, polygon_id)
