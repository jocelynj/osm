#! /usr/bin/env python3
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Jocelyn Jaubert <jocelyn.jaubert@gmail.com> 2011           ##
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

import re
from shapely.wkt import loads
from shapely.geometry import MultiPolygon
from shapely.geometry import Polygon
from shapely.geometry import Point

# Read a polygon from file
# NB: holes aren't supported yet
def read_polygon_wkt(f):

    coords = []
    first_coord = True
    while True:
        line = f.readline()
        if not(line):
            break;
            
        line = line.strip()
        if line == "END":
            break
        
        if not(line):
            continue
        
        ords = line.split()
        coords.append("%f %f" % (float(ords[0]), float(ords[1])))
    
    if len(coords) < 3:
        return None

    polygon = "((" + ", ".join(coords) + "))"
    
    return polygon    

# Read a multipolygon from the file
# First line: name (discarded)
# Polygon: numeric identifier, list of lon, lat, END
# Last line: END
def read_multipolygon_wkt(f):

    polygons = []
    skip_polygon = False
    while True:
        dummy = f.readline()
        if not(dummy):
            break
        if dummy[0] == "!":
            # this is a hole
            skip_polygon = True
        
        polygon = read_polygon_wkt(f)
        if polygon != None and not skip_polygon:
            polygons.append(polygon)
        skip_polygon = False

    wkt = "MULTIPOLYGON (" + ",".join(polygons) + ")"
    
    return wkt        

def read_multipolygon(f):
    wkt = read_multipolygon_wkt(f)
    return loads(wkt)

def write_polygon(f, wkt, p):

    match = re.search("^\(\((?P<pdata>.*)\)\)$", wkt)
    pdata = match.group("pdata")
    rings = re.split("\), *\(", pdata)

    first_ring = True
    for ring in rings:
        coords = re.split(",", ring)

        p = p + 1
        if first_ring:
            f.write(str(p) + "\n")
            first_ring = False
        else:
            f.write("!" + str(p) + "\n")

        for coord in coords:
            ords = coord.split()
            f.write("\t%s\t%s\n" % (ords[0], ords[1]))

        f.write("END\n")

    return p

def write_multipolygon(f, wkt):

    match = re.search("^MULTIPOLYGON *\((?P<mpdata>.*)\)$", wkt)

    if match:
        f.write("polygon\n")
        mpdata = match.group("mpdata")
        polygons = re.split("(?<=\)\)), *(?=\(\()", mpdata)

        p = 0
        for polygon in polygons:
            p = write_polygon(f, polygon, p)

        f.write("END\n")
        return

    match = re.search("^POLYGON *(?P<pdata>.*)$", wkt)
    if match:
        f.write("polygon\n")
        pdata = match.group("pdata")
        write_polygon(f, pdata, 0)
        f.write("END\n")


def check_intersection(polygon, coords):
    if len(coords) == 2:
        (lat, lon) = coords
        obj = Point((lon, lat))
    elif len(coords) == 4:
        minlat = float(coords["minlat"])
        minlon = float(coords["minlon"])
        maxlat = float(coords["maxlat"])
        maxlon = float(coords["maxlon"])
        obj = Polygon(((minlon, minlat), (minlon, maxlat),
                       (maxlon, maxlat), (maxlon, minlat)))

    return polygon.intersects(obj)

###########################################################################

if __name__ == "__main__":
    import sys
    f = sys.stdin
        
    name = f.readline().strip()
    geom = read_multipolygon(f)
    f.close()

    print(geom.area)

    print(check_intersection(geom, (1, 1)))
    print(check_intersection(geom, (48, 2)))
