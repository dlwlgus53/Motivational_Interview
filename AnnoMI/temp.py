import json

step1 = json.load(open("/home/jihyunlee/MI/AnnoMI/generated/step1_annomi.json", "r"))
step2 = json.load(open("/home/jihyunlee/MI/AnnoMI/generated/step2_annomi.json", "r"))


save_path = "/home/jihyunlee/MI/AnnoMI/generated/step1_step2_merged.json"

for idx in range(len(step1)):
    step2[idx]["stage_resistant"] = step1[idx]["stage_resistant"]



with open(save_path, "w") as f:
    json.dump(step2, f, indent=4)
    
