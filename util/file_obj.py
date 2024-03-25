import yaml
import json
from util.file_cache import file_cache
from serializers import CustomSerializer

class FileObject(object):

    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.file_type = file_path.split('.')[-1]
        self.file_cache = file_cache
        self.new_line = False

    def __eq__(self, obj) -> bool:
        return obj.file_type

    @property
    def file_name_without_extension(self):
        return self.file_path.split('/')[-1].replace('.' + self.file_type, '')

    def open_file(self, **kwargs):
        # if self.file_cache.cache_data.get(self.file_path):
        #     return self.file_cache.cache_data.get(self.file_path)
        with open(self.file_path, 'r') as stream:
            try:
                raw_data = stream.read()
                self.new_line = raw_data[-1] == '\n'
                serializer = CustomSerializer(self.file_type)
                if 'preserve_indentation' in kwargs:
                    serializer.preserve_indentation = kwargs.get('preserve_indentation')
                serializer.data = raw_data
                serializer.serialize()
                serializer.deserialize()
                assert serializer.data == raw_data
                serializer.serialize()
                content = serializer.content
                self.file_cache.cache_data[self.file_path] = content
                self.file_cache.update_cache()
                return content
            except yaml.YAMLError as exc:
                raise ValueError(f'Invalid XML file :: {self.file_path} @Line:{exc.args[-1].line + 1} @Column:{exc.args[-1].column + 1}')
            except json.JSONDecodeError as exc:
                raise ValueError(f'Invalid JSON file :: {self.file_path}')

    def write_file(self, data):
        with open(self.file_path, 'w') as f:
            f.write(data if self.new_line else data + '\n')