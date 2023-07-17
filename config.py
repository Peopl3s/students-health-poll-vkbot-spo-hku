import os
from dotenv import load_dotenv

load_dotenv()

settings = {
    'TOKEN': os.getenv('TOKEN'),
    'VK_GROUP_ID': os.getenv('VK_GROUP_ID'),
    'LOG_FILE': os.getenv('LOG_FILE'),
    'CREDS_FILE': os.getenv('CREDS_FILE')
}
