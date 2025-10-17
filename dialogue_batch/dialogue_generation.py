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

parser = argparse.ArgumentParser()
### source path
parser.add_argument('--config_path', type = str, default = "/home/jihyunlee/MI/utils/config.json")
### generation setting
parser.add_argument('--max_turn_num', type=int, default=5, help="Maximum number of turns in the dialogue")
parser.add_argument('--num_to_generate', type=int, default=1, help="Number of dialogues to generate")
parser.add_argument('--state', type=str, default="Pre-contemplation")
#### Save path
parser.add_argument('--run_type', type=str, default="live") # batch or live
args = parser.parse_args()

'''
How to run
python run.py  --run_type batch --llm_name gpt-4o-mini
'''

    
    
def get_next_stage(current_state, state_info):
    stages = list(state_info.keys())
    current_index = stages.index(current_state)
    if current_index < len(stages) - 1:
        return stages[current_index + 1]
    else:
        return current_state  # Already at the last stage
    
    
def generate_prompt(persona_id):
    persona = personas[persona_id]
    prompt = get_counseling_prompt(
        purpose="Provide supportive counseling to help the client address their concerns.",
        client_info=persona,
        turn_num=args.max_turn_num
    )
    return prompt
        
if __name__ == "__main__":
    random.seed(1)
    CONFIG = json.load(open(args.config_path))
    os.environ["OPENAI_API_KEY"] = CONFIG["api-key"]
    
    
    
    save_temp = f"./temp/dialogue/{args.state}/dial.jsonl"
    save_result = f"batch_output/dialogue/{args.state}/dial.jsonl"
    save_processed = CONFIG['dial_path'].replace(".json", f"_{args.state}.json")
    
    if os.path.exists(save_temp):
        os.remove(save_temp)
    os.makedirs(os.path.dirname(save_temp), exist_ok=True)
    os.makedirs(os.path.dirname(save_result), exist_ok=True)
    os.makedirs(os.path.dirname(save_processed), exist_ok=True)
    

    state_info = json.load(open(CONFIG['state_info_path']))
    num_to_generate = CONFIG['dial_num']
    personas = json.load(open(CONFIG['persona_path']))
    resistant_info_path = CONFIG['resistant_path']
    max_state_cnt = CONFIG['max_state_cnt']
    llm_name = CONFIG.get("LLM_name", "gpt-4o-mini")

    print("📚 Start Generate Theme")
    
    payloads = []
    for idx in range(num_to_generate):
        persona_id = random.choice(list(personas.keys()))
        dial_id = "dial_" + str(idx).zfill(4) + "_" + persona_id
        prompt = generate_prompt(persona_id)
        payload = make_line(dial_id, prompt, model_name=llm_name)
        payloads.append(payload)
        write_to_temp(save_temp, payload)
        
        
    print("Data length: ", len(payloads))
    time.sleep(5)
    if args.run_type == "batch":
        output = process_batch(save_temp, save_result)
    else:
        output = process_live(payloads)
    # # save the result
    
    
    # for r_key in output:
    #     output[r_key]['story'] = story[r_key]
    #     output[r_key]['options'] = options[r_key]
    
    with open(save_processed, "w") as f:
        json.dump(output, f, indent=4)
    print(f"✅ Dialogue saved to {save_processed}")
        
       