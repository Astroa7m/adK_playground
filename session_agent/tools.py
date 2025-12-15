def summary(summary_value: str, username: str) -> str:
    """
    Critical INSTRUCTIONS: YOU SHOULD USE THIS TOOL ONLY WHEN THE CONVERSATION IS DEFINITELY ENDED

    Call this tool ONLY when ALL of these conditions are met:
    1. The user has explicitly indicated they are done (e.g., "thanks", "goodbye", "that's all", "bye")
    2. There are NO pending questions or requests from the user
    3. The user is NOT asking for clarification, follow-up, or additional information
    4. The conversation has reached a natural conclusion

    DO NOT call this tool if:
    - The user is asking a question (even if they say "thanks" first)
    - The user says "thanks" but continues with more requests
    - The conversation is still ongoing or might continue
    - There is any ambiguity about whether they need more help

    Examples of when TO call:
    - "Thanks, that's all I needed!"
    - "Perfect, goodbye"
    - "Great, talk to you later"
    - "Thank you, bye"

    Examples of when NOT to call:
    - "Thanks! Can you also..."
    - "Thank you. One more thing..."
    - "Thanks for that. What about..."
    - User is still engaged in discussion

    :param summary_value: A concise summary of the entire conversation, including:
        - Main topics discussed
        - Key information provided
        - Any actions taken or decisions made
        Keep it brief but informative (2-4 sentences).
    :param username: The username of the person you conversed with
    :return: Formatted summary string with username and conversation summary
    """
    return f"""
    Summary of the conversation the model had with: {username}
    {summary_value} 
    """

