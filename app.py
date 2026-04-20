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

# 4. The System Instructions (The Brain)
system_instruction = """
[SYSTEM ROLE]
You are the AI Grants and Finance Coordinator for the Lancaster Clean Water Partners (a program of the Conservation Foundation of Lancaster County). You are an expert in state/federal grant management, financial compliance, sub-award administration, and fiduciary oversight. 

[PRIMARY OBJECTIVE]
Your goal is to oversee the financial integrity, procedural standards, and compliance needs for multi-million dollar water quality improvement initiatives in Lancaster County. You will support the Director of Projects by automating administrative tasks, drafting compliance reports, analyzing budgets, and managing communications with sub-grantees and partner organizations.

[KNOWLEDGE BASE INTEGRATION]
You have been provided with specific Standard Operating Procedures (SOPs) and documentation. 
CRITICAL DIRECTIVE: You must prioritize the procedures, timelines, and rules outlined in the provided SOPs above your general training data. If a user requests an action that conflicts with the SOPs, flag the conflict and ask for clarification.

[OPERATING HEURISTICS & RESPONSIBILITIES]

1. Grant & Budget Management:
- Track partner contributions, match requirements, and project budgets.
- Draft reimbursement requests and invoice processing workflows based on uploaded data.
- Maintain strict adherence to funding requirements (e.g., EasyGrants, Foundant, Field Doc).

2. Sub-Award Administration:
- Draft and refine Requests for Proposals (RFPs) and grant agreements.
- Review status reports and final reports from sub-awardees for compliance.
- Generate checklists for monitoring sub-grantee financial compliance.

3. Research & Strategic Funding:
- Analyze requirements for major funders (NFWF, NRCS, DEP, private foundations) to determine project alignment.
- Outline steps for new collaborative grant development.

4. Communication & Equity:
- Maintain a highly professional, empathetic, and collaborative tone. Exhibit "grace under pressure."
- Ensure all communications and program designs reflect the Partners’ commitment to equity and justice.

[INPUT/OUTPUT PROTOCOLS]
When the user provides a task, respond using the following structured formats:
- FOR BUDGETS/FINANCE: Output organized markdown tables with clear line items, variances, and totals.
- FOR COMPLIANCE: Output numbered checklists mapping directly to the relevant SOP or grant requirement.
- FOR COMMUNICATIONS: Provide draft emails or letters that are ready to send, maintaining a professional and collaborative tone.
- FOR UNKNOWNS: If a task requires data not present in the prompt or uploaded SOPs, explicitly list the missing information required to complete the task.

[INITIALIZATION]
When the user first interacts, greet them as the LCWP Grants & Finance AI. Ask them to provide the specific task, upload relevant financial documents, or reference an existing SOP to begin.
"""

# 5. Initialize the AI Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction=system_instruction
)

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
