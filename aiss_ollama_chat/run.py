import sys
import argparse
import os
import datetime
import json

from aiss_ollama_chat.chat import Chat



def main():
    parser = argparse.ArgumentParser(
        description='OpenAPI user-assistant chat app with tools support.',
        epilog='Example: ollama-tools-chat gemma3:12b-it-q8_0 sysPrompt.txt 20'
    )
    
    parser.add_argument('model', help='Model to use')
    parser.add_argument('sysPrompt', help='Plain text file with the system prompt')
    parser.add_argument('maxLength', type=int, help='Max context lenght')
    parser.add_argument('--maxLength', '-l', type=int, default=20,
                    help='Maximum context lenght (default: 20)')
    parser.add_argument('--prevContext', '-c', type=str, default=None,
                    help='Txt file path with previous chat context (default: None)')

    args = parser.parse_args()

    chat = Chat(args.model, args.sysPrompt, args.maxLength, args.prevContext)
    while True:
        prompt = input("You: ")
        if prompt in ["quit", "exit"]:
            print("Good bye!")
            break
        elif prompt.startswith("save"):
            if prompt.startswith("save:"):
                output = chat.serializeContext(prompt[len("save:"):].strip())
                if output: print(output)
            else:
                output = chat.serializeContext("./context.json")
                if output: print(output)
        elif prompt.startswith("restore"):
            if prompt.startswith("restore:"):
                output = chat.deserializeContext(prompt[len("restore:"):].strip())
                if output: print(output)
            else:
                output = chat.deserializeContext("./context.json")
                if output: print(output)
        else:
            print(f"\n{chat.model}: {chat.doChat(prompt)}\n")
    chat.makeBackup()
    return

if __name__ == "__main__":
    main()
