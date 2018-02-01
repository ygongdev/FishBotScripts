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

	start_times = []
	try:
		start_times = database.child("clans").child(CLAN_CODE).get().val()["clan_quest_start_time"]
	except KeyError as keyError:
		pass

	durations = []
	try:
		durations = database.child("clans").child(CLAN_CODE).get().val()["clan_quest_duration"]
	except KeyError as keyError:
		pass

	last_week_start_times = []
	try:
		last_week_start_times = database.child("clans").child(CLAN_CODE).get().val()["last_week_clan_quest_start_time"]
	except KeyError as keyError:
		pass

	last_week_durations = []
	try:
		last_week_durations = database.child("clans").child(CLAN_CODE).get().val()["last_week_clan_quest_duration"]
	except KeyError as keyError:
		pass

	return {
		"info": spreadsheet_info,
		"last_week_damage": spreadsheet_last_week_damage,
		"damage": spreadsheet_damage,
		"max_titans_hit": max_titans_hit,
		"start_time": start_times,
		"duration": durations,
		"last_week_start_time": last_week_start_times,
		"last_week_duration": last_week_durations,
	}

def write_to_firebase(data):
	memberInfo = data["memberInfo"]
	LWDInfo = data["LWDInfo"]
	damageInfo = data["damageInfo"]
	maxTitansHit = data["maxTitansHit"]
	startTimeInfo = data["startTimeInfo"]
	durationInfo = data["durationInfo"]
	last_week_start_time = data["lastWeekStartTime"]
	last_week_duration = data["lastWeekDuration"]

	database = firebase.database()

	database.child("clans").child(CLAN_CODE).update({
		"max_titans_hit": maxTitansHit,
		"clan_quest_start_time": startTimeInfo,
		"clan_quest_duration": durationInfo,
		"last_week_start_time": last_week_start_time,
		"last_week_duration": last_week_duration
	})

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
	max_titans_hit = data["max_titans_hit"]
	start_time = data["start_time"]
	duration = data["duration"]
	last_week_start_time = data["last_week_start_time"]
	last_week_duration = data["last_week_duration"]

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

	LWSTRow = 54
	minLWSTCol = "AT"
	maxLWSTCol = "BU"

	LWDuRow = 55
	minLWDuCol = "AT"
	maxLWDuCol = "BU"

	maxTitanHitsRow = 55
	maxTitanHitsCol = "J"

	startTimeRow = 54
	minStartTimeCol = "P"
	maxStartTimeCol = "AQ"

	durationRow = 55
	minDurationCol = "P"
	maxDurationCol = "AQ"

	clear_request_body = {
		"ranges": [
			minInfoCol + str(minInfoRow + len(members_info)) + ":" + maxInfoCol + str(maxInfoRow),
			minDamageCol + str(minDamageRow + len(members_damage)) + ":" + maxDamageCol + str(maxDamageRow),
			minLWDCol + str(minLWDRow + len(members_last_week_damage)) + ":" + maxLWDCol + str(maxLWDRow),
		]
	}

	if not members_damage or is_members_damage_empty(members_damage):
		clear_request_body["ranges"].append(minDamageCol + str(minDamageRow) + ":" + maxDamageCol + str(maxDamageRow))

	if not start_time:
		clear_request_body["ranges"].append(minStartTimeCol + str(startTimeRow) + ":" + maxStartTimeCol + str(startTimeRow))

	if not duration:
		clear_request_body["ranges"].append(minDurationCol + str(durationRow) + ":" + maxDurationCol + str(durationRow))

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
				{
					"range": minLWDCol + str(minLWDRow) + ":" + maxLWDCol + str(maxLWDRow),
					"values": members_last_week_damage
				},
				{
					"range": maxTitanHitsCol + str(maxTitanHitsRow),
					"values": [[int(max_titans_hit)]]
				},
				{
					"range": minStartTimeCol + str(startTimeRow) + ":" + maxStartTimeCol + str(startTimeRow),
					"values": [start_time]
				},
				{
					"range": minDurationCol + str(durationRow) + ":" + maxDurationCol + str(durationRow),
					"values": [duration]
				},
				{
					"range": minLWSTCol + str(LWSTRow) + ":" + maxLWSTCol + str(LWSTRow),
					"values": [last_week_start_time]
				},
				{
					"range": minLWDuCol + str(LWDuRow) + ":" + maxLWDuCol + str(LWDuRow),
					"values": [last_week_duration]
				},
			]
		}
	)

	response = request.execute()

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

	LWSTRow = 54
	minLWSTCol = "AT"
	maxLWSTCol = "BU"

	LWDuRow = 55
	minLWDuCol = "AT"
	maxLWDuCol = "BU"

	maxTitanHitsRow = 55
	maxTitanHitsCol = "J"

	startTimeRow = 54
	minStartTimeCol = "P"
	maxStartTimeCol = "AQ"

	durationRow = 55
	minDurationCol = "P"
	maxDurationCol = "AQ"

	request = service.spreadsheets().values().batchGet(
		spreadsheetId=GOOGLE_SPREADSHEET_ID,
		ranges=[
			minInfoCol + str(minInfoRow) + ":" + maxInfoCol + str(maxInfoRow),
			minDamageCol + str(minDamageRow) + ":" + maxDamageCol + str(maxDamageRow),
			minLWDCol + str(minLWDRow) + ":" + maxLWDCol + str(maxLWDRow),
			maxTitanHitsCol + str(maxTitanHitsRow),
			minStartTimeCol + str(startTimeRow) + ":" + maxStartTimeCol + str(startTimeRow),
			minDurationCol + str(durationRow) + ":" + maxDurationCol + str(durationRow),
			minLWSTCol + str(LWSTRow) + ":" + maxLWSTCol + str(LWSTRow),
			minLWDuCol + str(LWDuRow) + ":" + maxLWDuCol + str(LWDuRow)
		],
		valueRenderOption="FORMATTED_VALUE"
	)

	response = request.execute()

	valueRanges = response["valueRanges"]

	memberInfo = valueRanges[0]["values"]
	damageInfo = valueRanges[1]["values"]
	LWDInfo = valueRanges[2]["values"]
	maxTitansHit = int(valueRanges[3]["values"][0][0])
	startTimeInfo = valueRanges[4]["values"][0]
	durationInfo = valueRanges[5]["values"][0]
	last_week_start_time = []
	try:
		last_week_start_time = valueRanges[6]["values"][0]
	except:
		pass
	last_week_duration = []

	try:
		last_week_duration = valueRanges[7]["values"][0]
	except:
		pass

	write_to_firebase({
		"memberInfo": memberInfo,
		"damageInfo": damageInfo,
		"LWDInfo": LWDInfo,
		"maxTitansHit": maxTitansHit,
		"startTimeInfo": startTimeInfo,
		"durationInfo": durationInfo,
		"lastWeekStartTime": last_week_start_time,
		"lastWeekDuration": last_week_duration,
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






