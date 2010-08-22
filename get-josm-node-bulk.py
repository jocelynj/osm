#! /usr/bin/python

import os
import sys
import urllib2

node_ids = []
num = 0

def download(node_ids):
  url = "http://api.openstreetmap.org/api/0.6/nodes?nodes=%s" % ",".join(node_ids)
  webFile = urllib2.urlopen(url)
  localFile = open("/home/jocelyn/public_html/temp-nodes.osm", 'w')
  localFile.write(webFile.read())
  webFile.close()
  localFile.close()
  urllib2.urlopen("http://localhost:8111/import?url=http://localhost/~jocelyn/temp-nodes.osm")
 

for line in sys.stdin:
  node_ids.append("%d" % int(line.split()[0]))
  num += 1
  if num > 100:
    download(node_ids)
    node_ids = []
    num = 0

download(node_ids)
