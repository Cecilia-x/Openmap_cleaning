#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This is the main modul to clean data and output to csv files.
'''

import solutions
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
from zipfile import ZipFile

import cerberus

import schema


OSM_PATH = 'sample.osm'

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.findall("tag") != None:
        for child_e in element.findall("tag"):
            atts = child_e.attrib
            k = atts['k']
            v = atts['v']
            
            tag = {}
            tag['id'] = element.attrib['id']

            if re.match(problem_chars,k) != None:
                tag['value'] = ''
                
            tag['value'] = process_v(k,v)
            if tag['value'] != '':
                k_list = k.split(":")
                if len(k_list) == 1:
                    tag['key'], tag['type'] = k, default_tag_type
                else:
                    tag['type'], tag['key'] = process_k(k_list,default_tag_type)
                tags.append(tag)
                
    
    if element.tag == 'node':
        for nf in node_attr_fields:
            node_attribs[nf] = element.attrib[nf]
        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':
        for wf in way_attr_fields:
            way_attribs[wf] = element.attrib[wf]
        if element.findall("nd") != None:
            counter = 0
            for nd in element.findall("nd"):
                waynode = {}
                waynode['id'] = element.attrib['id']
                waynode['node_id'] = nd.attrib['ref']
                waynode['position'] = counter
                way_nodes.append(waynode)
                counter += 1
                
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


def process_v(k,v):
    mapping = solutions.mapping_v
    if k in mapping.keys():
        return mapping[k](v)
    else:
        return v

def process_k(k_list, default_type):
    k1, k2 = k_list[0], k_list[1]
    mapping = solutions.mapping_name
    addr_types = ['city', 'street', 'postcode', 'housenumber', 'housename']
    if k1 == 'name' and k2 in mapping.keys():
        return 'name',mapping[k2]
    elif k1 == 'addr' and k2 not in addr_types:
        return default_type, ':'.join(k_list)
    elif k1 != '' and k2 == '':
        return default_type, k1
    else:
        return k1,k2


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    process_map(OSM_PATH, validate=False)
