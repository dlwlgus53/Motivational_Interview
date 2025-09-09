def get_prompt(persona, resistant_types):
    prompt = f"""
    You are about to generate a fictional client persona participating in Motivational Interviewing (MI) counseling.
    Client persona:
    Background: {persona['background']}
    problems: {persona['problems']}
    reason_for_counseling: {persona['reason_for_counseling']}
    referred_by: {persona['referred_by']}
    specific_event_for_counseling: {persona['specific_event_for_counseling']}
    mi_focus: {persona['mi_focus']}
    change_goal: {persona['change_goal']}



    This is resistance types for each stage and descriptions:
    pre-contemplation : {resistant_types['pre-contemplation']}
    contemplation : {resistant_types['contemplation']}
    preparation : {resistant_types['preparation']}
    
    
    Task:
    1) For each MI stage — Pre-contemplation, Contemplation, Preparation we will show a list of resistance for each stage  
    2) Generate 1-2 detailed resistance action that user might exhibit in each stage.
    3) Assume a real counseling situation and use the client’s background information creatively to write specific and realistic resistance behaviors.
    4) If the given resistance type(s) and the client’s information (e.g., narrative, background, demographics, counselor role) are logically inconsistent or contradictory, return only this JSON:
    return only this JSON:
    {{"valid": "False", "reason": "<explanation>"}} 


    Else, write the resistance behaviors in detail for each stage.
    
    Your output should always be in **JSON format**.
    Example format:
    
    "resistant_action" : {{
        "pre-contemplation": "Detailed resistance that user exhibits in this stage, and example of what the client might actually say.",
        "contemplation": "Detailed resistance that user exhibits in this stage, and example of what the client might actually say.",
        "preparation": "Detailed resistance that user exhibits in this stage, and example of what the client might actually say.",
    }}
    """
    return prompt
