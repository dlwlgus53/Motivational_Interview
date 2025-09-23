'''
Labeling stage and stage's resistance type of AnnoMI dataset
'''
import os
import pdb
import json
import argparse
from prompts.stage_resistant_prompt import get_prompt
import random
import re
# generation/run_scenario.py
import os, sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from utils.utils import  process_batch, process_live, write_to_temp, make_line
from annomi_util import process_dialogue


parser = argparse.ArgumentParser()
parser.add_argument('--annomi_path', type=str, default = "/home/jihyunlee/MI/AnnoMI/raw/AnnoMI.json")
parser.add_argument('--num_to_generate', type=int, default=200) # number of intake forms to generate
parser.add_argument('--run_type', type=str, default="live") # batch or live
parser.add_argument('--llm_name', type=str, default="gpt-4o") # batch or live
parser.add_argument('--seed', type = int, default=1)
parser.add_argument('--save_folder', type = str, default = "./generated")
parser.add_argument('--api_key_path', type = str, default = "../utils/config.json")
parser.add_argument('--resistant_path', type = str, default = "/home/jihyunlee/MI/source/resistant.json")
args = parser.parse_args()

'''
How to run

python run.py  --run_type batch --llm_name gpt-4o-mini
'''

def process_resistant(resistant):
    resistant_str = ""
    for stage, items in resistant["resistant"].items():
        resistant_str += f"### {stage}\n"
        seen_codes = set()
        for item in items:
            code = item["code"]
            if code in seen_codes:
                continue  # 중복 제거
            seen_codes.add(code)
            name = item["name"]
            desc = item["description"]
            resistant_str += f"- {code} — {name}: {desc}  \n"
        resistant_str += "\n"
    return resistant_str

        
if __name__ == "__main__":
    # random.seed(args.seed)
    save_temp = f"./temp/step1.jsonl"
    save_result = f"batch_output/step1.jsonl"
    save_processed = f"{args.save_folder}/step1_annomi.json"

    os.environ["OPENAI_API_KEY"] = json.load(open(args.api_key_path))["api-key"]
    
    print("📚 Start Generate Theme")
    print(f"Will save temp in {save_temp}")
    print(f"Will save result in {save_processed}")
    if os.path.exists(save_temp):
        os.remove(save_temp)
    os.makedirs(os.path.dirname(save_temp), exist_ok=True)
    os.makedirs(os.path.dirname(save_result), exist_ok=True)
    os.makedirs(os.path.dirname(save_processed), exist_ok=True)


    annomi_data = json.load(open(args.annomi_path))
    resistant_data = json.load(open(args.resistant_path))
    resistant_str = process_resistant(resistant_data)

    payloads = []
    infos = {}
    num_to_generate = min(args.num_to_generate, len(annomi_data))
    for idx in range(num_to_generate):
        dialogue = annomi_data[idx % len(annomi_data)]["utterances"]
        processed_dialogue = process_dialogue(dialogue)
        prompt_text = get_prompt(processed_dialogue, resistant_str)
        payload =make_line(f"dial_{idx}", prompt_text, model_name=args.llm_name)
        payloads.append(payload)
        write_to_temp(save_temp, payload)

    if args.run_type == "batch":
        output = process_batch(save_temp, save_result)
    else:
        output = process_live(payloads)
        
    
    for idx, (key, value) in enumerate(output.items()):
        index = int(key.split("_")[-1])
        annomi_data[index]["stage_resistant"] = value
        # 원본에 추가해주기


    with open(save_processed, "w") as f:
        json.dump(annomi_data, f, indent=4)

    print("Saved in ", save_processed)