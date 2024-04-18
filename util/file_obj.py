import yaml
import json
from serializers import CustomSerializer

class FileObject(object):

    def __init__(self, file_path, **kwargs) -> None:
        self.file_path = file_path
        self.file_type = file_path.split('.')[-1]
        self.new_line = False
        self.serializer = CustomSerializer(self.file_type, **kwargs)

    def __eq__(self, obj) -> bool:
        return obj.file_type

    @property
    def file_name_without_extension(self):
        return self.file_path.split('/')[-1].replace('.' + self.file_type, '')

    def open_file(self, **kwargs):
        with open(self.file_path, 'r') as stream:
            try:
                raw_data = stream.read()
                self.new_line = raw_data[-1] == '\n'
                if 'preserve_indentation' in kwargs:
                    self.serializer.preserve_indentation = kwargs.get('preserve_indentation')
                self.serializer.data = raw_data
                self.serializer.serialize()
                self.serializer.deserialize()
                assert self.serializer.data == raw_data
                self.serializer.serialize()
                content = self.serializer.content
                return content
            except yaml.YAMLError as exc:
                raise ValueError(f'Invalid XML file :: {self.file_path} @Line:{exc.args[-1].line + 1} @Column:{exc.args[-1].column + 1}')
            except json.JSONDecodeError as exc:
                raise ValueError(f'Invalid JSON file :: {self.file_path}')

    def write_file(self, data):
        with open(self.file_path, 'w') as f:
            f.write(data if self.new_line else data + '\n')