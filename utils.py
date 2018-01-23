import json
from pprint import pprint

"""
Database Schema

clan_code: {
	clan_name: <string>,
	clan_level: <number>,
	max_titans_hit: <number>
	members: {
		member_id: {
			member_name: <string>
			max_stage: <number>
			last_week_max_stage: <number>
			damage: [<number>]
			last_week_damage: [<number>]
			clan_quest_participation: <number>
			last_week_clan_quest_participation: <number>
			clan_crates_shared: <number>
		},
		...
	}
}
"""

def parse_clan_info(file_path):
	"""
	Returns
		clan_code: {
			clan_name: <string>,
			members: {
				member_id: {
					member_name: <string>
					max_stage: <number>
					clan_quest_participation: <number>
					clan_crates_shared: <number>
				},
				...
			}
		}
	"""
	with open(file_path) as clan_info_file:
		clan_info_data = json.load(clan_info_file)

		clan_code = clan_info_data["members"][0]["clan_code"]
		clan_name = clan_info_data["members"][0]["clan_name"]

		member_dictionary = {}

		for member in clan_info_data["members"]:
			member_dictionary[member["player_code"]] = {
				"member_name": member["name"].replace("<MST>", "").strip(),
				"max_stage": member["max_stage"],
				"clan_quest_participation": member["weekly_dungeon_count"],
				"clan_crates_shared": member["crates_shared"],
			}

		clan_info = {
			clan_code: {
				"clan_name": clan_name,
				"members": member_dictionary
			}
		}

		return clan_info

def parse_clan_quest_info(file_path):
	"""
	Returns
		clan_code: {
			last_level_duration: <array>,
			start_time: <string>
			clan_level: <number>,
			members: {
				member_id: {
					member_name: <string>
					max_stage: <number>
					damage: <number>
					clan_crates_shared: <number>
				},
				...
			}
		}
	"""
	with open(file_path) as clan_quest_info_file:
		clan_quest_info_data = json.load(clan_quest_info_file)

		clan_code = clan_quest_info_data["contributions"][0]["clan_code"]
		clan_level = clan_quest_info_data["clan_level"]
		last_level_duration = clan_quest_info_data["last_level_duration"]
		start_time = clan_quest_info_data["start_time"]

		member_dictionary = {}

		for member in clan_quest_info_data["contributions"]:
			member_dictionary[member["player_code"]] = {
				"member_name": member["name"].replace("<MST>", "").strip(),
				"max_stage": member["max_stage"],
				"damage": member["contribution"],
				"clan_crates_shared": member["crates_shared"]
			}

		clan_quest_info = {
			clan_code: {
				"clan_level": clan_level,
				"last_level_duration": last_level_duration,
				"start_time": start_time,
				"members": member_dictionary
			}
		}

		return clan_quest_info