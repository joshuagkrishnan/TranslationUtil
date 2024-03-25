import re
import json
from collections import OrderedDict

from . import Serializer

class JSONSerializer(Serializer):
    def __init__(self, data = None) -> None:
        self.data = data

    def serialize(self):
        return self.data

    def deserialize(self):
        return self.data

    @staticmethod
    def remove_pirate_holder(m):
        return re.sub('[\'}{%]', '', m.group(0))

    @property
    def content(self):
        return json.loads(self.data, object_pairs_hook=OrderedDict)

    def content_dump(self, pri_lang, sanitize, root, **kwargs):
        self.data = json.dumps(root, indent='\t', separators=(',', ': '), sort_keys=False, **kwargs)
        if sanitize:
            print('Performing string sanitazion')
            # '%{{?[a-z_A-Z0-9]+}?}'
            p_l = ['\'{[a-zA-Z_0-9]+}\'']
            regex = re.compile("(%s)" % "|".join(p_l))
            self.data = regex.sub(self.remove_pirate_holder, self.data)
        return self.data

