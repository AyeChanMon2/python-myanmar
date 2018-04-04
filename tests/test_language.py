import glob
import os.path

from myanmar import language
from myanmar import encodings


def test_zawgyi_syllable_iter():
    for path in glob.glob(
        os.path.join(
            os.path.dirname(__file__), 'data', 'zgy-syllableiter*.txt'
        )
    ):
        with open(path, 'r', encoding='utf-8') as iFile:
            text = iFile.readline().strip()
            syllables = [l.strip('\n') for l in iFile.readlines()]
            print('syllables:', syllables)
            zgy = encodings.ZawgyiEncoding()
            itr = language.MorphoSyllableBreak(text=text, encoding=zgy)
            for i, each in enumerate(itr):
                assert each['syllable'] == syllables[i]


def test_unicode_syllable_iter():
    for path in glob.glob(
        os.path.join(
            os.path.dirname(__file__), 'data', 'uni-syllableiter*.txt'
        )
    ):
        with open(path, 'r', encoding='utf-8') as iFile:
            text = iFile.readline().strip()
            syllables = [l.strip('\n') for l in iFile.readlines()]

            uni = encodings.UnicodeEncoding()
            itr = language.MorphoSyllableBreak(text=text, encoding=uni)

            for i, each in enumerate(itr):
                assert each['syllable'] == syllables[i]
