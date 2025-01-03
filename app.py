import streamlit as st
import os
from io import StringIO
from datetime import datetime
import queue
import json

# Initialize session state
def init_session_state():
    if "saved_letters" not in st.session_state:
        st.session_state["saved_letters"] = []
    if "generation_queue" not in st.session_state:
        st.session_state["generation_queue"] = queue.Queue()
    if "letter_templates" not in st.session_state:
        st.session_state["letter_templates"] = {
            "Dispute Unauthorized Account": (
                "Subject: Request to Remove Unauthorized Account\n\n"
                "Dear [Credit Bureau Name],\n\n"
                "I am writing to dispute an account on my credit report that I believe is inaccurate. Specifically, "
                "the account with [Creditor Name] (Account Number: [Account Number]) appears on my report incorrectly.\n\n"
                "I did not authorize this account and have no knowledge of its origin. Under the Fair Credit Reporting "
                "Act (FCRA), I am entitled to dispute any information that is incorrect or unverified on my report.\n\n"
                "Please investigate this matter and provide written confirmation of the results. If you find the account "
                "to be in error, kindly remove it from my credit report. Enclosed are copies of my identification and "
                "supporting documents.\n\n"
                "Thank you for your assistance.\n\n"
                "Sincerely,\n[Your Full Name]\n[Your Address]\n[City, State, ZIP Code]\n[Phone Number]\n"
            ),
            "Dispute Late Payment": (
                "Subject: Request to Correct Late Payment Reporting\n\n"
                "Dear [Credit Bureau Name],\n\n"
                "I am writing regarding a late payment reported on my credit report for the account with "
                "[Creditor Name] (Account Number: [Account Number]). This entry is incorrect. I have included "
                "documentation that shows my payments were made on time.\n\n"
                "Under the FCRA, I have the right to request an investigation of inaccurate information. I kindly ask "
                "that you review this matter and remove the incorrect late payment from my credit report.\n\n"
                "Enclosed are copies of my payment records along with my personal identification.\n\n"
                "Thank you for your prompt attention to this matter.\n\n"
                "Sincerely,\n[Your Full Name]\n[Your Address]\n[City, State, ZIP Code]\n[Phone Number]\n"
            ),
            "Dispute Duplicate Entry": (
                "Subject: Dispute of Duplicate Credit Reporting\n\n"
                "Dear [Credit Bureau Name],\n\n"
                "I am writing to dispute a duplicate account listing on my credit report. The account with "
                "[Creditor Name] (Account Number: [Account Number]) appears twice on my report.\n\n"
                "This duplicate reporting is erroneous and could negatively affect my credit score. Please investigate this "
                "issue and remove the duplicate entry from my credit report.\n\n"
                "Thank you for your attention to this matter.\n\n"
                "Sincerely,\n[Your Full Name]\n[Your Address]\n[City, State, ZIP Code]\n[Phone Number]\n"
            ),
            "Dispute Closed Account": (
                "Subject: Request to Correct Closed Account Status\n\n"
                "Dear [Credit Bureau Name],\n\n"
                "I am disputing the status of an account on my credit report. The account with [Creditor Name] "
                "(Account Number: [Account Number]) is listed as open, but it was closed on [Date Closed].\n\n"
                "Please update this account to reflect its correct status as closed. I have included documentation showing "
                "the closure date for your review.\n\n"
                "Thank you for your assistance in correcting this matter.\n\n"
                "Sincerely,\n[Your Full Name]\n[Your Address]\n[City, State, ZIP Code]\n[Phone Number]\n"
            ),
            "Dispute Account with Fraudulent Charges": (
                "Subject: Request to Remove Fraudulent Charges\n\n"
                "Dear [Credit Bureau Name],\n\n"
                "I am writing to dispute fraudulent charges on my credit report for the account with "
                "[Creditor Name] (Account Number: [Account Number]). I have reviewed my records and did not authorize "
                "the charges listed.\n\n"
                "Please investigate the fraudulent activity and remove these charges from my credit report. I have enclosed "
                "a police report and supporting documents to verify the fraud.\n\n"
                "Thank you for your prompt attention to this issue.\n\n"
                "Sincerely,\n[Your Full Name]\n[Your Address]\n[City, State, ZIP Code]\n[Phone Number]\n"
            ),
            "Dispute Account Not Opened by Me": (
                "Subject: Request to Remove Account Not Opened by Me\n\n"
                "Dear [Credit Bureau Name],\n\n"
                "I am writing to dispute an account on my credit report that I did not open. The account with "
                "[Creditor Name] (Account Number: [Account Number]) appears on my report, but I have never opened "
                "or authorized this account.\n\n"
                "Please investigate this matter and remove the account from my report. I have enclosed a copy of my "
                "identification and additional supporting documents.\n\n"
                "Thank you for addressing this issue.\n\n"
                "Sincerely,\n[Your Full Name]\n[Your Address]\n[City, State, ZIP Code]\n[Phone Number]\n"
            ),
            "Dispute Account with Incorrect Balance": (
                "Subject: Request to Correct Incorrect Balance on Account\n\n"
                "Dear [Credit Bureau Name],\n\n"
                "I am disputing the balance reported on the account with [Creditor Name] (Account Number: [Account Number]) "
                "on my credit report. The reported balance is incorrect. The correct balance should be [Correct Balance].\n\n"
                "Please correct this error and update my credit report accordingly.\n\n"
                "Thank you for your cooperation.\n\n"
                "Sincerely,\n[Your Full Name]\n[Your Address]\n[City, State, ZIP Code]\n[Phone Number]\n"
            ),
            "Dispute Account with Incorrect Payment History": (
                "Subject: Request to Correct Payment History on Account\n\n"
                "Dear [Credit Bureau Name],\n\n"
                "I am disputing the payment history reported on my credit report for the account with "
                "[Creditor Name] (Account Number: [Account Number]). The payment history is inaccurate, and some payments "
                "are incorrectly listed as late.\n\n"
                "Please investigate this issue and correct the payment history for this account. I have included evidence "
                "of timely payments.\n\n"
                "Thank you for your attention to this matter.\n\n"
                "Sincerely,\n[Your Full Name]\n[Your Address]\n[City, State, ZIP Code]\n[Phone Number]\n"
            ),
            "Dispute Account with Incorrect Account Opening Date": (
                "Subject: Request to Correct Account Opening Date\n\n"
                "Dear [Credit Bureau Name],\n\n"
                "I am writing to dispute the opening date listed for the account with [Creditor Name] "
                "(Account Number: [Account Number]) on my credit report. The date listed is incorrect, and the account was "
                "actually opened on [Correct Opening Date].\n\n"
                "Please update my credit report to reflect the accurate opening date.\n\n"
                "Thank you for your prompt attention.\n\n"
                "Sincerely,\n[Your Full Name]\n[Your Address]\n[City, State, ZIP Code]\n[Phone Number]\n"
            ),
            "Dispute Account with Incorrect Credit Limit": (
                "Subject: Request to Correct Credit Limit on Account\n\n"
                "Dear [Credit Bureau Name],\n\n"
                "I am disputing the credit limit listed on my account with [Creditor Name] (Account Number: [Account Number]) "
                "on my credit report. The reported credit limit is incorrect.\n\n"
                "The correct credit limit for this account should be [Correct Credit Limit]. Please update my credit report "
                "to reflect the accurate limit.\n\n"
                "Thank you for your cooperation.\n\n"
                "Sincerely,\n[Your Full Name]\n[Your Address]\n[City, State, ZIP Code]\n[Phone Number]\n"
            ),
            # More templates can be added similarly
        }

# App title
st.title("Credit Dispute Letter Generator")

# Initialize session state
init_session_state()

# Sidebar for letter selection or template management
st.sidebar.header("Select or Add a Letter Template")
selected_template = st.sidebar.selectbox("Choose a Letter Template", ["Create New"] + list(st.session_state["letter_templates"].keys()))

# Letter editor
st.subheader("Edit Your Credit Dispute Letter")
letter_content = ""
if selected_template != "Create New":
    letter_content = st.session_state["letter_templates"][selected_template]

custom_letter = st.text_area(
    "Customize Your Letter Below:", value=letter_content, height=400
)

# Function to save the custom letter with title and timestamp
def save_letter(custom_letter):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = st.text_input("Enter a title for your letter:", value=f"Letter Saved on {timestamp}")
    if title:
        st.session_state["saved_letters"].append({
            "title": title,
            "content": custom_letter,
            "timestamp": timestamp
        })
        st.success(f"Letter '{title}' saved successfully!")

if st.button("Save Letter"):
    save_letter(custom_letter)

# AI Letter Generation (Integration Placeholder for AI API)
st.subheader("Generate a Letter with AI")
ai_prompt = st.text_area("Enter Prompt for AI to Generate a Letter:", value="Please generate a letter to dispute a credit report entry.")
if st.button("Generate AI Letter"):
    # Placeholder for AI generation (replace with actual API call)
    generated_letter = (
        f"AI-Generated Letter for: {ai_prompt}\n\n"
        "This is a placeholder for the AI-generated letter. Replace this section with actual API integration."
    )
    custom_letter = generated_letter
    st.text_area("Generated Letter:", value=generated_letter, height=400)

# Manage letter templates
st.sidebar.subheader("Manage Templates")
if st.sidebar.button("Clear All Saved Letters"):
    st.session_state["saved_letters"] = []
    st.sidebar.success("All saved letters cleared!")

if st.sidebar.button("Add New Template"):
    template_title = st.sidebar.text_input("Template Title")
    template_content = st.sidebar.text_area("Template Content")
    if template_title and template_content:
        st.session_state["letter_templates"][template_title] = template_content
        st.sidebar.success(f"Template '{template_title}' added successfully!")

# Template Preview in Sidebar
st.sidebar.subheader("Preview of Templates")
template_preview = st.selectbox("Select a Template to Preview", list(st.session_state["letter_templates"].keys()))
if template_preview:
    st.sidebar.text_area("Preview", st.session_state["letter_templates"][template_preview], height=200)

# Download saved letters
st.subheader("Download Your Letters")
for idx, letter in enumerate(st.session_state["saved_letters"]):
    with st.expander(letter["title"]):
        st.write(letter["content"])
        buffer = StringIO()
        buffer.write(letter["content"])
        buffer.seek(0)
        st.download_button(
            label="Download Letter", 
            data=buffer, 
            file_name=f"letter_{idx + 1}.txt", 
            mime="text/plain"
        )

# Clear saved letters
if st.button("Clear All Saved Letters"):
    st.session_state["saved_letters"] = []
    st.success("All saved letters have been cleared!")
