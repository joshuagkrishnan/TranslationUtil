import copy
import re

# 3rd Party Library Imports
from mergedeep import merge as merge_nested_dict
from deepdiff import DeepDiff

from util.exceptions import NoDiffItems
from util.file_obj import FileObject

from constants.settings import YML_INDENT_LEVEL

class DiffChecker(object):
    
    def __init__(self, f1, f2, prefix_path_list, output_file = None, sanitize = False):
        self.prefix_path_list = prefix_path_list
        self.sanitize = sanitize
        self.f1 = FileObject(f1, preserve_indentation = True)
        self.f2 = FileObject(f2, preserve_indentation = True)
        self.preserve_indentation = True
        self.output_file = FileObject(output_file if output_file else f'diff_output_{self.f1.file_name_without_extension}.{self.f1.file_type}')

    def parse_diff_lines(self, original_dict, diff_data):
        
        def parse_to_annotation(s):
            s = re.sub(r"(?:^root)?\['([^]]+)'\](?:\[[0-9]+\])?", r'\1.', s)
            return s.rstrip('.')
        
        def create_path(path, result, root_path = True):
            _result = result
            for p in path.split('.'):
                if p not in result:
                    result[p] = {}
                result = result[p]
            return _result if root_path else result
        
        def update_path(path, tree):
            data = self.nested_dict_extract(path, original_dict, 0 if self.preserve_indentation else False)
            path = path.split('.')
            for i, x in enumerate(path[:-1]):
                if len(path[:i]) > 0:
                    k = (x, self.calc_indent('.'.join(path[:i])))
                else:
                    k = (x, 0)
                print('k', k, i, path[:i])
                if k not in tree:
                    tree[k] = {}
                tree = tree[k]
            tree[path[-1]] = data
        update_list = [ parse_to_annotation(path) for path in diff_data ]

        if not self.prefix_path:
            root = {}
        else:
            root = create_path(self.prefix_path, {})

        for path in update_list:
            update_path(path, root)
        return root
    
    def calc_indent(self, path):
        return len(path.split('.')) * 2

    def nested_dict_extract(self, prefix_path, content, indent = None):
        for i, p in enumerate(prefix_path.split('.')):
            try:
                if indent is None:
                    content = content[p]
                else:
                    content = content[(p, indent)]
                    indent += YML_INDENT_LEVEL
            except:
                if p in content: return content[p]
                print(p, 'error', indent)
        return content

    def output_data(self, root):
        serializer = self.output_file.serializer
        if hasattr(serializer, 'preserve_indentation'):
            serializer.preserve_indentation = self.preserve_indentation
        print('self.pri_lang', self.pri_lang)
        data = serializer.content_dump(None, self.sanitize, root)
        self.output_file.write_file(data)
        print(f"Output file generated and store :: {self.output_file.file_path}")
        return data

    def extract_file_contents(self, pri_lang = '', sec_lang = ''):
        self.pri_lang = pri_lang or self.f1.file_name_without_extension
        self.sec_lang = sec_lang or self.f2.file_name_without_extension
        content_1 = self.f1.open_file(preserve_indentation = self.preserve_indentation)
        content_2 = self.f2.open_file(preserve_indentation = self.preserve_indentation)
        return (
            content_1.get(self.pri_lang, content_1),
            content_2.get(self.pri_lang, content_2)
        )
    
    def get_line_diff(self, **kwargs):
        content_1, content_2 = self.extract_file_contents(**kwargs)
        result = {}
        self.prefix_path = None
        if self.prefix_path_list:
            for prefix_path in self.prefix_path_list:
                content_1_copy = self.nested_dict_extract(prefix_path, copy.deepcopy(content_1), 0 if self.preserve_indentation else False)
                content_2_copy = self.nested_dict_extract(prefix_path, copy.deepcopy(content_2), 0 if self.preserve_indentation else False)
                diff = DeepDiff(content_1_copy, content_2_copy, ignore_order=True).get('dictionary_item_removed') 
                if not diff:
                    raise NoDiffItems(f'No Diff Items for \'{self.prefix_path}\' between files')
                else:
                    diff_data = self.parse_diff_lines(content_1_copy, diff)
                    result = merge_nested_dict(result, diff_data)
        else:
            diff = DeepDiff(content_1, content_2, ignore_order=True).get('dictionary_item_removed')
            if not diff:
                NoDiffItems(self.f1.file_name_without_extension, self.f2.file_name_without_extension)
            else:
                print('diff==', diff)
                result = self.parse_diff_lines(content_1, diff)
        return self.output_data(result)
