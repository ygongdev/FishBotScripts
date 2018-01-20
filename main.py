import sys
from firebaseConfig import firebase
from config import CLAN_CODE, CLAN_INFO_FILE_PATH, CLAN_QUEST_INFO_FILE_PATH
from clanDatabase import ClanDatabase

def main():
	db = ClanDatabase(
		CLAN_CODE,
		CLAN_INFO_FILE_PATH,
		CLAN_QUEST_INFO_FILE_PATH,
		firebase.database()
	)

	process_command(db)

def process_command(db):
	try:
		command = input(
			"Available commands:\n\n" +
			"1. (initial_load): populates the database with clan info (note: no clan quests), if your clan is not in the database. Else, it fails and does nothing.\n\n" +
			"2. (update_stats): updates all clan members' stats in the database (note: no clan quest damage).\n\n" +
			"3. (update_damages): updates all clan members' damages in the database (adds damage to an array of existing damages).\n\n" +
			"4. (weekly_reset): move current week's stats and damages to last week and reset current week.\n\n"
		)

		if (command == "initial_load"):
			db.initial_load_clan_info()
		elif (command == "update_stats"):
			db.update_everyone_stats()
		elif (command == "update_damages"):
			db.update_everyone_damage()
		elif (command == "weekly_reset"):
			db.weekly_reset()
		else:
			print("Sorry command not understood")

	except Exception as error:
		print(error)

if __name__ == "__main__":
	main()
