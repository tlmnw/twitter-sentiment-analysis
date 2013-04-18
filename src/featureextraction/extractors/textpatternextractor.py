# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from baseextractor import BaseExtractor
import re
from collections import OrderedDict


class BasePatternExtractor(BaseExtractor):
    """Extracts boolean features from a tweet based on regular expression.

    If the regular expression supplied by the subclass matches,
    it the corresponding attribute is set to "Y", "N" otherwise.
    
    Subclasses are required to populate the self.regexes field
    with an OrderedDict object. Keys are attribute names,
    values are regular expression objects.

    Tweets are matched against patterns with the search function,
    not the match function.
    """

    YES = "Y"
    NO = "N"

    def extractFeatures(self, tweet):
        ret = OrderedDict()
        for (field,regex) in self.regexes.iteritems():
            if regex.search(tweet.tweet):
                ret[field] = self.YES
            else:
                ret[field] = self.NO
        return ret
                

    def getFields(self):
        return self.regexes.keys()

    def getFieldType(self, field):
        return "{%s,%s}" % (self.YES,self.NO)


class RepeatedCharacterExtractor(BasePatternExtractor):
    """Extracts a boolean feature for repeated characters.

    If a character is repeated 3 times in a row as in "looool",
    then the "min_3_repeated_characters" field is set to "Y".
    """

    def __init__(self):
        self.regexes = OrderedDict()
        # http://stackoverflow.com/questions/2039140/python-re-how-do-i-match-an-alpha-character
        # regex is not optimal, ignores bmp and has digits and underscore
        self.regexes["min_3_repeated_characters"] = re.compile(ur"[^\W\d_]{3}")

class CapsExtractor(BasePatternExtractor):
    """Extracts a boolean feature for repeated uppercase characters.

    If three consecutive uppercase characters are found, as in "OMGWTF",
    then the "caps_lock_min_3_characters" field is set to "Y".
    """
    
    def __init__(self):
        self.regexes = OrderedDict()
        # regex is not optimal, ignores bmp
        self.regexes["caps_lock_min_3_characters"] = re.compile(ur"[A-Z]{3}")


