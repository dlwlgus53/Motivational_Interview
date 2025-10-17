'''
Generates extended client personas for Motivational Interviewing (MI) using real narratives and background profiles.
Randomly assigns referral type and infers reason for counseling and stage of change (pre-contemplation or contemplation).
Builds structured LLM prompts via get_prompt() and runs generation in batch or live mode.
Produces consistent JSON outputs describing problems, ambivalence, and behavioral goals.
Saves results to organized folders (temp/, batch_output/, generated/) for further MI data generation.
'''
import os
import pdb
import json
import argparse
from .prompts.extend_persona1 import get_prompt
import random
import re
# generation/run_scenario.py
import os, sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from utils.utils import  process_batch, process_live, write_to_temp, make_line


parser = argparse.ArgumentParser()
parser.add_argument('--num_to_generate', type=int, default=10) # number of intake forms to generate
parser.add_argument('--run_type', type=str, default="live") # batch or live
parser.add_argument('--llm_name', type=str, default="gpt-4o") # batch or live
parser.add_argument('--seed', type = int, default=1)
parser.add_argument('--save_folder', type = str, default = "/home/jihyunlee/MI/MI_profile/generated")
parser.add_argument('--config_path', type = str, default = "config.json")

args = parser.parse_args()

'''
How to run

python run.py  --run_type batch --llm_name gpt-4o-mini
'''



KEY_TO_USE = [
    "problems",
    "problem_metrics",
    "reason_for_counseling",
    "referred_by",
    "specific_event",
    "ambivalence_target",
    "future_change_goal"
]

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
    config = json.load(open(args.config_path))

    os.environ["OPENAI_API_KEY"] = config["api-key"]
    
    print("📚 Start Generate Theme")
    print(f"Will save temp in {save_temp}")
    print(f"Will save result in {save_processed}")
    if os.path.exists(save_temp):
        os.remove(save_temp)
    os.makedirs(os.path.dirname(save_temp), exist_ok=True)
    os.makedirs(os.path.dirname(save_result), exist_ok=True)
    os.makedirs(os.path.dirname(save_processed), exist_ok=True)

    random.seed(args.seed)
    narratives = process_narrative( json.load(open(config['narrative_path'])))
    # randomly shuffle
    random.shuffle(narratives)
    backgrounds = json.load(open(config['background_path']))


    payloads = []
    infos = {}
    for idx in range(args.num_to_generate):
        narrative = narratives[idx % len(narratives)]  # Cycle through personas
        referred_by = random.choices(
            ["self-referred", "referred by others (family, friend, teacher, doctor, etc.)"],
            weights=[0.2, 0.8],  # 70% vs 30% 확률
            k=1
        )[0]
        background = backgrounds[idx % len(backgrounds)]
        prompt_text = get_prompt(narrative['selftext'], background,  referred_by)
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
            merged_info = {**infos[key], **value}
            processed_output[infos[key]["key"]] = {'raw': {}, 'info': {}}
            for k in merged_info:
                if k in KEY_TO_USE:
                    processed_output[infos[key]["key"]]['info'][k] = merged_info[k]
                else:
                    processed_output[infos[key]["key"]]["raw"][k] = merged_info[k]
        else:
            continue
            

    with open(save_processed, "w") as f:
        json.dump(processed_output, f, indent=4)

    print("Saved in ", save_processed)