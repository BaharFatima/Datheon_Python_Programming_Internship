# Task 4 - Rule-Based Terminal Chatbot

## Run
```bash
python chatbot.py
```

## Try
```
You: hi
You: what are your hours?
You: how do I submit my project and when will I get my certificate?
You: what's the weather?     -> graceful fallback
You: bye
```

## Design
- `data/faq.json` holds greetings and FAQs (add entries + optional `keywords` - no code changes needed).
- Input is lower-cased, whitespace-normalised and tokenised with `re`; stopwords are dropped.
- Each FAQ gets a confidence score; every FAQ above the threshold is answered (multi-intent).
- States: GREETING -> LISTENING -> RESOLVED -> exit. Low confidence triggers a helpful fallback.
