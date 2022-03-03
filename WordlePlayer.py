import re

class WordlePlayer:
    """A generic boilerplate implementation of a Wordle Player.

    Contains all the basic functionality to solve a game of Wordle (defined in 
    the WordleGame class) semi-competently.

    Attributes:
        wordList: Set on initialization, this is a list of words meant to 
          represent the list of words that the player can use as guesses. 
          Naturally, this means that this list should at least contain all 
          possible answers, but can include more. No implementation should alter
          this list directly, as the base class assumes it's always complete. It
          is assumed that the length of every word in the list is a uniform 
          length.
        alphabet: A hard-coded list of all letters in lower case. This should 
          also never be tampered with as it's used in reset() to establish the
          knowledge dictionary. 
        pSpace: The working list of possible options. This list is reset with 
          the reset() method to be a copy of wordList. 
        playedWords: An internal record of the words that the Player has played
          in previous rounds, in the order they were played. 
        feedback: An internal record of the feedback for each word the Player
          has played in previous rounds. 
        knowledge: The representation of our knowledge about each letter. The 
          keys are the letters in the alphabet, and they map to a nested list 
          we'll call L. L[0] is a list of all indices of the solution word that
          we know are our letter (it defaults to an empty list). L[1] is a list
          of all the indices of the solution word that we know for certain are 
          not the letter, prepended by a boolean flag at L[1][0]. If L[1][0] is
          True, that means that we know the letter is not in the word at all (it
          defaults to False).
    """

    def __init__(self, wordList):
        """Initializes a WordlePlayer's default state.

        Sets its wordList with the passed argument. The wordList can and should
        be referenced to help solve the puzzle, but it should *not* be altered 
        in any way. 

        Creates the alphabet attribute.

        Also initializes the other documented attributes of the Player by making
        a call to the reset() method.

        Args: 
            wordList: The list of all words that the Player could guess. While
            the game of Wordle uses only 5-letter words, the player will accept
            wordLists with words of any length, so long as every word in the 
            list is of uniform length. 
        """
        self.wordList = wordList
        self.alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 
                         'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 
                         'w', 'x', 'y', 'z']
        self._reset()


    def reset(self):
        """Resets the state of the WordlePlayer so they can begin a new game. 
        
        The following attributes are set to their default states: pSpace 
        (defaults to a copy of wordList), playedWords, feedback, and knowledge.
        """
        self.pSpace = self.wordList.copy()
        self.playedWords = []
        self.feedback = []
        self.knowledge = {x: [[], [False]] for x in self.alphabet}
    _reset = reset


    def playWord(self):
        """The method that returns the word to be played this round. 

        The default implementation of this method is to transfer the word in 
        index 0 of the possibility space (self.pSpace) to the list of played 
        words (self.playedWords), removing it from there and finally returning 
        it. No decision making is intended to be made in this method. 
        """
        self.playedWords.append(self.pSpace.pop(0))
        return self.playedWords[-1]
        

    def takeFeedback(self, response):
        """Uses the feedback passed in and its own memory to narrow its choices.

        This is where the magic happens. This method is intended to cross-
        reference the list of playedWords with the feedback string passed in to
        expand its knowledge base and prune its possibility space. It's the 
        design intent that even if nothing else in a subclass is overridden, a
        change to this will change the strategy of how it plays. 

        Args:
            response: The feedback string that corresponds to the last word 
              played by this Player. 
        """
        # First we update our knowledge dictionary with the new informaiton we
        # just got. 
        self.feedback.append(response)
        lastWord = self.playedWords[-1]
        for i in range(len(lastWord)):
            # Update our knowledge-base dictionary
            letter = lastWord[i]
            knowns = self.knowledge[letter][0]
            excls = self.knowledge[letter][1]

            # Check if there's more than one of a letter in the word.
            doubleCheck = lastWord.replace(letter, "")
            doubles = len(lastWord) - len(doubleCheck) > 1
            
            if response[i] == "G":
                # We've just heard a new letter's position definitively
                if i not in knowns:
                    knowns.append(i)
            elif response[i] == "Y":
                # We've heard the letter is in the word, but not where we placed
                # it. 
                if i not in excls:
                    excls.append(i)
            else:
                # The only other character in response strings are underscores. 
                # If we get an underscore that usually means that the letter is
                # not in the word at all, but there's an edge case when the 
                # letter appears more than once. 
                if not excls[0] and not doubles:
                    # If we haven't already universally excluded it, and there's
                    # no chance that this is the edge case brought on by double
                    # letters, then we know to universally exclude it.
                    excls[0] = True
                elif doubles:
                    # If this is a double letter, we need to check if it's in
                    # the word elsewhere before we definitively say it's not. 
                    notInWord = True
                    for j in range(len(lastWord)):
                        if lastWord[j] == letter and j != i:
                            notInWord = notInWord and response[j] == response[i]
                    excls[0] = notInWord
        
        # Now we prune our possibility space. Start by composing as much of the
        # word as we know:
        knownSoFar = ["." for i in range(len(self.wordList[0]))]
        for letter in self.knowledge:
            for index in self.knowledge[letter][0]:
                knownSoFar[index] = letter
        compositeSoln = "".join(knownSoFar)

        # Build a new pSpace from pSpace
        todo = self.pSpace.copy()
        keepList = []
        while todo:
            word = todo.pop(0)

            # First check if the word could be a match for our known letters. 
            keep = re.fullmatch(compositeSoln, word) is not None
            
            # Then, assuming it was, check letter by letter against the 
            # exclusions list
            i = 0
            while keep and i < len(word):
                letter = word[i]
                excls = self.knowledge[letter][1]
                # Reminder: excls[0] is "Not in the word" and any remaining 
                # elements in the excls are indices we know the letter is not in
                keep = keep and not excls[0] and i not in excls[1:]
                i += 1
            if keep:
                keepList.append(word)
        self.pSpace = keepList

        # This is where we'd sort pSpace by some function determining which of 
        # the remaining words should be our next guess. 
