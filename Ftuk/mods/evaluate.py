__author__ = 'chris'

import tagger

class Evaluate(tagger.Tagger):

    # TODO: get the actual wsj10 file as gold standard
    # TODO: check for the actual amount of tags and n-grams (2/3) in gold file
    # TODO: compare these numbers with the actual statistics

    # TODO: from the top 5 n-grams (2/3), if correct output >> STRUC and GS
    #       sentence, validation by eye. Randomly output 100 sentence pairs.

    # TODO: check how the total structs GS and ST compare in number

    def __init__(self):
        pass