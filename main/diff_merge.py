from collections import OrderedDict
from util.file_obj import FileObject
from util.exceptions import PathDoesNotExist

from serializers import CustomSerializer

from constants.settings import FILE_TYPE

class DiffMerge(object):

    def __init__(self, source = None, dest = None, overwrite = False, output_file = None, path_list = [], dry_run = False, lang_map = {}) -> None:
        self.source = FileObject(source)
        self.dest = FileObject(dest)
        self.output_file = None
        self.dry_run = dry_run
        self.path_list = path_list
        self.lang_map = lang_map
        if not overwrite:
            self.output_file = FileObject(output_file or f'{self.source.file_name_without_extension}_{self.dest.file_name_without_extension}.{self.source.file_type}')

    @staticmethod
    def is_hashable(obj):
        t = type(obj)
        return t is dict or t is OrderedDict

    def _merge(self, a, b, path=None):
        if path is None: path = []
        for key in b:
            key_a = key
            if type(key) is tuple:
                if key in a:
                    key_a = key
                else:
                    for k in a.keys():
                        if type(k) is tuple and k[0] == key[0]:
                            key_a = k
                            break
            if key_a in a:
                try:
                    if self.is_hashable(a[key_a]) and self.is_hashable(b[key]):
                        self._merge(a[key_a], b[key], path + [str(key)])
                    elif a[key_a] == b[key]:
                        pass # same leaf value
                    else:
                        a[key_a] = b[key]
                        # raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
                except:
                    print(a, key_a)
                    raise
            else:
                a[key_a] = b[key]
        return a

    def get_path_obj_indent(self, path, data):
        ind = 0
        try:
            for p in path.split('.'):
                data = data[(p, ind)]
                ind += 2
            return data
        except KeyError as e:
            raise PathDoesNotExist(path, e)

    def get_path_obj(self, path, data):
        try:
            for p in path.split('.'):
                data = data[p]
            return data
        except KeyError as e:
            raise PathDoesNotExist(path, e)
        
    def update_lang_map(self, f, _type = 'source'):
        lang_name = list(f.keys())[0][0]
        if self.lang_map and _type in self.lang_map and lang_name in self.lang_map[_type]:
            f[0][0] = self.lang_map[_type][lang_name]

    def merge(self):
        f1 = self.source.open_file()
        f2 = self.dest.open_file()
        for path in self.path_list or []:
            if self.source.file_type == FILE_TYPE.YML:
                k = list(f1.keys())[0][0]
                _f1 = self.get_path_obj_indent(k + '.' + path, f1)
            else:
                _f1 = self.get_path_obj(path, f1)
            if self.dest.file_type == FILE_TYPE.YML:
                k = list(f2.keys())[0][0]
                _f2 = self.get_path_obj_indent(k + '.' + path, f2)
            else:
                _f2 = self.get_path_obj(path, f2)
            if type(_f1) is str:
                self.get_path_obj('.'.join(path.split('.')[:-1]))
            self._merge(_f2, _f1)
        if not self.path_list:
            if self.source.file_type == FILE_TYPE.YML:
                f1_lang_name = list(f1.keys())[0]
                f2_lang_name = list(f2.keys())[0]
                if f1_lang_name[0] != f2_lang_name[0]:
                    f1[f2_lang_name] = f1[f1_lang_name]
                    del f1[f1_lang_name]
            self._merge(f2, f1)
        serializer = CustomSerializer(self.source.file_type)
        data = serializer.content_dump(None, False, f2, ensure_ascii=False)
        if not self.dry_run:
            if self.output_file:
                self.output_file.write_file(data)
            else:
                self.dest.write_file(data)
