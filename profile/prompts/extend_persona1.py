import re

def additional_info(current_state: str) -> str:
    cs = (current_state or "").strip().lower()
    # 정규화
    if re.search(r'\bpre[-\s]?contemplation\b', cs) or cs.startswith('pre'):
        return "The client is not yet recognizing the need for change."
    return "The client is beginning to recognize the need for change but may still feel ambivalent."

def process_refer(referred_by: str) -> str:
    if not referred_by:
        return "referred by others"
    return "self-referred" if "self" in referred_by.lower() else "referred by others"

def process_refer_reason(referred_by: str, referral_reasons: str) -> str:
    if referred_by and "self" in referred_by.lower():
        return ""  # 자의 내담자는 별도 이유 생성 생략
    return (
        "Also, here are common reasons clients come to counseling (reason for counseling):\n"
        f"{referral_reasons}\n"
        "Based on this, generate a realistic referral reason for this client."
    )

def get_prompt(narrative: str, background: str, referral_reasons: str, referred_by: str) -> str:
    prompt = f"""
    
This is the personal narrative:
{narrative}

The client may or may not recognize their own problems.
However, assume that the client does NOT recognize their problems when imagining the situation of coming to counseling.

This is the client's background:
{background}





You are about to create a fictional client persona who has come to Motivational Interviewing (MI) counseling.
First, determine whether the personal narrative is:
A personal statement from an individual experiencing conflict, problems, or ambivalence about change that could realistically be addressed through MI, with a clear direction for positive behavioral change (e.g., reducing substance use, improving adherence, addressing avoidance), OR
An advertisement, spam, or irrelevant content with no genuine mental health issues, OR
A statement describing problems that are not suitable for MI (e.g., no ambivalence about change, issues outside MI’s scope such as purely medical problems, relationship conflicts without behavioral change goals, or narratives with no clear positive direction of change).
The narrative must explicitly or implicitly show a plausible and positive behavioral change goal that MI could support.
If this is not present or ambiguous, MI is not appropriate.
If MI is not appropriate, return only this JSON:
{{"valid": "False", "reason": "<explanation>"}} 

Second  If the background and narrative contain contradictory or inconsistent information (e.g., mismatched gender, age, occupation, or other key attributes), treat this as invalid and not suitable for MI.
in that case, return only this JSON:
{{"valid": "False", "reason": "<explanation>"}} 


If the narrative is a genuine counseling-suitable personal statement and background is consistent, create a fictional client profile as follows:

Client came to counseling as follows:
{process_refer(referred_by)}

Based on this, generate a plausible client profile and the problems that brought this client to counseling.
{process_refer_reason(referred_by, referral_reasons)}


specific_event_for_counseling  guidelines:
Should be exactly 5 sentences.
Sentence order: Background → Build-up → Trigger → Feelings/Impact → Motivation/Goal.
Naturally weave in information from background, reason_for_counseling, and referred_by (if available).
Write in plain text, first-person voice (e.g., “I …”).

Next, imagine as specifically as possible one concrete event this client might have experienced as a result of their issue.
These could include:

Family conflicts
Arguments with parents or siblings
Tension due to caregiving responsibilities
Disagreements about expectations or household rules
Friendship and relationships
Falling out with a close friend
Breakups or repeated conflicts with a partner
Social isolation or peer rejection

School/academic issues
Declining grades leading to teacher concern
Test anxiety disrupting class participation
Disciplinary warnings for incomplete assignments

Workplace problems
Arguments with a supervisor or colleagues
Absenteeism or decreased productivity
Being passed over for promotion due to performance
Health-related events
Panic attack during a medical appointment
Worsening condition due to skipped treatment
Emergency visit related to substance use or stress

Emotional/behavioral crises
Intense panic attack in a public setting
Self-harm urges or outbursts of anger
Withdrawing completely from daily activities
Legal or financial consequences
Involvement with police or court appearances
Debt or financial strain from overspending
Theft or risky behavior leading to consequences

Major life events
Relocation, graduation, or job transition
Experiencing loss such as a death in the family
Difficulty adjusting to a new environment
Community or social situations
Conflict within an online group or community
Feeling excluded in cultural or religious settings
Facing stigma or discrimination in society




Generate exactly ONE specific event that this client might have gone through due to their issue.
If the client's issue is not explicit, infer a plausible issue from the narrative and then generate the event.

Additionally, identify what should specifically be addressed through MI:
- Set "mi_focus" to a clear and concrete behavioral or motivational target related to the client’s problem.
- Do not use only broad labels like "depression" or "anxiety management".
- Instead, describe the specific change that MI would aim to support. Also add (A vs B) format , at the last. Examples are provided below.

Ambivalence about attending therapy (Wanting help vs Fearing stigma or discomfort)

Avoidance of social activities due to anxiety (Wanting connection vs Fear of judgment)

Resistance to reducing alcohol use (Enjoying relaxation vs Concern about health/relationships)

Lack of motivation to adhere to medical treatment (Wanting to stay healthy vs Feeling burdened by routines)

Ambivalence about starting antidepressant medication (Hoping for symptom relief vs Fear of side effects)

Avoidance of job applications due to fear of failure (Desiring independence vs Fear of rejection)

Resistance to attending group therapy sessions (Wanting support vs Discomfort sharing with others)

Lack of motivation to maintain regular exercise for stress relief (Knowing benefits vs Feeling too exhausted)

Procrastination in managing academic responsibilities (Wanting success vs Avoiding stress of tasks)

Inconsistent adherence to diabetes management plan (Wanting health stability vs Resenting restrictions)

Avoidance of driving after panic attacks (Wanting independence vs Fear of losing control)

Reluctance to reduce cannabis use despite memory problems (Enjoying relief vs Concern about cognitive decline)

Withdrawal from intimate relationships due to fear of rejection (Longing for closeness vs Fear of being hurt)

Low motivation to rebuild social connections after isolation (Wanting friends vs Anxiety about re-engaging)

Resistance to practicing coping skills learned in therapy (Knowing skills help vs Feeling they don’t fit naturally)

Avoidance of sleep hygiene routines despite chronic insomnia (Wanting rest vs Resisting strict routines)

Ambivalence about following through with anger management strategies (Wanting control vs Feeling too angry to try)

Reluctance to seek employment support despite financial stress (Wanting stability vs Fear of being judged)

Avoidance of medical checkups due to fear of bad news (Wanting reassurance vs Fear of diagnosis)

Resistance to reducing screen time despite worsening anxiety (Enjoying distraction vs Recognizing harm)

Difficulty committing to a daily routine despite wanting stability (Wanting order vs Feeling trapped by structure)

Reluctance to reduce alcohol use despite relationship conflicts (Wanting peace at home vs Relying on alcohol to cope)

Ambivalence about reconnecting with estranged family members (Longing for connection vs Fear of conflict)

Low motivation to attend follow-up therapy sessions consistently (Knowing consistency helps vs Feeling unmotivated)



Your output MUST be a single JSON object with the following keys and nothing else:
{{
  "valid": "True",
  "problems": "<Client's main issue in one sentence>",
  "problems in short": "<one or two words>",
  "reason_for_counseling": "<How the client came to counseling>",
  "referred_by": "<'self-referred' or 'referred by others'>",
  "specific_event_for_counseling": "<5 sentences>",
  "mi_focus": "<concise MI target>",
    "change_goal": "<specific behavioral change goal MI would aim to support>"  
}}

Rules:
- If and only if the narrative is NOT a genuine counseling-suitable personal statement, return ONLY:
  {{"valid": "False", "reason": "<explanation>"}}
- Otherwise, return ONLY the JSON object with "valid": "True".
- Ensure internal consistency with the narrative and background.
- Include emotional, relational, behavioral, and contextual elements.
- Use clear, concrete language for the event (who/what/where).
- Do not include any text outside the JSON.
"""
    return prompt
