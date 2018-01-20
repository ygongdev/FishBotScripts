from firebaseConfig import firebase
from utils import parse_clan_info, parse_clan_quest_info

"""
IMPORTANT READ:
Make sure you downloaded the modified version of Pyrebase from github

Due to weird issues with Pyrebase, there are duplicated code snippets
to make sure that it doesn't accidentally use a modified parent reference,
else it might accidentally erase the entire database.
"""

class ClanDatabase():
	def __init__(self, clan_code, clan_info_file_path, clan_quest_info_file_path, database):
		self.database = database
		self.clans_reference = database.child("clans")
		self.clan_code = clan_code
		self.clan_reference = self.clans_reference.child(clan_code)
		self.clan_info_file_path=clan_info_file_path
		self.clan_quest_info_file_path=clan_quest_info_file_path

	def initial_load_clan_info(self):
		try:
			print("Attempting to create new clan database")
			clan_info = parse_clan_info(self.clan_info_file_path)
			self.prevent_modifying_entire_database(database)
			self.clans_reference.update(clan_info)
			print("New clan database has been created successfully")
		except Exception as error:
			print("New clan database failed to be created.")
			print(error)

	def update_everyone_stats(self):
		try:
			clan_members = self.clan_reference.child("members")
			clan_info = parse_clan_info(self.clan_info_file_path)
			clan_info_members = clan_info[self.clan_code]["members"]

			print("Updating clan member stats...")
			for member_id, member_info in clan_members.get().val().items():
				if member_id in clan_info_members:
					member = clan_info_members[member_id]
					name = member["member_name"]
					max_stage = member["max_stage"]
					clan_quest_participation = member["clan_quest_participation"]
					clan_crates_shared = member["clan_crates_shared"]

					self._update_individual_stats(member_id, name, max_stage, clan_quest_participation, clan_crates_shared)
			print("Clan member stats have been updated successfully")
		except Exception as error:
			print("Clan member stats failed to update.")
			print(error)

	def _update_individual_stats(self, member_id, name, max_stage, clan_quest_participation, clan_crates_shared):
		try:
			self.prevent_modifying_entire_database(self.clan_reference.child("members").child(member_id))
			self.clan_reference.child("members").child(member_id).update({
				"member_name": name,
				"max_stage": max_stage,
				"clan_quest_participation": clan_quest_participation,
				"clan_crates_shared": clan_crates_shared,
			})
		except Exception as error:
			print(error)

	def update_everyone_damage(self):
		try:
			clan_members = self.clan_reference.child("members")
			clan_quest_info = parse_clan_quest_info(self.clan_quest_info_file_path)
			clan_quest_members = clan_quest_info[self.clan_code]["members"]

			print("Updating clan members damage...")
			for member_id, member_info in clan_members.get().val().items():
				if member_id in clan_quest_members:
					damage = clan_quest_members[member_id]["damage"]
					self._add_individual_damage(member_id, damage)
				else:
					self._add_individual_damage(member_id, 0)
			print("Clan members damage have been successfully updated.")

		except Exception as error:
			print("Clan members damage update failed.")
			print(error)

		self._update_max_titan_hits()

	def _update_max_titan_hits(self):
		try:
			print("Updating max titan hits...")
			maxTitansHit = self.clan_reference.child("max_titans_hit").get().val()
			if maxTitansHit is None:
				self.prevent_modifying_entire_database(self.clan_reference)
				self.clan_reference.update({"max_titans_hit": 1})
				print("Max titans hit has been successfully updated.")
				return

			self.prevent_modifying_entire_database(self.clan_reference.child("max_titans_hit"))
			self.clan_reference.child("max_titans_hit").set(maxTitansHit + 1)
			print("Max titans hit has been successfully updated.")

		except Exception as error:
			print("Max titans hit update failed.")
			print(error)

	def _add_individual_damage(self, member_id, damage):
		try:
			member_damage = self.clan_reference.child("members").child(member_id).child("damage").get().val()

			if not member_damage:
				raise KeyError("no damage exists")

			member_damage.append(damage)
			self.prevent_modifying_entire_database(self.clan_reference.child("members").child(member_id).child("damage"))
			self.clan_reference.child("members").child(member_id).child("damage").set(member_damage)

		# Member damage array is empty, so we make an new array with the first damage.
		except KeyError as keyError:
			member_damage = [damage]
			self.prevent_modifying_entire_database(self.clan_reference.child("members").child(member_id))
			self.clan_reference.child("members").child(member_id).update({"damage": member_damage})
		except Exception as error:
			print(error)

	def weekly_reset(self):
		self._move_current_week_stats_to_last_week()
		self._reset_max_titans_hit()

	def _move_current_week_stats_to_last_week(self):
		try:
			print("Moving current week stats to last week...")
			self.prevent_modifying_entire_database(self.clan_reference.child("members"))
			members = self.clan_reference.child("members").get().val()
			for member_id, member_info in members.items():
				member = members[member_id]
				old_max_stage = member["max_stage"]
				old_clan_quest_participation = member["clan_quest_participation"]
				old_damage = member["damage"]
				self.clan_reference.child("members").child(member_id).update({
					"last_week_max_stage": old_max_stage,
					"damage": [],
					"last_week_damage": old_damage,
					"clan_quest_participation": 0,
					"last_week_clan_quest_participation": old_clan_quest_participation,
				})
			print("Successfully moved current week stats to last week.")
		except Exception as error:
			print("Failed to move current week stats to last week.")
			print(error)

	def _reset_max_titans_hit(self):
		try:
			print("Resetting max titans hit...")
			self.prevent_modifying_entire_database(self.clan_reference.child("max_titans_hit"))
			self.clan_reference.child("max_titans_hit").set(0)
			print("Max titans hit reset successfully.")
		except Exception as error:
			print("Failed to reset max titans hit.")

	def prevent_modifying_entire_database(self, reference):
		try:
			if reference.child("clans").get().val():
				raise Exception("Modifying entire existing database is not allowed")
			return
		# If reference doesn't have clans node, it's not modifying entire database
		except KeyError as keyError:
			return
