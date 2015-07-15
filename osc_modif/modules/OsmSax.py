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

import re, commands, sys, os, time, bz2, xml, gzip, cStringIO
from xml.sax import make_parser, handler
from xml.sax.saxutils import XMLGenerator, quoteattr
from OrderedDict import OrderedDict

###########################################################################

class dummylog:
    def log(self, text):
        return

class dummyout:
    def __init__(self):
        self._n = 0
        self._w = 0
        self._r = 0
    def NodeCreate(self, data):
        self._n += 1
        return
    def WayCreate(self, data):
        self._w += 1
        return
    def RelationCreate(self, data):
        self._r += 1
        return
    def __del__(self):
        print self._n, self._w, self._r

def GetFile(f, mode="r"):
    if type(f) == file:
        return f
    elif f.endswith(".bz2"):
        return bz2.BZ2File(f, mode)
    elif f.endswith(".gz"):
        return gzip.open(f, mode)
    else:
        return open(f, mode)

###########################################################################

class OsmSaxReader(handler.ContentHandler):

    def log(self, txt):
        self._logger.log(txt)
    
    def __init__(self, filename, logger = dummylog()):
        self._filename = filename
        self._logger   = logger
        
    def CopyTo(self, output):
        self._debug_in_way      = False
        self._debug_in_relation = False
        self.log("starting nodes")
        self._output = output
        parser = make_parser()
        parser.setContentHandler(self)
        parser.parse(GetFile(self._filename))

    def startElement(self, name, attrs):
        attrs = attrs._attrs
        if name == u"changeset":
            self._tags = {}
        elif name == u"node":
            attrs[u"id"] = int(attrs[u"id"])
            attrs[u"lat"] = float(attrs[u"lat"])
            attrs[u"lon"] = float(attrs[u"lon"])
            if u"version" in attrs:
                attrs[u"version"] = int(attrs[u"version"])
            self._data = attrs
            self._tags = {}
        elif name == u"way":
            if not self._debug_in_way:
                self._debug_in_way = True
                self.log("starting ways")
            attrs["id"] = int(attrs["id"])
            if u"version" in attrs:
                attrs[u"version"] = int(attrs[u"version"])
            self._data = attrs
            self._tags = {}
            self._nodes = []
        elif name == u"relation":
            if not self._debug_in_relation:
                self._debug_in_relation = True
                self.log("starting relations")
            attrs["id"] = int(attrs["id"])
            if u"version" in attrs:
                attrs[u"version"] = int(attrs[u"version"])
            self._data = attrs
            self._members = []
            self._tags = {}
        elif name == u"nd":
            self._nodes.append(int(attrs["ref"]))
        elif name == u"tag":
            self._tags[attrs["k"]] = attrs["v"]
        elif name == u"member":
            attrs["ref"] = int(attrs["ref"])
            self._members.append(attrs)

    def endElement(self, name):
        if name == u"changeset":
            pass
        elif name == u"node":
            self._data[u"tag"] = self._tags
            try:
                self._output.NodeCreate(self._data)
            except:
                print self._data
                raise
        elif name == u"way":
            self._data[u"tag"] = self._tags
            self._data[u"nd"]  = self._nodes
            try:
                self._output.WayCreate(self._data)
            except:
                print self._data
                raise
        elif name == u"relation":
            self._data[u"tag"]    = self._tags
            self._data[u"member"] = self._members
            try:
                self._output.RelationCreate(self._data)
            except:
                print self._data
                raise

###########################################################################

class OsmTextReader:

    def log(self, txt):
        self._logger.log(txt)
    
    def __init__(self, filename, logger = dummylog()):
        self._filename = filename
        self._logger   = logger
        
    def CopyTo(self, output):
        
        _re_eid = re.compile( " id=['\"](.+?)['\"]")
        _re_lat = re.compile(" lat=['\"](.+?)['\"]")
        _re_lon = re.compile(" lon=['\"](.+?)['\"]")
        _re_usr = re.compile(" user=['\"](.+?)['\"]")
        _re_tag = re.compile(" k=['\"](.+?)['\"] v=['\"](.+?)['\"]")
        
        f = GetFile(self._filename)
        l = f.readline()
        while l:
            
            if "<node" in l:
                
                _dat = {}
                _dat["id"]  = int(_re_eid.findall(l)[0])
                _dat["lat"] = float(_re_lat.findall(l)[0])
                _dat["lon"] = float(_re_lon.findall(l)[0])
                _usr = _re_lon.findall(l)
                if _usr:
                    _dat["lon"] = _usr[0].decode("utf8")
                _dat["tag"] = {}
                
                if "/>" in l:
                    output.NodeCreate(_dat)
                    l = f.readline()
                    continue
                
                l = f.readline()
                while "</node>" not in l:
                    _tag = _re_tag.findall(l)[0]
                    _dat["tag"][_tag[0].decode("utf8")] = _tag[1].decode("utf8")
                    l = f.readline()
                
                output.NodeCreate(_dat)
                l = f.readline()
                continue
            
            if "<way" in l:
                
                _dat = {}
                _dat["id"]  = int(_re_eid.findall(l)[0])
                _usr = _re_lon.findall(l)
                if _usr:
                    _dat["lon"] = _usr[0].decode("utf8")
                _dat["tag"] = {}
                _dat["nd"]  = []
                
                l = f.readline()
                while "</way>" not in l:
                    if "<nd" in l:
                        _dat["nd"].append(int(_re_nod.findall(l)[0]))
                        continue
                    _tag = _re_tag.findall(l)[0]
                    _dat["tag"][_tag[0].decode("utf8")] = _tag[1].decode("utf8")
                    l = f.readline()
                
                output.WayCreate(_dat)
                l = f.readline()
                continue
            
            if "<relation" in l:
                l = f.readline()
                continue        
            
            l = f.readline()

###########################################################################

class OscSaxReader(handler.ContentHandler):

    def log(self, txt):
        self._logger.log(txt)

    def __init__(self, filename, logger = dummylog()):
        self._filename = filename
        self._logger   = logger
 
    def CopyTo(self, output):
        self._output = output
        parser = make_parser()
        parser.setContentHandler(self)
        parser.parse(GetFile(self._filename))
        
    def startElement(self, name, attrs):
        attrs = attrs._attrs
        if name == u"create":
            self._action = name
        elif name == u"modify":
            self._action = name
        elif name == u"delete":
            self._action = name
        elif name == u"changeset":
            self._tags = {}
        elif name == u"node":
            attrs[u"id"] = int(attrs[u"id"])
            attrs[u"lat"] = float(attrs[u"lat"])
            attrs[u"lon"] = float(attrs[u"lon"])
            attrs[u"version"] = int(attrs[u"version"])
            self._data = attrs
            self._tags = {}
        elif name == u"way":
            attrs["id"] = int(attrs["id"])
            attrs[u"version"] = int(attrs[u"version"])
            self._data = attrs
            self._tags = {}
            self._nodes = []
        elif name == u"relation":
            attrs["id"] = int(attrs["id"])
            attrs[u"version"] = int(attrs[u"version"])
            self._data = attrs
            self._members = []
            self._tags = {}
        elif name == u"nd":
            self._nodes.append(int(attrs["ref"]))
        elif name == u"tag":
            self._tags[attrs["k"]] = attrs["v"]
        elif name == u"member":
            attrs["ref"] = int(attrs["ref"])
            self._members.append(attrs)
        elif name == u"osmChange":
            self._output.begin()
        elif name == u"bbox":
            self._data["bbox"] = attrs

    def endElement(self, name):
        if name == u"changeset":
            pass
        elif name == u"node":
            self._data[u"tag"] = self._tags
            if self._action == u"create":
                self._output.NodeCreate(self._data)
            elif self._action == u"modify":
                self._output.NodeUpdate(self._data)
            elif self._action == u"delete":
                self._output.NodeDelete(self._data)             
        elif name == u"way":
            self._data[u"tag"] = self._tags
            self._data[u"nd"]  = self._nodes
            if self._action == u"create":
                self._output.WayCreate(self._data)
            elif self._action == u"modify":
                self._output.WayUpdate(self._data)
            elif self._action == u"delete":
                self._output.WayDelete(self._data)  
        elif name == u"relation":
            self._data[u"tag"]    = self._tags
            self._data[u"member"] = self._members
            if self._action == u"create":
                self._output.RelationCreate(self._data)
            elif self._action == u"modify":
                self._output.RelationUpdate(self._data)
            elif self._action == u"delete":
                self._output.RelationDelete(self._data)  
        elif name == u"osmChange":
            self._output.end()

###########################################################################

def _formatData(data):
    data = dict(data)
    if u"tag" in data:
        data.pop(u"tag")
    if u"nd" in data:
        data.pop(u"nd")
    if u"member" in data:
        data.pop(u"member")
    if u"visible" in data:
        data[u"visible"] = str(data[u"visible"]).lower()
    if u"id" in data:
        data[u"id"] = str(data[u"id"])
    if u"lat" in data:
        data[u"lat"] = str(data[u"lat"])
    if u"lon" in data:
        data[u"lon"] = str(data[u"lon"])
    if u"changeset" in data:
        data[u"changeset"] = str(data[u"changeset"])
    if u"version" in data:
        data[u"version"] = str(data[u"version"])
    if u"uid" in data:
        data[u"uid"] = str(data[u"uid"])
    return _orderData(data)

def _orderData(data):
    data_o = OrderedDict()
    attrs_list = ("id", "version", "timestamp", "uid", "user", "changeset", "lat", "lon")
    for a in attrs_list:
        if a in data:
            data_o[a] = data[a]
    return data_o


class OsmSaxWriter(XMLGenerator):

    def __init__(self, out, enc):
        if type(out) == str:
            XMLGenerator.__init__(self, open(out, "w"), enc)
        else:
            XMLGenerator.__init__(self, out, enc)
    
    def startElement(self, name, attrs):
        self._write(u'<' + name)
        for (name, value) in attrs.items():
            self._write(u' %s=%s' % (name, quoteattr(value)))
        self._write(u'>\n')
        
    def endElement(self, name):
        self._write(u'</%s>\n' % name)
    
    def Element(self, name, attrs):
        self._write(u'<' + name)
        for (name, value) in attrs.items():
            self._write(u' %s=%s' % (name, quoteattr(value)))
        self._write(u' />\n')


    def NodeCreate(self, data):
        if not data:
            return
        if data[u"tag"]:
            self.startElement("node", _formatData(data))
            for (k, v) in data[u"tag"].items():
                self.Element("tag", {"k":k, "v":v})
            self.endElement("node")
        else:
            self.Element("node", _formatData(data))
    
    def WayCreate(self, data):
        if not data:
            return
        self.startElement("way", _formatData(data))
        for (k, v) in data[u"tag"].items():
            self.Element("tag", {"k":k, "v":v})
        for n in data[u"nd"]:
            self.Element("nd", {"ref":str(n)})
        self.endElement("way")
    
    def RelationCreate(self, data):
        if not data:
            return
        self.startElement("relation", _formatData(data))
        for (k, v) in data[u"tag"].items():
            self.Element("tag", {"k":k, "v":v})
        for m in data[u"member"]:
            m[u"ref"] = str(m[u"ref"])
            self.Element("member", m)
        self.endElement("relation")
      
def NodeToXml(data, full = False):
    o = cStringIO.StringIO()
    w = OsmSaxWriter(o, "UTF-8")
    if full:
        w.startDocument()
        w.startElement("osm", {})
    if data:
        w.NodeCreate(data)
    if full:
        w.endElement("osm")
    return o.getvalue()

def WayToXml(data, full = False):
    o = cStringIO.StringIO()
    w = OsmSaxWriter(o, "UTF-8")
    if full:
        w.startDocument()
        w.startElement("osm", {})
    if data:
        w.WayCreate(data)
    if full:
        w.endElement("osm")
    return o.getvalue()

def RelationToXml(data, full = False):
    o = cStringIO.StringIO()
    w = OsmSaxWriter(o, "UTF-8")
    if full:
        w.startDocument()
        w.startElement("osm", {})
    if data:
        w.RelationCreate(data)
    if full:
        w.endElement("osm")
    return o.getvalue()


###########################################################################

class OscSaxWriter(XMLGenerator):

    def __init__(self, out, enc, reader = None):
        XMLGenerator.__init__(self, GetFile(out, "w"), enc)
        self.reader = reader

    def startElement(self, name, attrs):
        self._write(u'<' + name)
        for (name, value) in attrs.items():
            self._write(u' %s=%s' % (name, quoteattr(value)))
        self._write(u'>\n')
        
    def endElement(self, name):
        self._write(u'</%s>\n' % name)
    
    def Element(self, name, attrs):
        self._write(u'<' + name)
        for (name, value) in attrs.items():
            self._write(u' %s=%s' % (name, quoteattr(value)))
        self._write(u'/>\n')

    def begin(self):
        self.startElement("osmChange", { "version": "0.6",
                                         "generator": "OsmSax" })
        self.nodes_printed = []
        self.nodes_to_add = []
        self.ways_printed = []
        self.ways_to_add = []
        self.t1 = time.time()

    def end(self):
        t2 = time.time()

        if self.reader:
            # add ways that were not modified, but included by ways or relations
            t1 = time.time()
            ways_to_add = set(self.ways_to_add) - set(self.ways_printed)
            for i in ways_to_add:
                way_info = self.reader.WayGet(i)
                if way_info:
                    self.WayUpdate(way_info)
            t2 = time.time()
            print "new ways took:", t2 - t1, "for", len(ways_to_add)
    
            # add nodes that were not modified, but included by ways or relations
            t1 = time.time()
            nodes_to_add = set(self.nodes_to_add) - set(self.nodes_printed)
            for i in nodes_to_add:
                node_info = self.reader.NodeGet(i)
                if node_info:
                    self.NodeUpdate(node_info)
            t2 = time.time()
            print "new nodes took:", t2 - t1, "for", len(nodes_to_add)

        self.endElement("osmChange")


    def NodeNew(self, data, action):
        if not data:
            return
        self.startElement(action, {})
        if data[u"tag"]:
            self.startElement("node", _formatData(data))
            for (k, v) in data[u"tag"].items():
                self.Element("tag", {"k":k, "v":v})
            self.endElement("node")
        else:
            self.Element("node", _formatData(data))
        self.nodes_printed.append(int(data["id"]))
        self.endElement(action)

    def NodeCreate(self, data):
       self.NodeNew(data, "create")
    
    def NodeUpdate(self, data):
       self.NodeNew(data, "modify")
    
    def NodeDelete(self, data):
       self.NodeNew(data, "delete")
   
 
    def WayNew(self, data, action):
        if not data:
            return
        self.startElement(action, {})
        self.startElement("way", _formatData(data))
        for (k, v) in data[u"tag"].items():
            self.Element("tag", {"k":k, "v":v})
        for n in data[u"nd"]:
            self.Element("nd", {"ref":str(n)})
            self.nodes_to_add.append(n)
        self.endElement("way")
        self.ways_printed.append(int(data["id"]))
        self.endElement(action)

    def WayCreate(self, data):
       self.WayNew(data, "create")

    def WayUpdate(self, data):
       self.WayNew(data, "modify")

    def WayDelete(self, data):
       self.WayNew(data, "delete")
   
 
    def RelationNew(self, data, action):
        if not data:
            return
        self.startElement(action, {})
        self.startElement("relation", _formatData(data))
        for (k, v) in data[u"tag"].items():
            self.Element("tag", {"k":k, "v":v})
        for m in data[u"member"]:
            if m[u"type"] == u"node":
                self.nodes_to_add.append(m[u"ref"])
            elif m[u"type"] == u"way":
                self.ways_to_add.append(m[u"ref"])
            m[u"ref"] = str(m[u"ref"])
            self.Element("member", m)
        self.endElement("relation")
        self.endElement(action)

    def RelationCreate(self, data):
       self.RelationNew(data, "create")

    def RelationUpdate(self, data):
       self.RelationNew(data, "modify")

    def RelationDelete(self, data):
       self.RelationNew(data, "delete")

###########################################################################

class OscPositionSaxWriter(OscSaxWriter):

    def __init__(self, out, enc, reader = None):
        XMLGenerator.__init__(self, GetFile(out, "w"), enc)
        self.reader = reader
    
    def begin(self):
        self.startElement("osmChange", { "version": "0.6",
                                         "generator": "OsmSax" })
        self.nodes_printed = []
        self.nodes_to_add = []
        self.ways_printed = []
        self.ways_to_add = []
        self.t1 = time.time()

    def end(self):
        t2 = time.time()

        # add ways that were not modified, but included by ways or relations
        t1 = time.time()
        ways_to_add = set(self.ways_to_add) - set(self.ways_printed)
        for i in ways_to_add:
            way_info = self.reader.WayGetNodes(i)
            if way_info:
                self.WayNew(way_info, "")
        t2 = time.time()
        print "new ways took:", t2 - t1, "for", len(ways_to_add)

        # add nodes that were not modified, but included by ways or relations
        t1 = time.time()
        nodes_to_add = set(self.nodes_to_add) - set(self.nodes_printed)
        for i in nodes_to_add:
            node_info = self.reader.NodeGetPosition(i)
            if node_info:
                self.NodeNew(node_info, "")
        t2 = time.time()
        print "new nodes took:", t2 - t1, "for", len(nodes_to_add)
        self.endElement("osmChange")


    def NodeNew(self, data, action):
        if not data:
            return
        self.Element("node", { "id": str(data["id"]),
                               "lat": str(data["lat"]),
                               "lon": str(data["lon"])
                             }
                    )
        self.nodes_printed.append(int(data["id"]))

    def WayNew(self, data, action):
        if not data:
            return
        for n in data[u"nd"]:
            self.nodes_to_add.append(n)

    def RelationNew(self, data, action):
        if not data:
            return
        for m in data[u"member"]:
            if m[u"type"] == u"node":
                self.nodes_to_add.append(m[u"ref"])
            elif m[u"type"] == u"way":
                self.ways_to_add.append(m[u"ref"])

###########################################################################

class OscFilterSaxWriter(OscSaxWriter):

    def __init__(self, out, enc, reader = None, check_intersection = None, poly = None, poly_buffered = None):
        XMLGenerator.__init__(self, GetFile(out, "w"), enc)
        self.reader = reader
        self.check_intersection = check_intersection
        self.poly = []
        self.poly.append(poly)
        self.poly.append(poly_buffered)
        self.poly_num = 2

        self.num_read_nodes = 0
        self.num_read_ways = 0
        self.num_read_relations = 0
    
    def begin(self):
        self.startElement("osmChange", { "version": "0.6",
                                         "generator": "OsmSax" })
        self._prev_action = ""
        self.nodes_added_in_poly = []
        self.ways_added_in_poly = []
        self.rels_added_in_poly = []
        for i in xrange(self.poly_num):
            self.nodes_added_in_poly.append(set())
            self.ways_added_in_poly.append(set())
            self.rels_added_in_poly.append(set())
        self.t1 = time.time()

    def end(self):
        t2 = time.time()

        if self._prev_action != "":
            self.endElement(self._prev_action)
        self.endElement("osmChange")

        print "read %d nodes, %d ways, %d relations" % (self.num_read_nodes, self.num_read_ways, self.num_read_relations)


    def NodeNew(self, data, action):
        if not data:
            print "NodeNew - no data found..."
            return

        if self.NodeWithinPoly(1, data["id"], data):
            # new node is in buffered polygon
            self.nodes_added_in_poly[1].add(data["id"])
            if self.NodeWithinPoly(0, data["id"], data):
                self.nodes_added_in_poly[0].add(data["id"])
            else:
                action = "delete"
        elif self.NodeWithinPoly(1, data["id"], None):
            # node was previously in buffered polygon
            action = "delete"
        else:
            return

        if action != self._prev_action:
            if self._prev_action != "":
                self.endElement(self._prev_action)
            self.startElement(action, {})
            self._prev_action = action

        if data[u"tag"]:
            self.startElement("node", _formatData(data))
            for (k, v) in data[u"tag"].items():
                self.Element("tag", {"k":k, "v":v})
            self.endElement("node")
        else:
            self.Element("node", _formatData(data))

    def NodeWithinPoly(self, poly_idx, id, data = None):
        if not data:
            if id in self.nodes_added_in_poly[poly_idx]:
                return True
            data = self.reader.NodeGet(id)
            self.num_read_nodes += 1
            if not data:
                return False

        return self.check_intersection(self.poly[poly_idx], (data["lat"], data["lon"]))

    def WayNew(self, data, action):
        if not data:
            print "WayNew - no data found..."
            return

        if self.WayWithinPoly(1, data["id"], data):
            # new way is in buffered polygon
            self.ways_added_in_poly[1].add(data["id"])
            if self.WayWithinPoly(0, data["id"], data):
                self.ways_added_in_poly[0].add(data["id"])
            else:
                action = "delete"
        elif self.WayWithinPoly(1, data["id"], None):
            # way was previously in buffered polygon
            action = "delete"
        else:
            return

        if action != self._prev_action:
            if self._prev_action != "":
                self.endElement(self._prev_action)
            self.startElement(action, {})
            self._prev_action = action

        self.startElement("way", _formatData(data))
        if "bbox" in data:
            bbox = data["bbox"]
            self.Element("bbox", {"minlat":str(bbox["minlat"]),"minlon":str(bbox["minlon"]),
                                  "maxlat":str(bbox["maxlat"]),"maxlon":str(bbox["maxlon"])})
        for (k, v) in data[u"tag"].items():
            self.Element("tag", {"k":k, "v":v})
        for n in data[u"nd"]:
            self.Element("nd", {"ref":str(n)})
        self.endElement("way")

    def WayWithinPoly(self, poly_idx, id, data = None):
        if data and "bbox" in data:
            if not self.check_intersection(self.poly[poly_idx], data["bbox"]):
                return False

        if not data or len(data["nd"]) == 0:
            if id in self.ways_added_in_poly[poly_idx]:
                return True
            data = self.reader.WayGet(id)
            self.num_read_ways += 1
            if not data:
                return False

        way_nodes = data[u"nd"]
        for n in way_nodes:
            if self.NodeWithinPoly(poly_idx, n):
                return True
        return False

    def RelationNew(self, data, action):
        if not data:
            print "RelationNew - no data found..."
            return

        bbox_data = {}
        bbox_data["member"] = {}
        if "bbox" in data:
            bbox_data["bbox"] = data["bbox"]

        if self.RelationWithinPoly(1, data["id"], data):
            # new relation is in buffered polygon
            self.rels_added_in_poly[1].add(data["id"])
            if self.RelationWithinPoly(0, data["id"], data):
                self.rels_added_in_poly[0].add(data["id"])
            else:
                action = "delete"
        elif self.RelationWithinPoly(1, data["id"], bbox_data):
            # relation was previously in buffered polygon
            action = "delete"
        else:
            return

        if action != self._prev_action:
            if self._prev_action != "":
                self.endElement(self._prev_action)
            self.startElement(action, {})
            self._prev_action = action

        self.startElement("relation", _formatData(data))
        if "bbox" in data:
            bbox = data["bbox"]
            self.Element("bbox", {"minlat":str(bbox["minlat"]),"minlon":str(bbox["minlon"]),
                                  "maxlat":str(bbox["maxlat"]),"maxlon":str(bbox["maxlon"])})
        for (k, v) in data[u"tag"].items():
            self.Element("tag", {"k":k, "v":v})
        for m in data[u"member"]:
            m[u"ref"] = str(m[u"ref"])
            self.Element("member", m)
        self.endElement("relation")

    def RelationWithinPoly(self, poly_idx, id, data = None, rec_rel = []):
        if data and "bbox" in data:
            if not self.check_intersection(self.poly[poly_idx], data["bbox"]):
                return False

        if not data or len(data["member"]) == 0:
            if id in rec_rel:
                print "recursion on id=%d - rec_rel=%s" % (id, str(rec_rel))
                return False
            if id in self.rels_added_in_poly[poly_idx]:
                return True
            data = self.reader.RelationGet(id)
            self.num_read_relations += 1
            if not data:
                return False

        for m in data[u"member"]:
            ref = m[u"ref"]
            if m[u"type"] == u"node":
                if self.NodeWithinPoly(poly_idx, ref):
                    return True
            elif m[u"type"] == u"way":
                if self.WayWithinPoly(poly_idx, ref):
                    return True
            elif m[u"type"] == u"relation":
                if self.RelationWithinPoly(poly_idx, ref, rec_rel=rec_rel + [id]):
                    return True
        return False

###########################################################################

class OscBBoxSaxWriter(OscSaxWriter):

    def __init__(self, out, enc, reader):
        XMLGenerator.__init__(self, GetFile(out, "w"), enc)
        self.reader = reader

        self.num_read_nodes = 0
        self.num_read_ways = 0
        self.num_read_relations = 0
    
    def begin(self):
        self.startElement(u"osmChange", { u"version": u"0.6",
                                          u"generator": u"OsmSax" })
        self._prev_action = ""
        self.nodes_modified = {}
        self.ways_modified = {}
        self.rels_modified = {}

    def end(self):
        if self._prev_action != "":
            self.endElement(self._prev_action)
        self.endElement("osmChange")

        print "read %d nodes, %d ways, %d relations" % (self.num_read_nodes, self.num_read_ways, self.num_read_relations)

    def concat_bbox(self, bbox1, bbox2):
        if bbox1 == None:
            return bbox2
        if bbox2 == None:
            return bbox1
        bbox = self.expand_bbox(bbox1, bbox2[0], bbox2[1])
        bbox = self.expand_bbox(bbox,  bbox2[2], bbox2[3])
        return bbox

    def expand_bbox(self, bbox, lat, lon):
        if bbox == None:
            return [lat, lon, lat, lon]
        if lat < bbox[0]:
            bbox[0] = lat
        if lat > bbox[2]:
            bbox[2] = lat
        if lon < bbox[1]:
            bbox[1] = lon
        if lon > bbox[3]:
            bbox[3] = lon
        return bbox

    def NodeNew(self, data, action):
        if not data:
            print "NodeNew - no data found..."
            return

        bbox = self.NodeBBox(data["id"], data, action=action)

        if action != self._prev_action:
            if self._prev_action != "":
                self.endElement(self._prev_action)
            self.startElement(action, {})
            self._prev_action = action

        if data[u"tag"]:
            self.startElement("node", _formatData(data))
            for (k, v) in data[u"tag"].items():
                self.Element("tag", {"k":k, "v":v})
            self.endElement("node")
        else:
            self.Element("node", _formatData(data))

    def NodeBBox(self, id, data = None, action = None):
        if id in self.nodes_modified:
            return self.nodes_modified[id]
        bbox = None
        if data:
            bbox = self.expand_bbox(None, data["lat"], data["lon"])
            if action == "create":
                self.nodes_modified[id] = bbox
                return bbox

        data = self.reader.NodeGet(id)
        self.num_read_nodes += 1
        if not data:
            if not bbox:
                print "node %d is empty" % id
            self.nodes_modified[id] = bbox
            return bbox

        bbox = self.expand_bbox(bbox, data["lat"], data["lon"])
        self.nodes_modified[id] = bbox
        if bbox[0] == -180 and bbox[1] == -180:
            print "error on node %d" % id
        return bbox

    def WayNew(self, data, action):
        if not data:
            print "WayNew - no data found..."
            return

        bbox = self.WayBBox(data["id"], data, action)

        if action != self._prev_action:
            if self._prev_action != "":
                self.endElement(self._prev_action)
            self.startElement(action, {})
            self._prev_action = action


        self.startElement("way", _formatData(data))
        if bbox == None:
            print "way %d is empty" % data["id"]
        else:
            self.Element("bbox", {"minlat":str(bbox[0]),"minlon":str(bbox[1]),
                                  "maxlat":str(bbox[2]),"maxlon":str(bbox[3])})
        for (k, v) in data[u"tag"].items():
            self.Element("tag", {"k":k, "v":v})
        for n in data[u"nd"]:
            self.Element("nd", {"ref":str(n)})
        self.endElement("way")

    def WayBBox(self, id, data = None, action = None):
        if id in self.ways_modified:
            return self.ways_modified[id]
        bbox = None
        if data:
            for n in data[u"nd"]:
                bbox = self.concat_bbox(bbox, self.NodeBBox(n))
            if action == "create":
                self.ways_modified[id] = bbox
                return bbox

        data = self.reader.WayGet(id)
        self.num_read_ways += 1
        if not data:
            self.ways_modified[id] = bbox
            return bbox

        for n in data[u"nd"]:
            bbox = self.concat_bbox(bbox, self.NodeBBox(n))
        self.ways_modified[id] = bbox
        return bbox

    def RelationNew(self, data, action):
        if not data:
            print "RelationNew - no data found..."
            return

        bbox = self.RelationBBox(data["id"], data, action)

        if action != self._prev_action:
            if self._prev_action != "":
                self.endElement(self._prev_action)
            self.startElement(action, {})
            self._prev_action = action

        self.startElement("relation", _formatData(data))
        if bbox == None:
            print "relation %d is empty" % data["id"]
        else:
            self.Element("bbox", {"minlat":str(bbox[0]),"minlon":str(bbox[1]),
                                  "maxlat":str(bbox[2]),"maxlon":str(bbox[3])})
        for (k, v) in data[u"tag"].items():
            self.Element("tag", {"k":k, "v":v})
        for m in data[u"member"]:
            m[u"ref"] = str(m[u"ref"])
            self.Element("member", m)
        self.endElement("relation")

    def RelationBBox(self, id, data = None, action = None, rec_rel = []):
        if id in rec_rel:
            print "recursion on id=%d - rec_rel=%s" % (id, str(rec_rel))
            return None
        if id in self.rels_modified:
            return self.rels_modified[id]
        bbox = None
        if data:
            for m in data[u"member"]:
                ref = m[u"ref"]
                if m[u"type"] == u"node":
                    bbox = self.concat_bbox(bbox, self.NodeBBox(ref))
                elif m[u"type"] == u"way":
                    bbox = self.concat_bbox(bbox, self.WayBBox(ref))
                elif m[u"type"] == u"relation":
                    bbox = self.concat_bbox(bbox, self.RelationBBox(ref, rec_rel=rec_rel + [id]))
            if action == "create":
                self.rels_modified[id] = bbox
                return bbox

        data = self.reader.RelationGet(id)
        self.num_read_relations += 1
        if not data:
            self.rels_modified[id] = bbox
            return bbox

        for m in data[u"member"]:
            ref = m[u"ref"]
            if m[u"type"] == u"node":
                bbox = self.concat_bbox(bbox, self.NodeBBox(ref))
            elif m[u"type"] == u"way":
                bbox = self.concat_bbox(bbox, self.WayBBox(ref))
            elif m[u"type"] == u"relation":
                bbox = self.concat_bbox(bbox, self.RelationBBox(ref, rec_rel=rec_rel + [id]))
        self.rels_modified[id] = bbox
        if len(data[u"member"]) == 0:
            print "relation %d is empty [bbox=%s]" % (id, bbox)
        elif bbox == None or (bbox[0] == -180 and bbox[1] == -180):
            print "potential error on relation %d" % id
            print bbox
            import pprint
            pprint.pprint(data)
            bbox = self.expand_bbox(bbox, -89, -189)
            bbox = self.expand_bbox(bbox,  89,  189)
            return bbox
        return bbox
