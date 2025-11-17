import os
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

    def __init__(self, model:str, sysPrompt1:str, maxChatLength:int=20, prevContext=None):
        self.model:str = model
        self.chatHistory:dict[str, str] = []
        self.sysPrompt:str = ""
        self.maxChatLength:int = maxChatLength
        
        with open(sysPrompt1, "r") as archivo:
            self.sysPrompt = archivo.read()
        if prevContext:
            self.deserializeContext(prevContext)
    
    def __chatOllama(self, prompt:str) -> str:
        self.chatHistory.append(self.strMsg("user", prompt))
        response = ollama.chat(self.model, messages=[{"role": "system", "content": self.sysPrompt}] + self.chatHistory[-self.maxChatLength:])
        msg = response['message'].content
        self.chatHistory.append(self.strMsg("assistant", msg))
        return msg
    
    def doChat(self, prompt:str) -> str:
        return self.__chatOllama(prompt)
    
    def getChatHistory(self) -> str:
        return self.chatHistory
    
    def getChatHistoryFormatted(self) -> str:

        return ""
    
    def rewind(self, turns=1) -> str:
        self.chatHistory = self.chatHistory[:-min(turns, len(self.chatHistory))]

    def _safeSerialize(self, path, data) -> None:
        try:
            with open(path, "w") as archivo:
                archivo.write(json.dumps(data, indent=2, ensure_ascii=False))
        except FileNotFoundError:
            return f"The file '{path}' does not exist"
        except PermissionError:
            return f"You don't have permissions to access '{path}'"
        except UnicodeDecodeError:
            return f"Encoding error in '{path}'"
        except Exception as e:
            return f"Unknown error: {e}"
        return None

    def _safeDeserialize(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return f"The file '{path}' does not exist"
        except PermissionError:
            return f"You don't have permissions to access '{path}'"
        except UnicodeDecodeError:
            return f"Encoding error in '{path}'"
        except Exception as e:
            return f"Unknown error: {e}"
        return None

    def serializeContext(self, path):
        self._safeSerialize(path, self.chatHistory)
    
    def deserializeContext(self, path):
        self.chatHistory = self._safeDeserialize(path)

    def serializeParams(self, path):
        self._safeSerialize(path, {
                "model":self.model,
                "maxChatLength":self.maxChatLength,
                "sysPrompt":self.sysPrompt
            })

    def deserializeParams(self, path):
        data = self._safeDeserialize(path)
        self.model = data["model"]
        self.maxChatLength = data["maxChatLength"]
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
