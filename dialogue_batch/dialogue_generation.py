'''
code for turn_by_turn dialogue generation
'''

import os
import json
import argparse
import random
import time
from .prompts.generate import get_counseling_prompt
from utils.utils import make_line, write_to_temp, process_batch, process_live
import pdb

parser = argparse.ArgumentParser()
### source path
parser.add_argument('--config_path', type = str, default = "/home/jihyunlee/MI/utils/config.json") 
### generation setting
parser.add_argument('--num_to_generate', type=int, default=1, help="Number of dialogues to generate")
parser.add_argument('--state', type=str, default="Pre-contemplation")
#### Save path
parser.add_argument('--run_type', type=str, default="live") # batch or live
args = parser.parse_args()

'''
How to run
python run.py  --run_type batch --llm_name gpt-4o-mini
''' 

    
    
    
OPEN_INFORMATION = {
    "(Pre)Contemplation_A": ["background","problems","problem_metrics","problematic_client_action_need_to_be_changed","reason_for_counseling", "specific_event", "ambivalence_target","personal_values"],
    "(Pre)Contemplation_B": ["background","problems","problem_metrics","problematic_client_action_need_to_be_changed","reason_for_counseling", "specific_event", "ambivalence_target","personal_values"],
    "Preparation": ["background", "problems","problematic_client_action_need_to_be_changed", "ambivalence_target", "personal_values", "future_change_goal"]
}
    
def get_prev_dialogue(state, save_path):
    if state == "(Pre)Contemplation_A":
        return None
    elif state == "(Pre)Contemplation_B":
        path  = save_path.replace(".json", f"(Pre)Contemplation_A.json")
        return json.load(open(path))
    elif state == "Preparation":
        path  = save_path.replace(".json", f"(Pre)Contemplation_B.json")
        return json.load(open(path))
    else:
        raise NotImplementedError("Only (Pre)Contemplation and Contemplation stages are implemented for previous dialogue retrieval.")
    

def dialogue_to_string(dialogue):
    dialogue_str = ""
    for turn in dialogue:
        role = turn['role']
        utterance = turn['utterance']
        dialogue_str += f"{role}: {utterance}\n"
    return dialogue_str
    
    
def generate_resistant_info(resistant_info, persona, state):
    
    code =  persona['resistant']['code']
    name = persona['resistant']['name']
    description = persona['resistant']['profile'][state]
    
    if code == "NR":
        return "The client does not show any significant resistance at this time."
    else:
        resistant_str = f"""
        The client currently shows **{name}** resistance.
        {description}

        """
    return resistant_str

def generate_prompt(persona, resistant_info, state, state_purpose, prev_dialogue=None):
    persona = {k: v for k, v in persona['info'].items() if k in OPEN_INFORMATION[state]}
    assert len(persona) == len(OPEN_INFORMATION[args.state]), "Persona information is missing required fields."
    prompt = get_counseling_prompt(
        purpose=state_purpose, 
        client_info=persona,
        client_resistance=resistant_info,
        max_turns=CONFIG['dial_max_turn'][state],
        state=state,
        prev_dialogue=dialogue_to_string(prev_dialogue) if prev_dialogue else None
    )
    return prompt
        
def validation_test(dialogue, state):
    for turn in dialogue:
        if 'turn_id' not in turn or 'role' not in turn or 'utterance' not in turn:
            return False
        
        
    if state in ["Pre-contemplation", "Contemplation"]:
        if dialogue[-1]['role'] != 'client':
            print("Last turn is not from client")
            return False
    if state == "Preparation":
        if dialogue[-1]['role'] != 'counselor':
            print("Last turn is not from counselor")
            return False
    return True
         
if __name__ == "__main__":
    random.seed(1)
    CONFIG = json.load(open(args.config_path))
    os.environ["OPENAI_API_KEY"] = CONFIG["api-key"]
    save_temp = f"./temp/dialogue/{args.state}/dial.jsonl"
    save_result = f"batch_output/dialogue/{args.state}/dial.jsonl"
    save_processed = CONFIG['dial_path'].replace(".json", f"_{args.state}.json")
    if "(Pre)Contemplation" in args.state:
        assert CONFIG['dial_max_turn'][args.state] %2 ==0, "max_turn should be even number"
    else:
        assert CONFIG['dial_max_turn'][args.state] %2 ==1, "max_turn should be odd number"
        
        
    if os.path.exists(save_temp):
        os.remove(save_temp)
    os.makedirs(os.path.dirname(save_temp), exist_ok=True)
    os.makedirs(os.path.dirname(save_result), exist_ok=True)
    os.makedirs(os.path.dirname(save_processed), exist_ok=True)
    

    state_info = json.load(open(CONFIG['state_info_path']))
    personas = json.load(open(CONFIG['persona_path']))
    resistant_info = json.load(open(CONFIG['resistant_path']))['resistant_types']
    max_state_cnt = CONFIG['max_state_cnt']
    llm_name = CONFIG.get("LLM_name", "gpt-4o-mini")
    represent_state = args.state.split("_")[0]
    

    print("📚 Start Generate Theme")
    
    state_purpose = state_info[represent_state]['purpose']
    payloads = []
    
    prev_dialogues = get_prev_dialogue(args.state, CONFIG['dial_path'])
    for persona_id, persona in personas.items():
        dial_id = persona_id
        
        if persona['resistant']['code'] == "NR" : continue
        if prev_dialogues:
            prev_dialogue = prev_dialogues.get(persona_id)
        else:
            prev_dialogue = None
            
        persona_resistant_info = generate_resistant_info(resistant_info, persona, represent_state)
        prompt = generate_prompt(persona, persona_resistant_info, args.state, state_purpose, prev_dialogue)
        payload = make_line(dial_id, prompt, model_name=llm_name)
        payloads.append(payload)
        write_to_temp(save_temp, payload)
        
        
    print("Data length: ", len(payloads))
    time.sleep(5)
    if args.run_type == "batch":
        output = process_batch(save_temp, save_result)
    else:
        output = process_live(payloads)
    
    
    
    
    processed_output = {}
    for persona_id in personas.keys():
        if persona_id in output:
            ### validate output
            if validation_test(output[persona_id], args.state) is False:
                print(f"{persona_id}, skipping...")
                continue
            
            ### post-process
            for turn in output[persona_id]:
                del turn['turn_id']
                turn['stage'] = args.state
                
            ### if have previous dialogue, merge
            if prev_dialogues and prev_dialogues.get(persona_id):
                full_dialogue = prev_dialogues[persona_id] + output[persona_id]
                processed_output[persona_id] = full_dialogue
            else:
                processed_output[persona_id] = output[persona_id]
        else:
            processed_output[persona_id] = []
    
    
    
    print(f"✅ Saving {len(processed_output)} dialogues to {save_processed}")
    with open(save_processed, "w") as f:
        json.dump(processed_output, f, indent=4)
    print(f"✅ Dialogue saved to {save_processed}")
        
       
       
    #TODO : add validation for each dialogue
    #TODO : add planing stage