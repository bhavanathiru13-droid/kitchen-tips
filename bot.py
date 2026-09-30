"""Core engine: finds ONE matching entry and returns ONE simple definition."""
import json
import re
import difflib
from pathlib import Path

QUESTION_WORDS = re.compile(
    r"^(please\s+)?(can you\s+|could you\s+)?"
    r"(how\s+do\s+you|how\s+do\s+i|how\s+can\s+i|how\s+to|what\s+is|what\s+are|what's|whats|define|definition\s+of|explain|"
    r"meaning\s+of|what\s+does|tell\s+me\s+about|describe|who\s+is)\s+"
    r"(the\s+|a\s+|an\s+)?",
    re.I,
)
TRAILING = re.compile(r"\s+(mean|means|stand\s+for)$", re.I)
GREETINGS = {"hi", "hello", "hey", "hii", "good morning", "good evening", "good afternoon"}
THANKS = {"thanks", "thank you", "ok thanks", "thx"}
STOP = {
    "a", "an", "the", "is", "are", "of", "in", "on", "to", "and", "or", "for",
    "what", "how", "does", "do", "it", "that", "this", "with", "by", "as",
    "from", "be", "can", "me", "you", "about", "tell", "explain", "define",
}


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s\-+&]", " ", text)
    text = text.replace("-", " ")
    return re.sub(r"\s+", " ", text).strip()


def tokens(text: str) -> set:
    return {t for t in normalize(text).split() if t not in STOP and len(t) > 1}


class DomainBot:
    def __init__(self, base_dir=None):
        self.base = Path(base_dir) if base_dir else Path(__file__).parent
        self.config = json.loads((self.base / "config.json").read_text(encoding="utf-8"))
        self.entries = json.loads(
            (self.base / self.config["knowledge_file"]).read_text(encoding="utf-8")
        )
        self.index = {}
        for entry in self.entries:
            for phrase in [entry["term"]] + entry.get("aliases", []):
                self.index[normalize(phrase)] = entry

    # ---- helpers -------------------------------------------------------
    def _clean_query(self, query: str) -> str:
        q = query.strip().rstrip("?.! ")
        q = QUESTION_WORDS.sub("", q)
        q = TRAILING.sub("", q)
        return normalize(q)

    def _format(self, entry):
        return {"matched": True, "term": entry["term"], "answer": entry["definition"], "tip": entry.get("tip", "")}

    # ---- main API ------------------------------------------------------
    def ask(self, query: str) -> dict:
        if not query or not query.strip():
            return {"matched": False, "term": None, "tip": "", "answer": "Please type a term to define."}

        raw = normalize(query)
        if raw in GREETINGS:
            return {"matched": False, "term": None, "tip": "", "answer": self.config["greeting"]}
        if raw in THANKS:
            return {"matched": False, "term": None, "tip": "", "answer": "You're welcome! Ask me another term anytime."}

        cleaned = self._clean_query(query)

        # 1) exact term / alias
        if cleaned in self.index:
            return self._format(self.index[cleaned])

        # 2) a known term appears inside the sentence (longest wins)
        padded = f" {normalize(query)} "
        hits = [k for k in self.index if f" {k} " in padded]
        if hits:
            return self._format(self.index[max(hits, key=len)])

        # 3) fuzzy match for typos
        close = difflib.get_close_matches(
            cleaned, list(self.index), n=1, cutoff=self.config["fuzzy_cutoff"]
        )
        if close:
            return self._format(self.index[close[0]])

        # 4) keyword overlap with definitions
        q_tokens = tokens(query)
        best, best_score = None, 0.0
        if q_tokens:
            for entry in self.entries:
                pool = tokens(entry["term"]) | tokens(entry["definition"])
                score = len(q_tokens & pool) / len(q_tokens)
                if score > best_score:
                    best, best_score = entry, score
        if best and best_score >= self.config["keyword_min_score"]:
            return self._format(best)

        return {"matched": False, "term": None, "tip": "", "answer": self.config["fallback"]}


if __name__ == "__main__":
    bot = DomainBot()
    print(bot.ask("what is overfiting?")["answer"])
