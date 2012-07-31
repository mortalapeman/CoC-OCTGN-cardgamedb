'''
TODO:
    1. Write doc tests for everything
    2. Refactor stuff out so that it's more test able.
'''

import os.path as osp
import os

from zipfile import ZipFile
from uuid import uuid1
from lxml import etree
from urllib import urlretrieve

def _make_content_types():
        content_types = etree.Element('Types',
            nsmap = { None :
                     'http://schemas.openxmlformats.org/package/2006/content-types'})
        etree.SubElement(content_types, 'Default', Extension='rels', ContentType='application/vnd.openxmlformats-package.relationships+xml')
        etree.SubElement(content_types, 'Default', Extension='jpg', ContentType='images/jpeg') 
        etree.SubElement(content_types, 'Default', Extension='jpeg', ContentType='images/jpeg')
        etree.SubElement(content_types, 'Default', Extension='jpe', ContentType='images/jpeg')
        etree.SubElement(content_types, 'Default', Extension='png', ContentType='images/png')
        etree.SubElement(content_types, 'Default', Extension='wdp', ContentType='image/vnd.ms-photo')
        etree.SubElement(content_types, 'Default', Extension='hdp', ContentType='image/vnd.ms-photo')
        etree.SubElement(content_types, 'Default', Extension='jxr', ContentType='image/vnd.ms-photo')
        etree.SubElement(content_types, 'Default', Extension='xml', ContentType='text/xml')
        etree.SubElement(content_types, 'Default', Extension='o8d', ContentType='octgn/deck')
        etree.SubElement(content_types, 'Default', Extension='py', ContentType='text/x-python')
        return content_types
        
def _make_dot_rels():
        dot_rels = etree.Element('Relationships', nsmap= { None : 'http://schemas.openxmlformats.org/package/2006/relationships' })
        etree.SubElement(dot_rels, 'Relationship', Target='/definition.xml', Id='def', Type='http://schemas.octgn.org/set/definition')
        return dot_rels

def _make_definitions_rels():
    def_rels = etree.Element('Relationships', nsmap={ None : 'http://schemas.openxmlformats.org/package/2006/relationships' })
    return def_rels


class CoCCard:
    Type = ''
    Descriptor = ''
    Cost = ''
    Faction = ''
    Icons = ''
    Skill = ''
    Subtypes = ''
    Card_Text = ''
    Keyword = ''
    Resource_Icon = ''
    Collector_Info = ''
    Struggle_Icons = ''
    def getelement(self):
        names = [x for x in dir(self) if not '__' in x]
        attrs = [x for x in names if x[0].istitle()]
        xml = etree.Element('card', id=str(self.card_id), name=self.name)
        for attr in attrs:
            etree.SubElement(xml, 'property',name=attr.replace('_', ' '), value=getattr(self, attr))
        return xml
    element = property(getelement, doc='Xml element value.')    
    
    def __init__(self, setid, imageurl, name, number):
        self.card_id = '%s%03d' % (setid[:-3], number)
        self.name = name
        self.imageurl = imageurl
        self.number = number

    def  __str__(self):
        names = [x for x in dir(self) if not '__' in x]
        attrs = [x for x in names if x[0].istitle()]
        dic = {}
        for k in attrs:
            dic[k] = getattr(self, k)
        return str(dic)


class CoCCardSet:
    defaultfiles = ('definition.xml', '[Content_Types].xml',
        '_rels/.rels', '_rels/definition.xml.rels')
    defaultfolders = ('markers', 'decks', 'cards', '_rels')
    setid = str(uuid1())[:-3] + '000'
    
    def __init__(self, name):
        # TODO have game version as a parameter.
        self.definition = etree.Element('set', nsmap={
            'noNamespaceSchemaLocation' : 'CardSet.xsd' },
            name=name, id=self.setid,
            gameId='43054c18-2362-43e0-a434-72f8d0e8477c',
            gameVersion='1.0.9')
        self.cards = etree.SubElement(self.definition, 'cards')
        self.content_types = _make_content_types()
        self.dot_rels = _make_dot_rels()
        self.definition_rels = _make_definitions_rels()
        self.cocCards = []
        self.name = name
         
    def addcard(self, cocCard):
        self.cocCards.append(cocCard)
        self.cards.append(cocCard.element);
        etree.SubElement(self.definition_rels, 'Relationship',
            Target=('/cards/%03d.jpg' % cocCard.number), Id='C' + cocCard.card_id.replace('-',''), Type='http://schemas.octgn.org/picture')
        
    def write(self, dest):
        with ZipFile(osp.join(dest, ('%s.o8s' % self.name)), 'w') as z:
            def write_file(z, name, tree, header):
                xml = '%s\r\n%s' % (header, etree.tostring(tree, pretty_print=True))
                z.writestr(name, xml)
        
            header = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            write_file(z, 'definition.xml', self.definition, header)
            write_file(z, '[Content_Types].xml', self.content_types, header)
            write_file(z, osp.join('_rels', '.rels'), self.dot_rels, header)
            write_file(z, osp.join('_rels', 'definition.xml.rels'), self.definition_rels, header)
            for c in self.cocCards:
                path = osp.join(dest, ('%03d.jpg' % c.number))
                urlretrieve(c.imageurl, path)
                z.write(path, osp.join('cards', ('%03d.jpg' % c.number)))
                os.remove(path)

class CoCCardFactory:
    # TODO Fix struggle icons issue, forgot to scrape that data.
    mapping = { 
        'type' : 'Type',
        'faction' : 'Faction',
        'cost' : 'Cost',
        'skill' : 'Skill',
        'icons' : 'Icons',
        'subtype' : 'Subtypes',
        'gametext' : 'Card_Text',
        'titleflavortext' : 'Descriptor',
        'illustrator' : 'Collector_Info'}
        #'struggleicons' : 'Struggle_Icons' }

    def create(self, cardsetid, carddic, number):
        name = '*%s' % carddic['name'] if carddic['isunique'] else carddic['name']
        imageurl = carddic['imageurl']
        card = CoCCard(cardsetid, imageurl, name, number)
        for k in self.mapping.keys():
            val = carddic[k].replace(u'\r\n', u' ')
            attr = self.mapping[k]
            setattr(card, attr, val)
        return card
