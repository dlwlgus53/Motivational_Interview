'''
extend persona. add  referral_reason, state (pre-contemplation or contemplation) 
'''
import os
import json
import argparse
from prompts.extend_persona2 import get_prompt
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
parser.add_argument('--resistant_path', type=str, default = "./source/resistant.json")

parser.add_argument('--run_type', type=str, default="live") # batch or live
parser.add_argument('--llm_name', type=str, default="gpt-4o") # batch or live
parser.add_argument('--seed', type = int, default=1)
parser.add_argument('--save_folder', type = str, default = "./generated")
parser.add_argument('--api_key_path', type = str, default = "../utils/config.json")
parser.add_argument('--output_path', type = str, default = "extend_persona2.json")

args = parser.parse_args()

'''
How to run

python run.py  --run_type batch --llm_name gpt-4o-mini
'''
    
    

def process_resistant(resistants):
    resistant_str_dict = {}
    random_ress = {}
    for stage_name, stage_list in resistants.items():
        resistant_str_dict[stage_name] = f"{stage_name}:\n"
        random_res = random.choice(stage_list)
        random_ress[stage_name] = random_res
        resistant_str_dict[stage_name] += f"{random_res['name']}-{random_res['description']}"

    return resistant_str_dict
    
    
    
if __name__ == "__main__":
    random.seed(args.seed)
    save_temp = f"./temp/extend_persona2_{args.output_path}l"
    save_result = f"batch_output/extend_persona2_{args.output_path}l"
    save_processed = f"{args.save_folder}/{args.output_path}" 

    os.environ["OPENAI_API_KEY"] = json.load(open(args.api_key_path))["api-key"]
    
    print("📚 Start Generate Theme")
    print(f"Will save temp in {save_temp}")
    print(f"Will save result in {save_processed}")
    if os.path.exists(save_temp):
        os.remove(save_temp)
    os.makedirs(os.path.dirname(save_temp), exist_ok=True)
    os.makedirs(os.path.dirname(save_result), exist_ok=True)
    os.makedirs(os.path.dirname(save_processed), exist_ok=True)


    personas = json.load(open(args.persona_path))
    resistant_raw = json.load(open(args.resistant_path))["resistant"]


    payloads = []
    infos = {}
    for idx, persona in personas.items():
        resistant_dict = process_resistant(resistant_raw)
        prompt_text = get_prompt(persona, resistant_dict)
        payload =make_line(idx, prompt_text, model_name=args.llm_name)
        
        infos[idx] = {
            "persona":persona,
            "resistant": resistant_dict
        }
        payloads.append(payload)
        write_to_temp(save_temp, payload)

    if args.run_type == "batch":
        output = process_batch(save_temp, save_result)
    else:
        output = process_live(payloads)
        
        
        
    processed_output = {}
    
    for idx, (key, value) in enumerate(output.items()):
        processed_output[key] = {**infos[key], **value}

    with open(save_processed, "w") as f:
        json.dump(processed_output, f, indent=4)

    print("Saved in ", save_processed)