class WordlePlayer:
    """A generic boilerplate implementation of a Wordle Player.

    Contains all the basic functionality to solve a game of Wordle (defined in 
    the WordleGame class) semi-competently.  
    """

    def __init__(self, wordList):
        """Initializes a WordlePlayer's default state.

        Sets up its wordList with the passed argument. The wordList can and 
        should be referenced to help solve the puzzle, but it should *not* be
        altered in any way. 

        An alphabet is also provided as a list of lowercase character strings, 
        and preparation for the first game via this baseclass's implementation 
        (via name mangling) of the reset() (see that method's docstring for 
        attributes used elsewhere in this implementation).
        """
        self.wordList = wordList
        self.alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 
                         'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 
                         'w', 'x', 'y', 'z']
        self._reset()


    def reset(self):
        """Resets the state of the WordlePlayer so they can begin a new game.

        Defines the instance variables pSpace as a list that contains the word
        list passed on instantiation; playedWords as a list that is to contain 
        the words played in order for the current game; and feedback as a list 
        that is to contain the responses to each word played, such that 
        playedWords[i] is the word that elicited the response stored in 
        feedback[i].
        """
        self.pSpace = wordList.copy()
        self.playedWords = []
        self.feedback = []
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
        


    def takeFeedback(self, feedback):
        """Uses the feedback passed in and its own memory to narrow its choices.

        This is where the magic happens. This method is intended to cross-
        reference the list of playedWords with the feedback string passed in to
        expand its knowledge base and prune its possibility space. It's the 
        design intent that even if nothing else in a subclass is overridden, a
        change to this will change the strategy of how it plays. 
        """











