from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import os

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class CalendarTool:
    def __init__(self):
        self.service = self.authenticate()

    #def debug_calendar_identity(self):
    #    info = self.service.calendars().get(calendarId="primary").execute()
    #    print(info)

    def normalize_datetime(self, value):
        """
        Converts a datetime without timezone information into
        America/New_York timezone format.
        """

        if value and value[-1] != "Z" and "+" not in value and "-" not in value[10:]:
            dt = datetime.fromisoformat(value)
            value = dt.replace(tzinfo=ZoneInfo("America/New_York")).isoformat()

        return value
    
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

    def schedule_event(self, summary: str, start: str, end: str, location: str = ""):
        """Creates a new calendar event. Use when the user wants to add an event to their calendar.

        Args:
        summary: The name of the event.
        location: Where the event takes place.
        start: Start date and time in strict RFC3339 format YYYY-MM-DDTHH:MM:SS±HH:MM. Derive the date from the current date provided in the system prompt when the user says "today", "tomorrow", etc.
        end: End date and time in strict RFC3339 format YYYY-MM-DDTHH:MM:SS±HH:MM. Derive the date from the current date provided in the system prompt when the user says "today", "tomorrow", etc.

        Returns:
        The created calendar event.
        """

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
        "reminders": {
        "useDefault": True
            }
        }  

        if location:
            event_data["location"] = location

        #service is the calendar
        event = self.service.events().insert(calendarId="primary", sendUpdates="all", body=event_data).execute()
        print(f"Created event: {event.get('htmlLink')}") #DEBUG
        return event


    def get_events(self, time_min: str = None, time_max: str = None):
        """Retrieves the user's calendar events. Use only when the user asks about their schedule.

        Args:
        time_min: Start of the range, in strict RFC3339 format YYYY-MM-DDTHH:MM:SS±HH:MM. Derive from the current date in the system prompt for words like "today" or "tomorrow".
        time_max: End of the range, in strict RFC3339 format YYYY-MM-DDTHH:MM:SS±HH:MM. Derive from the current date in the system prompt for words like "today" or "tomorrow".

        Returns:
        A list of calendar events.
        """

        time_min = self.normalize_datetime(time_min)
        time_max = self.normalize_datetime(time_max)

        if time_min is None:
            time_min = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        params = {
        "calendarId": "primary",
        "timeMin": time_min,
        "maxResults": 10,
        "singleEvents": True,
        "orderBy": "startTime",
        }
        if time_max:
            params["timeMax"] = time_max

        events = self.service.events().list(**params).execute()


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


#USING WRONG FORMAT!!! AGAIN
    def delete_event(self, title: str, date: str, start_time: str = None):
        """Deletes an event from the user's calendar.

        Use only when the user explicitly asks to remove or cancel an event.
        
        Args:
        title: The title of the event to delete.
        date: The date of the event to delete in YYYY-MM-DD format.
        start_time: The start time of the event to delete in HH:MM format.

        Returns:
        Nothing. The event is removed from the calendar.
        """
        # Create beginning and end of the requested day
        time_min = f"{date}T00:00:00"
        time_max = f"{date}T23:59:59"

        # Find the event using get_events
        events = self.get_events(time_min=time_min, time_max=time_max)
        event_id = None
        for event in events:
            if event.get("title") and title.lower() in event["title"].lower() and (start_time is None or event["start"].startswith(f"{date}T{start_time}")):
                event_id = event["id"]
                break

        if not event_id:
            raise ValueError("Event not found.")

        self.service.events().delete(calendarId="primary", eventId = event_id, sendUpdates="all").execute()
        return f"{title} has been deleted from your calendar."
