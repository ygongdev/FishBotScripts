from firebaseConfig import firebase
from config import CLAN_CODE
from googleapiclient import discovery
from pprint import pprint
from config import GOOGLE_SPREADSHEET_ID

def read_from_firebase():
	database = firebase.database()
	# each member is one row
	members = database.child("clans").child(CLAN_CODE).get().val()["members"]
	max_titans_hit = database.child("clans").child(CLAN_CODE).get().val()["max_titans_hit"]
	spreadsheet_info = []
	spreadsheet_last_week_damage = []
	spreadsheet_damage = []
	for member_id, member_info in members.items():
		pprint(member_info)
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

		spreadsheet_info.append([member_id, name, last_week_max_stage, max_stage, last_week_clan_quest_participation, clan_quest_participation, clan_crates_shared])

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

def write_to_firebase(data):
	memberInfo = data["memberInfo"]
	LWDInfo = data["LWDInfo"]
	damageInfo = data["damageInfo"]

	database = firebase.database()
	name_to_id = {}

	memberInfoJson = {}
	for member in memberInfo:
		member_id = member[0]
		member_name = member[1]
		last_week_max_stage = member[2]
		max_stage = member[3]
		last_week_clan_quest_participation = member[4]
		clan_quest_participation = member[5]
		clan_crates_shared = member[6]

		name_to_id[member_name] = member_id
		memberInfoJson[member_id] = {
			"member_name": member_name,
			"last_week_max_stage": last_week_max_stage,
			"max_stage": max_stage,
			"last_week_clan_quest_participation": last_week_clan_quest_participation,
			"clan_quest_participation": clan_quest_participation,
			"clan_crates_shared": clan_crates_shared,
		}

	LWDInfoJson = {}
	for member in LWDInfo:
		member_name = member[0]
		last_week_damage = member[1:]
		memberInfoJson[name_to_id[member_name]]["last_week_damage"] = last_week_damage

	damageJson = {}
	for member in damageInfo:
		member_name = member[0]
		damage = member[1:]
		memberInfoJson[name_to_id[member_name]]["damage"] = damage

	database.child("clans").child(CLAN_CODE).child("members").update(memberInfoJson)

def firebase_to_google_spreadsheet(credentials):
	service = discovery.build('sheets', 'v4', credentials=credentials)

	data = read_from_firebase()
	members_info = data["info"]
	members_last_week_damage = data["last_week_damage"]
	members_damage = data["damage"]

	minInfoRow = 4
	maxInfoRow = 53
	minInfoCol = "B"
	maxInfoCol = "H"

	minDamageRow = 4
	maxDamageRow = 53
	minDamageCol = "O"
	maxDamageCol = "AQ"

	minLWDRow = 4
	maxLWDRow = 53
	minLWDCol = "AS"
	maxLWDCol = "BU"

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
					"range": minDamageCol + str(minDamageRow) + ":" + maxDamageCol + str(maxDamageRow),
					"values": members_damage
				},
				{
					"range": minLWDCol + str(minLWDRow) + ":" + maxLWDCol + str(maxLWDRow),
					"values": members_last_week_damage
				},
			]
		}
	)

	response = request.execute()

	# Removing kicked or left members from the spreadsheet.
	clear_request = service.spreadsheets().values().batchClear(
		spreadsheetId=GOOGLE_SPREADSHEET_ID,
		body={
			"ranges": [
				minInfoCol + str(minInfoRow + len(members_info)) + ":" + maxInfoCol + str(maxInfoRow),
				minDamageCol + str(minDamageRow + len(members_damage)) + ":" + maxDamageCol + str(maxDamageRow),
				minLWDCol + str(minLWDRow + len(members_last_week_damage)) + ":" + maxLWDCol + str(maxLWDRow)
			]
		}
	)

	clear_request.execute()

def google_spreadsheet_to_firebase(credentials):
	service = discovery.build('sheets', 'v4', credentials=credentials)
	minInfoRow = 4
	maxInfoRow = 53
	minInfoCol = "B"
	maxInfoCol = "H"

	minDamageRow = 4
	maxDamageRow = 53
	minDamageCol = "O"
	maxDamageCol = "AQ"

	minLWDRow = 4
	maxLWDRow = 53
	minLWDCol = "AS"
	maxLWDCol = "BU"

	request = service.spreadsheets().values().batchGet(
		spreadsheetId=GOOGLE_SPREADSHEET_ID,
		ranges=[
			minInfoCol + str(minInfoRow) + ":" + maxInfoCol + str(maxInfoRow),
			minDamageCol + str(minDamageRow) + ":" + maxDamageCol + str(maxDamageRow),
			minLWDCol + str(minLWDRow) + ":" + maxLWDCol + str(maxLWDRow),
		],
		valueRenderOption="UNFORMATTED_VALUE"
	)

	response = request.execute()

	valueRanges = response["valueRanges"]

	memberInfo = valueRanges[0]["values"]
	damageInfo = valueRanges[1]["values"]
	LWDInfo = valueRanges[2]["values"]

	write_to_firebase({
		"memberInfo": memberInfo,
		"damageInfo": damageInfo,
		"LWDInfo": LWDInfo,
	})

