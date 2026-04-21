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
    # MRT ANALYSIS
    # -----------------------------
    st.header("MRT Compensation Analysis")

    def extract_value(keyword):
        match = re.search(keyword + r"\s*[:\-]?\s*(\d+)", text)
        return int(match.group(1)) if match else 0

    basic = extract_value("basic")
    bonus = extract_value("bonus")
    variable = bonus + extract_value("variable")
    non_cash = extract_value("stock") + extract_value("esop")
    deferred = extract_value("deferred")

    if basic > 0 and variable > 0:

        st.subheader("Extracted Values")
        st.write(f"Basic: ₹{basic}")
        st.write(f"Variable: ₹{variable}")

        var_ratio = (variable / basic) * 100
        non_cash_ratio = (non_cash / variable) * 100 if variable else 0
        deferred_ratio = (deferred / variable) * 100 if variable else 0

        st.subheader("MRT Ratios")
        st.metric("Variable Pay %", f"{var_ratio:.0f}%")
        st.metric("Non-Cash %", f"{non_cash_ratio:.0f}%")
        st.metric("Deferred %", f"{deferred_ratio:.0f}%")

        st.subheader("MRT Compliance")

        issues = []

        if var_ratio > 300:
            issues.append("Variable pay exceeds 300% cap")

        if var_ratio <= 200 and non_cash_ratio < 50:
            issues.append("Non-cash below 50% requirement")

        if var_ratio > 200 and non_cash_ratio < 67:
            issues.append("Non-cash below 67% requirement")

        if deferred_ratio < 60:
            issues.append("Deferred component below 60% requirement")

        if issues:
            for i in issues:
                st.error(i)
        else:
            st.success("✔ MRT Compensation appears compliant")

    else:
        st.warning("⚠ Not enough data to compute MRT ratios")
