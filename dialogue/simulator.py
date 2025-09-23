from abc import ABC, abstractmethod
from system_prompts import default_prompt as system_default_prompt
from client_prompts import default_prompt as client_default_prompt
import os, sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from utils.utils import process_live, make_line



class Simulator(ABC):
    def __init__(self, llm_name: str):
        self.llm_name = llm_name

    @abstractmethod
    def initialize_conversation(self, persona: dict) -> str:
        """
        첫 발화를 생성 (예: 상담자 입장에서는 첫 질문, 클라이언트는 자기소개 등).
        """
        pass

    @abstractmethod
    def respond(self, input_text: str, dialogue: list) -> str:
        """
        이전 발화를 바탕으로 응답 생성.
        """
        pass

    
    def generate_live_response(self,  prompt) -> str:
        payload =make_line("idx", prompt, model_name=self.llm_name)
        output = process_live([payload], need_state_bar=False)
        return output["idx"]["utterance"]
    
    def _history_to_string(self, history):
        return "\n".join([f"{turn['role']}: {turn['utterance']}" for turn in history])

class Client_Simulator(Simulator):
    def initialize_conversation(self, persona: dict) -> str:
        pass # 클라이언트는 첫 발화를 하지 않음
        return ""  

    def respond(self, history: list) -> str:
        prompt = client_default_prompt.get_prompt(self._history_to_string(history))
        response = self.generate_live_response(prompt)
        return response


class Counselor_Simulator(Simulator):
    def initialize_conversation(self) -> str:
        return f"Hello, I’d like to understand you better. Can you tell me about yourself?"
    
    def respond(self, history: list) -> str:
        prompt = system_default_prompt.get_prompt(self._history_to_string(history))
        response = self.generate_live_response(prompt)
        return response



