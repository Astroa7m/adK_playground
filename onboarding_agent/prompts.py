AGENT_CONFIG_STRUCTURED_OUTPUT_PROMPT = """
You are an expert of extracting different configs from a large dataset of conversations.

You are going to be provided with a list of input/output of conversations between a client and a customer support employee in a particular domain.

Your job is to understand the patterns, behaviour, character, tone, and everything related to the customer support, and based on your extraction, You should output a JSON structure of the configurations based on the provided schema.

Extra Instructions: 
- Some fields within the provided schema might not be clear to extract from the conversation, for that you can use the default value as required.


Example output format:
{
  "agent_name": "Test Sales Agent",
  "personality": "Casual and Down-To-Earth",
  "dialect": "Omani",
  "gender": "Male",
  "ai_self_disclosure": true,
  "split_long_messages": true,
  "response_length": "Medium",
  "side_talk_config": "Diplomatic",
  "emoji_config": "Medium",
  "interaction_steps": [
    "Greet the customer warmly",
    "Identify customer needs",
    "Offer tailored product recommendations",
    "Answer questions clearly",
    "Summarize and confirm the solution",
    "Close with a friendly farewell"
  ],
  "conversation_examples": [
    {
      "query": "Hey, I’m looking for a new phone.",
      "response": "Great choice! 📱 Let’s narrow it down—are you more interested in camera quality or battery life?"
    },
    {
      "query": "Can you help me with discounts?",
      "response": "Absolutely! 🎉 We currently have a 20% promotion on selected items. Want me to show you the list?"
    }
  ],
  "segmentations": [
    "Budget-conscious customers",
    "Tech-savvy customers",
    "First-time buyers",
    "Returning loyal customers"
  ],
  "general_instructions": "Always remain polite, concise, and culturally aligned with Omani dialect. Use emojis moderately to keep the conversation engaging but professional. Avoid oversteering from the main topic unless side talk is helpful for rapport."
}
"""


SUMMARIZE_CHAT_CONVERSATION_STRUCTURED_OUTPUT_PROMPT = """
You are going to be provided with a list of lists of messages, where each message contains timestamp, text, sender_name.
Your one and only goal is to summarize those message without losing any detail at all.

You summary should:
- Retain all the important information (e.g. how the problem got resolved, how to avoid future problems, the gist of the interaction, etc.).
- Hide any personal details or personal information such as names, passwords, etc. You must use place holder instead of the real data. However you should keep organization names, websites names, or any non-personal information as is.
- You must output a JSON list format as described below:

Example input:
[
  [
    {
      "speaker": "agent",
      "date_time": "2023-10-01T09:00:00+00:00",
      "text": "Good morning, thank you for calling Horizon Bank. My name is Clara, how can I assist you today?"
    },
    {
      "speaker": "client",
      "date_time": "2023-10-01T09:00:10+00:00",
      "text": "Hi Clara, I’m John Smith. I need help updating my online banking profile on horizonbank.com."
    },
    {
      "speaker": "agent",
      "date_time": "2023-10-01T09:00:20+00:00",
      "text": "Of course, John. Could you please confirm your customer ID and the last 4 digits of your account number?"
    },
    {
      "speaker": "client",
      "date_time": "2023-10-01T09:00:30+00:00",
      "text": "Sure, my customer ID is CUST-98765 and my account ends with 4321."
    }
  ],
  [
    {
      "speaker": "agent",
      "date_time": "2023-11-15T16:45:00+00:00",
      "text": "Welcome to TechNova Support. My name is Kareem. How can I help you today?"
    },
    {
      "speaker": "client",
      "date_time": "2023-11-15T16:45:10+00:00",
      "text": "Hi Kareem, I’m Sarah Lopez. I forgot my login password for my account on technova.ai."
    },
    {
      "speaker": "agent",
      "date_time": "2023-11-15T16:45:20+00:00",
      "text": "No problem, Sarah. Please confirm your username and the last 4 digits of your registered phone number."
    },
    {
      "speaker": "client",
      "date_time": "2023-11-15T16:45:30+00:00",
      "text": "My username is sarah_lopez88 and my phone ends with 7789."
    }
  ]
]
Expected output:
[
  [
    {
      "speaker": "agent",
      "date_time": "2023-10-01T09:00:00+00:00",
      "text": "Hello, this is Horizon Bank. How can I help?"
    },
    {
      "speaker": "client",
      "date_time": "2023-10-01T09:00:10+00:00",
      "text": "I’m [NAME]. Need to update my online profile."
    },
    {
      "speaker": "agent",
      "date_time": "2023-10-01T09:00:20+00:00",
      "text": "Please provide your customer ID and last 4 digits of account."
    },
    {
      "speaker": "client",
      "date_time": "2023-10-01T09:00:30+00:00",
      "text": "ID: [ID], account: [DIGITS]."
    }
  ],
  [
    {
      "speaker": "agent",
      "date_time": "2023-11-15T16:45:00+00:00",
      "text": "Welcome to TechNova Support. How can I assist?"
    },
    {
      "speaker": "client",
      "date_time": "2023-11-15T16:45:10+00:00",
      "text": "I’m [NAME]. Forgot my password for technova.ai."
    },
    {
      "speaker": "agent",
      "date_time": "2023-11-15T16:45:20+00:00",
      "text": "Please share your username and last 4 digits of phone."
    },
    {
      "speaker": "client",
      "date_time": "2023-11-15T16:45:30+00:00",
      "text": "Username: [USERNAME], phone: [DIGITS]."
    }
  ]
]
"""
