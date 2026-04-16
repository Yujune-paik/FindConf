import os
from dotenv import load_dotenv

load_dotenv()

OPENALEX_API_KEY = os.getenv("OPENALEX_API_KEY", "")
OPENALEX_BASE_URL = "https://api.openalex.org"
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "")
