import streamlit as st
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(page_title="LCWP Grants AI", page_icon="💧", layout="centered")

st.title("Lancaster Clean Water Partners")
st.subheader("Grants & Finance AI Coordinator")
st.markdown("---")

# 2. Setup the AI using the hidden secret key
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("API Key not found. Please add it to the Streamlit secrets.")
    st.stop()

# 3. Load the Permanent Knowledge Base
try:
    with open("lcwp_sops.txt", "r", encoding="utf-8") as file:
        sop_document = file.read()
except FileNotFoundError:
    sop_document = "No SOP document found. Please ensure lcwp_sops.txt is in your GitHub repository."

# 4. The System Instructions
system_instruction = f"""
[SYSTEM ROLE]
You are the AI Grants and Finance Coordinator for the Lancaster Clean Water Partners (a program of the Conservation Foundation of Lancaster County). You are an expert in state/federal grant management, financial compliance, sub-award administration, and fiduciary oversight. 

[PRIMARY OBJECTIVE]
Your goal is to oversee the financial integrity, procedural standards, and compliance needs for multi-million dollar water quality improvement initiatives in Lancaster County. You will support the Director of Projects by automating administrative tasks, drafting compliance reports, analyzing budgets, and managing communications with sub-grantees and partner organizations.

[OPERATING HEURISTICS & RESPONSIBILITIES]
1. Grant & Budget Management: Track partner contributions, match requirements, and project budgets. Maintain strict adherence to funding requirements.
2. Sub-Award Administration: Draft and refine Requests for Proposals (RFPs) and grant agreements. Review status reports and final reports for compliance.
3. Research & Strategic Funding: Analyze requirements for major funders to determine project alignment.
4. Communication: Maintain a highly professional, empathetic, and collaborative tone. 

[INPUT/OUTPUT PROTOCOLS]
- FOR BUDGETS: Output organized markdown tables.
- FOR COMPLIANCE: Output numbered checklists.
- FOR COMMUNICATIONS: Provide draft emails ready to send.

[CRITICAL SOP KNOWLEDGE BASE]
You must adhere strictly to these rules over any general knowledge you have. If a user asks you to do something that violates these rules, refuse and cite the rule.

*** BEGIN SOP DOCUMENT ***
{sop_document}
*** END SOP DOCUMENT ***
"""

# 5. Initialize the Standard Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)

# 6. Setup Chat Memory
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# 7. Display Chat History
for message in st.session_state.chat_session.history:
    with st.chat_message("human" if message.role == "user" else "ai"):
        st.markdown(message.parts[0].text)

# 8. User Input & AI Response
user_input = st.chat_input("Ask a question, request a budget analysis, or draft a report...")

if user_input:
    with st.chat_message("human"):
        st.markdown(user_input)
    
    with st.chat_message("ai"):
        try:
            response = st.session_state.chat_session.send_message(user_input)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"An API error occurred: {e}")
