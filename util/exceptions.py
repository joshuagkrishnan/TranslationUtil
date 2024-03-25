
class UnSupportedFileType(Exception):
    def __init__(self, file_type):
        self.file_type = file_type

    def __str__(self):
        return f'This file_type({self.file_type}) is not currently supported. Please add the serializer to support this file'


class PathDoesNotExist(Exception):

    def __init__(self, path, key_name):
        self.path = path
        self.key_name = key_name

    def __str__(self):
        return f'This path ({self.path} does not exist in source/dest file for key {self.file_namekey_name})'


class NoDiffItems(Exception):

    def __init__(self, source, dest):
        self.source = source
        self.dest = dest

    def __str__(self):
        return f'No diff lines between {self.source} and {self.dest}'

class YMLParserError(Exception):

    def __init__(self, line_no, line_str):
        self.line_no = line_no
        self.line_str = line_str

    def __str__(self) -> str:
        return f'YML Parsing error @Line {self.line_no} = {self.line_str}'