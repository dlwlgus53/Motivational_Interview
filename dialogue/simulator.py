from abc import ABC, abstractmethod
from counselor_prompts import counselor_default_prompt
from client_prompts import client_state_checker, client_default_prompt
import os, sys
import pdb

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
        self.current_state = "pre-contemplation"  # 초기 상태 설정

    def initialize_conversation(self, persona: dict) -> str:
        pass # 클라이언트는 첫 발화를 하지 않음
        return ""  


    def state_transition(self, update_output: str) -> str:
        if "stay" in update_output.lower():
            pass
        else:
            if self.current_state == "pre-contemplation":
                self.current_state = "contemplation"
            elif self.current_state == "contemplation":
                self.current_state = "preparation"
            elif self.current_state == "preparation":
                self.current_state = "termination"
                
                
    def _personal_info_to_string(self):
        info = ""
        if self.current_state == "pre-contemplation":
            info = (
                f"Referred by: {self.persona['persona']['referred_by']}\n"
                f"Reason for counseling: {self.persona['persona']['reason_for_counseling']}\n"
                f"Specific event for counseling: {self.persona['persona']['specific_event_for_counseling']}\n"
            )

        elif self.current_state == "contemplation":
            info = (
                f"Referred by: {self.persona['persona']['referred_by']}\n"
                f"Reason for counseling: {self.persona['persona']['reason_for_counseling']}\n"
                f"Specific event for counseling: {self.persona['persona']['specific_event_for_counseling']}\n"
                f"Ambivalence target: {self.persona['persona'].get('ambivalence_target', '')}\n"
                f"Problem metrics: {self.persona['persona'].get('problem_metrics', '')}\n"
            )

        elif self.current_state == "preparation":
            info = (
                f"Referred by: {self.persona['persona']['referred_by']}\n"
                f"Reason for counseling: {self.persona['persona']['reason_for_counseling']}\n"
                f"Specific event for counseling: {self.persona['persona']['specific_event_for_counseling']}\n"
                f"Ambivalence target: {self.persona['persona'].get('ambivalence_target', '')}\n"
                f"Problem metrics: {self.persona['persona'].get('problem_metrics', '')}\n"
                f"Change goal: {self.persona['persona'].get('change_goal', '')}\n"
            )

        # 항상 태도(action) 포함
        action_text = self.persona['resistant'][self.current_state]['action']
        info += f"Client's exhibited attitude in this stage: {action_text}\n"

        return info
        
        
        
    def respond(self, history: list) -> str:
        
        resistant_code = self.persona['resistant'][self.current_state]['state']
        stage_prompt = client_state_checker.get_prompt(self._history_to_string(history), resistant_code)
        stage_transition_output = self.generate_live_response(stage_prompt)['move_or_stay']
        self.state_transition(stage_transition_output)
        
        prompt = client_default_prompt.get_prompt(self._history_to_string(history), self._personal_info_to_string())
        
        response = self.generate_live_response(prompt)['utterance']
        return response

    def update_current_state(self, new_state: str):
        self.current_state = new_state
        assert new_state in ["Pre-Contemplation", "Contemplation", "Preparation", "Termination"]

class Counselor_Simulator(Simulator):
    def initialize_conversation(self) -> str:
        return f"Hello, I’d like to understand you better. Can you tell me about yourself?"
    
    def respond(self, history: list) -> str:
        prompt = counselor_default_prompt.get_prompt(self._history_to_string(history))
        response = self.generate_live_response(prompt)['utterance']
        return response



