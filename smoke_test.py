import os, cohere
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("COHERE_API_KEY")
assert key, "COHERE_API_KEY missing from .env"
print("Cohere SDK version:", cohere.__version__)

co = cohere.Client(key)
out = co.generate(model="command-r-plus", prompt="Say hello in 3 words.", max_tokens=16, temperature=0)
print("OK generate():", out.generations[0].text.strip())
