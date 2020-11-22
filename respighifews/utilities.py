# -*- coding: utf-8 -*-

__title__ = 'fews_utilities'
__description__ = 'to read a Deltares-FEWS config-files into Python'
__version__ = '0.1'
__author__ = 'Daniel Tollenaar'
__author_email__ = 'daniel@d2hydro.nl'
__license__ =  'MIT License'


from collections import defaultdict
from lxml import etree as ET

def xml_to_etree(xml_file):
    ''' parses an xml-file to an etree. ETree can be used in function etree_to_dict '''
    
    t = ET.parse(f'{xml_file}').getroot()
    
    return t

def etree_to_dict(t,section_start=None,section_end=None):
    ''' converts an etree to a dictionary '''
    
    if not isinstance(t,ET._Comment):
        
        d = {t.tag.rpartition('}')[-1]: {} if t.attrib else None}
        children = list(t)
        
        #get a section only
        if (not section_start == None) | (not section_end == None):
            if section_start:
                start = [idx for idx, child in enumerate(children) 
                               if isinstance(child,ET._Comment) 
                               if ET.tostring(child).decode("utf-8").strip() 
                               == section_start][0]
            else: start = 0
            if section_end:
                end = [idx for idx, child in enumerate(children) 
                           if isinstance(child,ET._Comment) 
                           if ET.tostring(child).decode("utf-8").strip() 
                           == section_end][0]
                if start < end:
                    children = children[start:end]
            else: children = children[start:]

        
        children = [child for child in children if not isinstance(child,ET._Comment)]
        
        if children:
            dd = defaultdict(list)
            #for dc in map(etree_to_dict, children):
            for dc in [etree_to_dict(child) for child in children]:
                for k, v in dc.items():
                    dd[k].append(v)
            
            d = {t.tag.rpartition('}')[-1]: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
        if t.attrib:
            d[t.tag.rpartition('}')[-1]].update((k, v) for k, v in t.attrib.items())
        if t.text:
            text = t.text.strip()
            if children or t.attrib:
                if text:
                  d[t.tag.rpartition('}')[-1]]['#text'] = text
            else:
                d[t.tag.rpartition('}')[-1]] = text
            
        return d

def xml_to_dict(xml_file,section_start=None,section_end=None):
    ''' converts an xml-file to a dictionary '''
    
    t = xml_to_etree(xml_file)
    d = etree_to_dict(t,section_start=section_start,section_end=section_end)
    
    return d