import os
import re
import json
import time
from datetime import datetime
import praw

# =========================
# Reddit API credentials
# (권장) 환경변수로 관리
# =========================
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "s9bMbpUERY85dSyddaC0UQ")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "4RBV7dtySDUByT99VLwzlQTB8q7R0A")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "No-Trouble846")

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
    ratelimit_seconds=5,
)

def iso(ts):
    from datetime import datetime
    try:
        return datetime.utcfromtimestamp(ts).isoformat() + "Z"
    except Exception:
        return None

# -------------------------
# Narrative filter (heuristic)
# -------------------------
FIRST_PERSON_PAT = re.compile(
    r"\b(i|i'm|i’ve|i'd|i’d|i am|i was|i want|i wanted|i need|i needed|i decide|i decided|"
    r"i'm trying|i try|i tried|i struggle|i'm struggling|my|me|myself)\b",
    flags=re.IGNORECASE,
)

CHANGE_TALK_PAT = re.compile(
    r"\b(i (want|plan|hope|aim|intend|decide|decided|will|am going) to|"
    r"trying to|working on|quit|cutting (back|down)|stop|start)\b",
    flags=re.IGNORECASE,
)

URL_OR_MEDIA_PAT = re.compile(r"https?://|\b(imgur|i\.redd\.it|youtu\.be|youtube\.com)\b", re.IGNORECASE)

def is_narrative_post(title: str, selftext: str, min_chars: int = 200) -> bool:
    """
    내러티브(자기고백형) 글 필터:
    - 본문 길이 기준
    - 1인칭 표현 포함
    - 변화 의지/시도 표현(change talk) 가점
    - 링크/미디어-only 글 배제
    """
    text = (title or "").strip() + "\n" + (selftext or "").strip()
    if not text:
        return False

    # 너무 짧으면 제외 (제목+본문 합산으로 판단)
    if len(text) < min_chars:
        return False

    # 링크/미디어 위주 글 배제 (본문 전체가 URL뿐인 경우 등)
    if URL_OR_MEDIA_PAT.search(text) and len((selftext or "").strip()) < min_chars:
        return False

    # 1인칭 자기서술 필수
    if not FIRST_PERSON_PAT.search(text):
        return False

    # 변화 의지/시도 표현이 있으면 가점 -> 여기서는 필수는 아님
    # 필요시 다음 줄을 활성화하여 "필수"로 만들 수 있음:
    # if not CHANGE_TALK_PAT.search(text): return False

    return True

def fetch_reddit_data(
    subreddit_name: str,
    sort_by: str = "hot",
    limit: int = 800,
    time_filter: str = "all",     # top 전용
    fetch_comments: bool = False,
    max_comments: int = 50,
    sleep_sec: float = 0.05,
    min_chars: int = 200,
):
    sr = reddit.subreddit(subreddit_name)
    print(f"[{subreddit_name}] fetching sort='{sort_by}', limit={limit}, time_filter='{time_filter}'")

    if sort_by == "hot":
        submissions = sr.hot(limit=limit)
    elif sort_by == "new":
        submissions = sr.new(limit=limit)
    elif sort_by == "top":
        submissions = sr.top(limit=limit, time_filter=time_filter)
    elif sort_by == "rising":
        submissions = sr.rising(limit=limit)
    else:
        raise ValueError(f"Unknown sort_by: {sort_by}")

    out = {}
    total = kept = 0

    for sub in submissions:
        total += 1

        # 삭제/제거된 글 제외
        if getattr(sub, "removed_by_category", None) or getattr(sub, "selftext", "").strip() in ("[deleted]", "[removed]"):
            if sleep_sec: time.sleep(sleep_sec)
            continue

        title = getattr(sub, "title", "") or ""
        selftext = getattr(sub, "selftext", "") or ""

        if not is_narrative_post(title, selftext, min_chars=min_chars):
            if sleep_sec: time.sleep(sleep_sec)
            continue

        item = {
            "id": sub.id,
            "subreddit": subreddit_name,
            "title": title,
            "selftext": selftext,
            "author": str(getattr(sub, "author", None)) if getattr(sub, "author", None) else None,
            "created_utc": getattr(sub, "created_utc", None),
            "created_iso": iso(getattr(sub, "created_utc", None)),
            "permalink": f"https://www.reddit.com{getattr(sub, 'permalink', '')}",
            "url": getattr(sub, "url", None),
            "score": getattr(sub, "score", None),
            "upvote_ratio": getattr(sub, "upvote_ratio", None),
            "num_comments": getattr(sub, "num_comments", None),
            "over_18": getattr(sub, "over_18", None),
            "removed_by_category": getattr(sub, "removed_by_category", None),
            "link_flair_text": getattr(sub, "link_flair_text", None),
        }

        # (옵션) 댓글 수집
        if fetch_comments and item["num_comments"]:
            try:
                sub.comment_sort = "top"
                sub.comments.replace_more(limit=0)
                comments_data = []
                for c_idx, c in enumerate(sub.comments):
                    if c_idx >= max_comments:
                        break
                    comments_data.append({
                        "id": c.id,
                        "author": str(c.author) if c.author else None,
                        "body": c.body,
                        "score": c.score,
                        "created_utc": c.created_utc,
                        "created_iso": iso(c.created_utc),
                        "is_submitter": getattr(c, "is_submitter", None),
                    })
                item["comments"] = comments_data
            except Exception as e:
                item["comments_error"] = str(e)

        out[item["id"]] = item
        kept += 1

        if sleep_sec:
            time.sleep(sleep_sec)

    print(f"[{subreddit_name}] scanned {total} posts | kept (narrative) {kept}")
    return out

def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def save_results_to_json(data: dict, subreddit_name: str, sort_by: str, time_filter: str, tag: str = "narrative"):
    ensure_dir("../done4")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"../done4/{subreddit_name}_{sort_by}_{time_filter}_{tag}_{ts}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved: {fname}")

def main():
    subreddits = [
        # "Anxiety",
        # "MentalHealth",
        # "DecidingToBeBetter",
        # "REDDITORSINRECOVERY",
        # "addiction",
        # "leaves",
        # "OCD",
        # "hoarding",
        # "Laziness",
        # "depression",
        # "getdisciplined",
        # "EatingDisorders",
        # "fuckeatingdisorders"
        # "DecidingToBeBetter",
        # "loseit",
        # "AskMenAdvice",
        # "AskWomenAdvice",
        # "relationships",
        # "advice"
        # "AnorexiaNervosa"
        "stopdrinking",
        "problemgambling",
        "GamblingAddiction",
        "StopGaming",
        "diabetes",
        "ChronicIllness",
        "Productivity",
        "procrastination",
        "NoSurf"
        
    ]

    sort_by = "hot"        # hot/new/top/rising
    time_filter = "all"    # top일 때만 사용
    limit = 800
    fetch_comments = False
    max_comments = 50

    # 내러티브 필터 기준
    min_chars = 200  # 제목+본문 최소 길이(원하면 300~500으로 강화)

    for sr in subreddits:
        try:
            data = fetch_reddit_data(
                subreddit_name=sr,
                sort_by=sort_by,
                limit=limit,
                time_filter=time_filter,
                fetch_comments=fetch_comments,
                max_comments=max_comments,
                sleep_sec=0.05,
                min_chars=min_chars,
            )
            save_results_to_json(data, sr, sort_by, time_filter, tag=f"narr_{min_chars}")
        except Exception as e:
            print(f"[{sr}] ERROR: {e}")

if __name__ == "__main__":
    main()
