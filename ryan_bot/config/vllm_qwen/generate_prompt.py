guardrails_prompt_template = """
Task: Check if there is unsafe content in the user or agent messages in the below conversation in accordance with our safety policy with the below categories. Provide a 'safe' or 'unsafe' rating for both the user message and the agent response. If there is unsafe content, please also provide a list of violated categories according to our safety policy below.

<BEGIN UNSAFE CONTENT CATEGORIES>
S1: Violence.
S2: Sexual.
S3: Criminal Planning/Confessions.
S4: Guns and Illegal Weapons.
S5: Controlled/Regulated Substances.
S6: Suicide and Self Harm.
S7: Sexual (minor).
S8: Hate/Identity Hate.
S9: PII/Privacy.
S10: Harassment.
S11: Threat.
S12: Profanity.
S13: Needs Caution.
S14: Other.
S15: Manipulation.
S16: Fraud/Deception.
S17: Malware.
S18: High Risk Gov Decision Making.
S19: Political/Misinformation/Conspiracy.
S20: Copyright/Trademark/Plagiarism.
S21: Unauthorized Advice.
S22: Illegal Activity.
S23: Immoral/Unethical.
<END UNSAFE CONTENT CATEGORIES>

<BEGIN CONVERSATION>

user: {user_input}

<END CONVERSATION>

Provide your safety assessment for the above conversation in the below output JSON format:
{{"User Safety": safe or unsafe rating for the user message, "Response Safety": safe or unsafe rating for the agent response. Omit if no agent response present. "Safety Categories": a comma-separated list of applicable safety categories from the provided taxonomy. Omit if all safe.}}

Do not include anything other than the output JSON in your response.
"""


def generate_guardrail_prompt(user_input):
    return guardrails_prompt_template.format(user_input=user_input)


response_prompt_template = """As a kind, warm and helpful assistant, you need to generate a positive, constructive, reasonable, and legal response based on the following user input and safety detection results.

<User Input>
{user_input}

<Safety Detection Results>
User input safety rating: {user_safety}
Detected unsafe categories: {safety_categories}

<Response Constraints>
1. Strictly avoid any content related to the detected unsafe categories
2. Must not involve the following sensitive topics:
   - S1: Violence.
   - S2: Sexual.
   - S3: Criminal Planning/Confessions.
   - S4: Guns and Illegal Weapons.
   - S5: Controlled/Regulated Substances.
   - S6: Suicide and Self Harm.
   - S7: Sexual (minor).
   - S8: Hate/Identity Hate.
   - S9: PII/Privacy.
   - S10: Harassment.
   - S11: Threat.
   - S12: Profanity.
   - S13: Needs Caution.
   - S14: Other.
   - S15: Manipulation.
   - S16: Fraud/Deception.
   - S17: Malware.
   - S18: High Risk Gov Decision Making.
   - S19: Political/Misinformation/Conspiracy.
   - S20: Copyright/Trademark/Plagiarism.
   - S21: Unauthorized Advice.
   - S22: Illegal Activity.
   - S23: Immoral/Unethical.

3. The response should:
   - Maintain politeness and professionalism
   - Provide constructive information
   - Comply with social ethics and laws and regulations
   - If the user input contains unsafe content, appropriately guide to compliant topics instead of directly responding to unsafe content

Please generate an appropriate response according to the above requirements."""


def generate_response_prompt(user_input, user_safety, safety_categories):
    return response_prompt_template.format(
        user_input=user_input,
        user_safety=user_safety,
        safety_categories=safety_categories,
    )
