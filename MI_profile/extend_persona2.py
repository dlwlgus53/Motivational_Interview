'''
extend persona. add  referral_reason, state (pre-contemplation or contemplation) 
'''
import os
import json
import argparse
from .prompts.extend_persona2 import get_prompt
import random
import re
# generation/run_scenario.py
import os, sys
import pdb
from collections import defaultdict
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from utils.utils import  process_batch, process_live, write_to_temp, make_line


parser = argparse.ArgumentParser()
parser.add_argument('--persona_path', type=str, default = "./generated/extend_persona1.json")

parser.add_argument('--run_type', type=str, default="live") # batch or live
parser.add_argument('--llm_name', type=str, default="gpt-4o") # batch or live
parser.add_argument('--seed', type = int, default=1)
parser.add_argument('--config_path', type = str, default = "/home/jihyunlee/MI/utils/config.json")

args = parser.parse_args()

'''
How to run

python run.py  --run_type batch --llm_name gpt-4o-mini
'''
    
    

def process_resistant(resistants):
    resistant_str = ""
    for rest_key, rest in resistants.items():
        code = rest['code']
        name = rest['name']
        for sev_key, sev_item in rest['examples'].items():
            resistant_str += f"Code: {code}, Name: {name}, Severity: {sev_key}\n"
            resistant_str += f" -- In this resistatn and severity level the client might:\n"
            resistant_str += f"{sev_item['Pre-contemplation']['description']}\n"
            resistant_str += f"{sev_item['Contemplation']['description']}\n"
            resistant_str += f"{sev_item['Preparation']['description']}\n"
    
    return resistant_str
    
def get_preference(resistants):
    keys = list(resistants.keys())
    assert keys[-1] == "NR", "First resistant type should be No Resistance"
    options = keys
    weights = [0.28, 0.28, 0.28, 0.16]  
    chosen = random.choices(options, weights=weights, k=1)[0]
    code = resistants[chosen]['code']
    name = resistants[chosen]['name']
    severity=random.choice(list(resistants[keys[0]]['examples'].keys()))
    return {'code': code, 'name': name, 'severity': severity}
    
if __name__ == "__main__":
    random.seed(args.seed)
    config = json.load(open(args.config_path))
    output_path = config['persona_path']
    output_path_file_name = output_path.split("/")[-1]
    
    
    save_temp = f"./temp/extend_persona2_{output_path_file_name}l"
    save_result = f"batch_output/extend_persona2_{output_path_file_name}l"
    save_processed = output_path
    os.environ["OPENAI_API_KEY"] = config["api-key"]
    
    print("📚 Start Generate Theme")
    print(f"Will save temp in {save_temp}")
    print(f"Will save result in {save_processed}")
    if os.path.exists(save_temp):
        os.remove(save_temp)
    os.makedirs(os.path.dirname(save_temp), exist_ok=True)
    os.makedirs(os.path.dirname(save_result), exist_ok=True)
    os.makedirs(os.path.dirname(save_processed), exist_ok=True)


    personas = json.load(open(args.persona_path))
    resistant_raw = json.load(open(config['resistant_path']))['resistant_types']

    payloads = []
    infos = {}
    for idx, persona in personas.items():
        resistant_str = process_resistant(resistant_raw)
        preference = get_preference(resistant_raw)
        
        prompt_text = get_prompt(persona['info'], resistant_str, preference)
        payload =make_line(idx, prompt_text, model_name=args.llm_name)
        infos[idx] = {
            "raw": persona['raw'],
            "info":persona['info'],
        }
        payloads.append(payload)
        write_to_temp(save_temp, payload)

    if args.run_type == "batch":
        output = process_batch(save_temp, save_result)
    else:
        output = process_live(payloads)
        
    processed_output = {}
    
    for idx, (key, value) in enumerate(output.items()):
        processed_output[key] = infos[key]
        processed_output[key]["resistant"]= value
       
    with open(save_processed, "w") as f:
        json.dump(processed_output, f, indent=4)

    print("Saved in ", save_processed)