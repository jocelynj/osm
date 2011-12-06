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

###########################################################################

class OsmSaxReader(handler.ContentHandler):

    def log(self, txt):
        self._logger.log(txt)
    
    def __init__(self, filename, logger = dummylog()):
        self._filename = filename
        self._logger   = logger
        
    def _GetFile(self):
        if type(self._filename) == file:
            return self._filename
        elif self._filename.endswith(".bz2"):
            return bz2.BZ2File(self._filename)
        elif self._filename.endswith(".gz"):
            return gzip.open(self._filename)
        else:
            return open(self._filename)
        
    def CopyTo(self, output):
        self._debug_in_way      = False
        self._debug_in_relation = False
        self.log("starting nodes")
        self._output = output
        parser = make_parser()
        parser.setContentHandler(self)
        parser.parse(self._GetFile())

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
        if name == u"node":
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
        
    def _GetFile(self):
        if type(self._filename) == file:
            return self._filename
        elif self._filename.endswith(".bz2"):
            return bz2.BZ2File(self._filename)
        elif self._filename.endswith(".gz"):
            return gzip.open(self._filename)
        else:
            return open(self._filename)
        
    def CopyTo(self, output):
        
        _re_eid = re.compile( " id=['\"](.+?)['\"]")
        _re_lat = re.compile(" lat=['\"](.+?)['\"]")
        _re_lon = re.compile(" lon=['\"](.+?)['\"]")
        _re_usr = re.compile(" user=['\"](.+?)['\"]")
        _re_tag = re.compile(" k=['\"](.+?)['\"] v=['\"](.+?)['\"]")
        
        f = self._GetFile()
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
 
    def _GetFile(self):
        if type(self._filename) == file:
            return self._filename
        elif self._filename.endswith(".bz2"):
            return bz2.BZ2File(self._filename)
        elif self._filename.endswith(".gz"):
            return gzip.open(self._filename)
        else:
            return open(self._filename)
        
    def CopyTo(self, output):
        self._output = output
        parser = make_parser()
        parser.setContentHandler(self)
        parser.parse(self._GetFile())
        
    def startElement(self, name, attrs):
        attrs = attrs._attrs
        if name == u"create":
            self._action = name
        elif name == u"modify":
            self._action = name
        elif name == u"delete":
            self._action = name
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

    def endElement(self, name):
        if name == u"node":
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
    return data

class OsmSaxWriter(XMLGenerator):

    def __init__(self, out, enc):
        if type(out) == str:
            XMLGenerator.__init__(self, open(out, "w"), enc)
        else:
            XMLGenerator.__init__(self, out, enc)
    
    def startElement(self, name, attrs):
        self._write('<' + name)
        for (name, value) in attrs.items():
            self._write(' %s=%s' % (name, quoteattr(value)))
        self._write('>\n')
        
    def endElement(self, name):
        self._write('</%s>\n' % name)
    
    def Element(self, name, attrs):
        self._write('<' + name)
        for (name, value) in attrs.items():
            self._write(' %s=%s' % (name, quoteattr(value)))
        self._write(' />\n')


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

    def __init__(self, out, enc, osmosis_conn = None):
        if type(out) == str:
            XMLGenerator.__init__(self, open(out, "w"), enc)
        else:
            XMLGenerator.__init__(self, out, enc)

        self.osmosis_conn = osmosis_conn
    
    def startElement(self, name, attrs):
        self._write('<' + name)
        for (name, value) in attrs.items():
            self._write(' %s=%s' % (name, quoteattr(value)))
        self._write('>\n')
        
    def endElement(self, name):
        self._write('</%s>\n' % name)
    
    def Element(self, name, attrs):
        self._write('<' + name)
        for (name, value) in attrs.items():
            self._write(' %s=%s' % (name, quoteattr(value)))
        self._write(' />\n')

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
        print ".osc read took: ", t2 - self.t1

        if self.osmosis_conn:
            # add ways that were not modified, but included by ways or relations
            t1 = time.time()
            ways_to_add = set(self.ways_to_add) - set(self.ways_printed)
            for i in ways_to_add:
                way_info = self.osmosis_conn.WayGet(i)
                if way_info:
                    self.WayUpdate(way_info)
            t2 = time.time()
            print "new ways took:", t2 - t1, "for", len(ways_to_add)
    
            # add nodes that were not modified, but included by ways or relations
            t1 = time.time()
            nodes_to_add = set(self.nodes_to_add) - set(self.nodes_printed)
            for i in nodes_to_add:
                node_info = self.osmosis_conn.NodeGet(i)
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

    def __init__(self, out, enc, osmosis_conn = None):
        if type(out) == str:
            XMLGenerator.__init__(self, open(out, "w"), enc)
        else:
            XMLGenerator.__init__(self, out, enc)

        self.osmosis_conn = osmosis_conn
    
    def startElement(self, name, attrs):
        self._write('<' + name)
        for (name, value) in attrs.items():
            self._write(' %s=%s' % (name, quoteattr(value)))
        self._write('>\n')
        
    def endElement(self, name):
        self._write('</%s>\n' % name)
    
    def Element(self, name, attrs):
        self._write('<' + name)
        for (name, value) in attrs.items():
            self._write(' %s=%s' % (name, quoteattr(value)))
        self._write(' />\n')

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
        print ".osc read took: ", t2 - self.t1

        # add ways that were not modified, but included by ways or relations
        t1 = time.time()
        ways_to_add = set(self.ways_to_add) - set(self.ways_printed)
        for i in ways_to_add:
            way_info = self.osmosis_conn.WayGetNodes(i)
            if way_info:
                self.WayNew(way_info, "")
        t2 = time.time()
        print "new ways took:", t2 - t1, "for", len(ways_to_add)

        # add nodes that were not modified, but included by ways or relations
        t1 = time.time()
        nodes_to_add = set(self.nodes_to_add) - set(self.nodes_printed)
        for i in nodes_to_add:
            node_info = self.osmosis_conn.NodeGetPosition(i)
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

    def __init__(self, out, enc, osmosis_conn = None, poly = None, check_intersection = None):
        if type(out) == str:
            XMLGenerator.__init__(self, open(out, "w"), enc)
        else:
            XMLGenerator.__init__(self, out, enc)

        self.osmosis_conn = osmosis_conn
        self.poly = poly
        self.check_intersection = check_intersection
    
    def begin(self):
        self.startElement("osmChange", { "version": "0.6",
                                         "generator": "OsmSax" })
        self.nodes_added_in_poly = set()
        self.ways_added_in_poly = set()
        self.rels_added_in_poly = set()
        self.t1 = time.time()

    def end(self):
        t2 = time.time()
        print ".osc read took: ", t2 - self.t1

        self.endElement("osmChange")


    def NodeNew(self, data, action):
        if not data:
            return

        if self.check_intersection(self.poly, data["lat"], data["lon"]):
            action = "delete"
        else:
            self.nodes_added_in_poly.add(data["id"])

        self.startElement(action, {})
        if data[u"tag"]:
            self.startElement("node", _formatData(data))
            for (k, v) in data[u"tag"].items():
                self.Element("tag", {"k":k, "v":v})
            self.endElement("node")
        else:
            self.Element("node", _formatData(data))
        self.endElement(action)

    def WayNew(self, data, action):
        if not data:
            return

        way_nodes = set(data[u"nd"])
        if way_nodes.isdisjoint(self.nodes_added_in_poly):
            delete_way = True
            for n in way_nodes:
                if self.osmosis_conn.NodeExists(n):
                    delete_way = False
                    break
        else:
            delete_way = False

        if delete_way:
            action = "delete"
        else:
            self.ways_added_in_poly.add(data["id"])

        self.startElement(action, {})
        self.startElement("way", _formatData(data))
        for (k, v) in data[u"tag"].items():
            self.Element("tag", {"k":k, "v":v})
        for n in data[u"nd"]:
            self.Element("nd", {"ref":str(n)})
        self.endElement("way")
        self.endElement(action)

    def RelationNew(self, data, action):
        if not data:
            return

        rel_nodes = set()
        rel_ways = set()
        rel_rels = set()
        for m in data[u"member"]:
            if m[u"type"] == u"node":
                rel_nodes.add(m[u"ref"])
            elif m[u"type"] == u"way":
                rel_ways.add(m[u"ref"])
            elif m[u"type"] == u"relation":
                rel_rels.add(m[u"ref"])

        if (rel_nodes.isdisjoint(self.nodes_added_in_poly) and
            rel_ways.isdisjoint(self.ways_added_in_poly) and
            rel_rels.isdisjoint(self.rels_added_in_poly)):
            delete_rel = True
            for n in rel_nodes:
                if self.osmosis_conn.NodeExists(n):
                    delete_rel = False
                    break
            if delete_rel:
                for n in rel_ways:
                    if self.osmosis_conn.WayExists(n):
                        delete_rel = False
                        break
            if delete_rel:
                for n in rel_rels:
                    if self.osmosis_conn.RelationExists(n):
                        delete_rel = False
                        break
 
        else:
            delete_rel = False

        if delete_rel:
            action = "delete"
        else:
            self.rels_added_in_poly.add(int(data["id"]))

        self.startElement(action, {})
        self.startElement("relation", _formatData(data))
        for (k, v) in data[u"tag"].items():
            self.Element("tag", {"k":k, "v":v})
        for m in data[u"member"]:
            m[u"ref"] = str(m[u"ref"])
            self.Element("member", m)
        self.endElement("relation")
        self.endElement(action)
