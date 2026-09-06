import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()


def generate_fallback_summary(patient, language):

    complaint = patient.get("chief_complaint", "Not available")
    symptoms = ", ".join(patient.get("symptoms", []))

    if language == "हिंदी":
        return (
            f"उपलब्ध जानकारी के अनुसार रोगी की मुख्य शिकायत: "
            f"{complaint}। बताए गए लक्षण: {symptoms}। "
            "यह उपलब्ध जानकारी का सारांश है और निदान नहीं है।"
        )

    return (
        f"The patient's main complaint is: {complaint}. "
        f"Reported symptoms include: {symptoms}. "
        "This summary is based on the available information and is not a diagnosis."
    )


def generate_report(patient, language="English"):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return generate_fallback_summary(patient, language)

    try:

        client = genai.Client(api_key=api_key)

        language_instruction = (
            "Write the report in Hindi."
            if language == "हिंदी"
            else
            "Write the report in English."
        )

        prompt = f"""
You are assisting a doctor by creating a concise patient history summary.

{language_instruction}

Patient information:

{json.dumps(patient, indent=2, ensure_ascii=False)}

Create a clear, structured doctor-facing summary.

Include:
1. Patient overview
2. Chief complaint
3. Reported symptoms
4. Relevant medical history
5. Medications and allergies
6. Ayurvedic examination information, if available
7. Red-flag information, if present
8. Points that may require clinical attention

Rules:
- Do NOT diagnose the patient.
- Do NOT prescribe medication.
- Do NOT claim certainty about diseases.
- Clearly distinguish reported information from clinical interpretation.
- If a red flag is present, clearly mention it.
- Keep the language professional and concise.
- This is a clinical summary, not a diagnosis.
"""

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as error:

        return (
            generate_fallback_summary(patient, language)
            + "\n\nAI summary unavailable. Fallback summary displayed."
        )