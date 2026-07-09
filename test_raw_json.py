import json
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

prompt = """
Analyze this resume snippet and return a JSON object with these keys: score (int), strengths (list), weaknesses (list).
Do not return any extra text, markdown formatting, or markdown code blocks like ```json. Just return raw text.

Resume: "Mechanical Engineer transitioning to AI. Expert in Python. Built an IoT Irrigation system."
"""

print("Requesting raw JSON text...")
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt
)

raw_text = response.text
print(f"\n--- Raw Model Output ---\n{raw_text}\n------------------------")

try:
    parsed_data = json.loads(raw_text.strip())
    print("\n✅ Success! Python successfully parsed the raw string into JSON.")
except Exception as e:
    print(f"\n❌ CRASH! Standard Python json.loads failed: {e}")