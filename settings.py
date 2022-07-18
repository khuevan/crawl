﻿import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", 8000)
DEBUG = os.getenv("DEBUG", False)
CHROME_PATH = os.environ.get("CHROME_PATH")
MONGODB_CONNSTRING = os.environ.get("MONGODB_CONNSTRING")
