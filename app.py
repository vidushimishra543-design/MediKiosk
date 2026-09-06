import streamlit as st
import json
from pathlib import Path

from translations import TRANSLATIONS
from report_generator import generate_report


# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------

st.set_page_config(
    page_title="MediKiosk",
    page_icon="🏥",
    layout="wide"
)


# ---------------------------------------
# LOAD DATA
# ---------------------------------------

BASE_DIR = Path(__file__).parent

# Test patient data
TEST_DATA_DIR = BASE_DIR / "test_data"

patient_options = {
    "🟢 Normal Patient": BASE_DIR / "sample_data.json",
    "🔴 Red-Flag Test Patient": TEST_DATA_DIR / "red_flag_patient.json"
}

selected_patient = st.sidebar.selectbox(
    "Select Test Patient",
    list(patient_options.keys())
)

DATA_FILE = patient_options[selected_patient]

with open(DATA_FILE, "r", encoding="utf-8") as file:
    patient = json.load(file)

# ---------------------------------------
# LANGUAGE
# ---------------------------------------

st.sidebar.title("🏥 MediKiosk")

language = st.sidebar.selectbox(
    "Language / भाषा",
    ["English", "हिंदी"]
)

t = TRANSLATIONS[language]


# ---------------------------------------
# HEADER
# ---------------------------------------

st.title(t["title"])

st.caption(t["disclaimer"])


# ---------------------------------------
# TABS
# ---------------------------------------

overview_tab, history_tab, ayurveda_tab, documents_tab, doctor_tab = st.tabs([
    f"👤 {t['overview']}",
    f"🩺 {t['history']}",
    f"🌿 {t['ayurveda']}",
    f"📄 {t['documents']}",
    f"👨‍⚕️ {t['doctor_review']}"
])


# =======================================
# OVERVIEW TAB
# =======================================

with overview_tab:

    st.header(t["patient_info"])

    details = patient.get("patient_details", {})

    col1, col2, col3 = st.columns(3)

    col1.metric(t["name"], details.get("name", "Not available"))
    col2.metric(t["age"], details.get("age", "Not available"))
    col3.metric(t["gender"], details.get("gender", "Not available"))

    st.divider()

    st.header(t["red_flag"])

    red_flag = patient.get("red_flag", {})

    if red_flag.get("status", False):

        st.error(
            f"🚨 {t['urgent']}\n\n"
            f"Reason: {red_flag.get('reason', 'Not specified')}\n\n"
            "This is an alert for clinical review and is not a diagnosis."
        )

    else:

        st.success(t["no_red_flag"])

    st.divider()

    st.header(t["chief_complaint"])

    st.info(patient.get("chief_complaint", "Not available"))


# =======================================
# CLINICAL HISTORY TAB
# =======================================

with history_tab:

    st.header(t["symptoms"])

    for symptom in patient.get("symptoms", []):
        st.write(f"• {symptom}")

    st.divider()

    st.header(t["medical_history"])

    for item in patient.get("medical_history", []):
        st.write(f"• {item}")

    st.header(t["medications"])

    for item in patient.get("medications", []):
        st.write(f"• {item}")

    st.header(t["allergies"])

    for item in patient.get("allergies", []):
        st.write(f"• {item}")


# =======================================
# AYURVEDA TAB
# =======================================

with ayurveda_tab:

    assessment = patient.get("ayurvedic_assessment", {})

    # TRIVIDHA
    with st.expander(f"🌿 {t['trividha']}", expanded=True):

        trividha = assessment.get("trividha_pariksha", {})

        st.subheader("👁️ Darshana — Observation")
        st.write(trividha.get("darshana", "Not assessed"))

        st.subheader("✋ Sparshana — Touch / Palpation")
        st.write(trividha.get("sparshana", "Not assessed"))

        st.subheader("💬 Prashna — Questioning")
        st.write(trividha.get("prashna", "Not assessed"))

    # ASHTAVIDHA
    with st.expander(f"🌿 {t['ashtavidha']}"):

        ashtavidha = assessment.get("ashtavidha_pariksha", {})

        labels = {
            "nadi": "Nadi — Pulse",
            "mutra": "Mutra — Urine",
            "mala": "Mala — Stool",
            "jihva": "Jihva — Tongue",
            "shabda": "Shabda — Voice / Speech",
            "sparsha": "Sparsha — Touch / Body Temperature",
            "drik": "Drik — Eyes / Vision",
            "akriti": "Akriti — Body Appearance"
        }

        for key, label in labels.items():
            st.subheader(label)
            st.write(ashtavidha.get(key, "Not assessed"))

    # DASHAVIDHA
    with st.expander(f"🌿 {t['dashavidha']}"):

        dashavidha = assessment.get("dashavidha_pariksha", {})

        labels = {
            "prakriti": "Prakriti — Constitution",
            "vikriti": "Vikriti — Current Imbalance",
            "sara": "Sara — Tissue Quality",
            "samhanana": "Samhanana — Body Build / Compactness",
            "pramana": "Pramana — Body Measurements",
            "satmya": "Satmya — Adaptation / Suitability",
            "satva": "Satva — Mental Strength",
            "ahara_shakti": "Ahara Shakti — Digestive Capacity",
            "vyayama_shakti": "Vyayama Shakti — Exercise Capacity",
            "vaya": "Vaya — Age"
        }

        for key, label in labels.items():
            st.subheader(label)
            st.write(dashavidha.get(key, "Not assessed"))


# =======================================
# DOCUMENTS TAB
# =======================================

# =======================================
# DOCUMENTS TAB
# =======================================

with documents_tab:

    st.header("📄 " + t["documents"])

    documents_dir = BASE_DIR / "documents"

    if documents_dir.exists():

        pdf_files = list(documents_dir.glob("*.pdf"))

        if pdf_files:

            for pdf in pdf_files:

                st.subheader(f"📄 {pdf.stem}")

                # Original PDF
                with open(pdf, "rb") as file:
                    st.download_button(
                        label=f"📥 Open / Download Original PDF: {pdf.name}",
                        data=file.read(),
                        file_name=pdf.name,
                        mime="application/pdf",
                        key=f"pdf_{pdf.name}"
                    )

                # Corresponding TXT file
                txt_file = documents_dir / f"{pdf.stem}.txt"

                if txt_file.exists():

                    st.markdown("### 📝 Extracted Information")

                    with open(txt_file, "r", encoding="utf-8") as file:
                        extracted_text = file.read()

                    st.text_area(
                        "Extracted Report Information",
                        extracted_text,
                        height=200,
                        key=f"txt_{pdf.name}"
                    )

                else:
                    st.info("No extracted TXT information available.")

                st.divider()

        else:
            st.info("No PDF documents available.")

    else:
        st.info("Medical documents folder not found.")


# =======================================
# DOCTOR REVIEW TAB
# =======================================

with doctor_tab:

    st.header(t["final_summary"])

    if st.button("Generate Summary"):

        with st.spinner("Generating summary..."):

            summary = generate_report(patient, language)

            st.success(summary)

    st.divider()

    st.header(t["doctor_notes"])

    st.text_area(
        "Notes",
        height=200,
        placeholder="Doctor can write additional observations here..."
    )


# ---------------------------------------
# FOOTER
# ---------------------------------------

st.divider()

st.caption(t["disclaimer"])