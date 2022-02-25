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
        """Initializes a game by running it's reset() function. 
        """
        self.reset(soln)

    def reset(self, soln=None):
        """Prepares for a new game by choosing a solution word and overwriting 
        its list to store round information. If a solution word is provided, 
        that is the solution, otherwise it picks randomly from the legal 
        solutions list.
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

    def checkWordIsLegal(self, word, player):
        """Check that the word is a legal guess in Wordle (a five letter word in
        the game's dictionary).

        This is only necessary if the Player Class can input something that 
        isn't in the word list; if they're a Human, for instance. The logic can
        be revisited if classes are ever created that can guess illegal words, 
        but for now if the player is not an instance of the HumanPlayer class
        we can short circuit this check, as I'm sure it's not helping 
        performance.  
        """
        if isinstance(player, HumanPlayer):
            return word in self.words
        else:
            return True

    def tryRound(self, word, player):
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
        expected to process that and try again. The method takes the player 
        trying to play the word in as an argument, so that the nested methods
        can check if they're a human. Otherwise the 'legal' check just short 
        circuits, because robots are infallible. 
        """
        if self.checkWordIsLegal(word, player) and not self.isOver():
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

    def reset(self, game):
        """Updates the player object with a reference to the game object so that
        it may play another game. 
        """
        self.game = game

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

    def reset(self, game):
        """Technically, reset() for the MK I updates the internal reference to 
        the game being played, but since the Mk I doesn't concern itself with 
        trivial things like "feedback" or "competence", it never really uses it
        anyways. It just has one because its brothers do. 
        """
        self.game = game

    def __str__(self):
        return "AutoPlayer (Mark I)"

class AutoPlayer_MkII:
    """Player control logic for a computer that uses the feedback to narrow down
    its random guesses. 
    """
    def __init__(self, game):
        """Initialization runs the reset() function on the initial game. 
        """
        self.reset(game) 

    def reset(self, game):
        """Sets up the player to play a new game of Wordle, by dumping it's 
        knowledge base from the previous game, resetting the list of possible 
        words and updating it's internal references to the new game. This means 
        it assumes that the game object passed is the new game, which has not 
        had any rounds played on it yet.
        """
        # Initialize references to the game being played. 
        self.game = game

        # Choosing the appropriate one of the next two lines is a bit of a 
        # matter of prefrerence. In truth, the results are probably more 
        # realistic if you use only the words from the solution list, because 
        # most of the words not in that list are bizarre and not choices a human
        # would make. 
        #
        # On the other hand, it kind of feels like cheating! It's so small that
        # performance goes way up as the possibilities it needs to weed out go
        # way down, and every guess it makes is the solution to *some* puzzle. 
        #
        # But it's also *much* faster...
        #
        # Whichever line is uncommented is based on the mood I'm in :) 
        #self.possibilities = self.game.words.copy()
        self.possibilities = self.game.soln_words.copy()

        # Set up the knowledge base of letters in the final answer that we're 
        # certain about the position of, letters in the answer we're uncertain
        # of the position of, and letters we're certain aren't in the answer
        self.solvedLetters = [".", ".", ".", ".", "."]  # Sentinels to hold posn
        self.includedLetters = []   
        self.excludedLetters = []  
        self.targetedExclusions = []    # (Letter, index) tuples we know are 
                                        # wrong

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
            if (self.choice[i], i) not in self.targetedExclusions:
                # We know it's included, but not at *this* index. That narrows 
                # the search
                self.targetedExclusions.append((self.choice[i], i))

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
            i = 0
            while test and i < 5:
                # If solved letters don't match the test word, the test fails. 
                test = test and self.solvedLetters[i] in [testWord[i], "."]
                i += 1
            i = 0
            while test and i < len(self.includedLetters):
                # If the test word doesn't have a letter that's in the include 
                # list, the test fails. 
                incl = self.includedLetters[i]
                test = test and testWord.find(incl) != -1
                i += 1
            i = 0
            while test and i < len(self.excludedLetters):
                # ^Ditto, but opposite. 
                excl = self.excludedLetters[i]
                test = test and testWord.find(excl) == -1
                i += 1
            i = 0
            while test and i < len(self.targetedExclusions):
                # Lastly, while it may have the letter from the include list, if
                # the letter's in a spot we know is wrong, we can eliminate it
                tup = self.targetedExclusions[i]
                if testWord.find(tup[0]) == tup[1]:
                    test = False
                i += 1
            if test:
                keep.append(testWord)
        self.possibilities = keep
        if len(keep) == 0:
            raise Exception("AutoPlayer_MkII says there's no solution.")

    def __str__(self):
        return "AutoPlayer (Mark II)"

class AutoPlayer_MkIII(AutoPlayer_MkII):
    """A small improvement (hopefully!) on Mk II, Mk III operates identicaly 
    except that it uses its first two rounds to play two fixed 'starter' words 
    that I personally use when I play the game recreationally: 'TENIA' and 
    'YOURS'. I use those words because they incorporate all vowels (including
    'Y') and a few of the most common consonants in the english language. 
    """
    def playWord(self):
        if len(self.game.rounds) == 0:
            self.choice = "tenia"
            return self.choice
        elif len(self.game.rounds) == 1:
            self.choice = "yours"
            return self.choice
        else:
            return super().playWord()

def wordleGameLoop(player, game):
    """ A Generic game loop that takes a player and game object and runs an 
    entire game of Wordle. It returns a score from 6 to 0, where 6 is a game 
    they won on the first try, and 0 is a game they didn't win. 
    """
    while not game.isOver():
        feedback = None
        while feedback == None:
            feedback = game.tryRound(player.playWord(), player)
        player.processFeedback(feedback)
    return 7-len(game.rounds) if game.isWon() else 0

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

def runSimulation(iterations):
    """ For all AutoPlayer generations in the file, it runs them through a 
    number of games specified as the iterations argument, tracking their 
    performance and outputting statistics to the console at the end. 
    """
    game = Game()
    print()
    print(" WORDLE SOLVER SIMULATION")
    print(" ------------------------")
    print()
    print(" Each solver plays " + str(iterations) + " games with randomly chose"
         + "n words from the list of possible Worlde solutions (of which there "
         + "are " + str(len(game.soln_words)) + ")")
    print(" Scores range from 0 to 6, based on how many guesses they had remain"
         + "ing before they made their winning guess. IE: 6 means they got it o"
         + "n the first try, 1 means they got it on the last guess, and 0 means"
         + " they didn't get it.)")
    print()

    # Progress bars... those are a cool trick!
    progressChunk = int(iterations/10)
    
    for i in [1,2,3]:
    #for i in [3]:
        if i == 1:
            player = AutoPlayer_MkI(game) 
        elif i == 2:
            player = AutoPlayer_MkII(game) 
        else:
            player = AutoPlayer_MkIII(game)
        print(" Testing the Mk. " + str(i) + ": ")
        print(" ---------------------------")
        print(" PROG.: ", end="", flush=True)
        total_wins = 0
        best_score = 0
        avg_score = 0.0
        for j in range(iterations):

            # Progress update:
            if j % progressChunk == progressChunk - 1:
                print(" X", end="", flush=True)


            score = wordleGameLoop(player, game)
            game.reset()
            player.reset(game)
            total_wins += 1 if score > 0 else 0
            if score > 0:
                best_score = score if score > best_score else best_score
            avg_score += float(score)
        print()
        avg_of_wins = round(avg_score / total_wins,2) if total_wins > 0 else 0.0
        avg_score /= float(iterations)
        winrate = round(float(total_wins)/float(iterations)*100, 2)
        print("         Total Wins: " + str(total_wins))
        print("       Win Rate (%): " + str(winrate) + "%")
        print("         Best Score: " + str(best_score))
        print("         Avg. Score: " + str(round(avg_score,2)))
        print(" Avg. Score of Wins: " + str(avg_of_wins))
        print()

runSimulation(100)
#playWordle()


