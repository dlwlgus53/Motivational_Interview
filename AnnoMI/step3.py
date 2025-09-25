'''
Labeling turn-level actions of AnnoMI dataset
'''


import os
import pdb
import json
import argparse
from prompts.turn_labeling_counselor_prompt import get_prompt
import random
import re
# generation/run_scenario.py
import os, sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from utils.utils import  process_batch, process_live, write_to_temp, make_line


parser = argparse.ArgumentParser()
parser.add_argument('--step1_path', type=str, default = "/home/jihyunlee/MI/AnnoMI/generated/step2_annomi.json")
parser.add_argument('--actions_path', type=str, default = "/home/jihyunlee/MI/source/behavior_counts.json")
parser.add_argument('--num_to_generate', type=int, default=1) # for debug
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



def make_action_description(attitude_actions):
    action_descriptions = "\n".join(
        [
            f"- {code} ({v['name']}): {v['description']}"
            for code, v in attitude_actions.items()
        ]
    )
    return action_descriptions

        
if __name__ == "__main__":
    # random.seed(args.seed)
    save_temp = f"./temp/step3.jsonl"
    save_result = f"batch_output/step3.jsonl"
    save_processed = f"{args.save_folder}/step3_annomi.json"

    os.environ["OPENAI_API_KEY"] = json.load(open(args.api_key_path))["api-key"]
    
    print("📚 Start Generate Theme")
    print(f"Will save temp in {save_temp}")
    print(f"Will save result in {save_processed}")
    if os.path.exists(save_temp):
        os.remove(save_temp)
    os.makedirs(os.path.dirname(save_temp), exist_ok=True)
    os.makedirs(os.path.dirname(save_result), exist_ok=True)
    os.makedirs(os.path.dirname(save_processed), exist_ok=True)


    annomi_data = json.load(open(args.step1_path))
    attitude_actions = json.load(open(args.actions_path))['BehaviorCounts']
    action_descriptions = make_action_description(attitude_actions)


    payloads = []
    infos = {}
    num_to_generate = min(args.num_to_generate, len(annomi_data))
    for idx in range(num_to_generate):
        dialogue = annomi_data[idx % len(annomi_data)]["utterances"]
        for turn_idx, turn in enumerate(dialogue):
            if turn["interlocutor"] != "therapist": continue
            prev_text = dialogue[turn_idx-1]["utterance_text"] if turn_idx > 0 else None
            prompt_text = get_prompt(turn["utterance_text"], prev_text, action_descriptions)
            payload =make_line(f"dial{idx}_turn{turn_idx}", prompt_text, model_name=args.llm_name)
            payloads.append(payload)
            write_to_temp(save_temp, payload)
            

    if args.run_type == "batch":
        output = process_batch(save_temp, save_result)
    else:
        output = process_live(payloads)
        
    
    for idx, (key, value) in enumerate(output.items()):
        d_id, turn_id = key.split("_")
        d_id = int(d_id.replace("dial", ""))
        turn_id = int(turn_id.replace("turn", ""))
        annomi_data[d_id]["utterances"][turn_id]["actions"] = value
        # 원본에 추가해주기


    with open(save_processed, "w") as f:
        json.dump(annomi_data, f, indent=4)

    print("Saved in ", save_processed)