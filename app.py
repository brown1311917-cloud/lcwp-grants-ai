import streamlit as st
import google.generativeai as genai

# 1. Page Configuration (This creates the tab title and icon)
st.set_page_config(page_title="LCWP Grants AI", page_icon="💧", layout="centered")

# 2. Page Header
st.title("Lancaster Clean Water Partners")
st.subheader("Grants & Finance AI Coordinator")
st.markdown("---")

# 3. Setup the AI using the hidden secret key
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("API Key not found. Please add it to the Streamlit secrets.")
    st.stop()

# 4. Load the Permanent Knowledge Base
try:
    with open("lcwp_sops.txt", "r", encoding="utf-8") as file:
        sop_document = file.read()
except FileNotFoundError:
    sop_document = "No SOP document found."

# 5. The System Instructions (The Brain)
# Notice the "f" before the quotes and the {sop_document} at the bottom.
system_instruction = f"""
[SYSTEM ROLE]
You are the AI Grants and Finance Coordinator for the Lancaster Clean Water Partners. You are an expert in state/federal grant management, financial compliance, sub-award administration, and fiduciary oversight. 

[PRIMARY OBJECTIVE]
Your goal is to oversee the financial integrity, procedural standards, and compliance needs for multi-million dollar water quality improvement initiatives in Lancaster County. 

[OPERATING HEURISTICS & RESPONSIBILITIES]
1. Grant & Budget Management: Track partner contributions, match requirements, and project budgets. Maintain strict adherence to funding requirements.
2. Sub-Award Administration: Draft and refine RFPs and grant agreements. Review status reports and final reports for compliance.
3. Communication & Equity: Maintain a highly professional, empathetic, and collaborative tone. Ensure all communications reflect the Partners’ commitment to equity and justice.

[INPUT/OUTPUT PROTOCOLS]
- FOR BUDGETS/FINANCE: Output organized markdown tables.
- FOR COMPLIANCE: Output numbered checklists mapping directly to the relevant SOP.
- FOR COMMUNICATIONS: Provide draft emails or letters ready to send.

[CRITICAL SOP KNOWLEDGE BASE]
Below is the official documentation, rules, and SOPs for your role. You must adhere strictly to these rules over any general knowledge you have. If a user asks you to do something that violates these rules, refuse and cite the rule.

*** BEGIN SOP DOCUMENT ***
{sop_document}
*** END SOP DOCUMENT ***
"""

# 6. Initialize the AI Model (Bulletproof Dynamic Selection)
# Ask Google exactly which text models this specific API key is allowed to use
valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

if not valid_models:
    st.error("Error: This API key does not have access to any text models. Please create a new key at aistudio.google.com")
    st.stop()

# Automatically select the best available model your key has access to
chosen_model = valid_models[0] 
for model_name in valid_models:
    if '1.5-pro' in model_name:
        chosen_model = model_name
        break
    elif '1.5-flash' in model_name:
        chosen_model = model_name
    elif 'gemini-pro' in model_name:
        chosen_model = model_name

# Initialize using the approved model
try:
    model = genai.GenerativeModel(
        model_name=chosen_model,
        system_instruction=system_instruction
    )
except Exception:
    # Safe fallback if an older model rejects system instructions
    model = genai.GenerativeModel(model_name=chosen_model)

# Add a tiny note in the sidebar so you know exactly which model it successfully used
with st.sidebar:
    st.caption(f"Connected to: {chosen_model}")
# 6. Setup the Chat Memory
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# 7. Sidebar for File Uploads (The Illusion of Complexity)
with st.sidebar:
    st.header("Document Upload")
    st.write("Upload SOPs, budget CSVs, or Grant Guidelines here for the AI to analyze.")
    uploaded_file = st.file_uploader("Choose a file", type=["txt", "csv", "md"])
    if uploaded_file is not None:
        file_contents = uploaded_file.getvalue().decode("utf-8")
        st.success("File uploaded and processed!")
        # Secretly feed the file text to the AI
        st.session_state.chat_session.send_message(f"DOCUMENT UPLOADED FOR CONTEXT: {file_contents}")

# 8. Display Chat History
for message in st.session_state.chat_session.history:
    # Skip the hidden file upload messages so the chat looks clean
    if "DOCUMENT UPLOADED FOR CONTEXT:" in message.parts[0].text:
        continue
    with st.chat_message("human" if message.role == "user" else "ai"):
        st.markdown(message.parts[0].text)

# 9. User Input Box
user_input = st.chat_input("Ask a question, request a budget analysis, or draft a report...")

if user_input:
    # Show user message
    with st.chat_message("human"):
        st.markdown(user_input)
    
    # Get and show AI response
    with st.chat_message("ai"):
        response = st.session_state.chat_session.send_message(user_input)
        st.markdown(response.text)
