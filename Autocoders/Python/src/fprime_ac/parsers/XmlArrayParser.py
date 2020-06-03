#!/usr/bin/env python3
#===============================================================================
# NAME: XmlArrayParser.py
#
# DESCRIPTION: This class parses the XML Array types files. 
#
# USAGE: 
#
# AUTHOR: jishii
# EMAIL:  jordan.ishii@jpl.nasa.gov
# DATE CREATED  : May 28, 2020
#
# Copyright 2020, California Institute of Technology.
# ALL RIGHTS RESERVED. U.S. Government Sponsorship acknowledged.
#===============================================================================
#
# Python standard modules
#
import logging
import os
import sys
import time
import hashlib
from fprime_ac.utils import ConfigManager
from optparse import OptionParser
from lxml import etree
from lxml import isoschematron
from fprime_ac.parsers import XmlParser
from fprime_ac.utils.exceptions import FprimeXmlException, FprimeRngXmlValidationException
#
# Python extention modules and custom interfaces
#

#
# Universal globals used within module go here.
# (DO NOT USE MANY!)
#
# Global logger init. below.
PRINT = logging.getLogger('output')
DEBUG = logging.getLogger('debug')
ROOTDIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
#
class XmlArrayParser(object):
    """
    An XML parser class that uses lxml.etree to consume an XML
    array type documents.  The class is instanced with an XML file name.
    """

    def __init__(self, xml_file=None):
        """
        Given a well formed XML file (xml_file), read it and turn it into
        a big string.
        """
        self.__name = ""
        self.__namespace = None

      # List of C++ include files for serializable *.hpp file
        self.__include_header_files = []
        # List of XML serializable description dependencies
        self.__includes = []
        # List of XML enum type files
        self.__include_enum_files = []
        # List of XML array type files
        self.__include_array_files = []

        self.__format = ""
        self.__default = []
        self.__xml_filename = xml_file
        self.__type = "U32"
        self.__size = "4"
        
        self.Config = ConfigManager.ConfigManager.getInstance()

        if os.path.isfile(xml_file) == False:
            stri = "ERROR: Could not find specified XML file %s." % xml_file
            raise IOError(stri)
        fd = open(xml_file,'r')
        xml_file = os.path.basename(xml_file)
        self.__xml_filename = xml_file

        xml_parser = etree.XMLParser(remove_comments=True)
        element_tree = etree.parse(fd,parser=xml_parser)
        
        #Validate against current schema. if more are imported later in the process, they will be reevaluated
        relax_file_handler = open(ROOTDIR + self.Config.get('schema', 'array') , 'r')
        relax_parsed = etree.parse(relax_file_handler)
        relax_file_handler.close()
        relax_compiled = etree.RelaxNG(relax_parsed)

        # 2/3 conversion
        if not relax_compiled.validate(element_tree):
            raise FprimeRngXmlValidationException(relax_compiled.error_log)
        
        array = element_tree.getroot()
        if array.tag != "array":
            PRINT.info("%s is not an array definition file" % xml_file)            
            sys.exit(-1)
            
        print("Parsing Array %s" %array.attrib['name'])
        self.__name = array.attrib['name']
            
        if 'namespace' in array.attrib:
            self.__namespace = array.attrib['namespace']
        else:
            self.__namespace = None

        if 'format' in array.attrib:
            self.__format = array.attrib['format']
        else:
            self.__format = None

        if 'typeid' in array.attrib:
            self.__type_id = array.attrib['typeid']
        else:
            self.__type_id = None

        self.__type = array.attrib["type"]
        self.__size = int(array.attrib["size"])
        
        for array_tag in array:
            if array_tag.tag == 'default':
                for value_tag in array_tag:
                    self.__default.append(value_tag.text)
            elif array_tag.tag == 'include_header':
                self.__include_header_files.append(array_tag.text)
            elif array_tag.tag == 'import_serializable_type':
                self.__includes.append(array_tag.text)
            elif array_tag.tag == 'import_enum_type':
                self.__include_enum_files.append(array_tag.text)
            elif array_tag.tag == 'import_array_type':
                self.__include_array_files.append(array_tag.text)

        #
        # Generate a type id here using SHA256 algorithm and XML stringified file.
        #

        if not 'typeid' in array.attrib:
            s = etree.tostring(element_tree.getroot())
            h = hashlib.sha256(s)
            n = h.hexdigest()
            self.__type_id = "0x" + n.upper()[-8:]

    def get_name(self):
        return self.__name
    
    def get_namespace(self):
        return self.__namespace

    def get_type(self):
        return self.__type
    
    def get_size(self):
        return self.__size

    def get_format(self):
        return self.__format

    def get_default(self):
        return self.__default

    def get_type_id(self):
        return self.__type_id

    def get_include_header_files(self):
        return self.__include_header_files
    
    def get_includes(self):
        return self.__includes
        
    def get_include_enum_files(self):
        return self.__include_enum_files

    def get_include_array_files(self):
        return self.__include_array_files


if __name__ == '__main__':
    xmlfile = sys.argv[1]
    xml = XmlParser.XmlParser(xmlfile)
    print("Type of XML is: %s" % xml())
    print("Array XML parse test (%s)" % xmlfile)
    xml_parser = XmlArrayParser(xmlfile)
    print("Array name: %s, namespace: %s" % (xml_parser.get_name(),xml_parser.get_namespace()))
    print("Size: %s, member type: %s" % (self.get_size(), self.get_type()))

