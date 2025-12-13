import signal
import sys
import argparse
import os
import datetime
import json

from aiss_ollama_chat.chat import Chat
from aiss_ollama_chat.fileIO import FileIO

FORCE_EXIT:int = 3
CHAT:Chat

class OllamaChat:
    def __init__(self):

        return

    def run(self):

        return
    

def main():
    def signalHandler(sig, frame):
        global FORCE_EXIT
        if FORCE_EXIT == 0:
            global CHAT
            print("\n--FORCE EXIT--")
            FileIO.serializeDict("./context.json.back", CHAT.chatHistory)
            sys.exit(0)
        else:
            print(f"\n--FORCE EXIT IN {FORCE_EXIT}--")
            FORCE_EXIT -= 1
        return
    
    signal.signal(signal.SIGINT, signalHandler)

    parser = argparse.ArgumentParser(
        description='OpenAPI user-assistant chat app.',
        epilog='Example: ollama-chat gemma3:12b-it-q8_0 sysPrompt.txt 20'
    )
    
    parser.add_argument('model', help='Model to use')
    parser.add_argument('sysPrompt', help='Plain text file with the system prompt')
    parser.add_argument('--maxLength', '-l', type=int, default=20,
                    help='Maximum context lenght (default: 20)')
    parser.add_argument('--userName', '-u', type=str, default="user",
                    help='User name (default: "user")')
    parser.add_argument('--assistantName', '-g', type=str, default=None,
                    help='Assistant name (for agentic purpouses) (default: "model_name")')
    parser.add_argument('--prevContext', '-c', type=str, default=None,
                    help='Txt file path with previous chat context (default: None)')
    parser.add_argument('--addDateTimeToPrompt', '-t', type=str, default="False",
                    help='Experimental feature. Add date and time to prompt, so the AI assistant can tell what time it is (default: False)')
    parser.add_argument('--sysPromptDropTurn', '-d', type=int, default=None,
                    help='Experimental feature. Add a turn count number where the model drops its system prompt (default: None)')

    args = parser.parse_args()
    if args.addDateTimeToPrompt == "True":
        v1 = True
    else:
        v1 = False

    global CHAT
    CHAT = Chat(args.model, args.sysPrompt, args.maxLength, args.userName, args.assistantName, args.prevContext, v1, args.sysPromptDropTurn)
    backupFolderSuffix = ""
    while True:
        global FORCE_EXIT
        FORCE_EXIT = 3
        prompt = input(f"{CHAT.userName}: ")
        try:
            if prompt.endswith("RETRY"):
                continue
            if prompt.startswith("exit"):
                if prompt.startswith("exit:"):
                    backupFolderSuffix = prompt[len("exit:"):].strip() # TODO: Set max num characters
                    print("Good bye!")
                    break
                else:
                    print("Good bye!")
                    break
            prompt = CHAT.chat(prompt)
            print(f"\n\n{prompt}")
        except Exception as e:
            print(f"{e}\n")
    CHAT.makeBackup(None, backupFolderSuffix)
    return

if __name__ == "__main__":
    main()
