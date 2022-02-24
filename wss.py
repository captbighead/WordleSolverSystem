import io
import random

loggingEnabled = False

def log(message):
    if loggingEnabled:
        print(message)

class Game:
    """Stores the game-state information for an instance of a Wordle Game, as 
    well as the lists of all possible words and all words elligible to be 
    solutions. 
    """
    words = []                      # List of all valid guesses
    soln_words = []                 # List of guesses that can be solutions
    with open("all.txt", "r") as f:
        for word in f:
            words.append(word[:5])          # Strip the newlines
    with open("actual.txt", "r") as f:
        for word in f:
            soln_words.append(word[:5])     # Strip the newlines
    
    def __init__(self, soln=None):
        """Initializes a game by choosing a solution word and creating a list to
        store round information. If a solution word is provided, that is the 
        solution, otherwise it picks randomly from the legal solutions list. 
        """
        self.solution = soln if soln else random.choice(self.soln_words)
        self.rounds = []

    def isOver(self):
        """If the game has played 6 rounds it's over. It's also over if the game
        has already been won.
        """
        return len(self.rounds) == 6 or self.isWon()

    def isWon(self):
        """If the last guess made was the solution then the player has won. If 
        the player has made no guesses, they haven't won. 
        """
        return len(self.rounds) > 0 and self.rounds[-1][0] == self.solution

    def checkWordIsLegal(self, word):
        """Check that the word is a legal guess in Wordle (a five letter word in
       the game's dictionary)
       """
        for legal in self.words:
            if word == legal:
                return True
        return False

    def tryRound(self, word):
        """Attempts to play a word in the game. If the word is legal and the
        game isn't already finished (win or lose) then it returns the feedback
        for that word as the game Wordle would:

          - '_' Means the corresponding character in the guess is not in the
            solution at all
          - 'Y' Means the corresponding character in the guess is in the 
            solution, but in the wrong position
          - 'G' Means the corresponding character in the guess is in the 
            solution in that position

        It's possible (esp. with an impatient human) that the words played are 
        not valid guesses. In that case, the feedback is null and the Player is
        expected to process that and try again. 
        """
        if self.checkWordIsLegal(word) and not self.isOver():
            return self.matchWord(word)
        return None

    def matchWord(self, word):
        """Checks the word against the solution and creates a five letter string
        representing the feedback as per the rules of Wordle. The 
        (word, feedback) tuple is logged as a round in the instance's "rounds" 
        list, and then the feedback string is returned. 
        
        The key is outlined in the comment of the tryRound method. 
        """
        # Approach: Keep track of letters that are matched; removing them from
        # consideration so that double-matching for any reason is impossible. 
        # We do two passes for reasons (explained later) so we want to be able
        # to edit the working values of the words on the fly. Lists of chars was
        # more easy to do that with right away than to edit strings (I'm new).
        wordUnchecked = [word[0], word[1], word[2], word[3], word[4]]
        solnUnchecked = [self.solution[0], self.solution[1], self.solution[2], 
                     self.solution[3], self.solution[4]]
        output = ["_","_","_","_","_"] # Defaults to unmatched
    
        # Do an inital pass to avoid jumping the gun; when multiple matches are
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

        # At this point, the word has been checked. Log the results for future
        # reference:
        self.rounds.append((word, str.join("", output)))
        return str.join("", output)

class HumanPlayer:
    """Player control logic for a human being to provide input through the 
    console. 
    """
    def __init__(self, game):
        """Initializes a player with a reference to the game they're playing.
        """
        self.game = game
        #self.butIWonTho = False    # This was for debugging why the game wasn't 
                                    # ending when choosing random words from the
                                    # source list (I forgot to remove '\n's)

    def playWord(self):
        """Prompts the player to enter a word through to console and returns 
        that word. Doesn't check validity of the word, that's the Game object's
        job"""
        #if self.butIWonTho:
        #    holUp = True       # Null statement I can throw a breakpoint on
        prompt = "Enter a word for round " + str(len(self.game.rounds)+1) + ": "
        return input(prompt)

    def processFeedback(self, feedback):
        """Prints the feedback string provided to the console, aligned so it 
        should be directly under the word they input (if they're playing like a
        civilized person and not trying to mess with my program).
        """
        print("                          " + feedback + "\n")
        #if feedback == "GGGGG":    # Checking for wins is done in the game loop
        #    self.butIWonTho = True # but I needed to debug it here. 

    def __str__(self):
        return "Human Player"

class AutoPlayer_MkI:
    """Player control logic for a computer that makes random guesses. 
    """
    def __init__(self, game):
        self.game = game

    def playWord(self):
        """Grabs a random word from the list of all possible words"""
        choice = random.choice(self.game.words)
        log(str(self) + ": Uhhhhh.... is it '" + choice + "'?")
        return random.choice(self.game.words)

    def processFeedback(self, feedback):
        """Like any good dumb player, the MkI ignores all feedback. 
        """
        log("               Game:                   " + feedback)
        self.ignoreFeedback = True

    def __str__(self):
        return "AutoPlayer (Mark I)"

class AutoPlayer_MkII:
    """Player control logic for a computer that uses the feedback to narrow down
    its random guesses. 
    Currently set up to only play the game it's given on instantiation; for 
    later incarnations/simulations I'll need to implement a reset() function.
    """
    def __init__(self, game):
        """Initialization is used to make a local copy of the game's complete
        word list and to initialize the knowledge base.
        """
        self.game = game
        self.possibilities = self.game.words.copy()

        # Set up the knowledge base of letters in the final answer that we're 
        # certain about the position of, letters in the answer we're uncertain
        # of the position of, and letters we're certain aren't in the answer
        self.solvedLetters = [".", ".", ".", ".", "."]  # Sentinels to hold posn
        self.includedLetters = []   
        self.excludedLetters = []   

    def playWord(self):
        """Grabs a random word from its local list of remaining possible words.
        Inelligible words are excluded in the feedback step after each round. 
        """
        self.choice = random.choice(self.possibilities)
        # Formatting for the console with nasty string concatenation
        log(str(self) + ": I've narrowed it down to " + 
            str(len(self.possibilities)) + " words..." + " " * 
            (5-len(str(len(self.possibilities)))) + " '" + self.choice + "'?")
        return self.choice

    def processFeedback(self, feedback):
        """Uses the feedback to expand its knowledge base, and then uses that
        base to pare down the possibility space. 
        """
        # Nasty string concatenation
        log("                Game:                                          " 
            + feedback)

        # Do three passes on the feedback, for... reasons (outlined below). 
        for i in range(5):
            # "G": Letters we know for sure are most absolute.
            if feedback[i] != 'G':
                continue
            if self.solvedLetters[i] == ".":
                # '.' is a sentinel for an unsolved letter. Don't solve a letter
                # twice
                self.solvedLetters[i] = self.choice[i]
                if self.choice[i] in self.includedLetters:
                    # If this was a letter that we were uncertain about in the
                    # "includedLetters" list, we aren't anymore, so we remove it
                    self.includedLetters.remove(self.choice[i])

        for i in range(5):
            # "Y": Letters we know are included.
            if feedback[i] != 'Y':
                continue
            if self.choice[i] not in self.includedLetters:
                # I'm hesitant to make this restriction... there are edge cases,
                # but I'm breaking my brain trying to deal with them.
                self.includedLetters.append(self.choice[i])

        for i in range(5):
            # "_": Letters we know are excluded.
            if feedback[i] != '_':
                continue
            # There are some edge cases where you can get a "_" for a letter 
            # that *is* in the word if another instance of the letter has been 
            # matched in another spot. (IE: Guessing SPEED on OTHER matches the
            # first 'E' as an exclusion (___G_), but we obviously can't put 'E' 
            # in the exclusion list!) So add it to the exclusions so long as 
            # it's not already in an inclusion list (which is coincidentally why
            # we made those the most up-to-date we could first). 
            notSolved = self.choice[i] not in self.solvedLetters
            notIn = self.choice[i] not in self.includedLetters
            notEx = self.choice[i] not in self.excludedLetters  # Also no dupes
            if notSolved and notIn and notEx:
                self.excludedLetters.append(self.choice[i])

        # So now that we have our knowledge base up to date, we can pare down
        # the results:
        todo = self.possibilities.copy()
        keep = []
        for testWord in todo:
            # Test every word in the list of possible words against the 
            # knowledge base. Start by assuming it passes, and then iterate over
            # the things we know to prove by contradiction. 
            test = True 
            for i in range(5):
                # If solved letters don't match the test word, the test fails. 
                test = test and self.solvedLetters[i] in [testWord[i], "."]
            for incl in self.includedLetters:
                # If the test word doesn't have a letter that's in the include 
                # list, the test fails. 
                test = test and testWord.find(incl) != -1
            for excl in self.excludedLetters:
                # ^Ditto, but opposite. 
                test = test and testWord.find(excl) == -1
            if test:
                keep.append(testWord)
        self.possibilities = keep
        if len(keep) == 0:
            raise Exception("AutoPlayer_MkII says there's no solution.")

    def __str__(self):
        return "AutoPlayer (Mark II)"

def wordleGameLoop(player, game):
    """ A Generic game loop that takes a player and game object and runs an 
    entire game of Wordle. It returns a boolean representing if the player won.
    """
    while not game.isOver():
        feedback = None
        while feedback == None:
            feedback = game.tryRound(player.playWord())
        player.processFeedback(feedback)
    return len(game.rounds) if game.isWon() else 0

def playWordle():
    """ Runs a game for a human player. Mostly just for funsies/testing that the
    game logic works :) 
    """
    # Instantiation
    loggingEnabled = True   # Humans need logging
    current = Game()
    player = HumanPlayer(current)
    print("Let's Play Wordle!")
    if wordleGameLoop(player, current):
        print("You won in " + str(len(current.rounds)) + "! :D")
    else:
        print("You lost... :(  The word was " + current.solution + "!")

def runSim(version):
    game = Game()
    player = AutoPlayer_MkI(game) if version == 1 else AutoPlayer_MkII(game) 
    print(str(player) + " got a score of " + str(wordleGameLoop(player, game)))
    print("The word was " + game.solution)


runSim(1)
runSim(2)
playWordle()
