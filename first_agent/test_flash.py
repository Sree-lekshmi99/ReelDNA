import os
from dotenv import load_dotenv
from google import genai

# 1. Load the API key from your .env file
load_dotenv()

# 2. Initialize the standard Gemini client
client = genai.Client()

# 3. Test a regular text prompt to make sure it works
response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Hello Gemini! I am building a video analyzer app for a hackathon. Confirm you can hear me.",
)

print("--- GEMINI RESPONSE ---")
print(response.text)
print("-----------------------")