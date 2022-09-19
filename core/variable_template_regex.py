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
        var_count = 0
        template = []
        self._regex = ''
          
        for match in self._textRegex.finditer(string):
            start,end = match.span()
            for var_match in self._variableRegex.finditer(string[i:start]):
                template.append((self.Variable, var_match.group()))
            template.append(match.group())
            i = end
        
        for var_match in self._variableRegex.finditer(string[i:]):
            var = var_match.group()
            if var in var_index:
                index = var_index[var]
            else:
                index = var_count
                var_index[var] = index
                var_count += 1
            template.append(f'(?P<V{var_count}>.+)')
            i = var_match.span()[1]
        
        ending = string[i:]
        template.append(ending)
            
        self._regex = "".join(template)
        
    def __str__(self):
        return str(self._regex)
    
    def __repr__(self):
        return str(self)
        