import re
from bidict import bidict

var_regex = re.compile(r"(?P<V>[a-zA-Z])");
keywod_regex = re.compile(r"(<b>.+</b>)|(<i>.</i>)")



def regex_from_var_expr(user_input:str, var_index:bidict=None, matched_vars:dict=None):
   if var_index is None:
      var_index = bidict()
      
   if matched_vars is None:
      matched_vars = {}
      
   user_input = user_input.strip()
   
   regex = ""
   end = 0
   
   for match in var_regex.finditer(user_input):
      regex += user_input[end:match.span()[0]]
      var_str = match.group("V")
      
      if var_str in var_index:
         if var_str in matched_vars:
            exp_expr = matched_vars[var_str]
            regex += exp_expr
         else:
            i = var_index[var_str]
            regex += f"(?P=V{i})"
      else:
         i = len(var_index)
         var_index[var_str] = i
         regex += f"(?P<V{i}>.+)"
      
      end = match.span()[1]
      match = var_regex.match(user_input, pos=end)
      
   regex += user_input[end:]
   
   return regex


if __name__ == '__main__':
   while True:
      i = input("> ")
      d = bidict()
      print(regex_from_var_expr(i), d)
      print(d)