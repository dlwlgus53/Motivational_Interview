'''
code for turn_by_turn dialogue generation
'''

import pdb
import os
import json
import argparse
import random
import re
import os, sys
from simulator import Client_Simulator, Counselor_Simulator



ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

parser = argparse.ArgumentParser()
### source path
parser.add_argument('--persona_path', type=str, default="/home/jihyunlee/MI/MI_profile/generated/extend_persona2.json")
parser.add_argument('--api_key_path', type = str, default = "../utils/config.json")
### generation setting
parser.add_argument('--max_turn_num', type=int, default=6, help="Maximum number of turns in the dialogue")
parser.add_argument('--llm_name', type=str, default="gpt-4o") # batch or live
parser.add_argument('--seed', type = int, default=1)
parser.add_argument('--num_to_generate', type=int, default=3, help="Number of dialogues to generate")
#### Save path
parser.add_argument('--save_folder', type = str, default = "./generated/dialogue")

args = parser.parse_args()

'''
How to run
python run.py  --run_type batch --llm_name gpt-4o-mini
'''

    
if __name__ == "__main__":
    random.seed(args.seed)
    os.environ["OPENAI_API_KEY"] = json.load(open(args.api_key_path))["api-key"]
    print("📚 Start Generate Theme")
    os.makedirs(os.path.dirname(args.save_folder), exist_ok=True)

    personas = json.load(open(args.persona_path))
    counselor = Counselor_Simulator(args.llm_name)
    result = {}
    
    for idx in range(args.num_to_generate):
        persona_id = random.choice(list(personas.keys()))
        dial_id = "dial_" + str(idx).zfill(4) + "_" + persona_id
        
        persona = personas[persona_id]
        client = Client_Simulator(args.llm_name, persona)
        print(f"📝 Generating dialogue {dial_id} with persona {persona_id}")
        
        for t_idx in range(args.max_turn_num):
            if t_idx == 0:
                counselor_utterance = counselor.initialize_conversation()
                result[dial_id] = {"persona": persona, "dialogue": [{"role": "counselor", "utterance": counselor_utterance}]}
            else:
                client_utterance = client.respond(result[dial_id]["dialogue"])
                client_utterance['role'] = 'client'
                result[dial_id]["dialogue"].append(client_utterance)
                if t_idx == args.max_turn_num - 1:
                    break
                counselor_utterance = counselor.respond(result[dial_id]["dialogue"])
                counselor_utterance['role'] = 'counselor'
                result[dial_id]["dialogue"].append(counselor_utterance)
            print(f"Dialogue {dial_id}, Turn {t_idx} completed.")
    
    
    # save the result
    with open(os.path.join(args.save_folder, f"dialogue.json"), "w") as f:
        json.dump(result, f, indent=4)
    print(f"✅ Dialogue saved to {os.path.join(args.save_folder, f'dialogue.json')}")
        
       