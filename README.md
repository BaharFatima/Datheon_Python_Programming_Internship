# Python Internship Projects

Four hands-on, industry-style Python projects built with the standard library, each with clean modular code, input validation and error handling.

| # | Project | Entry point | Key skills |
|---|---------|-------------|-----------|
| 1 | Hangman Word Guessing Game | `task1_hangman/hangman.py` | strings, sets, `random`, control flow |
| 2 | Stock Portfolio Performance Tracker | `task2_portfolio/portfolio.py` | dicts, `csv`, file I/O, optional `yfinance` |
| 3 | File Organizer & Cleanup Utility | `task3_file_organizer/organizer.py` | `os`, `shutil`, `pathlib`, `logging`, exceptions |
| 4 | Rule-Based Terminal Chatbot | `task4_chatbot/chatbot.py` | `re`, `json`, state management |

## Folder structure
```
python-internship-projects/
├── README.md
├── requirements.txt
├── .gitignore
├── task1_hangman/
│   ├── hangman.py
│   ├── words.txt
│   └── README.md
├── task2_portfolio/
│   ├── portfolio.py
│   ├── data/
│   │   ├── sp500_sample_prices.csv
│   │   └── sample_holdings.csv
│   └── README.md
├── task3_file_organizer/
│   ├── organizer.py
│   └── README.md
├── task4_chatbot/
│   ├── chatbot.py
│   ├── data/faq.json
│   └── README.md
└── tests/
    └── test_projects.py
```

## Requirements
Python 3.10+. No installs needed (only `pip install yfinance` if you want live prices in Task 2).

## Quick start
```bash
python task1_hangman/hangman.py
python task2_portfolio/portfolio.py --demo
python task3_file_organizer/organizer.py ~/Downloads --dry-run
python task4_chatbot/chatbot.py
```

## Run the tests
```bash
python -m unittest discover -s tests -v
```

## Notes
- Task 2 prices in `sp500_sample_prices.csv` are illustrative sample values; use `--live` for real market data.
- Task 3 always supports `--dry-run`; try it before organizing a real folder.
