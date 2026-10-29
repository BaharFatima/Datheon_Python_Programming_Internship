#!/usr/bin/env python3
"""Hangman - a console word-guessing game.

Features
--------
* Secret word chosen with random.choice() from words.txt (built-in fallback list).
* Masked word display, e.g. "_ A _ H O N".
* 6 allowed mistakes with ASCII gallows art that updates on each wrong guess.
* Previously guessed letters are tracked in sets; repeats never cost an attempt.
* Clean victory / defeat screens and a play-again prompt.
"""
import random
from pathlib import Path

MAX_MISTAKES = 6
WORDS_FILE = Path(__file__).with_name("words.txt")
FALLBACK_WORDS = ["python", "hangman", "developer", "algorithm", "internship"]

STAGES = [
    r"""
      +---+
      |   |
          |
          |
          |
          |
    =========""",
    r"""
      +---+
      |   |
      O   |
          |
          |
          |
    =========""",
    r"""
      +---+
      |   |
      O   |
      |   |
          |
          |
    =========""",
    r"""
      +---+
      |   |
      O   |
     /|   |
          |
          |
    =========""",
    r"""
      +---+
      |   |
      O   |
     /|\  |
          |
          |
    =========""",
    r"""
      +---+
      |   |
      O   |
     /|\  |
     /    |
          |
    =========""",
    r"""
      +---+
      |   |
      O   |
     /|\  |
     / \  |
          |
    =========""",
]


def load_words(path: Path = WORDS_FILE) -> list[str]:
    """Load alphabetic words (>= 3 letters) from a text file, or fall back."""
    try:
        words = [w.strip().lower() for w in path.read_text().splitlines()]
        words = [w for w in words if w.isalpha() and len(w) >= 3]
        return words or FALLBACK_WORDS
    except OSError:
        return FALLBACK_WORDS


def mask_word(word: str, correct: set[str]) -> str:
    """Return the word with unguessed letters replaced by underscores."""
    return " ".join(ch.upper() if ch in correct else "_" for ch in word)


def is_won(word: str, correct: set[str]) -> bool:
    return all(ch in correct for ch in word)


def read_guess(correct: set[str], wrong: set[str]) -> str:
    """Prompt until the user enters a valid, not-yet-guessed single letter."""
    while True:
        guess = input("Guess a letter: ").strip().lower()
        if len(guess) != 1 or not guess.isalpha():
            print("  Please enter exactly one letter (a-z).")
        elif guess in correct or guess in wrong:
            print(f"  You already guessed '{guess}'. Try another letter.")
        else:
            return guess


def play_round(word: str) -> bool:
    """Play one round. Returns True if the player wins."""
    correct: set[str] = set()
    wrong: set[str] = set()

    while len(wrong) < MAX_MISTAKES and not is_won(word, correct):
        print(STAGES[len(wrong)])
        print(f"\n  Word:   {mask_word(word, correct)}")
        print(f"  Wrong:  {' '.join(sorted(wrong)) or '-'}")
        print(f"  Lives:  {MAX_MISTAKES - len(wrong)}\n")

        guess = read_guess(correct, wrong)
        if guess in word:
            correct.add(guess)
            print(f"  Good guess! '{guess}' is in the word.")
        else:
            wrong.add(guess)
            print(f"  Sorry, '{guess}' is not in the word.")

    won = is_won(word, correct)
    print(STAGES[len(wrong)])
    if won:
        print(f"\n  *** VICTORY! You guessed it: {word.upper()} ***")
    else:
        print(f"\n  *** GAME OVER. The word was: {word.upper()} ***")
    return won


def main() -> None:
    print("=" * 40)
    print("        H A N G M A N")
    print("=" * 40)
    words = load_words()
    wins = games = 0
    while True:
        games += 1
        wins += play_round(random.choice(words))
        print(f"\n  Score: {wins} win(s) in {games} game(s)")
        if input("\nPlay again? (y/n): ").strip().lower() not in ("y", "yes"):
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
