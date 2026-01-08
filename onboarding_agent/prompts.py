AGENT_CONFIG_STRUCTURED_OUTPUT_PROMPT = """
You are an expert of extracting different configs from a large dataset of conversations.

You are going to be provided with a list of input/output of conversations between a client and a customer support employee in a particular domain.

Your job is to understand the patterns, behaviour, character, tone, categories of the conversations, and everything related to the customer support, and based on your extraction, You should output a JSON structure of the configurations based on the provided schema.

Extra Instructions: 
- Some fields within the provided schema might not be clear to extract from the conversation, for that you can use the default value as required.
"""

QA_CHAT_CONVERSATION_STRUCTURED_OUTPUT_PROMPT = """
You are going to be provided with a tuple of both:
1. A list of input/output of conversations between a client and a customer support employee in a particular domain
2. A list of categories that classify different conversations
Your task is to transform this data into a comprehensive question/answer without losing any detail at all and reducing redundancy.

Guidelines:
- Cover all information contained in the provided data.
- group all the related generated Q/A under the category key/field 
- Do not make up new categories use only the ones provided within the input categories list
"""
