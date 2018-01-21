import google.oauth2.credentials
import google_auth_oauthlib.flow
from flask import Flask, session, redirect, request, url_for
from spreadsheet import google_spreadsheet_to_firebase
import os

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
app = Flask(__name__)
app.secret_key = "lol"

def credentials_to_dict(credentials):
  return {
		'token': credentials.token,
		'refresh_token': credentials.refresh_token,
		'token_uri': credentials.token_uri,
		'client_id': credentials.client_id,
		'client_secret': credentials.client_secret,
		'scopes': credentials.scopes
	}

@app.route("/authorize")
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
		CLIENT_SECRETS_FILE,
		scopes=SCOPES
	)

  flow.redirect_uri = url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
		# Enable offline access so that you can refresh an access token without
		# re-prompting the user for permission. Recommended for web server apps.
		access_type='offline',
		# Enable incremental authorization. Recommended as a best practice.
		include_granted_scopes='true',
	)

  # Store the state so the callback can verify the auth server response.
  session['state'] = state

  return redirect(authorization_url)

@app.route("/oauth2callback")
def oauth2callback():
	# Specify the state when creating the flow in the callback so that it can
	# verified in the authorization server  response.
	state = session['state']

	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
		CLIENT_SECRETS_FILE,
		scopes=SCOPES,
		state=state
	)
	flow.redirect_uri = url_for('oauth2callback', _external=True)

	# Use the authorization server's response to fetch the OAuth 2.0 tokens.
	authorization_response = request.url
	flow.fetch_token(authorization_response=authorization_response)
	# Store credentials in the session.
	# ACTION ITEM: In a production app, you likely want to save these
	#              credentials in a persistent database instead.
	credentials = flow.credentials
	session['credentials'] = credentials_to_dict(credentials)

	return redirect(url_for('api'))
	firebase_to_google_spreadsheet(credentials)

@app.route("/api")
def api():
	if 'credentials' not in session:
		return redirect('authorize')

	# Load credentials from the session.
	credentials = google.oauth2.credentials.Credentials(
		**session['credentials']
	)

	# Save credentials back to session in case access token was refreshed.
	# ACTION ITEM: In a production app, you likely want to save these
	#              credentials in a persistent database instead.
	session['credentials'] = credentials_to_dict(credentials)

	try:
		google_spreadsheet_to_firebase(credentials)
		return "Successfully imported google spreadsheet into database."
	except Exception as error:
		raise Exception(error)
		return "Failed to import google spreadsheet into database."

if __name__ == "__main__":
	os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
	app.run(port=8080)