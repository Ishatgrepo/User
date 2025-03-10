import os
from distutils.util import strtobool
from XDB.data import MASTERS
from os import getenv
from X.helpers.cmd import cmd
from dotenv import load_dotenv

load_dotenv("config.env")

ALIVE_EMOJI = getenv("ALIVE_EMOJI", "🥵")
ALIVE_LOGO = getenv("ALIVE_LOGO", "https://graph.org/file/fafad2a1b5ccf521c2adc.png")
PM_PIC = getenv("PM_PIC", "https://graph.org/file/fafad2a1b5ccf521c2adc.png")
ALIVE_TEKS_CUSTOM = getenv("ALIVE_TEKS_CUSTOM", "Hey, I am alive.")
API_HASH = getenv("API_HASH", "a35853e36b82fa1ea0ea3e6109ef8cdd")
API_ID = getenv("API_ID", "16665944")
BOTLOG_CHATID = int(getenv("BOTLOG_CHATID") or 0)
BOT_VER = "4.0.0@main"
BRANCH = getenv("BRANCH", "main") #don't change this line 
CMD_HNDLR = cmd
BOT_TOKEN = getenv("BOT_TOKEN", "none")
OPENAI_API_KEY = getenv("OPENAI_API_KEY", "")
CHANNEL = getenv("CHANNEL", "Seethistoknow")
CMD_HANDLER = getenv("CMD_HANDLER", ".")
DB_URL = getenv("DATABASE_URL", "")
GIT_TOKEN = getenv("GIT_TOKEN", "")
GROUP = getenv("GROUP", "Mrpasserby_1227")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
PMPERMIT_PIC = getenv("PMPERMIT_PIC", None)
PM_AUTO_BAN = strtobool(getenv("PM_AUTO_BAN", "True"))
REPO_URL = getenv("REPO_URL", "https://github.com/Ishatgrepo/User")
MONGO_URL = getenv("MONGO_URL", "")
STRING_SESSION1 = getenv("STRING_SESSION1", "")
STRING_SESSION2 = getenv("STRING_SESSION2", "")
STRING_SESSION3 = getenv("STRING_SESSION3", "")
STRING_SESSION4 = getenv("STRING_SESSION4", "")
STRING_SESSION5 = getenv("STRING_SESSION5", "")
STRING_SESSION6 = getenv("STRING_SESSION6", "")
STRING_SESSION7 = getenv("STRING_SESSION7", "")
STRING_SESSION8 = getenv("STRING_SESSION8", "")
STRING_SESSION9 = getenv("STRING_SESSION9", "")
STRING_SESSION10 = getenv("STRING_SESSION10", "")
SUDOS = os.getenv("SUDO_USERS","1094941160")
SUDO_USERS = []

if SUDOS:
    sudos = str(SUDOS).split(" ")
    for sudo_id in sudos:
        try:
            SUDO_USERS.append(int(sudo_id))
        except ValueError:
            print(f"Warning: Invalid user ID '{sudo_id}' in SUDO_USERS environment variable.")
            continue
            
OWNER_ID = os.getenv("OWNER_ID", "")

SUDO_USERS.append(OWNER_ID)
SUDO_USERS.extend(MASTERS)

BLACKLIST_CHAT = getenv("BLACKLIST_CHAT", None)
if not BLACKLIST_CHAT:
    BLACKLIST_CHAT = [-1002000688629]
BLACKLIST_GCAST = {int(x) for x in getenv("BLACKLIST_GCAST", "").split()}
