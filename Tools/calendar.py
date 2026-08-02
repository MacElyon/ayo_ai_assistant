from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class CalendarTool:
    def __init__(self):
        self.service = self.authenticate()

    #
    def authenticate(self):
        creds = None

        # checks if we are logged in already
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        #create the google caledar connection
        service = build("calendar", "v3", credentials=creds)

        return service

    def schedule_event(self, summary, location, start, end):
        event_data = {
        "summary": summary,
        "location": location,
        "start": {
            "dateTime": start,
            "timeZone": "America/New_York"
            },
        "end": {
            "dateTime": end,
            "timeZone": "America/New_York"
            },
        'reminders': {
        'useDefault': True
            }
        }  

        #service is the calendar
        event = self.service.events().insert(calendarId="primary", body=event_data).execute()
        print("Event created")
        return event


    def get_events(self):
        events = self.service.events().list(calendarId="primary").execute()

        clean_events = []

        for event in events.get("items", []):
            clean_events.append({
                "id": event.get("id"),
                "title": event.get("summary"),
                "location": event.get("location"),
                "start": event.get("start", {}).get("dateTime"),
                "end": event.get("end", {}).get("dateTime")
            })
        return clean_events



    def delete_event(self, event_id):
        self.service.events().delete(calendarId="primary", eventId = event_id, sendNotifications = True).execute()
        
