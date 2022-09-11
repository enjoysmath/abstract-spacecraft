from bidict import bidict

subscript_digs = bidict({
    '₀' : '0', 
    '₁' : '1',
    '₂' : '2',
    '₃' : '3',
    '₄' : '4',
    '₅' : '5',
    '₆' : '6',
    '₇' : '7',
    '₈'	: '8',
    '₉' : '9',
    '₋' : '-',
})

superscript_digs = bidict({
    '⁰' : '0',
    '¹' : '1',
    '²' : '2',
    '³' : '3',
    '⁴' : '4',
    '⁵' : '5',
    '⁶' : '6',
    '⁷'	: '7', 
    '⁸'	: '8', 
    '⁹' : '9',
    '⁻' : '-',
})

def str_digit_map(string:str, charmap:bidict):
    return ''.join(map(lambda c: charmap[c], string))

def inv_str_digit_map(string:str, charmap:bidict):
    return ''.join(map(lambda c: charmap.inv[c], string)) 


def check_for_int(string:str):
    try:
        x = int(string)
        return x, lambda i: str(i)
    except:
        try:
            x = str_digit_map(string, charmap=superscript_digs)
            x = int(x)
            return x, lambda i: inv_str_digit_map(str(i), superscript_digs)
        except:
            try:
                x = str_digit_map(string, charmap=subscript_digs)
                x = int(x)
                return x, lambda i: inv_str_digit_map(str(i), subscript_digs)
            except:
                return None, None
        
        