from collections import OrderedDict
import re
from util.exceptions import YMLParserError

class YMLParser(object):
    """
        YML parser that reads each line and converts it into a OrderedDict
    """
    def __init__(self, reg_key = r'^[a-z0-9-_A-Z\/\'\"]+:', doc_seperator = True, debug_mode = False, preserve_indentation = False, trim_whitespace = False):
        self.reg_key = reg_key
        self.debug_mode = debug_mode
        self.data = OrderedDict()
        self.doc_seperator = doc_seperator
        self._preserve_indentation = preserve_indentation
        self.trim_whitespace = trim_whitespace
    
    @staticmethod
    def is_hashable(obj):
        t = type(obj)
        return t is dict or t is OrderedDict
    
    @staticmethod
    def str_indent(s):
        return len(s) - len(s.lstrip())
    
    @staticmethod
    def is_list_type(s, ind):
        return ind < len(s) and s[ind].lstrip().startswith('-')

    @staticmethod
    def is_quoted_str(s):
        s = s.strip()
        return '"' == s[0] or "'" == s[0]

    @staticmethod
    def is_str_closed(s, quote_type):
        if not s:
            return False
        # return quote_type == s[-1]
        return quote_type == s.rstrip()[-1]

    def preserve_indentation(self, obj):
        return self._preserve_indentation and type(obj) is tuple

    def is_key_header(self, s):
        _match = re.findall(self.reg_key, s.strip())
        return len(_match) > 0 and s.strip() == _match[0]
    
    def is_empty_header(self, cur_indent, yml_str, ind):
        if ind > len(yml_str):
            return True
        if self.is_list_type(yml_str, ind):
            return False
        if cur_indent >= self.str_indent(yml_str[ind]):
            return True
        return False
    
    def key_val(self, s):
        if not re.match(r'^[^ ]+: ', s.strip()) and not re.match(r'^[^ ]+ : ', s.strip()) and not re.match(self.reg_key + ' ', s.strip()):
            return [s, None]

        l = s.split(': ', 1)
        return l[0].strip(), l[1]

    def parse_raw_yml(self, yml_str, meta, d = {'i': 0}, prev_indent = None, prev_temp_holder = None):
        unterminated_str = False
        quote_type = None

        while d['i'] < len(yml_str):
            try:
                l = yml_str[d['i']]

                if not l or not l.strip():
                    if prev_temp_holder and self.is_hashable(meta):
                        if self._preserve_indentation:
                            s = meta[prev_temp_holder][0] + '\n'
                            meta[prev_temp_holder] = (s, meta[prev_temp_holder][1])
                        else:
                            meta[prev_temp_holder] += '\n'
                    d['i'] += 1
                    continue

                cur_indent = self.str_indent(l)
                
                if self.debug_mode:
                    print('row: ', d['i'] + 1, 'prev: ', prev_indent, 'cur: ', cur_indent, 'l:', l, 'keyHeader:', self.is_key_header(l))
                
                if prev_indent and prev_indent > cur_indent:
                    # return if the indent level is the same as or greater than the current indentation level   
                    return

                if self.is_key_header(l):
                    # check if the l:str is a header key 
                    if type(meta) is list:
                        # since list values are not indented we're having the based cond here to return
                        return
                    k = l.split(':')[0].strip()
                    if self._preserve_indentation:
                        _k = (k, cur_indent)
                    else:
                        _k = k
                    d['i'] += 1
                    if self.is_list_type(yml_str, d['i']):
                        meta[_k] = []
                    else:
                        meta[_k] = {}
                    prev_indent = cur_indent
                    if not self.is_empty_header(cur_indent, yml_str, d['i']):
                        self.parse_raw_yml(yml_str, meta[_k], d, cur_indent, k)
                else:
                    k, v = self.key_val(l)

                    if type(meta) is list:
                        if l.lstrip().startswith('-'):
                            meta.append(re.sub(r'^[-]', '', l, count=1))
                        else:
                            return

                    elif (unterminated_str or v is None) and prev_temp_holder:
                        # If the value is null that is the line is without a key
                        if self._preserve_indentation:
                            s = meta[prev_temp_holder][0] + '\n' + k + (': ' + v if v is not None else '')
                            meta[prev_temp_holder] = (s, meta[prev_temp_holder][1])
                        else:
                            meta[prev_temp_holder] += '\n' + k + (': ' + v if v is not None else '')
                        # if unterminated_str:
                        #     # If the string is unterminated check here to see if it is closed
                        #     if self.is_str_closed(l):
                        #         unterminated_str = False
                        #         quote_type = None
                    else:
                        k = k.strip()

                        if self.trim_whitespace:
                            v = v.rstrip()

                        meta[k] = (v, cur_indent) if self._preserve_indentation else v

                        v = v.strip()

                        quote_type = v[0]
                        while self.is_quoted_str(v) and not self.is_str_closed(v, quote_type) and d['i'] + 1 < len(yml_str):
                            if self._preserve_indentation:
                                s = meta[k][0] + '\n' + yml_str[d['i'] + 1]
                                meta[k] = (s, meta[k][1])
                            else:
                                meta[k] += '\n' + yml_str[d['i'] + 1]
                            d['i'] += 1
                            if self.is_str_closed(yml_str[d['i']], quote_type):
                                break

                        # check if its a quoted string and if the string is not terminated
                        # if self.is_quoted_str(v) and not self.is_str_closed(v):
                        #     unterminated_str = True
                        #     quote_type = v.strip()[0]
                        # else:
                        #     unterminated_str = False
                        #     quote_type = None

                        # if its a multi line str loop until the indentation
                        while v in ['|-', '|'] and d['i'] + 1 < len(yml_str) and (not yml_str[d['i'] + 1] or cur_indent < self.str_indent(yml_str[d['i'] + 1])):
                            if self._preserve_indentation:
                                s = meta[k][0] + '\n' + yml_str[d['i'] + 1]
                                meta[k] = (s, meta[k][1])
                            else:
                                meta[k] += '\n' + yml_str[d['i'] + 1]
                            d['i'] += 1

                        prev_indent = cur_indent
                        prev_temp_holder = k
                    d['i'] += 1
            except Exception as e:
                print(meta.keys())
                if self.debug_mode:
                    raise e
                raise YMLParserError(line_no=d['i'] + 1, line_str = yml_str[d['i']])
        return
    
    def dict_to_yml_str(self, r, indent = 0, res = []):
        for k, v in r.items():
            if self.is_hashable(v):
                if self.preserve_indentation(k):
                    indent = k[1]
                res.append(' ' * indent + f'{k[0]}:')
                self.dict_to_yml_str(v, indent + 2, res)
            elif type(v) is list:
                if self.preserve_indentation(k):
                    indent = k[1]
                res.append(' ' * indent + f'{k[0]}:')
                for _v in v:
                    res.append(_v)
            else:
                if self.preserve_indentation(v):
                    indent = v[1]
                res.append(' ' * indent + f'{k}: {v[0]}')
        return res
    
    def load(self, file_path = None, yml_str = None):
        if file_path is not None:
            with open(file_path, 'r') as f:
                yml_str = f.read()
        if yml_str:
            yml_str = yml_str.split('\n')
        if yml_str[0] == '---':
            yml_str = yml_str[1:]
        if self.debug_mode:
            print('Parsing YML file with total lines: ',len(self.data))
        self.parse_raw_yml(yml_str, self.data, {'i': 0})
        
    def dump(self, file_path = None, data = None):
        _data = lambda :  ('---\n' if self.doc_seperator else '') + '\n'.join(self.dict_to_yml_str(data or self.data, res = []))
        if file_path is not None:
            with open(file_path, 'w') as f:
                f.write(_data())
        return _data()
