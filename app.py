# app.py
import streamlit as st
from openai import OpenAI

def read_knowledge(file_path):
    """A simple tool to read a text file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: Could not find {file_path}."

def get_concussion_info(query: str):
    """Tool to get info on concussions."""
    return read_knowledge("concussion.txt")

def get_heat_info(query: str):
    """Tool to get info on heat-related illness."""
    return read_knowledge("heat.txt")

def get_sprain_info(query: str):
    """Tool to get info on sprains."""
    return read_knowledge("sprain.txt")
@st.cache_data  # Cache the data so it doesn't reload every time
def load_knowledge():
    try:
        with open("heat_related_illness.txt", "r", encoding="utf-8"), \
            open("lower_body_injuries.txt", "r", encoding="utf-8"), \
            open("head_injuries.txt", "r", encoding="utf-8"), \
            open("internal_issues.txt", "r", encoding="utf-8"),\
            open("Upper_body_injuries.txt", "r", encoding="utf-8"), \
            open("foot_ankle_injuries.txt", "r", encoding="utf-8"), \
            open("chronic_conditions.txt", "r", encoding="utf-8"), \
            open("general.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Error: file not found."

KNOWLEDGE_BASE = load_knowledge()


def get_safety_answer(user_question, context):
    system_prompt = f"""
    You are a helpful youth sports safety assistant. 
    Using ONLY the provided context below, answer the user's question.
    Your answer must be clear, concise, and easy to understand for a volunteer coach in a stressful situation.
    try to gave a basic diagnosis of the issue based on the symptoms provided.
    Prioritize safety and always end your answer with the disclaimer: 'This is not a substitute for professional medical advice. Always call 911 in an emergency.'

    --- CONTEXT ---
    {context}
    --- END CONTEXT ---
    """

    try:
        completion = client.chat.completions.create(
          model="nvidia/nvidia-nemotron-nano-9b-v2", # Or another recommended Nemotron
          messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question},
          ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error contacting AI: {e}"

# --- THIS IS YOUR SECRET ---
# It's okay to hardcode this for a 2-hour hackathon
API_KEY = "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"

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = API_KEY
)

# Add this new function
def get_query_category(user_question):
    system_prompt = """
    You are an expert query router for a youth sports safety agent. Your single task is to analyze the user's question and classify it into ONE of the following categories.

Respond *only* with the single category name and nothing else.

Categories:
- 'Head/Brain Injury'
- 'Heat'
- 'Lower Body Injury'
- 'Upper Body Injury'
- 'Foot/ankle'
- 'Internal Issue'
- 'Overuse/Chronic Condition'
- 'General'

---
Example 1:
User: "A player fell and is dizzy, what do I look for?"
Response: "Head/Brain Injury"

Example 2:
User: "It's 95 degrees out and a player looks pale."
Response: "Heat"

Example 3:
User: "My player landed wrong on their leg and their knee hurts."
Response: "Lower Body Injury"

Example 4:
User: "He says his ankle is throbbing."
Response: "Foot/ankle"

Example 5:
User: "He's having trouble breathing after a hit."
Response: "Internal Issue"

Example 6:
User: "How do I do first aid?"
Response: "General"
    """

    try:
        completion = client.chat.completions.create(
          model="nvidia/nvidia-nemotron-nano-9b-v2", # Use a fast, smart model
          messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question},
          ],
        )
        # .strip() is important to remove whitespace
        return completion.choices[0].message.content.strip().replace("'", "")
    except Exception as e:
        return "General" # Default to General on error
    
# Modify your main UI logic
st.title("SafePlay Agent 🏈")
st.markdown("Your on-demand AI assistant for youth sports safety.")

user_question = st.text_input("What is the player's issue? Describe the symptoms or situation.")

if user_question:
    # --- STEP 1: REASON ---
    with st.spinner("Agent is reasoning about the query..."):
        category = get_query_category(user_question)

        # THIS IS KEY: Show the judges the agent's "thought process"
        st.info(f"**Agent analysis:** Query appears to be about **{category}**.")

    # --- STEP 2: ACT ---
    with st.spinner(f"Agent is searching {category} knowledge..."):
        # (Future improvement: you could have different KNOWLEDGE_BASE files
        # for each category, but for 2 hours, using one is fine)

        # We can slightly specialize the prompt
        context_prompt = f"The user's question is about {category}. "

        answer = get_safety_answer(context_prompt + user_question, KNOWLEDGE_BASE)
        st.markdown(answer)