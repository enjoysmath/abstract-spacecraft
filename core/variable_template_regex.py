import re
from core.python_tools import escape_regex_str
from bidict import bidict

class VariableTemplateRegex:
    _variableRegex = re.compile(r'[a-zA-Z]')
    _textRegex = re.compile(r'(<b>.*</b>)|(<i>.*</i>)')
    
    def __init__(self, string:str, var_index:bidict=None):
        if var_index is None:
            var_index = bidict()

        i = 0
        var_count = len(var_index)
        template = []
        self._regex = ''
        
        def match_vars(string:str, i:int, start:int, var_count:int) ->  int:
            var_end = i
            for var_match in self._variableRegex.finditer(string[i:start]):
                var_start, var_end = var_match.span()
                text = string[i:var_start]
                template.append(text)
                var = var_match.group()
                if var in var_index:
                    index = var_index[var]
                else:
                    index = var_count
                    var_index[var] = index
                    var_count += 1
                template.append(f'(?P<V{index}>.+)')            
            return var_end, var_count
        
        for match in self._textRegex.finditer(string):
            start,end = match.span()
            var_end, var_count = match_vars(string, i, start, var_count)
            if var_end < start:
                template.append(string[var_end:start])
            template.append(match.group())
            i = end

        var_end, var_count = match_vars(string, i, len(string), var_count)
        if var_end < len(string):
            template.append(string[var_end:])
            
        self._regex = re.compile("".join(template))
        
    def __str__(self):
        return str(self._regex)
    
    def __repr__(self):
        return str(self)
        
    @property
    def regex(self):
        return self._regex