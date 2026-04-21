import streamlit as st
import re

st.set_page_config(page_title="Compliance Analyzer", layout="wide")

st.title("Labour Code + MRT Compliance Analyzer")

uploaded = st.file_uploader("Upload Document (TXT format recommended)", type=["txt"])

if uploaded:

    # -----------------------------
    # TEXT EXTRACTION
    # -----------------------------
    try:
        text = uploaded.read().decode("utf-8", errors="ignore").lower()
    except:
        st.error("⚠ Unable to read file. Please upload a TXT file.")
        st.stop()

    st.subheader("Document Preview")
    st.text(text[:500])

    # -----------------------------
    # DOCUMENT TYPE DETECTION
    # -----------------------------
    st.subheader("Document Type")

    if "payslip" in text or "earnings" in text:
        doc_type = "Payslip"
    elif "appointment" in text:
        doc_type = "Appointment Letter"
    elif "register" in text:
        doc_type = "Register"
    else:
        doc_type = "Unknown"

    st.success(f"Detected: {doc_type}")

    # -----------------------------
    # LABOUR COMPLIANCE CHECK
    # -----------------------------
    st.header("Labour Code Compliance")

    checks = {
        "Employee Details": ["employee", "name"],
        "Wage Period": ["period"],
        "Basic Salary": ["basic"],
        "Earnings Breakdown": ["allowance", "salary"],
        "Deductions": ["deduction", "pf", "tax"],
        "Net Pay": ["net"],
        "Payment Date": ["payment"]
    }

    present = []
    missing = []

    for item, keywords in checks.items():
        if any(word in text for word in keywords):
            st.success(f"✔ {item}")
            present.append(item)
        else:
            st.error(f"❌ {item}")
            missing.append(item)

    score = (len(present) / len(checks)) * 100

    # -----------------------------
    # SUMMARY
    # -----------------------------
    st.header("Compliance Summary")

    st.write("### ✅ Present")
    for p in present:
        st.write(f"- {p}")

    st.write("### ❌ Missing")
    for m in missing:
        st.write(f"- {m}")

    st.metric("Compliance Score", f"{score:.0f}%")

    if score >= 80:
        st.success("High Compliance")
    elif score >= 50:
        st.warning("Moderate Compliance")
    else:
        st.error("Low Compliance")

    # -----------------------------
    # DISCLAIMER
    # -----------------------------
    st.header("⚠️ Disclaimer")

    if missing:
        st.write("The document is missing the following elements required under labour compliance:")
        for m in missing:
            st.write(f"- {m}")
    else:
        st.success("Document appears compliant with key labour provisions")

    st.info("This is a preliminary automated check and does not replace legal audit.")

    # -----------------------------
  st.header("🏦 MRT Ratio Analysis (Auto Extracted)")

import re

# -----------------------------
# EXTRACT VALUES FROM DOCUMENT
# -----------------------------
def extract_amount(keywords):
    for k in keywords:
        match = re.search(k + r"\s*[:\-]?\s*(\d+)", text)
        if match:
            return int(match.group(1))
    return 0

fixed_pay = extract_amount(["fixed pay", "basic salary", "basic"])
variable_pay = extract_amount(["variable pay", "bonus", "performance bonus"])
non_cash = extract_amount(["stock", "esop", "non-cash"])
deferred = extract_amount(["deferred"])

# -----------------------------
# SHOW EXTRACTED DATA
# -----------------------------
st.subheader("📊 Extracted Compensation Data")

st.write(f"Fixed Pay: ₹{fixed_pay}")
st.write(f"Variable Pay: ₹{variable_pay}")
st.write(f"Non-Cash Component: ₹{non_cash}")
st.write(f"Deferred Component: ₹{deferred}")

# -----------------------------
# CALCULATE RATIOS
# -----------------------------
if fixed_pay > 0 and variable_pay > 0:

    var_ratio = (variable_pay / fixed_pay) * 100
    non_cash_ratio = (non_cash / variable_pay) * 100 if variable_pay else 0
    deferred_ratio = (deferred / variable_pay) * 100 if variable_pay else 0

    st.subheader("📈 MRT Ratios")

    col1, col2, col3 = st.columns(3)

    col1.metric("Variable Pay %", f"{var_ratio:.0f}%")
    col2.metric("Non-Cash %", f"{non_cash_ratio:.0f}%")
    col3.metric("Deferred %", f"{deferred_ratio:.0f}%")

    # -----------------------------
    # COMPLIANCE CHECK
    # -----------------------------
    st.subheader("⚖️ MRT Compliance Evaluation")

    issues = []

    # Variable cap
    if var_ratio > 300:
        issues.append("Variable pay exceeds 300% cap")

    elif var_ratio > 200:
        st.warning("⚠ Variable pay above 200% → higher non-cash requirement applies")

    # Non-cash rule
    if var_ratio <= 200 and non_cash_ratio < 50:
        issues.append("Non-cash component below 50%")

    if var_ratio > 200 and non_cash_ratio < 67:
        issues.append("Non-cash component below 67%")

    # Deferral rule
    if deferred_ratio < 60:
        issues.append("Deferred component below 60%")

    # Output
    if issues:
        for issue in issues:
            st.error(issue)
    else:
        st.success("✔ MRT Compensation is compliant")

else:
    st.warning("⚠ Unable to extract sufficient MRT data from document")
