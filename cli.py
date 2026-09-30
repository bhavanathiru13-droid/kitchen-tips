"""Terminal chat:  python cli.py"""
from bot import DomainBot


def main():
    bot = DomainBot()
    print(f"\n=== {bot.config['bot_name']} | {bot.config['domain_name']} ===")
    print(bot.config["greeting"])
    print("(type 'exit' to quit)\n")
    while True:
        try:
            q = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if q.lower() in {"exit", "quit", "bye"}:
            print("Bot: Goodbye!")
            break
        r = bot.ask(q); print("Bot:", r["answer"]); print("Tip:", r["tip"]) if r.get("tip") else None; print()


if __name__ == "__main__":
    main()
