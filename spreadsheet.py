from firebaseConfig import firebase
from config import CLAN_CODE
from googleapiclient import discovery
from pprint import pprint
from config import GOOGLE_SPREADSHEET_ID

def read_firebase():
	database = firebase.database()
	# each member is one row
	members = database.child("clans").child(CLAN_CODE).get().val()["members"]
	max_titans_hit = database.child("clans").child(CLAN_CODE).get().val()["max_titans_hit"]
	spreadsheet_info = []
	spreadsheet_last_week_damage = []
	spreadsheet_damage = []
	for member_id, member_info in members.items():
		name = member_info["member_name"]
		last_week_max_stage = None
		if "last_week_max_stage" in member_info:
			last_week_max_stage = member_info["last_week_max_stage"]
		max_stage = member_info["max_stage"]
		last_week_clan_quest_participation = None
		if "last_week_clan_quest_participation" in member_info:
			last_week_clan_quest_participation = member_info["last_week_clan_quest_participation"]
		clan_quest_participation = member_info["clan_quest_participation"]
		clan_crates_shared = member_info["clan_crates_shared"]

		spreadsheet_info.append([name, last_week_max_stage, max_stage, last_week_clan_quest_participation, clan_quest_participation, clan_crates_shared])

		last_week_damage = []
		if "last_week_damage" in member_info:
			last_week_damage = member_info["last_week_damage"]
		damage = []
		if "damage" in member_info:
			damage = member_info["damage"]

		spreadsheet_last_week_damage.append([name] + last_week_damage)
		spreadsheet_damage.append([name] + damage)

	return {
		"info": spreadsheet_info,
		"last_week_damage": spreadsheet_last_week_damage,
		"damage": spreadsheet_damage,
		"max_titans_hit": max_titans_hit
	}

def firebase_to_google_spreadsheet(credentials):
	service = discovery.build('sheets', 'v4', credentials=credentials)

	data = read_firebase()
	members_info = data["info"]
	members_last_week_damage = data["last_week_damage"]
	members_damage = data["damage"]

	minInfoRow = 3
	maxInfoRow = minInfoRow + len(members_info)
	minInfoCol = "B"
	maxInfoCol = "G"

	minDamageRow = 3
	maxDamageRow = minDamageRow + len(members_last_week_damage)
	minDamageCol = "L"
	maxDamageCol = "AN"

	minLWDRow = 3
	maxLWDRow = minLWDRow + len(members_last_week_damage)
	minLWDCol = "AP"
	maxLWDCol = "BR"

	request = service.spreadsheets().values().batchUpdate(
		spreadsheetId=GOOGLE_SPREADSHEET_ID,
		body={
			"valueInputOption": "USER_ENTERED",
			"data": [
				{
					"range": minInfoCol + str(minInfoRow) + ":" + maxInfoCol + str(maxInfoRow),
					"values": members_info
				},
				{
					"range": minLWDCol + str(minLWDRow) + ":" + maxLWDCol + str(maxLWDRow),
					"values": members_last_week_damage
				},
				{
					"range": minDamageCol + str(minDamageRow) + ":" + maxDamageCol + str(maxDamageRow),
					"values": members_damage
				}
			]
		}
	)

	response = request.execute()
	pprint(response)

#read_firebase()
