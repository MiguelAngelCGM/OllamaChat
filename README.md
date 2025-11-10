# Ollama Chat - Chatbot with Ollama

Very simple chatbot with context memory that uses Ollama models for conversations.

## 📋 Description

Allows to interact with local language models using Ollama. Conversation history is automatically saved to a JSON file when using run.py.

## 🚀 Features

- Real-time interaction with local models
- Conversation history saved in JSON format
- Support for multiple Ollama models
- Exit commands (`quit` or `exit`)

## 🛠 Requirements

- Python 3.7+
- Ollama installed and running
- Required packages:
  - `ollama`

## 📦 Installation - A) Download and run via run.py

1. Clone the repository:
   ```bash
   git clone <your-repository>
   cd ollamaChat
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install ollama
   ```

## 📦 Installation - B) Download and run via package install

1. Clone the repository:
   ```bash
   git clone <your-repository>
   cd ollamaChat
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install ollama
   ```

4. Install package using:
   ```bash
   pip install .
   ```

## ▶️ Usage - A

Run the program with:
```bash
./run.sh <model> <prompt_file> <max_length>
```

Example:
```bash
./run.sh gemma3:12b-it-q8_0 prompt.txt 20
```

## ▶️ Usage - B

Run the program with:
```bash
./ollama-chat <model> <prompt_file> <max_length>
```

Example:
```bash
./ollama-chat gemma3:12b-it-q8_0 prompt.txt 20
```


## 📁 Project Structure

```
.
├── chat.py          # Main chat class
├── run.py           # Main execution script
├── run.sh           # Execution script
├── prompt.txt       # System prompt file
└── README.md        # This file
```

## 📄 Output

Conversation history is saved in a timestamped folder:
```
2025-11-09_21-00-00/
└── chat.log
```

The file contains the conversation history in JSON format.

## 🤝 Contributions

Contributions are welcome! Please open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License.
