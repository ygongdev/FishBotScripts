import pyrebase

config = {
    "apiKey": "AIzaSyCoH0PdIWl5x_xIrb0V54TB0svAw2i4p3w",
    "authDomain": "tt2discordbot.firebaseapp.com",
    "databaseURL": "https://tt2discordbot.firebaseio.com",
    "projectId": "tt2discordbot",
    "storageBucket": "tt2discordbot.appspot.com",
    "messagingSenderId": "834055864551"
}

firebase = pyrebase.initialize_app(config)