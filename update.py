from config import firebase
from utils import parse_clan_info, parse_clan_quest_info

CLAN_INFO_FILE_PATH = "data/tt2_clan_info.json"
CLAN_QUEST_INFO_FILE_PATH = "data/tt2_clan_quest_info.json"

database = firebase.database()
clans_reference = database.child("clans")

info = parse_clan_info(CLAN_INFO_FILE_PATH)

clans_reference.update(info)


