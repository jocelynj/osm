#! /usr/bin/python

import sys
import urllib2

for line in sys.stdin:
  way_id = int(line.split()[0])
  urllib2.urlopen("http://localhost:8111/import?url=http://api.openstreetmap.org/api/0.6/way/%d/full" % way_id)
  urllib2.urlopen("http://localhost:8111/import?url=http://api.openstreetmap.org/api/0.6/way/%d/relations" % way_id)
