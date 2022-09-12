import re
from core.python_tools import escape_regex_str

class VariableTemplateRegex:
    Variable, TextString = range(2)
    _variableRegex = re.compile(r'[a-zA-Z]')
    _textRegex = re.compile(r'(<b>.*</b>)|(<i>.*</i>)')
    
    def __init__(self, string:str):
        i = 0
        self._template = []
        
        for match in self._textRegex.finditer(string):
            start,end = match.span()
            for var_match in self._variableRegex.finditer(string[i:start]):
                self._template.append((self.Variable, var_match.group()))
            self._template.append((self.TextString, match.group()))
            i = end
        
        for var_match in self._variableRegex.finditer(string[i:]):
            self._template.append((self.Variable, var_match.group()))
            i = var_match.span()[1]
        
        ending = string[i:]
        
        if ending:
            self._template.append(ending)
            
        self._regex = ''
        var_base = 'v'
        var_count = 0
        self._variables = {}
        
        for t in self._template:
            if t[0] == self.Variable:
                var_name = f'{var_base}{var_count}'
                self._regex += f'(?P<{var_name}>.*)'
                self._variables[var_name] = t[1]
                var_count += 1
            elif t[0] == self.TextString:
                self._regex += escape_regex_str(t[1])
                
    def __str__(self):
        return str(self._regex)
    
    def __repr__(self):
        return str(self)
        