import copy

# 3rd Party Library Imports
from mergedeep import merge as merge_nested_dict
from deepdiff import DeepDiff, extract

from util.exceptions import NoDiffItems
from util.file_obj import FileObject
from serializers import CustomSerializer


class DiffChecker(object):
    
    def __init__(self, f1, f2, prefix_path_list, output_file = None, sanitize = False):
        self.prefix_path_list = prefix_path_list
        self.sanitize = sanitize
        self.f1 = FileObject(f1)
        self.f2 = FileObject(f2)
        self.output_file = FileObject(output_file if output_file else f'diff_output_{self.f1.file_name_without_extension}.{self.f1.file_type}')

    def parse_diff_lines(self, original_dict, diff_data):
        
        def parse_to_annotation(s):
            s = '.'.join(s.replace('root[', '').replace('\'', '').replace('[', '').split(']'))
            return s[:-1] if s[-1] == '.' else s
        
        def create_path(path, result, root_path = True):
            _result = result
            for p in path.split('.'):
                if p not in result:
                    result[p] = {}
                result = result[p]
            return _result if root_path else result

        update_list = [ (parse_to_annotation(path), path) for path in  diff_data ]
        if not self.prefix_path:
            root = {}
        else:
            root = create_path(self.prefix_path, {})
        for path_obj in update_list:
            p, origin_path = path_obj
            p = p.split('.')
            data = self.nested_dict_extract(root)
            serializer = CustomSerializer(self.f1.file_type)
            if hasattr(serializer, 'preserve_indentation'):
                serializer.preserve_indentation = True
            try:
                serializer.data = extract(original_dict, origin_path)
            except:
                print(root, p, origin_path)
                raise
            path_data = serializer.deserialize()
            if len(p) > 1:
                new_path = create_path('.'.join(p[:-1]), data, root_path = False)
                new_path[p[-1]] = path_data
            elif len(p) == 1:
                data[p[0]] = path_data
        return root
    
    def nested_dict_extract(self, content):
        if not self.prefix_path:
            return content
        for p in self.prefix_path.split('.'):
            content = content[p]
        return content

    def output_data(self, root):
        serializer = CustomSerializer(self.output_file.file_type)
        if hasattr(serializer, 'preserve_indentation'):
            serializer.preserve_indentation = True
        data = serializer.content_dump(self.pri_lang, self.sanitize, root)
        self.output_file.write_file(data)
        print(f"Output file generated and store :: {self.output_file.file_path}")
        return data

    def extract_file_contents(self, pri_lang = '', sec_lang = ''):
        self.pri_lang = pri_lang or self.f1.file_name_without_extension
        self.sec_lang = sec_lang or self.f2.file_name_without_extension
        content_1 = self.f1.open_file(preserve_indentation = True)
        content_2 = self.f2.open_file(preserve_indentation = True)
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
                self.prefix_path = prefix_path
                content_1_copy = self.nested_dict_extract(copy.deepcopy(content_1))
                content_2_copy = self.nested_dict_extract(copy.deepcopy(content_2))
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
                diff_data = self.parse_diff_lines(content_1, diff)
                result = merge_nested_dict(result, diff_data)
        return self.output_data(result)
