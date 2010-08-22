#! /usr/bin/python

import os
import sys
import urllib2

way_ids = []
num = 0

def download(way_ids):
  url = "http://api.openstreetmap.org/api/0.6/ways?ways=%s" % ",".join(way_ids)
  webFile = urllib2.urlopen(url)
  localFile = open("/home/jocelyn/public_html/temp-ways.osm", 'w')
  localFile.write(webFile.read())
  webFile.close()
  localFile.close()
  urllib2.urlopen("http://localhost:8111/import?url=http://localhost/~jocelyn/temp-ways.osm")
 

for line in sys.stdin:
  way_ids.append("%d" % int(line.split()[0]))
  num += 1
  if num > 100:
    download(way_ids)
    way_ids = []
    num = 0

download(way_ids)
