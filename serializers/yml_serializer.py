
import re
import json

from parsers.yml_parser import YMLParser

from . import Serializer

class YMLSerializer(Serializer):
    
    def __init__(self, data = None, preserve_indentation = True):
        self.data = data
        self.escape_strs = '%{<}>'
        self.str_map = {
            '%' : 'XPTX',
            '{' : 'XLCX',
            '}' : 'XRGX',
            '<' : 'XSLX',
            '>' : 'XSGX'
        }
        self.preserve_indentation = preserve_indentation
        self.parser = YMLParser(preserve_indentation = self.preserve_indentation)

    def serialize(self, escape_strs = None):
        for r in escape_strs or self.escape_strs:
            self.data = self.data.replace(r, self.str_map[r])
        return self.data
    
    def deserialize(self):
        is_dict = False
        if any(isinstance(self.data, _type) for _type in [list, dict, tuple]):
            self.data = json.dumps(self.data)
            is_dict = True
        for r in self.escape_strs:
            self.data = self.data.replace(self.str_map[r], r)
        if is_dict:
            self.data = json.loads(self.data)
        return self.data

    @staticmethod
    def remove_pirate_holder(m):
        return re.sub('[}{%]', '', m.group(0))

    def clean_data(self):
        print('Performing string sanitazion')
        p_l = ['{[a-zA-Z_0-9]+}', '%{{?[a-z_A-Z0-9]+}?}']
        regex = re.compile("(%s)" % "|".join(p_l))
        self.data = regex.sub(self.remove_pirate_holder, self.data)
        return self.data

    @property
    def content(self):
        self.parser.load(yml_str=self.data)
        return self.parser.data

    def content_dump(self, pri_lang, sanitize, root, **kwargs):
        kwargs['allow_unicode'] = True
        if pri_lang is not None:
            root = {pri_lang: root}
        self.data = self.parser.dump(data = root)
        self.deserialize()
        if sanitize:
            self.clean_data()
        return self.data
