#! /usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Etienne Chové <chove@crans.org> 2009                       ##
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

"""
usage: mega-relation-analyser ##### (where ##### is the relation id)
It will create :
    - relation-#####.svg   # svg image
    - relation-#####.gpx   # gpx data
    - relation-#####.way   # python usable data
    - relation-#####.poly  # osmosis aware polygon
"""

import re, sys, urllib2

ReGetId   = re.compile(u" id=\"[^\"]*\"")
ReGetLat  = re.compile(u" lat=\"[^\"]*\"")
ReGetLon  = re.compile(u" lon=\"[^\"]*\"")
ReGetRef  = re.compile(u" ref=\"[^\"]*\"")
ReGetType = re.compile(u" type=\"[^\"]*\"")

#############################################################
# Data reader

def GetLinesFromApi(page):
    print "Downloading : http://www.openstreetmap.org/api/0.6/"+page
    req = urllib2.Request("http://www.openstreetmap.org/api/0.6/"+page)
    return [ x.decode("utf8").strip() for x in urllib2.urlopen(req).readlines() ]

def GetNodesForWay(wayid):
    nodes_coords = {}
    nodes_order  = []
    for line in GetLinesFromApi("way/"+str(wayid)+"/full"):
        if line.startswith("<node "):
            NodeId  = ReGetId.findall(line)[0][5:-1]
            NodeLat = ReGetLat.findall(line)[0][6:-1]
            NodeLon = ReGetLon.findall(line)[0][6:-1]
            nodes_coords[NodeId] = (NodeLat, NodeLon)
        elif line.startswith("<nd "):
            NodeId  = ReGetRef.findall(line)[0][6:-1]
            nodes_order.append(NodeId)
    if not nodes_order:
        raise ValueError("Empty way : "+wayid)
    return [(NodeId, nodes_coords.get(NodeId,(0,0))[0], nodes_coords.get(NodeId,(0,0))[1]) for NodeId in nodes_order]

def GetWaysForRelation(relationid):
    ways = []
    for line in GetLinesFromApi("relation/"+str(relationid)):
        if line.startswith("<member "):
            MembType = ReGetType.findall(line)[0][7:-1]
            MembRef  = ReGetRef.findall(line)[0][6:-1]
            if MembType == "way":
                ways.append(GetNodesForWay(MembRef))
            elif MembType == "relation":
                ways += GetWaysForRelation(MembRef)
    return ways

#############################################################
# Data analysis

def JoinWays(ways):
    #return ways
    dicoways = {}
    for i in range(len(ways)):
        dicoways[str(i)+"-1"] = []
        dicoways[str(i)+"-2"] = []
        for x in ways[i]:
            dicoways[str(i)+"-1"].append(x)
            dicoways[str(i)+"-2"].insert(0, x)
    newways = []
    for i in range(len(ways)):
        if not str(i)+"-1" in dicoways.keys(): continue
        newway = dicoways[str(i)+"-1"]
        dicoways.pop(str(i)+"-1")
        dicoways.pop(str(i)+"-2")
        ok = True
        while ok and newway[0][0] <> newway[-1][0]:
            ok = False
            for j in dicoways.keys():
                if dicoways[j][0][0] == newway[-1][0]:
                    ok = True
                    newway = newway + dicoways[j][1:]
                    dicoways.pop(j[:-2]+"-1")
                    dicoways.pop(j[:-2]+"-2")
                    break
                elif dicoways[j][-1][0] == newway[0][0]:
                    ok = True
                    newway = dicoways[j] + newway[1:]
                    dicoways.pop(j[:-2]+"-1")
                    dicoways.pop(j[:-2]+"-2")
                    break
        newways.append(newway)
    return newways

def WaysCheck(ways):
    ok = True
    for w in ways:
        if w[0][0] <> w[-1][0]:
            print "open way " + w[0][0] + "-" + w[-1][0]
            ok = False
    return ok

def WaysToBbox(ways):
    x = float(ways[0][0][1])
    y = float(ways[0][0][2])
    xmin = x
    xmax = x
    ymin = y
    ymax = y
    for w in ways:
        for n in w:
            x = float(n[1])
            y = float(n[2])
            xmin = min(xmin, x)
            xmax = max(xmax, x)
            ymin = min(ymin, y)
            ymax = max(ymax, y)
    return [xmin, ymin, xmax, ymax]
    
#############################################################
# Data formaters

def WaysToSvg(ways, file):
    marge = 0.1
    b = WaysToBbox(ways)
    file.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n")
    file.write("<svg width=\""+str(abs(b[3]-b[1])+2*marge)+"\" height=\""+str(abs(b[2]-b[0])+2*marge)+"\">\n")
    for i in range(len(ways)):
        file.write("<path d=\"M " + " L ".join(str(marge+float(x[2])-b[1]) + "," + str(marge+b[2]-float(x[1])) for x in ways[i]))
        file.write("\" fill=\"none\" stroke=\"#0000FF\" stroke-width=\"0.05\" stroke-linecap=\"round\" stroke-linejoin=\"round\" />\n")
        if ways[i][0][0] <> ways[i][-1][0]:
            d = 0.1
            x = marge+float(ways[i][0][2])-b[1]
            y = marge+b[2]-float(ways[i][0][1])
            file.write("<path d=\"M " + str(x-d) + "," + str(y-d) + " L " + str(x+d) + "," + str(y+d) + "\" fill=\"none\" stroke=\"#FF0000\" stroke-width=\"0.02\" stroke-linecap=\"round\" stroke-linejoin=\"round\" />\n")
            file.write("<path d=\"M " + str(x+d) + "," + str(y-d) + " L " + str(x-d) + "," + str(y+d) + "\" fill=\"none\" stroke=\"#FF0000\" stroke-width=\"0.02\" stroke-linecap=\"round\" stroke-linejoin=\"round\" />\n")
            x = marge+float(ways[i][-1][2])-b[1]
            y = marge+b[2]-float(ways[i][-1][1])
            file.write("<path d=\"M " + str(x-d) + "," + str(y-d) + " L " + str(x+d) + "," + str(y+d) + "\" fill=\"none\" stroke=\"#FF0000\" stroke-width=\"0.02\" stroke-linecap=\"round\" stroke-linejoin=\"round\" />\n")
            file.write("<path d=\"M " + str(x+d) + "," + str(y-d) + " L " + str(x-d) + "," + str(y+d) + "\" fill=\"none\" stroke=\"#FF0000\" stroke-width=\"0.02\" stroke-linecap=\"round\" stroke-linejoin=\"round\" />\n")
    file.write("</svg>\n")
    file.close()

def WaysToPoly(ways, title, file):
    file.write(title + "\n")
    for i in range(len(ways)):
        file.write(str(i+1) + "\n")
        for n in ways[i]:
            file.write("  " + n[1] + " " + n[2] + "\n")
        file.write("END\n")
    file.write("END\n")
    file.close()

def WaysToGpx(ways, file):
    file.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\" standalone=\"yes\"?>\n")
    file.write("<gpx version=\"1.1\" creator=\"relation-to-data.py\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" ")
    file.write("xmlns=\"http://www.topografix.com/GPX/1/1\" ")
    file.write("xsi:schemaLocation=\"http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd\">\n")
    file.write("<metadata>\n")
    file.write("</metadata>\n")
    for i in range(len(ways)):
        file.write("<trk>\n")
        file.write("<name></name>\n")
        file.write("<desc></desc>\n")
        file.write("<trkseg>\n")
        for pt in ways[i]:
            file.write("<trkpt lat=\""+pt[1]+"\" lon=\""+pt[2]+"\"></trkpt>\n")
        file.write("</trkseg>\n")
        file.write("</trk>\n")
    file.write("<extensions>\n")
    file.write("</extensions>\n")
    file.write("</gpx>\n")
    file.close()

#############################################################
# Simplify ways (improve this)

def SimplifyWay2(way):
    return [way[i] for i in range(len(way)) if (i==0 or i==(len(way)-1) or not i%50)]

import math
def Distance(pt1, pt2):
    lat1 = float(pt1[1])
    lon1 = float(pt1[2])
    lat2 = float(pt2[1])
    lon2 = float(pt2[2])
    return math.acos(math.sin(lat1)*math.sin(lat2)+math.cos(lat1)*math.cos(lat2)*math.cos(lon1-lon2))

def SimplifyWay(way):
    print "debut ", len(way)
    ok = True
    m = 0
    while ok and len(way)>21:
        ok = False
        for i in range(m, len(way)-2):
            if Distance(way[i], way[i+2]) <= .005: #0.005=30km
                m = i
                ok = True
                way.pop(i+1)
                break
    print "fin ", len(way)
    return way

def SimplifyWays(ways):
    return [SimplifyWay2(w) for w in ways]

#############################################################
# Mercator projection

import math

def WaysToMercator(ways):
    bbox   = WaysToBbox(ways) # [xmin, ymin, xmax, ymax]
    center = [(bbox[0]+bbox[2])/2, (bbox[1]+bbox[3])/2]
    return [WayToMercator(w, center) for w in ways]

def WayToMercator(way, center):
    return [PointToMercator(pt, center) for pt in way]

def PointToMercator(pt, center):
    x = float(pt[2]) - center[0]
    y = (180/math.pi) * math.log(math.tan( (math.pi/4) + (math.pi/360)*float(pt[1]) ) )
    #print float(pt[1]), y
    return (pt[0], str(y), str(x))

#############################################################

if __name__ == "__main__":
    relid = sys.argv[1]

    if "--debug" in sys.argv:
        print "Load ways"
        w = eval(open("relation-"+relid+".way").read())
    else:
        print "Read ways"
        w = GetWaysForRelation(relid)
        print "Save ways"
        f = open("relation-"+relid+".way","w").write(repr(w))

    print "Join ways"
    w = JoinWays(w)

    print "Projection"
    w2 = WaysToMercator(w)

    print "Write and Write Svg"
    WaysToSvg(w2, open("relation-"+relid+".svg","w"))
    
    print "Make and Write Gpx"
    WaysToGpx(w, open("relation-"+relid+".gpx","w"))

    print "Way Check"
    c = WaysCheck(w)

    if c:
        print "Make and Write Poly"
        r = WaysToPoly(w, "relation-"+relid, open("relation-"+relid+".poly","w"))

    print "Simplify Ways"
    w = SimplifyWays(w)

    print "Projection"
    w2 = WaysToMercator(w)

    print "Write and Write Svg"
    WaysToSvg(w2, open("relation-"+relid+"-simp.svg","w"))

    print "Make and Write Gpx"
    WaysToGpx(w, open("relation-"+relid+"-simp.gpx","w"))

    print "Way Check"
    c = WaysCheck(w)

    if c:
        print "Make and Write Poly"
        r = WaysToPoly(w, "relation-"+relid, open("relation-"+relid+"-simp.poly","w"))
