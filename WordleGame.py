import random

class WordleGame:
    """ An object to represent the state of a Wordle game. 
    """

    def __init__(self, seedSoln=None):
        # Builds out the lists of words from hard-coded files. 
        self.dict_words = []
        self.soln_words = []
        with open("all.txt", "r") as f:
            for word in f:
                self.dict_words.append(word[:5])    # Strip the newlines
        with open("actual.txt", "r") as f:
            for word in f:
                self.soln_words.append(word[:5])    # Strip the newlines
        self.reset(seedSoln)


    def reset(self, seedSoln=None):
        self.solution = seedSoln if seedSoln else random.choice(self.soln_words)


    def evalWord(self, word):
        # Approach: Keep track of letters that are matched; removing them from
        # consideration so that double-matching for any reason is impossible. 
        # We do two passes for reasons (explained later) so we want to be able
        # to edit the working values of the words on the fly. Lists of chars was
        # more easy to do that with right away than to edit strings (I'm new).
        wordUnchecked = [letter for letter in word]
        solnUnchecked = [letter for letter in self.solution]
        output = ["_","_","_","_","_"] # Defaults to unmatched
    
        # Do an initial pass to avoid jumping the gun; when multiple matches are
        # possible, exact matches take priority and should exclude the inexact
        # variant matches from happening.    
        for i in range(5):
            if wordUnchecked[i] == solnUnchecked[i]:
                output[i] = "G"
                # '.' is sentinel below to skip that index
                wordUnchecked[i] = "."
                solnUnchecked[i] = "."

        # Exact matches are no longer in the set, so inexact matches are all 
        # that's left
        for i in range(5):
            if wordUnchecked[i] == ".": 
                continue
            elif wordUnchecked[i] in solnUnchecked:
                # Match to the first unchecked occurence in the word, then
                # don't match to that occurence again. 
                solnUnchecked.remove(wordUnchecked[i])
                output[i] = "Y"

        # Lastly, output
        return str.join("", output)
