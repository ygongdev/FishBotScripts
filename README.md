# FishBotScripts
Contains all of the scripts needed to populate the database and interacting with google spreadsheet for FishBot.

# Table of Contents
1. [Python Environment Setup](#setup)
2. [Configuration](#config)
3. [Firebase](#firebase)
4. [Usage](#usage)

# Set Up <a name="setup"></a> #
First of all, you will need to install Python 3.5 or above. This should include `pip`, which is an useful tool for installing Python packages.

`virtualenv` is a recommended tool for installing Python packages in an isolated environment. But it is also fine if you don't use it.

All of the python packages you need are listed inside `requirements.txt`, so all you need to do is `pip install -r requirements.txt`.
### IMPORTANT : 
You need to install a specific modified version of `Pyrebase` (a Python wrapper around `firebase`) from github. You just need to do this `pip install -e git+https://github.com/jlowin/Pyrebase@dont-modify-self#egg=Pyrebase`. I specifically wrote a function to detect if you're able to modify the entire database. If you are, then most likely, you didn't get this version of `Pyrebase`

## Configuration <a name="config"></a> ##
You'll need to create 2 files, `config.py` and `firebaseConfig.py`, which contains your own personal credentials such as tokens.

### Example `firebaseConfig.py` ###
```
import pyrebase

config = {
    "apiKey": <your api key>,
    "authDomain": <your auth domain>,
    "databaseURL": <your database url>,
    "projectId": <your project id>,
    "storageBucket": <your storage bucket>,
    "messagingSenderId": <your id>
}

firebase = pyrebase.initialize_app(config)
```

### Example `config.py` ###
```
# Modify these to the your data paths. I suggest creating a folder called data and putting them in there.
CLAN_INFO_FILE_PATH = "data/clan_info.json"
CLAN_QUEST_INFO_FILE_PATH = "data/clan_quest_info.json"
CLAN_CODE = <your clan code>
GOOGLE_SPREADSHEET_ID = <your google spreadsheet id>
GOOGLE_SPREADSHEET_API_KEY = <your google spreadsheet api key>
```

## Firebase <a name="firebase"></a> ##
I use firebase to store all of the data. You shouldn't need to touch the database at all, but you can if need to.
Here's an example of the schema. Don't be alert if you don't see all of the fields in the database. They are usually not there if it is the first time you're updating the database or a new member joined.

### Example `Clan Schema` ###
```
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
```
# Usage <a name="usage"></a> #
Before running the program, make sure you have the required json files, there are two, one for clan information, and one for clan quest information. Some commands require these json files. Example of the jsons are shown below.

### Update database from json ###
Start running the program by `python main.py` or `python3 main.py`, whichever one that works.

The program will display some instructions and prompt you to enter a command. There are 4 commands:

`initial_load`: populates the database with clan info (note: no clan quests), if your clan is not in the database. Else, it fails and does nothing. Only use this command if your clan is not inside the database yet.<br>
`update_stats`: updates all clan members' stats in the database (note: no clan quest damage). This reads from the clan info json.<br>
`update_damages`: updates all clan members' damages in the database (adds damage to an array of existing damages). This reads from the clan quest info.<br>
`weekly_reset`: move current week's stats and damages to last week and reset current week. Only do this every week after you've added all the needed data into the database.<br>

### Update spreadsheet from database ###
This approach uses Google OAuth2 with Google Sheets API. I've made the process as simple as opening an url and clicking a button

1. Start running the program by `python update_spreadsheet_from_database.py` or `python3 update_spreadsheet_from_database.py`. This will host a local web server.
2. Go to your browser and type in the link `http://localhost:8080/authorize`. This will prompt you for permission to edit the file.
3. Click allow and now the program will execute. The redirected page should inform you whether or not the execution succeeded or failed.

### Update database from spreadsheet ###
1. Start running the program by `python update_database_from_spreadsheet.py` or `python3 update_database_from_spreadsheet.py`. 
2. Repeat the same steps as above.

### Example `spreadsheet` ###
![spreadsheet](assets/fishbot_scripts_spreadsheet.png "spreadsheet")

### Example `clan information json` ###
```
{
  "members": [
    {
      "artifacts": "53", 
      "clan_code": "gg8e6", 
      "clan_icon": "14", 
      "clan_name": "Mistborns", 
      "country_code": "PT", 
      "crates_shared": "3", 
      "current_avatar": "AvatarUndisputed", 
      "equipment": [
        {
          "EquipmentCategory": "Weapon", 
          "LookID": "Weapon_GoldSword"
        }, 
        {
          "EquipmentCategory": "Hat", 
          "LookID": "Hat_MadHatter"
        }, 
        {
          "EquipmentCategory": "Suit", 
          "LookID": "Suit_DarkAlien"
        }, 
        {
          "EquipmentCategory": "Aura", 
          "LookID": "Aura_Bones"
        }, 
        {
          "EquipmentCategory": "Slash", 
          "LookID": "Slash_Ghost"
        }
      ], 
      "highest_pet_id": "Pet12", 
      "highest_tournament": "-1", 
      "last_used": "2018-01-19 00:08:47", 
      "max_prestige": false, 
      "max_stage": "7028", 
      "name": "<MST> Skim", 
      "player_code": "emmqxr", 
      "rank": 1, 
      "role": "CoLeader", 
      "score": 7028, 
      "titan_points": "1010", 
      "total_clan_quests": "401", 
      "total_tournaments": "23", 
      "weekly_dungeon_count": "17"
    }, 
    ...
```
### Example `clan quest information json` ###
```
{
  "active": false, 
  "clan_goal": 100211636, 
  "clan_level": 353, 
  "contributions": [
    {
      "artifacts": "49", 
      "clan_code": "gg8e6", 
      "clan_icon": "14", 
      "clan_name": "Mistborns", 
      "contribution": 23984702, 
      "country_code": "US", 
      "crates_shared": "4", 
      "current_avatar": "AvatarUndisputed", 
      "equipment": "[{\"EquipmentCategory\": \"Weapon\", \"LookID\": \"Weapon_BlueSword\"}, {\"EquipmentCategory\": \"Hat\", \"LookID\": \"Hat_Ghost\"}, {\"EquipmentCategory\": \"Suit\", \"LookID\": \"Suit_Ghost\"}, {\"EquipmentCategory\": \"Aura\", \"LookID\": \"Aura_Ghost\"}, {\"EquipmentCategory\": \"Slash\", \"LookID\": \"Slash_Ghost\"}]", 
      "highest_pet_id": "Pet14", 
      "highest_tournament": "-1", 
      "last_used": "2018-01-19 01:18:06", 
      "max_prestige": false, 
      "max_stage": "6574", 
      "name": "<MST>Crypto", 
      "player_code": "b6p9bm", 
      "role": "Elder", 
      "titan_points": "1312", 
      "total_clan_quests": "502", 
      "total_tournaments": "36"
    }, 
    ...
```

