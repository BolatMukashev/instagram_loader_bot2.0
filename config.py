import os
from dotenv import load_dotenv

load_dotenv()

INST_USERNAME = os.getenv('INST_USERNAME')
INST_PASSWORD = os.getenv('INST_PASSWORD')
