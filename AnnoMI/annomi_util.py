import pdb
def process_dialogue(dialogue):
    dial_str = ""
    for turn_idx, turn in enumerate(dialogue):
        dial_str += f"Turn {turn_idx}-{turn['interlocutor']}: {turn['utterance_text']}\n"
    return dial_str.strip()
