# Task 1 - Hangman (Console)

Interactive terminal Hangman with ASCII gallows art.

## Run
```bash
python hangman.py
```

## How it works
- `random.choice()` picks a secret word from `words.txt` (edit this file to add your own words).
- Correct and wrong guesses are stored in **sets**, so duplicate guesses never cost a life.
- 6 mistakes allowed; the gallows art advances after every wrong guess.
- Input validation rejects numbers, symbols and multi-character entries.
