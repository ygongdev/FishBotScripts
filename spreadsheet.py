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
	#spreadsheet_last_week_damage = []
	spreadsheet_damage = []
	for member_id, member_info in members.items():
		name = member_info["member_name"]

		spreadsheet_info.append([member_id, name])

		# last_week_damage = []
		# if "last_week_damage" in member_info:
		# 	last_week_damage = member_info["last_week_damage"]

		damage = []
		if "damage" in member_info:
			damage = member_info["damage"]

		#spreadsheet_last_week_damage.append([name] + last_week_damage)
		spreadsheet_damage.append(damage)

	return {
		"info": spreadsheet_info,
		#"last_week_damage": spreadsheet_last_week_damage,
		"damage": spreadsheet_damage,
		"max_titans_hit": max_titans_hit,
	}

def write_to_firebase(data):
	memberInfo = data["memberInfo"]
	#LWDInfo = data["LWDInfo"]
	damageInfo = data["damageInfo"]
	maxTitansHit = data["maxTitansHit"]

	database = firebase.database()

	database.child("clans").child(CLAN_CODE).update({
		"max_titans_hit": maxTitansHit
	})

	name_to_id = {}

	memberInfoJson = {}
	for member in memberInfo:
		member_id = member[0]
		member_name = member[1]

		name_to_id[member_name] = member_id
		memberInfoJson[member_id] = {
			"member_name": member_name
		}

	# LWDInfoJson = {}
	# for member in LWDInfo:
	# 	member_name = member[0]
	# 	last_week_damage = member[1:]
	# 	memberInfoJson[name_to_id[member_name]]["last_week_damage"] = last_week_damage

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
	#members_last_week_damage = data["last_week_damage"]
	members_damage = data["damage"]
	max_titans_hit = data["max_titans_hit"]

	minInfoRow = 6
	maxInfoRow = 55
	minInfoCol = "A"
	maxInfoCol = "B"

	minDamageRow = 6
	maxDamageRow = 55
	minDamageCol = "H"
	maxDamageCol = "AO"

	# minLWDRow = 4
	# maxLWDRow = 53
	# minLWDCol = "AS"
	# maxLWDCol = "BU"

	maxTitanHitsRow = 1
	maxTitanHitsCol = "F"

	clear_request_body = {
		"ranges": [
			minInfoCol + str(minInfoRow + len(members_info)) + ":" + maxInfoCol + str(maxInfoRow),
			minDamageCol + str(minDamageRow + len(members_damage)) + ":" + maxDamageCol + str(maxDamageRow),
			#minLWDCol + str(minLWDRow + len(members_last_week_damage)) + ":" + maxLWDCol + str(maxLWDRow),
		]
	}

	if not members_damage or is_members_damage_empty(members_damage):
		clear_request_body["ranges"].append(minDamageCol + str(minDamageRow) + ":" + maxDamageCol + str(maxDamageRow))

	# Removing kicked or left members from the spreadsheet.
	clear_request = service.spreadsheets().values().batchClear(
		spreadsheetId=GOOGLE_SPREADSHEET_ID,
		body=clear_request_body,
	)

	clear_request.execute()

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
				# {
				# 	"range": minLWDCol + str(minLWDRow) + ":" + maxLWDCol + str(maxLWDRow),
				# 	"values": members_last_week_damage
				# },
				{
					"range": maxTitanHitsCol + str(maxTitanHitsRow),
					"values": [[int(max_titans_hit)]]
				},
			]
		}
	)

	response = request.execute()

def google_spreadsheet_to_firebase(credentials):
	service = discovery.build('sheets', 'v4', credentials=credentials)
	minInfoRow = 6
	maxInfoRow = 55
	minInfoCol = "A"
	maxInfoCol = "B"

	minDamageRow = 6
	maxDamageRow = 55
	minDamageCol = "H"
	maxDamageCol = "AO"

	# minLWDRow = 4
	# maxLWDRow = 53
	# minLWDCol = "AS"
	# maxLWDCol = "BU"

	maxTitanHitsRow = 1
	maxTitanHitsCol = "F"

	request = service.spreadsheets().values().batchGet(
		spreadsheetId=GOOGLE_SPREADSHEET_ID,
		ranges=[
			minInfoCol + str(minInfoRow) + ":" + maxInfoCol + str(maxInfoRow),
			minDamageCol + str(minDamageRow) + ":" + maxDamageCol + str(maxDamageRow),
			#minLWDCol + str(minLWDRow) + ":" + maxLWDCol + str(maxLWDRow),
			maxTitanHitsCol + str(maxTitanHitsRow)
		],
		valueRenderOption="FORMATTED_VALUE"
	)

	response = request.execute()

	valueRanges = response["valueRanges"]

	memberInfo = valueRanges[0]["values"]
	damageInfo = valueRanges[1]["values"]
	#LWDInfo = valueRanges[2]["values"]
	maxTitansHit = int(valueRanges[2]["values"][0][0])

	write_to_firebase({
		"memberInfo": memberInfo,
		"damageInfo": damageInfo,
		#"LWDInfo": LWDInfo,
		"maxTitansHit": maxTitansHit,
	})

def increment_spreadsheet_column(column, increment):
	lastChar = column[-1]

	for i in range(increment):
		if lastChar < "Z":
			lastChar = chr(ord(lastChar) + 1)
			column = column[:-1] + lastChar
		else:
			length = len(column)
			column = ""
			for j in range(length + 1):
				column += "A"
			lastChar = "A"

	return column

def is_members_damage_empty(members_damage):
	for damage in members_damage:
		if len(damage) > 1:
			return False
	return True






