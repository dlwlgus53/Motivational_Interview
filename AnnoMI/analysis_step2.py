import json
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pdb 

def compute_salience(transition_data):
    """
    transition_data: {rcode: {(a,b): count, ...}, ...}
    return: {rcode: {(a,b): (salience_raw, salience_norm)}}
    """
    codes = list(transition_data.keys())
    N = len(codes)

    # 전이별 등장 코드 수
    df_count = defaultdict(int)
    for rcode, transitions in transition_data.items():
        for (a, b) in transitions.keys():
            df_count[(a, b)] += 1

    # salience 원본 값
    salience_data = defaultdict(dict)
    all_vals = []

    for rcode, transitions in transition_data.items():
        total = sum(transitions.values())
        if total == 0:
            continue
        for (a, b), c in transitions.items():
            tf = c / total
            idf = np.log(N / (1 + df_count[(a, b)]))
            salience = tf * idf
            salience_data[rcode][(a, b)] = salience
            all_vals.append(salience)

        # Min–Max 보정
    salience_data_norm = defaultdict(dict)
    for rcode, transitions in salience_data.items():
        total = sum(transitions.values())
        if total == 0:
            continue
        for (a, b), val in transitions.items():
            norm_val = val / total
            salience_data_norm[rcode][(a, b)] = (val, norm_val)

    return salience_data_norm

def plot_salience_heatmap(salience_data, filename_suffix="salience"):
    rows = []
    for rcode, transitions in salience_data.items():
        for (a, b), (raw, norm) in transitions.items():
            rows.append({
                "code": rcode,
                "transition": f"{a}→{b}",
                "salience_raw": raw,
                "salience_norm": norm
            })
    df = pd.DataFrame(rows)

    pivot_df = df.pivot_table(
        index="code", columns="transition", values="salience_norm", fill_value=0
    )

    # 열을 반으로 나누기
    columns = pivot_df.columns
    mid = len(columns) // 2
    parts = [columns[:mid], columns[mid:]]

    for i, cols in enumerate(parts, 1):
        sub_df = pivot_df[cols]

        plt.figure(figsize=(20, 8))  # 분할 시 더 작게 잡아도 됨
        ax = sns.heatmap(
            sub_df,
            cmap="YlOrBr",
            annot=False,
            cbar=True
        )

        ax.set_xticks(range(len(sub_df.columns)))
        ax.set_xticklabels(sub_df.columns, rotation=90, fontsize=8)

        plt.title(f"Behavior Salience Map (Normalized, Part {i})", fontsize=16, pad=20)
        plt.xlabel("Action1 → Action2", fontsize=12)
        plt.ylabel("Resistance Code/Group", fontsize=12)
        plt.tight_layout()

        output_path = f"/home/jihyunlee/MI/AnnoMI/generated/transition_salience_{filename_suffix}_part{i}.pdf"
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"저장 완료: {output_path}")


# def plot_transition_heatmap_split(transition_data, filename_suffix="by_code_split"):
#     rows = []
#     for rcode, transitions in transition_data.items():
#         total = sum(transitions.values())
#         if total == 0:
#             continue
#         for (a, b), c in transitions.items():
#             prob = c / total
#             rows.append({
#                 "code": rcode,
#                 "transition": f"{a}→{b}",
#                 "prob": prob
#             })

#     df = pd.DataFrame(rows)
#     pivot_df = df.pivot_table(
#         index="code", columns="transition", values="prob", fill_value=0
#     )

#     # split columns into two halves
#     columns = pivot_df.columns
#     mid = len(columns) // 2
#     parts = [columns[:mid], columns[mid:]]

#     for i, cols in enumerate(parts, 1):
#         sub_df = pivot_df[cols]

#         plt.figure(figsize=(20, 8))  # 작은 크기로 두 번 그림
#         ax = sns.heatmap(
#             sub_df,
#             cmap="YlOrRd",
#             annot=False,
#             cbar=True
#         )
#         ax.set_xticks(range(len(sub_df.columns)))
#         ax.set_xticklabels(sub_df.columns, rotation=90, fontsize=8)
#         plt.title(f"Action Transition Probabilities (Part {i})", fontsize=16)
#         plt.xlabel("Action1 → Action2", fontsize=12)
#         plt.ylabel("Resistance Code", fontsize=12)
#         plt.tight_layout()

#         output_path = f"/home/jihyunlee/MI/AnnoMI/generated/transition_heatmap_{filename_suffix}_part{i}.pdf"
#         plt.savefig(output_path, dpi=300, bbox_inches="tight")
#         plt.close()
#         print(f"저장 완료: {output_path}")


# def plot_transition_heatmap(transition_data, filename_suffix="by_code"):
#     rows = []
#     for rcode, transitions in transition_data.items():
#         total = sum(transitions.values())
#         if total == 0:
#             continue
#         for (a, b), c in transitions.items():
#             if a == "NoAction" or b == "NoAction":
#                 continue  # NoAction→NoAction 전이는 제외
#             if a== "terminate" or b == "terminate":
#                 continue  # terminate 관련 전이 제외
#             prob = c / total
#             rows.append({
#                 "code": rcode,
#                 "transition": f"{a}→{b}",
#                 "prob": prob
#             })

#     df = pd.DataFrame(rows)

#     pivot_df = df.pivot_table(
#         index="code", columns="transition", values="prob", fill_value=0
#     )
#     plt.figure(figsize=(30, 12))
#     ax = sns.heatmap(
#         pivot_df,
#         cmap="YlOrRd",
#         annot=False,
#         cbar=False  # sns 자체 cbar 끔
#     )
#         # x축 모든 라벨 강제 표시
#     ax.set_xticks(range(len(pivot_df.columns)))
#     ax.set_xticklabels(pivot_df.columns, rotation=90, fontsize=8)
#     # 제목
#     plt.title("Action Transition Probabilities", fontsize=18, pad=40)
#     plt.xlabel("Action1 → Action2", fontsize=14)
#     plt.xticks(rotation=90, fontsize=10)
#     plt.yticks(fontsize=10)

#     # 따로 컬러바 추가 (제목 바로 아래)
#     # cbar = plt.colorbar(ax.collections[0],
#     #                     orientation="horizontal",
#     #                     fraction=0.046, pad=0.08)  # pad를 줄이면 제목과 더 가까워짐
#     # cbar.set_label("Probability", fontsize=12)
#     # cbar.ax.xaxis.set_label_position("top")
#     # cbar.ax.xaxis.set_ticks_position("top")

#     plt.tight_layout()


#     output_path = f"/home/jihyunlee/MI/AnnoMI/generated/transition_heatmap_{filename_suffix}.pdf"
#     plt.savefig(output_path, dpi=300, bbox_inches="tight")
#     plt.close()
#     print(f"저장 완료: {output_path}")


def get_transitions(utterances):
    client_utterances = [turn for turn in utterances if turn["interlocutor"] == "client"]
    actions = {}
    actions[0] = ['NoAction']
    for idx, turn in enumerate(client_utterances):
        if turn['actions']:
            actions[idx+1] = turn['actions']
        else:
            actions[idx+1] = ['NoAction']
    transitions = defaultdict(int)

    for i in range(len(actions) - 1):
        action1, action2 = actions[i], actions[i + 1]
        for a1 in action1:
            for a2 in action2:
                transitions[(a1, a2)] += 1
    return transitions

def plot_transition_heatmap_split(transition_data, filename_suffix="by_code_split"):
    rows = []
    for rcode, transitions in transition_data.items():
        for from_, items in transitions.items():
            for to_, vals in items.items():
                if from_ == "NoAction" or to_ == "NoAction":
                    continue  # NoAction→NoAction 전이는 제외
                if  from_ == "termination" or from_ == "terminate":
                    continue  # terminate 관련 전이 제외
                from_  = from_.replace("ambivalenceexpression","ambivalence").replace("ambivalence_expression","ambivalence")
                to_ = to_.replace("ambivalenceexpression","ambivalence").replace("ambivalence_expression","ambivalence")
                rows.append({
                    "code": rcode,
                    "transition": f"{from_}→{to_}",
                    "prob": vals['prob']
                })

    # === [여기 추가] DataFrame + Pivot ===
    df = pd.DataFrame(rows)

    if df.empty:
        print("No transitions to plot.")
        return

    pivot_df = df.pivot_table(
        index="code", columns="transition", values="prob", fill_value=0
    )
    columns = pivot_df.columns
    mid = len(columns) // 2
    parts = [columns[:mid], columns[mid:]]

    for i, cols in enumerate(parts, 1):
        sub_df = pivot_df[cols]

        plt.figure(figsize=(20, 8))  # 작은 크기로 두 번 그림
        ax = sns.heatmap(
            sub_df,
            cmap="YlOrRd",
            annot=False,
            cbar=True
        )
        ax.set_xticks(range(len(sub_df.columns)))
        ax.set_xticklabels(sub_df.columns, rotation=90, fontsize=8)
        plt.title(f"Action Transition Probabilities (Part {i})", fontsize=16)
        plt.xlabel("Action1 → Action2", fontsize=12)
        plt.ylabel("Resistance Code", fontsize=12)
        plt.tight_layout()
        
        prev_from = None
        for j, col in enumerate(sub_df.columns):
            from_action = col.split("→")[0]
            if prev_from is not None and from_action != prev_from:
                ax.axvline(j, color="black", linestyle="--", linewidth=0.5)
            prev_from = from_action

        output_path = f"/home/jihyunlee/MI/AnnoMI/generated/transition_heatmap_{filename_suffix}_part{i}.pdf"
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"저장 완료: {output_path}")
        
        
        
def plot_salience_heatmap_split(salience_data, filename_suffix="salience_split"):
    rows = []
    for rcode, transitions in salience_data.items():
        for (a, b), (raw, norm) in transitions.items():
            rows.append({
                "code": rcode,
                "transition": f"{a}→{b}",
                "salience": norm  # normalized 값만 사용
            })

    df = pd.DataFrame(rows)
    pivot_df = df.pivot_table(
        index="code", columns="transition", values="salience", fill_value=0
    )

    # split columns into halves
    columns = pivot_df.columns
    mid = len(columns) // 2
    parts = [columns[:mid], columns[mid:]]

    for i, cols in enumerate(parts, 1):
        sub_df = pivot_df[cols]

        plt.figure(figsize=(20, 8))
        ax = sns.heatmap(
            sub_df, cmap="YlOrBr", annot=False, cbar=True,
            vmin=0, vmax=1  # salience norm 범위 고정
        )
        ax.set_xticks(range(len(sub_df.columns)))
        ax.set_xticklabels(sub_df.columns, rotation=90, fontsize=8)
        plt.title(f"Behavior Salience Map (Part {i})", fontsize=16)
        plt.xlabel("Action1 → Action2", fontsize=12)
        plt.ylabel("Resistance Code", fontsize=12)
        plt.tight_layout()

        output_path = f"/home/jihyunlee/MI/AnnoMI/generated/transition_salience_{filename_suffix}_part{i}.pdf"
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"저장 완료: {output_path}")


def simplify_code(rcode):
    """PC-IR → IR, PR-NR → NR 등으로 축약"""
    return rcode.split("-")[1] if "-" in rcode else rcode


if __name__ == "__main__":
    data_path = "/home/jihyunlee/MI/AnnoMI/generated/train.json"
    dataset = json.load(open(data_path))
    save_path_code = data_path.replace(".json", "_transition_by_resistance.json")

    # 전이 데이터 (저항 코드 기준)
    transition_data = defaultdict(lambda: defaultdict(int))

    # 턴 수 카운트 (세부 코드, 그룹)
    turn_counts_code = defaultdict(int)

    for dial_item in dataset:
        for stage in ["pre-contemplation", "contemplation", "preparation"]:
            start_idx = dial_item["stage_resistant"][stage]["start_index"]
            if stage == "pre-contemplation":
                end_idx = dial_item["stage_resistant"]["contemplation"]["start_index"]
            elif stage == "contemplation":
                end_idx = dial_item["stage_resistant"]["preparation"]["start_index"]
            else:
                end_idx = len(dial_item["utterances"])

            rcode = dial_item["stage_resistant"][stage]["attitude_code"]


            # 턴 수 기록
            try:
                turn_len = end_idx - start_idx
                turn_counts_code[rcode] += turn_len
            except Exception as e:
                print(f"Error calculating turn length for dialogue {dial_item.get('dialogue_id', 'N/A')} in stage {stage}: {e}")
                continue

            transitions = get_transitions(dial_item["utterances"][start_idx:end_idx])
            for k, v in transitions.items():
                transition_data[rcode][k] += v

    # JSON 저장 (세부 코드별)
    final_data_code = {}
    transition_count = defaultdict(int)
    for rcode, transitions in transition_data.items():
        if rcode not in final_data_code:
            final_data_code[rcode] = defaultdict(lambda: defaultdict(int))
            all_cnt = 0
        for (a, b), c in transitions.items():
            if b in final_data_code[rcode][a]:
                final_data_code[rcode][a][b]['count'] += c
            else:
                final_data_code[rcode][a][b] = {'count': c}
            all_cnt += c
            transition_count[(a, b)] += c
        
        final_data_code[rcode] = dict(final_data_code[rcode])
        

        for action in final_data_code[rcode]:
            action_sum = sum(v['count'] for v in final_data_code[rcode][action].values())

            for b in final_data_code[rcode][action]:
                final_data_code[rcode][action][b]['prob'] = final_data_code[rcode][action][b]['count'] / action_sum if action_sum > 0 else 0.0
                final_data_code[rcode][action][b]['all_prob'] = final_data_code[rcode][action][b]['count'] / all_cnt if all_cnt > 0 else 0.0
            

    with open(save_path_code, "w") as f:
        json.dump(final_data_code, f, indent=4)
    print("Saved detailed JSON in", save_path_code)

    # 턴 수 출력 (세부 코드, 그룹)
    print("\n=== Turn counts by resistance code ===")
    for k, v in sorted(turn_counts_code.items(), key=lambda x: x[0]):
        print(f"{k}: {v}")
    
    plot_transition_heatmap_split(final_data_code, filename_suffix="by_code")