import streamlit as st
import re
import os
import pandas as pd
import matplotlib.pyplot as plt
from pdfminer.high_level import extract_text as pdf_extract
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------------
# TEXT EXTRACTION
# -------------------------------
def extract_text(file):
    if file.name.endswith(".pdf"):
        with open("temp.pdf", "wb") as f:
            f.write(file.read())
        return pdf_extract("temp.pdf")
    else:
        return file.read().decode("utf-8")


# -------------------------------
# AI ANALYSIS
# -------------------------------
def ai_analysis(text):
    prompt = f"""
    You are a labour law compliance expert.

    Analyze the following document and provide:
    1. Document type
    2. Summary
    3. Compliance score (0-100)
    4. Missing provisions
    5. Risk level (Low/Medium/High)
    6. MRT ratios if possible

    Document:
    {text[:4000]}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# -------------------------------
# MRT (basic fallback)
# -------------------------------
def calculate_mrt(text):
    numbers = list(map(int, re.findall(r"\d+", text)))

    if not numbers:
        return {"status": "Not computable"}

    return {
        "avg": sum(numbers)/len(numbers),
        "max": max(numbers),
        "min": min(numbers)
    }


# -------------------------------
# STREAMLIT UI
# -------------------------------
st.set_page_config(page_title="AI Labour Compliance Checker", layout="wide")

st.title("AI Labour Compliance Checker (Big4 Style)")

uploaded_file = st.file_uploader("Upload document", type=["pdf", "txt"])

if uploaded_file:
    with st.spinner("Analyzing with AI..."):
        text = extract_text(uploaded_file)
        ai_result = ai_analysis(text)
        mrt = calculate_mrt(text)

    # -------------------------------
    # OUTPUT
    # -------------------------------
    st.subheader("AI Analysis")
    st.write(ai_result)

    st.subheader("MRT (Auto Extracted)")
    st.json(mrt)

    # -------------------------------
    # CHART
    # -------------------------------
    st.subheader("Compliance Visualization")

    data = {
        "Category": ["Compliance", "Gaps"],
        "Score": [70, 30]  # Placeholder (AI upgrade later)
    }

    df = pd.DataFrame(data)

    fig, ax = plt.subplots()
    ax.bar(df["Category"], df["Score"])
    ax.set_title("Compliance Overview")

    st.pyplot(fig)

    # -------------------------------
    # ⚠️ DISCLAIMER
    # -------------------------------
    st.warning("This AI output is indicative and should not replace legal audit.")
