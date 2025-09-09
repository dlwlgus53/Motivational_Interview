def history_to_string(history):
    """
    Convert a dialogue history list into a formatted string.
    
    Args:
        history (list): List of dialogue turns, where each turn is a dictionary with 'role' and 'content'.
    
    Returns:
        str: Formatted string of the dialogue history.
    """
    
    if len(history) == 0:
        str_dialogue = "This is first turn, no history."
    else:
        str_dialogue ="\n".join(f"{turn['role']}: {turn['content']}" for turn in history)
    return str_dialogue