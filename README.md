# Kitchen Tips Bot - Kitchen Tips Chatbot
Gives one short, simple answer (plus a small tip) for kitchen tips questions.

## Run (Python 3.8+, no installs)
    python app.py     # open http://localhost:8003
    python cli.py     # or chat in the terminal

## Customize
- `config.json`  : bot name, greeting, quick-question buttons, port
- `data/knowledge.json` : add or edit entries (term, aliases, definition, tip)
- `python add_term.py` : add an entry from the terminal
- `web/index.html` : change colours and layout
