from WordlePlayer import WordlePlayer

class WordlePlayerII(WordlePlayer):
    """description of class"""

    def __init__(self, wordList):
        super().__init__(wordList)  
        self.scorePSpace()

    def reset(self):
        super().reset()
        self.scorePSpace()

    def scorePSpace(self):
        # Across all words in the dictionary, count the number of occurrences of
        # each letter in each possible position. These will be the basis for the
        # score
        scoreDict = {l : [0 for i in self.wordList[0]] for l in self.alphabet}
        for word in self.pSpace:
            for i in range(len(word)):
                scoreDict[word[i]][i] += 1

        # Now we score. The score is the number of words in the possibility 
        # space that have the same letter in the same position for each letter 
        # in the word. 
        pSpaceScores = {} 
        for word in self.pSpace:
            pSpaceScores[word] = 0
            for i in range(len(word)):
                pSpaceScores[word] += scoreDict[word[i]][i]
        
        # Finally, we sort pSpace by the word scores. 
        def score(word):
            return pSpaceScores[word]
        self.pSpace.sort(reverse=True, key=score)

    def takeFeedback(self, response):
        super().takeFeedback(response)
        self.scorePSpace()






