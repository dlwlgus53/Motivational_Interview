from abc import ABC, abstractmethod
from counselor_prompts import counselor_default_prompt
from client_prompts import client_state_checker, client_default_prompt, client_action_prompt
import os, sys
import pdb
import json
import random

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
        return output["idx"]
    
    def _history_to_string(self, history):
        return "\n".join([f"{turn['role']}: {turn['utterance']}" for turn in history])

class Client_Simulator(Simulator):
    def __init__(self, llm_name: str, persona: dict):
        super().__init__(llm_name)
        self.persona = persona  # client 전용 프로필 저장
        self.actions = json.load(open("/home/jihyunlee/MI/source/action.json"))
        self.actions_string = self.actions_to_string()
        # self.actions_statics = 

    def initialize_conversation(self, persona: dict) -> str:
        pass # 클라이언트는 첫 발화를 하지 않음
        return ""  

    def actions_to_string(self):
        actions_str = "Here are some actions you might take:\n"
        for k,v in self.actions.items():
            actions_str += f"- {k}: {v['description']}\n"
        return actions_str
    
    
    def choose_action(self, action_list):
        action = random.choice(action_list)
        return action
    
                
    def _personal_info_to_string(self):

        info = (
            f"Referred by: {self.persona['persona']['referred_by']}\n"
            f"Reason for counseling: {self.persona['persona']['reason_for_counseling']}\n"
            f"Specific event for counseling: {self.persona['persona']['specific_event_for_counseling']}\n"
            f"Ambivalence target: {self.persona['persona'].get('ambivalence_target', '')}\n"
            f"Problem metrics: {self.persona['persona'].get('problem_metrics', '')}\n"
            f"Change goal: {self.persona['persona'].get('change_goal', '')}\n"
        )

        
        attitudes = f"You shows {self.persona['resistant']['name']} to change, which means {self.persona['resistant']['description']}.\n"
        attitudes += "You might say things like:\n"
        for example in self.persona['resistant']['statements']:
            attitudes += f"- {example['utterance']}\n"
        return info, attitudes
        
        
        
    def respond(self, history: list) -> str:
        
        info_str, attitude_str = self._personal_info_to_string()

        action_prompt = client_action_prompt.get_prompt(self._history_to_string(history), info_str, attitude_str, self.actions_string)
        action_result = self.generate_live_response(action_prompt)
        chosen_action = self.choose_action(action_result['actions'])
        
        prompt = client_default_prompt.get_prompt(self._history_to_string(history), info_str, attitude_str, chosen_action)
        
        response = self.generate_live_response(prompt)['utterance']
        return {'utterance' : response, 'action' : chosen_action, 'action_list': action_result['actions'], 'action_reasoning': action_result['reasoning']}



class Counselor_Simulator(Simulator):
    def initialize_conversation(self) -> str:
        return f"Hello, I’d like to understand you better. Can you tell me about yourself?"
    
    def respond(self, history: list) -> str:
        prompt = counselor_default_prompt.get_prompt(self._history_to_string(history))
        response = self.generate_live_response(prompt)['utterance']
        return {'utterance': response}



