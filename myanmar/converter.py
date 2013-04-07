import os.path
import json
import re
import itertools
import glob

_ROOT = os.path.dirname (os.path.abspath (__file__))

class BaseEncoding (object):

    def __init__ (self):
        """
        """
        # get json file name dynamically from class name
        name = self.__class__.__name__
        name = name[:name.find('Encoding')].lower() + '.json'
        self.json_data = self.load_json (os.path.join(_ROOT, 'data', name))

        self.reverse_table = self.get_reverse_table ()
        self.table = self.get_table ()
        self.pattern = self.get_compiled_pattern ()

    def get_table (self):
        ret = {}
        for key, value in self.json_data.items ():
            ret.update ({k: v for k, v in value.items() if v})
        return ret

    def get_reverse_table (self):
        ret = {}
        for key, value in self.json_data.items ():
            ret.update ({v: k for k, v in value.items() if v})
        return ret

    def get_compiled_pattern (self):
        #print (self.get_pattern () + '\n')
        return re.compile (self.get_pattern(), re.UNICODE)

    def get_pattern (self):
        def build_pattern (pattern):
            if isinstance (pattern, str):
                node = pattern
                #or_expr = "|".join(["--%s--(%s)" %(x, x.encode ('unicode_escape')) \
                #for x in sorted(self.json_data[node].values ()) if x])
                or_expr = "|".join([x for x in sorted(self.json_data[node].values ()) if x])
                return '(?P<' + pattern + '>'+  or_expr + ')'

            if isinstance (pattern, tuple):
                ret_list = [build_pattern (x) for x in pattern]
                if len(ret_list) > 1:
                    return '(' + "|".join (ret_list) + ')*'
                else:
                    return ret_list[0] + '*'

            if isinstance (pattern, list):
                return ''.join([build_pattern (x) for x in  pattern])

        return "(?P<syllable>"+ "|".join ([build_pattern(x) for x in self.syllable_form]) + ")"

    def load_json (self, jsonFile):
        if not jsonFile:
            raise RuntimeError ("jsonFile must not be None.")

        if not os.path.exists (jsonFile):
            raise RuntimeError ("jsonFile doesn't exists on the system.")

        with open (jsonFile, 'r') as iFile:
            data = json.load (iFile)
            return data

class UnicodeEncoding (BaseEncoding):

    def __init__ (self, *args, **kwargs):
        self.syllable_pattern = [("kinzi",), "consonant", ("stack",),
                                 ("yapin",), ("yayit",), ("wasway",), ("hatoh",),
                                 ("eVowel",), ("iVowel",), ("uVowel",), ("anusvara",),
                                 ("aiVowel",), ("aaVowel",), ("dot_below", "asat"), ("visarga",)]
        self.syllable_form = [
            "independent",
            "digit",
            "punctuation",
            "ligature",
            self.syllable_pattern
            ]

        super ().__init__(*args, **kwargs)

class LegacyEncoding (BaseEncoding):

    def __init__ (self, *args, **kwargs):
        self.syllable_pattern  = [("eVowel",), ("yayit",), "consonant", ("kinzi",),
                                  ("stack",), ("yapin", "wasway", "hatoh",),
                                  ("iVowel", "uVowel", "anusvara", "aiVowel"),
                                  ("aaVowel",), ("dot_below", "asat"), ("visarga",)]
        self.syllable_form = [
            "independent",
            "digit",
            "punctuation",
            "ligature",
            self.syllable_pattern
            ]
        super ().__init__(*args, **kwargs)

class ZawgyiEncoding (LegacyEncoding):
    pass

class SyllableIter ():
    """
    Return an iterator of clusters, in given encoding.
    """
    def __init__ (self, text, encoding):
        if not isinstance(encoding, BaseEncoding):
            raise TypeError ("is not a valid encoding.")

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
            # no unmatched text
            self.start = match.end ()
            ret = { k: v for k , v in match.groupdict().items() if v }
        else:
            # if there is unmatched text,
            ret = {'syllable': self.text[self.start:match.start()]}
            self.start = match.start ()
        return ret

def get_available_encodings ():
    encodings = []
    for path in glob.glob (os.path.join (_ROOT, 'data', '*.json')):
        encodings += [os.path.splitext (os.path.basename(path))[0]]
    return encodings

def convert (text, from_encoding, to_encoding):
    """
    Take a unicode string, and convert it to from_encoding to
    to_encoding.

    Supported encodings can be obtained by get_available_encodings ()
    function.
    """
    print (get_available_encodings())
    encodings = { encoding: globals()[encoding.title() + 'Encoding'] \
                  for encoding in get_available_encodings() }

    for encoding  in [from_encoding, to_encoding]:
        if not encoding in encodings:
            raise NotImplementedError ("Unsupported encoding: %s" % encoding)

    from_encoding = encodings[from_encoding]()
    to_encoding = encodings[to_encoding]()
    iterator = SyllableIter (text=text, encoding=from_encoding)

    otext = ""
    for each_syllable in iterator:
        complete_syllable = each_syllable['syllable']

        if len(each_syllable) == 1:
            # unmatched text, no need to convert
            otext += complete_syllable
            continue

        if complete_syllable in from_encoding.reverse_table:
            # Direct mapping
            key = from_encoding.reverse_table[complete_syllable]
            otext += to_encoding.table[key]
            continue

        # flattern syllable_pattern, convert to a list of tuples first
        syllable_pattern = [(x,) if isinstance(x, str) else x for x in to_encoding.syllable_pattern]
        syllable_pattern = list(itertools.chain(*syllable_pattern))

        # collect codepoints in syllable, in correct syllable order
        #print(syllable_pattern)
        syllable = ""
        for each_pattern in syllable_pattern:
            if each_pattern in each_syllable:
                key = from_encoding.reverse_table[each_syllable[each_pattern]]
                syllable += to_encoding.table[key]
                #print (str(each_syllable) + '\t' + syllable)
        otext += syllable

    return otext

def main  ():
    with open ('data/test2.txt', mode='r', encoding='utf-8') as iFile:
        data = iFile.read ()
        print(convert (data, 'unicode', 'zawgyi'))

if __name__ == "__main__":
    main ()
