import os
import time
import ollama
import datetime
import re
import pyperclip
from typing import List

from aiss_ollama_chat.fileIO import FileIO

class Chat:
    @staticmethod
    def addClipBoardIfNeeded(text):
        index = text.find('@@')
        if index < 0:
            return text
        clipBoard = repr(pyperclip.paste())[1:-1]
        out = f"{text[:index]}\n```\n{clipBoard}\n```\n{text[index + len('@@'):]}"
        return out
    
    def strMsg(self, event_type:str, content:str, turn:int=None) -> dict[str, str]:
        dateTime = datetime.datetime.now().isoformat()
        dict = {
            'role': event_type,
            'content': f"{dateTime}\n{content}" if self.addDateTimeToPrompt else content
        }
        if self.addTurnToOllamaDict and turn:
            dict['turn'] = turn
        if self.addTimestampToOllamaDict:
            dict['timestamp'] = dateTime
        return dict
    
    def strSys(self, sysPrompt=None) -> dict[str, str]:
        return {"role": "system", "content": sysPrompt if sysPrompt else self.sysPrompt}

    def __init__(self, model:str, sysPrompt:str, maxChatLength:int=20, userName:str="user", assistantName:str="assistant", prevContext:str=None, addTimestampToOllamaDict:bool=False, addTurnToOllamaDict:bool=False, addDateTimeToPrompt:bool=False, sysPromptDropTurn:int=None):
        self.model:str = model
        self.sysPrompt:str = ""
        if sysPrompt.endswith(".txt"):
            try:
                with open(sysPrompt, "r") as archivo:
                    self.sysPrompt = archivo.read()
            except Exception as e:
                print(e)
        else:
            self.sysPrompt = sysPrompt
        self.maxChatLength:int = maxChatLength
        self.userName:str = userName
        self.assistantName:str = assistantName
        if prevContext:
            try:
                self.chatHistory = FileIO.deserializeDict(prevContext)
            except Exception as e:
                print(e)
        self.addTimestampToOllamaDict:bool = addTimestampToOllamaDict
        self.addTurnToOllamaDict:bool = addTurnToOllamaDict
        self.addDateTimeToPrompt:bool = addDateTimeToPrompt
        self.sysPromptDropTurn:int = sysPromptDropTurn
        self.chatHistory:dict[str, str] = []
        self.chatOperations = {
            "save": self._handleSave,
            "restore": self._handleRestore,
            "rewind": self._handleRewind,
            "print": self._handlePrint
        }
        
    def doChat(self, prompt:str) -> str:
        turn = self.getLastContextTurn()+1 if self.addTurnToOllamaDict else None
        self.chatHistory.append(self.strMsg("user", prompt, turn))
        if self.sysPromptDropTurn:
            response = ollama.chat(self.model, messages=[self.strSys(self.strSys(self.sysPrompt) if turn > self.sysPromptDropTurn else "...")] + self.chatHistory[-self.maxChatLength:])
        else:
            response = ollama.chat(self.model, messages=[self.strSys(self.sysPrompt)] + self.chatHistory[-self.maxChatLength:])
        msg = response['message'].content
        self.chatHistory.append(self.strMsg("assistant", msg, turn))
        return msg
    
    def chat(self, prompt: str) -> str:
        try:
            for operation, handler in self.chatOperations.items():
                if prompt.startswith(operation):
                    return handler(prompt)
            return f"{self.assistantName}: {self.doChat(Chat.addClipBoardIfNeeded(prompt))}\n\n"
        except Exception as e:
            raise Exception(f"{e}\\n")
        return

    def _handleSave(self, prompt: str) -> str:
        if prompt.startswith("save:"):
            path = prompt[len("save:"):].strip()
            FileIO.serializeDict(path, self.chatHistory)
            return f"-- serialized to {path} --\n\n"
        else:
            FileIO.serializeDict("./context.json", self.chatHistory)
            return "-- serialized to ./context.json --\n\n"

    def _handleRestore(self, prompt: str) -> str:
        if prompt.startswith("restore:"):
            path = prompt[len("restore:"):].strip()
            self.chatHistory = FileIO.deserializeDict(path)
            return f"-- restored from {path} --\n\n"
        else:
            self.chatHistory = FileIO.deserializeDict("./context.json")
            return "-- restored from ./context.json --\n\n"

    def _handleRewind(self, prompt: str) -> str:
        if prompt.startswith("rewind:"):
            amount = int(prompt[len("rewind:"):].strip())
            self.rewind(amount)
            return f"-- rewind: {amount} --\n\n"
        else:
            self.rewind()
            return "-- rewind: 1 --\n\n"
        
    def _handlePrint(self, prompt:str) -> str:
        if prompt.startswith("print:"):
            prompt = prompt[len("print:"):].strip()
            if prompt.startswith("system"):
                return f"-- System prompt: {self.sysPrompt}\n\n"
            elif prompt.startswith("chat"):
                return f"-- Chat History --\n{self.getChatHistoryFormatted()}\n-- Chat History End --\n\n"
        else:
            return f"-- System prompt: {self.sysPrompt}--\n\n"
    
    def rewind(self, turns=1) -> str:
        if turns < 0:
            raise ValueError(f"Rewind parameter `turns` cannot be a negative value. Request: {turns}")
        if turns == 0 or len(self.chatHistory) == 0:
            return
        rewindTurnTarget = max(0, self.getLastContextTurn() - turns)
        if (rewindTurnTarget == 0):
            self.chatHistory = []
            return
        i = 0
        while self.chatHistory[i]["turn"] <= rewindTurnTarget:
            i += 1
        self.chatHistory = self.chatHistory[:i]

    def retrieveChatHistory(self, startingTurn, endingTurn) -> List[dict[str, str]]:
        lastContextTurn = self.getLastContextTurn()
        if lastContextTurn < startingTurn or startingTurn < 1:
            raise ValueError(f"Invalid startingTurn {startingTurn} (lastContextTurn = {lastContextTurn}). Out of bounds.")
        if lastContextTurn < endingTurn or endingTurn < 1:
            raise ValueError(f"Invalid endingTurn {endingTurn} (lastContextTurn = {lastContextTurn}). Out of bounds.")
        if startingTurn > endingTurn:
            raise ValueError(f"Invalid startingTurn/endingTurn {startingTurn}/{endingTurn}.")
        startIndex = self._getFirstChatHistoryIndexForTurn(startingTurn)
        endIndex = self._getLastChatHistoryIndexForTurn(endingTurn)+1
        return self.chatHistory[startIndex:endIndex]

    def _getFirstChatHistoryIndexForTurn(self, turn) -> int:
        for i in range(len(self.chatHistory)):
            if self.chatHistory[i]["turn"] == turn:
                return i
        return -1

    def _getLastChatHistoryIndexForTurn(self, turn) -> int:
        for i in range(len(self.chatHistory) - 1, -1, -1):
            if self.chatHistory[i]["turn"] == turn:
                return i
        return -1

    def getLastContextTurn(self) -> int:
        if len(self.chatHistory) == 0:
            return 0
        return self.chatHistory[-1]["turn"]
    
    def getLastContextMsg(self):
        if len(self.chatHistory) == 0:
            return ""
        else:
            return self.chatHistory[-1]['content']

    def getChatHistoryFormatted(self) -> str:
        formattedStrings = []
        i = 0
        for dictionary in self.chatHistory:
            role = dictionary.get("role", "")
            content = dictionary.get("content", "")
            if role == "user":
                formattedString = f"Turn {dictionary.get('turn','')} - {self.userName}: {content}"
            else:
                formattedString = f"Turn {dictionary.get('turn','')} - {self.model}: {content}"
            formattedStrings.append(formattedString)
            i += 1
        return "\n\n".join(formattedStrings)

    def makeBackup(self, path:str = None, folderName:str = None, folderSuffix:str = ""):
        if not path:
            path = "./logs"
        os.makedirs(path, exist_ok=True)
        if not folderName:
            folderName = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fullPath = os.path.join(path, f"{folderName}{folderSuffix}")
        os.makedirs(fullPath, exist_ok=True)
        print(f"Folder '{fullPath}' Created")
        FileIO.serializeDict(os.path.join(fullPath, "chat.json"), self.chatHistory)
        FileIO.serializeDict(os.path.join(fullPath, "params.log"), {
                "app":"aiss_ollama_chat",
                "model":self.model,
                "userName":self.userName,
                "assistantName":self.assistantName,
                "maxChatLength":self.maxChatLength,
                "sysPrompt":self.sysPrompt,
                "addTimestampToOllamaDict":self.addTimestampToOllamaDict,
                "addTurnToOllamaDict":self.addTurnToOllamaDict,
                "addedDateTimeToPrompt":self.addDateTimeToPrompt,
                "sysPromptDropTurn":self.sysPromptDropTurn
            })
