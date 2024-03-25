# TODO: INPROGRESS:

import json
from serializers import JSONSerializer

class GenerateFileList(object):
    
    LANG_MAP = {}
    
    def __init__(self, source, dest, overwrite = 1, file_format = '.json'):
        self.source_dir = source
        self.dest_dir = dest
        self.overwrite = overwrite
        self.file_format = file_format
        self.data = []
        self.load_meta()

        return self.get_file_list(True)

    @classmethod
    def load_meta(cls):
        with open('meta/lang_map.json', 'r') as f:
            cls.LANG_MAP = json.loads(f.read())
        
    def get_file_path(self, _dir, lang_file):
        return f'{_dir}/{lang_file}{self.file_format}'
    
    def get_file_list(self, reload = True):
        
        for cur_dir, _, file_name in os.walk(self.source_dir):
            lang_file = cur_dir.split('/')[-1]
            
            if self.source_dir.split('/')[-1] == lang_file:
                continue
                
            source = f'{self.source_dir}/{lang_file}/{file_name[0]}'
            dest = f'{self.dest_dir}/{self.LANG_MAP.get(lang_file, lang_file)}{self.file_format}'

            self.data.append({
                'source': source,
                'dest': dest,
                'overwrite': self.overwrite
            })
            
        return self.data
    
    def remove_keys(self, _typ, keys):
        for d in self.data:
            f = d[_typ]
            lang = f.split('/')[-1].split('.')[0]
            with open(f, 'r') as _f:
                data = JSONSerializer(_f.read()).content
            with open(f, 'w') as _f:
                _f.write(JSONSerializer().content_dump(lang, False, data, ensure_ascii=False))



