#!/usr/bin/env python3
"""Rule-Based Interactive Terminal Assistant (Chatbot).

* Intents loaded from data/faq.json (greetings + FAQs with optional keywords).
* Input normalised (lowercase, whitespace stripped, regex tokenisation).
* Keyword / regex matching with a confidence score; multi-intent messages
  ("what are your hours and when do I get my certificate?") get every answer.
* Conversation state: GREETING -> LISTENING -> RESOLVED -> EXIT.
* Graceful fallback for low-confidence queries; exit with bye / exit / quit.
"""
import json
import re
import sys
from pathlib import Path

FAQ_FILE = Path(__file__).parent / "data" / "faq.json"
EXIT_WORDS = {"bye", "exit", "quit", "goodbye"}
THANKS_RE = re.compile(r"\b(thanks?|thank you|thx|cheers)\b")
HELP_RE = re.compile(r"\b(help|what can you do|options|menu)\b")
STOPWORDS = {
    "a", "an", "the", "is", "are", "am", "do", "does", "did", "i", "my", "me", "you",
    "your", "we", "our", "how", "what", "when", "where", "will", "can", "to", "of",
    "for", "and", "or", "in", "on", "it", "this", "that", "please", "tell", "about",
}
MIN_CONFIDENCE = 0.34

GREETING, LISTENING, RESOLVED = "GREETING", "LISTENING", "RESOLVED"


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def tokenize(text: str) -> set[str]:
    """Lowercase word tokens, stopwords removed, trailing plural 's' stripped."""
    words = re.findall(r"[a-z0-9']+", text.lower())
    return {w.rstrip("s") if len(w) > 3 else w for w in words if w not in STOPWORDS}


class Chatbot:
    def __init__(self, faq_path: Path = FAQ_FILE):
        data = json.loads(Path(faq_path).read_text(encoding="utf-8"))
        self.greetings = [normalize(g) for g in data.get("greetings", [])]
        self.faqs = []
        for item in data.get("faqs", []):
            keys = tokenize(item["question"]) | tokenize(" ".join(item.get("keywords", [])))
            self.faqs.append({"question": item["question"],
                              "answer": item["answer"], "keys": keys})
        self.state = GREETING

    # ----- intent detection -----
    def is_exit(self, text: str) -> bool:
        return normalize(text) in EXIT_WORDS or bool(
            re.fullmatch(r"(ok(ay)? )?(bye|goodbye|quit|exit)( now)?", normalize(text)))

    def is_greeting(self, text: str) -> bool:
        t = normalize(text)
        return any(re.search(rf"\b{re.escape(g)}\b", t) for g in self.greetings)

    def match_faqs(self, text: str) -> list[dict]:
        """Return FAQs whose keyword overlap meets the confidence threshold."""
        tokens = tokenize(text)
        scored = []
        for faq in self.faqs:
            overlap = len(tokens & faq["keys"])
            if overlap:
                score = overlap / min(len(faq["keys"]), max(len(tokens), 1))
                if score >= MIN_CONFIDENCE:
                    scored.append((score, faq))
        return [f for _, f in sorted(scored, key=lambda s: -s[0])]

    # ----- response -----
    def respond(self, text: str) -> str:
        if not normalize(text):
            return "I didn't catch that - could you type your question?"
        if self.is_exit(text):
            return "Goodbye! Have a great day."

        parts = []
        if self.is_greeting(text):
            parts.append("Hello! How can I help you today?")
        matches = self.match_faqs(text)
        parts.extend(f["answer"] for f in matches)
        if THANKS_RE.search(normalize(text)):
            parts.append("You're welcome!")
        if HELP_RE.search(normalize(text)) and not matches:
            parts.append(self.help_text())

        if not parts:
            self.state = LISTENING
            return ("Sorry, I'm not sure I understood. " + self.help_text())

        self.state = RESOLVED if matches else LISTENING
        reply = "\n".join(parts)
        if self.state == RESOLVED:
            reply += "\nIs there anything else I can help with?"
        return reply

    def help_text(self) -> str:
        topics = "\n".join(f"  - {f['question']}" for f in self.faqs)
        return f"You can ask me things like:\n{topics}\nType 'bye' to exit."

    # ----- main loop -----
    def run(self) -> None:
        print("=" * 50)
        print(" Support Assistant  (type 'bye', 'exit' or 'quit' to leave)")
        print("=" * 50)
        print("Bot: Hi there! Ask me about hours, project submission or certificates.")
        self.state = LISTENING
        while True:
            try:
                text = input("\nYou: ")
            except (EOFError, KeyboardInterrupt):
                print("\nBot: Goodbye!")
                break
            reply = self.respond(text)
            print(f"Bot: {reply}")
            if self.is_exit(text):
                break


def main() -> int:
    try:
        Chatbot().run()
    except FileNotFoundError:
        print(f"Could not find FAQ file: {FAQ_FILE}")
        return 1
    except json.JSONDecodeError as e:
        print(f"FAQ file is not valid JSON: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
