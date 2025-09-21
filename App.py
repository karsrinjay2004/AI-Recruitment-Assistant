import streamlit as st
from groq import Groq
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import PyPDF2  # For reading PDF content

# 🔑 Initialize Groq client with API key (stored in env variable)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="AI Recruitment Assistant", page_icon="🤖", layout="centered")

st.title("🤖 AI Recruitment Assistant")
st.write("Upload your resume (PDF) and optionally paste the job description to get AI-powered feedback.")

# Upload PDF resume
uploaded_file = st.file_uploader("📄 Upload your Resume (PDF)", type=["pdf"])
job_desc = st.text_area("📝 Paste the Job Description (optional):")

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

if st.button("Get Feedback"):
    if not uploaded_file:
        st.warning("Please upload your resume PDF first.")
    else:
        try:
            # Extract text from PDF
            resume_text = extract_text_from_pdf(uploaded_file)

            # 1️⃣ Resume Feedback with Strengths, Weaknesses, Fixes
            resume_prompt = f"""
            You are an AI career assistant.
            Analyze the following resume and structure your response into 3 sections:

            1. ✅ Strengths: Mention what is good about the resume.  
            2. ⚠️ Weaknesses: Mention what is wrong or missing.  
            3. 🔧 Fix Suggestions: For each weakness, give a clear way to improve it.

            Resume:
            {resume_text}
            """

            resume_response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": resume_prompt}],
                max_tokens=500
            )
            ai_resume_reply = resume_response.choices[0].message.content.strip()

            # 2️⃣ Comparison with Job Description (if provided)
            ai_comparison_reply = None
            if job_desc.strip():
                comparison_prompt = f"""
                Compare the following resume against the job description.
                Structure your response into:
                ✅ Strengths (aligned parts),
                ⚠️ Weaknesses (missing parts),
                🔧 Fix Suggestions (how to add missing parts).

                Resume:
                {resume_text}

                Job Description:
                {job_desc}
                """

                comparison_response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": comparison_prompt}],
                    max_tokens=500
                )
                ai_comparison_reply = comparison_response.choices[0].message.content.strip()

            # --------- Show Results ---------
            st.subheader("AI Feedback on Resume:")
            st.success(ai_resume_reply)

            if ai_comparison_reply:
                st.subheader("AI Comparison with Job Description:")
                st.info(ai_comparison_reply)

            # --------- Generate PDF Report ---------
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4

            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, height - 50, "AI Resume Feedback Report")

            c.setFont("Helvetica", 12)
            text_object = c.beginText(50, height - 100)
            text_object.setLeading(16)

            # Add Resume Feedback
            for line in ai_resume_reply.split("\n"):
                text_object.textLine(line)

            # Add Comparison if available
            if ai_comparison_reply:
                text_object.textLine("")
                text_object.textLine("📌 Job Description Comparison:")
                for line in ai_comparison_reply.split("\n"):
                    text_object.textLine(line)

            c.drawText(text_object)
            c.showPage()
            c.save()

            buffer.seek(0)

            # --------- Download Button ---------
            st.download_button(
                label="⬇️ Download Feedback Report (PDF)",
                data=buffer,
                file_name="AI_Resume_Feedback.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"⚠️ Error: {e}")





        
