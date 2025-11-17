import os
from pathlib import Path
import time
import ollama
import datetime
import json
import re

class Chat:

    @staticmethod
    def strMsg(event_type:str, content:str) -> dict[str, str]:
        return {
            'timestamp': datetime.datetime.now().isoformat(),
            'role': event_type,
            'content': content
        }

    def __init__(self, model:str, sysPrompt1:str, maxChatLength:int=20, userName:str="user", prevContext:str=None):
        self.model:str = model
        self.userName:str = userName
        self.chatHistory:dict[str, str] = []
        self.sysPrompt:str = ""
        self.maxChatLength:int = maxChatLength
        
        with open(sysPrompt1, "r") as archivo:
            self.sysPrompt = archivo.read()
        if prevContext:
            self.deserializeContext(prevContext)
    
    def doChat(self, prompt:str) -> str:
        self.chatHistory.append(self.strMsg("user", prompt))
        response = ollama.chat(self.model, messages=[{"role": "system", "content": self.sysPrompt}] + self.chatHistory[-self.maxChatLength:])
        msg = response['message'].content
        self.chatHistory.append(self.strMsg("assistant", msg))
        return msg
    
    def getChatHistory(self) -> str:
        return self.chatHistory
    
    def getChatHistoryFormatted(self) -> str:
        formattedStrings = []
        i = 0
    
        for dictionary in self.chatHistory:
            turnNum = (i // 2) * 2
            role = dictionary.get("role", "")
            content = dictionary.get("content", "")
            if role == "user":
                formattedString = f"Turn {turnNum} - {self.userName}: {content}"
            else:
                formattedString = f"Turn {turnNum} - {self.model}: {content}"
            formattedStrings.append(formattedString)
            i += 1
        return "\n".join(formattedStrings)

    def rewind(self, turns=1) -> str:
        if turns < 0:
            raise ValueError(f"Rewind parameter `turns` cannot be a negative value. Request: {turns}")
        self.chatHistory = self.chatHistory[:-min(turns*2, len(self.chatHistory))]

    def _safeSerialize(self, path, data) -> None:
        try:
            fullPath = Path(path)
            fullPath.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as file:
                file.write(json.dumps(data, indent=2, ensure_ascii=False))
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{path}' does not exist")
        except PermissionError:
            raise PermissionError(f"You don't have permissions to access '{path}'")
        except UnicodeDecodeError:
            raise UnicodeDecodeError(f"Encoding error in '{path}'")
        except Exception as e:
            raise Exception(f"Unknown error: {e}")
        return None

    def _safeDeserialize(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{path}' does not exist")
        except PermissionError:
            raise PermissionError(f"You don't have permissions to access '{path}'")
        except UnicodeDecodeError:
            raise UnicodeDecodeError(f"Encoding error in '{path}'")
        except Exception as e:
            raise Exception(f"Unknown error: {e}")
        return None

    def serializeContext(self, path):
        self._safeSerialize(path, self.chatHistory)
    
    def deserializeContext(self, path):
        self.chatHistory = self._safeDeserialize(path)

    def serializeParams(self, path):
        self._safeSerialize(path, {
                "model":self.model,
                "maxChatLength":self.maxChatLength,
                "userName":self.userName,
                "sysPrompt":self.sysPrompt
            })

    def deserializeParams(self, path):
        data = self._safeDeserialize(path)
        self.model = data["model"]
        self.maxChatLength = data["maxChatLength"]
        self.userName = data["userName"]
        self.sysPrompt = data["sysPrompt"]

    def makeBackup(self, folder:str = None):
        logsFolder = "./logs"
        os.makedirs(logsFolder, exist_ok=True)
        if folder:
            folderName = f"{folder}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        else:
            folderName = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fullPath = os.path.join(logsFolder, folderName)
        os.makedirs(fullPath, exist_ok=True)
        print(f"Folder '{fullPath}' Created")
        self.serializeContext(os.path.join(fullPath, "chat.json"))
        self.serializeParams(os.path.join(fullPath, "params.log"))
        return
