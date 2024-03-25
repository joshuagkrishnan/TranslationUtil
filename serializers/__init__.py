from util.exceptions import UnSupportedFileType
from .abstract import Serializer
from .yml_serializer import YMLSerializer
from .json_serializer import JSONSerializer

class CustomSerializer(object):
    
    def __new__(cls, file_type, data = None, **kwargs):
        if file_type == 'yml':
            return YMLSerializer(data, **kwargs)
        elif file_type == 'json':
            return JSONSerializer(data, **kwargs)
        raise UnSupportedFileType(file_type)
