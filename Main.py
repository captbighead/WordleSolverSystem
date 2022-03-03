from WordleGame import WordleGame
from WordlePlayer import WordlePlayer
from WordlePlayerII import WordlePlayerII

loggingEnabled = False

def log(message):
    if loggingEnabled:
        print(message)

def simulation(game, player, iterations):
    print("SIMULATION START")
    wins = 0
    agg_score = 0
    for i in range(iterations):

        # Show a progress bar if we're not tracking each trial through logging.
        if not loggingEnabled:
            if i == 0:
                print("-" * 19)
            if i % (iterations/10) == 0:
                print("X ", flush=True, end = "")

        log("Trial " + str(i+1))
        result = playGame(game, player)
        game.reset()
        player.reset()
        wins += 1 if result else 0
        agg_score += result

    if not loggingEnabled:
        print()
        print("-" * 19)
    print("\nSIMULATION RESULTS\n")
    print("        Total Wins: " + str(wins))
    print("      Win Rate (%): " + str(round(wins/float(iterations)*100.0, 2)))
    print("        Avg. Score: " + str(round(agg_score/float(iterations), 2)))
    print("Avg. Score of Wins: " + str(round(agg_score/float(wins), 2)))
    print("\nSIMULATION COMPLETE\n")

def playGame(game, player):
    log("Game Start")
    log("----------")
    log("")
    for i in range(6):
        word = player.playWord()
        feedback = game.evalWord(word)
        log("P: " + word)
        log("G: " + feedback)
        if feedback == "G" * len(word):
            break   # If we've won, kill the loop early
        player.takeFeedback(feedback)
        log("P: That narrows it down to " + str(len(player.pSpace)) + " words")

    # Final log with results (if we're doing logging. 
    if loggingEnabled and feedback == "G" * len(word):
        log("Victory! " + str(6-i) + " Points")
    elif loggingEnabled:
        log("Defeat! 0 Points")

    return 6-i if feedback == "G" * len(word) else 0

game = WordleGame()
player = WordlePlayer(game.dict_words)
playerII = WordlePlayerII(game.soln_words)

loggingEnabled = True
#simulation(game, player, 10000)
simulation(game, playerII, 1000)
