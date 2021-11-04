from mtg import *
from prices import *
from categorize import *
from replacements import *


def main() -> None:
    possibleWords = ['aardvark', 'queueing']
    currentWord = ""
    guessesRemaining = 10
    currentGuess = ""
    guessedCorrectly = ""
    guessed = ""
    toDisplay = ""
    for currentWord in possibleWords:
        print(f"The length of the word is {len(currentWord)}.")
        toDisplay = list("_"*len(currentWord))
        print(len(toDisplay))
        while guessesRemaining > 0 or guessedCorrectly.lower() != currentWord.lower():
            print(f"You have {guessesRemaining} guesses remaining for this word.")
            print(f"You have guessed {','.join(list(guessed))}")
            print(''.join(toDisplay))
            #this ensures that if they accidentally enter multiple letters that it only takes the first one.
            currentGuess = input("Enter a letter: ")
            currentGuess = currentGuess[0] if currentGuess else ""
            #strings are basically already lists of characters, and can be indexed like lists.
            if (currentGuess in currentWord) and currentGuess != "":
                print(f"Correct! Hell yeah! Fucking excellent my dude! So proud of you!")
                guessed += currentGuess
                guessedCorrectly += currentGuess
                for x in range(len(currentWord)):
                    print(x)
                    if currentWord[x] == currentGuess:
                        toDisplay[x] = currentGuess
            elif currentGuess in guessed:
                print(f"{currentGuess} has already been guessed, try again!")
            else:
                print(f"Nope, that wasn't quite right. Try again!")
                guessed += currentGuess

        guessed = ""
        guessedCorrectly = ""

if __name__ == "__main__":
    main()
