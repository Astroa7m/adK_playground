"""
Plan:
1- prepare & clean input
    - remove useless, very short convo
    - normalize latin characters
    - clean extra spaces, new lines, duplicates,
    - etc

2- give convo for LLM for summarization in a form of structured output

3- chunk and embed result and store in vector db

4- give same convo for LLM to generate config and save them in mongo db

5- done
"""