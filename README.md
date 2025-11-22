# Ollama Chat - Chatbot with Ollama

Simple chatbot with context memory that uses Ollama models for conversations.

## 📋 Description

Allows to interact with local language models using Ollama. Conversation history is automatically saved to a JSON file when using run.py. Can resume previous conversations via serialization/deserialization.

## 🚀 Features

- Real-time interaction with local models
- Conversation history saved in JSON format
- Support for multiple Ollama models
- Exit commands (`quit` or `exit`)
  - When used, the app makes a backup at "./logs/date_time" located at run path.
- Text commands (`save`, `save:`, `restore`, `restore:`, `rewind` and `rewind:`)
  - `save` - Stores a conversational context file named "context.json" at run path.
  - `save:` - Stores a conversational context file at path inidicated next, related to run path.
  - `restore` - Restores a conversational context file at "context.json" located at run path.
  - `restore:` - Restores a conversational context file at path inidicated next, related to run path.
  - `rewind` - Goes back to a previous turn.
  - `rewind:` - Goes back an ammount of turns indicated next.
- Commands are avaliable at function chat.py -> chat(prompt). Please use doChat(prompt) if you don't need commands.
- Flow control keyboard commands:
  - `3x Cntrl+C` - Forces App exit.
- Clipboard commands:
  - `@@` - It will be replaced with clipboard's contents.

## 🛠 Requirements

- Python 3.7+
- Ollama installed and running
- Required packages:
  - `ollama`
- (Linux) 'pyperclip' clipboard support requires:
  - `xclip` for X11
  - `wl-clipboard` for Wayland (not tested)
  - `cliphist` for Wayland (not tested)

## 📦 Installation

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Clone the repository:
   ```bash
   git clone <your-repository>
   ```

3. Install package using:
   ```bash
   pip install ./OllamaChat
   ```

## Optional

pyperclip requires 

## ▶️ Usage

Run the program with:
```bash
./ollama-chat <model> <prompt_file> <max_length> [options]
```

Where options are:
--maxLength or -l: Maximum context length (default: 20)
--userName or -u: User name (default: "User")  
--prevContext or -c: Path to previous chat context file (default: None) 

Example:
```bash
./ollama-chat gemma3:12b-it-q8_0 prompt.txt -l 20 -u Me -c context.json
```

## 📁 Project Structure

```
.
├── aiss_ollama_tools_chat/
│   ├── __init__.py
│   ├── chat.py
│   └── run.py
├── _ai.txt
├── run.sh
├── setup.py
├── LICENSE
└── README.md
```

## 📄 Output

Conversation data is saved in a timestamped folder:
```
.
└── logs/
    └── 2025-11-09_21-00-00/
        ├── chat.json
        └── params.log
```

- chat.json: the conversation history in JSON format.
- params.log: model data, system prompt, etc.

## 🤝 Contributions

Contributions are welcome! Please open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License.
