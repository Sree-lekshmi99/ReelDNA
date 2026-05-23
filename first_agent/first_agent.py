from dotenv import load_dotenv
from google import genai

# Load your API key
load_dotenv()

# Initialize the client
client = genai.Client()

# Create an interaction with the "Antigravity" managed agent
interaction = client.interactions.create(
    agent="antigravity-preview-05-2026",
    input="Install the matplotlib package, verify its installation, and report back.",
    environment="remote"
)

# Output results
print(f"Status: {interaction.status}")
print(f"Output: {interaction.output_text}")
