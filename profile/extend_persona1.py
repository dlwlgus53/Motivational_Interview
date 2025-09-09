'''
extend persona. add  referral_reason, state (pre-contemplation or contemplation) 
'''
import os
import pdb
import json
import argparse
from profile.prompts.extend_persona1 import get_prompt
import random
import re
# generation/run_scenario.py
import os, sys

from collections import defaultdict
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from utils.utils import  process_batch, process_live, write_to_temp, make_line


parser = argparse.ArgumentParser()
parser.add_argument('--narrative_path', type=str, default = "./source/reddit_posts_masked.json")
parser.add_argument('--persona_path', type=str, default = "./source/persona.json")
parser.add_argument('--referral_path', type=str, default = "./source/referral_reasons.json")

parser.add_argument('--num_to_generate', type=int, default=20) # number of intake forms to generate

parser.add_argument('--run_type', type=str, default="live") # batch or live
parser.add_argument('--llm_name', type=str, default="gpt-4o") # batch or live
parser.add_argument('--seed', type = int, default=1)
parser.add_argument('--save_folder', type = str, default = "./generated")
parser.add_argument('--api_key_path', type = str, default = "../utils/config.json")

args = parser.parse_args()

'''
How to run

python run.py  --run_type batch --llm_name gpt-4o-mini
'''


def process_referral_reasons(referral_reasons):
    referral_reasons_str = ""
    for reason in referral_reasons:
        referral_reasons_str += f"- {reason}\n"
    referral_reasons_str = referral_reasons_str.strip()  # Remove any trailing whitespace
    return referral_reasons_str
    
    
def process_narrative(profiles):
    processed_profiles = []
    for key, profile in profiles.items():
        profile["key"] = key
        processed_profiles.append(profile)
    return processed_profiles
        
        
    return profiles
if __name__ == "__main__":
    # random.seed(args.seed)
    save_temp = f"./temp/extend_persona1.jsonl"
    save_result = f"batch_output/extend_persona1.jsonl"
    save_processed = f"{args.save_folder}/extend_persona1.json"

    os.environ["OPENAI_API_KEY"] = json.load(open(args.api_key_path))["api-key"]
    
    print("📚 Start Generate Theme")
    print(f"Will save temp in {save_temp}")
    print(f"Will save result in {save_processed}")
    if os.path.exists(save_temp):
        os.remove(save_temp)
    os.makedirs(os.path.dirname(save_temp), exist_ok=True)
    os.makedirs(os.path.dirname(save_result), exist_ok=True)
    os.makedirs(os.path.dirname(save_processed), exist_ok=True)


    narratives = process_narrative(json.load(open(args.narrative_path)))
    # randomly shuffle
    random.shuffle(narratives)
    personas = json.load(open(args.persona_path))
    referral_reasons = process_referral_reasons(
        json.load(open(args.referral_path))["referral_reasons"])
    

    payloads = []
    infos = {}
    for idx in range(args.num_to_generate):
        narrative = narratives[idx % len(narratives)]  # Cycle through personas
        referred_by = random.choice(["self-referred", "referred by others"])
        background = personas[idx % len(personas)]
        prompt_text = get_prompt(narrative['selftext'], background,  referral_reasons, referred_by)
        payload =make_line(f"persona_{idx}", prompt_text, model_name=args.llm_name)
        infos["persona_" + str(idx)] = {
            "key": narrative['key'],
            "narrative":narrative['selftext'],
            "referred_by(input)": referred_by,
            "background": background
        }
        payloads.append(payload)
        write_to_temp(save_temp, payload)

    if args.run_type == "batch":
        output = process_batch(save_temp, save_result)
    else:
        output = process_live(payloads)
        
    processed_output = {}
    
    for idx, (key, value) in enumerate(output.items()):
        if "problems" in value:
            processed_output[infos[key]["key"]] = {**infos[key], **value}
        else:
            continue
            

    with open(save_processed, "w") as f:
        json.dump(processed_output, f, indent=4)

    print("Saved in ", save_processed)