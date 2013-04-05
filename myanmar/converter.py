import os.path
import json
import regex as re

class BaseEncoding (object):

    def __init__ (self, jsonFile=None):
        """
        """
        _ROOT = os.path.dirname (os.path.abspath (__file__))
        self.mappings = self.load_json (os.path.join(_ROOT, 'data', jsonFile))
        self.pattern = self.get_compiled_pattern ()

    def get_compiled_pattern (self):
        print (self.get_pattern ())
        print ('\n\n')
        return re.compile (self.get_pattern(), re.UNICODE)

    def get_pattern (self):
        def build_pattern (pattern):
            if isinstance (pattern, str):
                node = pattern
                or_expr = "|".join([x for x in sorted(self.mappings[node].values ()) if x])
                return '(?P<' + pattern + '>'+  or_expr + ')'
            if isinstance (pattern, tuple):
                ret_list = [build_pattern (x) for x in pattern]
                if len(ret_list) > 1:
                    return '(' + "|".join (ret_list) + ')*'
                else:
                    return ret_list[0] + '*'
            if isinstance (pattern, dict):
                for k, v in pattern.items ():
                    node = v
                    or_expr = ''.join([build_pattern (x) for x in  node])
                    return '(?P<'+ k + '>' + or_expr + ')'

        return "|".join ([build_pattern(x) for x in self.syllable_pattern])

    def load_json (self, jsonFile):
        if not jsonFile:
            raise RuntimeError ("jsonFile must not be None.")

        if not os.path.exists (jsonFile):
            raise RuntimeError ("jsonFile doesn't exists on the system.")

        with open (jsonFile, 'r') as iFile:
            mappings = json.load (iFile)
            return mappings

class UnicodeEncoding (BaseEncoding):
    def __init__ (self, *args, **kwargs):

        self.syllable_pattern = [
            "independent",
            "digits",
            "puncts",
            "lig",
            {"syllable": [("kinzi",), "cons", ("stack",),
                           ("yapin",), ("yayit",), ("wasway",), ("hatoh",),
                           ("eVowel",), ("iVowel",), ("uVowel",), ("anusvara",),
                           ("aiVowel",), ("aaVowel",), ("dot_below", "asat"), ("visarga",)]
                           }
            ]

        super ().__init__(*args, **kwargs)

class ZawgyiEncoding (BaseEncoding):

    def __init__ (self, *args, **kwargs):
        self.syllable_pattern = [
            "independent",
            "digits",
            "puncts",
            "lig",
            {"syllable": [("eVowel",), ("yayit",), "cons", ("kinzi",),
                          ("stack",), ("yapin", "wasway", "hatoh",),
                          ("iVowel", "uVowel", "anusvara", "aiVowel"),
                          ("aaVowel",), ("dot_below", "asat"), ("visarga",)]
                          }
            ]
        super ().__init__(*args, **kwargs)

class SyllableIter ():

    def __init__ (self, text="", encoding=UnicodeEncoding('unicode.json')):
        self.text = text
        self.pattern  = encoding.get_compiled_pattern ()
        self.start = 0

    def __iter__ (self):
        return self

    def __next__ (self):
        match = self.pattern.search (self.text, self.start)
        if not match:
            raise StopIteration

        if match.start () == self.start:
            self.start = match.end ()
        else:
            self.start = match.start ()

        return { k: v for k , v in match.groupdict().items() if v }

class Converter ():

    def __init__ (self):
        self.uni = UnicodeEncoding ( 'unicode.json')
        self.zgy = ZawgyiEncoding ('zawgyi.json')

    def convert (self, text):
        itr = SyllableIter (text=text, encoding=self.zgy)

        for syllable in itr:
            print (syllable)
        #syllable = text[start:end]


def main  ():

    with open ('data/test.txt', mode='r', encoding='utf-8') as iFile:
        data = iFile.read ()
        conv = Converter ()
        conv.convert (data)


if __name__ == "__main__":
    main ()
