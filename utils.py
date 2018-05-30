import csv
from pprint import pprint

"""
Database Schema
clan_code: {
	clan_name: <string>,
	clan_level: <number>,
	max_titans_hit: <number>,
	members: {
		member_id: {
			member_name: <string>
			damage: [<number>]
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
				},
				...
			}
		}
	"""
	with open(file_path) as clan_quest_info_file: #File should be a csv
		clan_info_data = csv.reader(clan_quest_info_file, delimiter=',')

		#skip cq line and header
		next(clan_info_data)
		next(clan_info_data)

		clan_code = "gg8e6"
		clan_name = "Mistborns"

		member_dictionary = {}

		for member in clan_info_data:
			member_dictionary[member[2]] = {
				"member_name": member[1].replace("<MST>", "").strip(),
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
			last_level_duration: <string>,
			start_time: <string>,
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
	with open(file_path) as clan_quest_info_file: #File should be a csv
		clan_quest_info_data = csv.reader(clan_quest_info_file, delimiter=',') #Change json.load to csv.reader

		cq = (next(clan_quest_info_data)) #Get cq on first line
		cq = cq[0] #CQ stored as number
		#0 - Rank
                #1 - Name
                #2 - ID/Code
                #3 - Damage
		next(clan_quest_info_data) #Skip header line
		
		#TODO: replace hard coded clan code
		clan_code = "gg8e6"
		clan_level = cq.replace("CQ", "").strip()
		#clan_level = clan_quest_info_data["clan_level"] #2 option, 1) Read file name and get cq lvl or in the file name we add cq lvl
		#last_level_duration = clan_quest_info_data["last_level_duration"] #Unable to track
		#start_time = clan_quest_info_data["start_time"] #Unable to track

		member_dictionary = {}

		for member in clan_quest_info_data:
			member_dictionary[member[2]] = {
				"member_name": member[1].replace("<MST>", "").strip(),
				#"max_stage": member["max_stage"], #Unable to track
				"damage": member[3],
				#"clan_crates_shared": member["crates_shared"] #Unable to track
			}

		clan_quest_info = {
			clan_code: {
				"clan_level": clan_level,
				#"last_level_duration": last_level_duration, #Need to be removed, unable to track
				#"start_time": start_time, #Need to be removed, unable to track
				"members": member_dictionary
			}
		}

		return clan_quest_info
