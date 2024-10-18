import os
import caldav
from datetime import datetime
from icalendar import Calendar, Event as ICalEvent

# TODO replace with environment variables "henryaspegren@gmail.com"
icloud_username = os.getenv("ICLOUD_USER_NAME") 
# This password is an app-specific password for my personal assistant "dzbn-skmg-svwc-lnjf"
icloud_app_password = os.getenv("ICLOUD_ASSISTANT_APP_PASSWORD") 
icloud_calendar_url = "https://caldav.icloud.com"

def get_calendar_events(start: str, end: str):
    """Get the events on Henry's calendar from a specific time period. 
    Start and end should be dates in the ISO datetime format of: %Y-%m-%dT%H:%M:%S""" 
    print("Getting calendar events from", start, "to", end)
    start_date = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
    end_date = datetime.strptime(end,"%Y-%m-%dT%H:%M:%S")
    # Establish a connection to the CalDAV server
    client = caldav.DAVClient(
        url=icloud_calendar_url, 
        username=icloud_username, 
        password=icloud_app_password,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    results = []
    try:
        # Access your calendar principal (the user calendar account)
        principal = client.principal()
        calendars = principal.calendars()
        if not calendars:
            print("No calendars found for this account.")
        else:
            # Iterate over all calendars
            for calendar in calendars:
                print(f"Accessing calendar: {calendar.name}")
                # Fetch events within the specified time range
                calendar_events = calendar.date_search(start=start_date, end=end_date)
                if not calendar_events:
                    print(f"No events found in the specified time range for calendar: {calendar.name}.")
                else:
                    for event in calendar_events:
                        print("event:", event)
                        event_data = event.data
                        calendar_obj = Calendar.from_ical(event_data)
                        for component in calendar_obj.walk():
                            if component.name == "VEVENT":
                                # Extract relevant details
                                event_summary = component.get('summary')
                                event_start = component.get('dtstart').dt
                                event_end = component.get('dtend').dt
                                event_location = component.get('location')
                                event_transparency = component.get('transp')
                                # Determine if the event is busy or free
                                is_busy = event_transparency != "TRANSPARENT"

                                # Store the event details in a dictionary
                                event_info = {
                                    "summary": event_summary,
                                    "start": event_start,
                                    "end": event_end,
                                    "location": event_location,
                                    "is_busy": is_busy
                                }
                                results.append(event_info)
    except caldav.error.AuthorizationError:
        print("Authorization failed. Check your credentials or app-specific password.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return results

def create_calendar_event(summary: str, location: str, start: str, end: str, description: str):
    """Create a new event on Henry's calendar. 
    Takes in a summary of the event, a location, start time and end time and description
    of the event. The start and end should be dates in the ISO datetime format of: %Y-%m-%dT%H:%M:%S""" 

    print("Creating calendar event", summary, "@", location, "starting", start, "to", end, "desc:", description)
    start_time = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
    end_time = datetime.strptime(end,"%Y-%m-%dT%H:%M:%S")

    # Establish a connection to the CalDAV server
    client = caldav.DAVClient(
        url=icloud_calendar_url, 
        username=icloud_username, 
        password=icloud_app_password,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    try:
        # Access your calendar principal (the user calendar account)
        principal = client.principal()
        calendars = principal.calendars()

        if not calendars:
            print("No calendars found for this account.")
            return

        # Find the calendar named "personal"
        personal_calendar = None
        for calendar in calendars:
            if calendar.name.lower() == "agent":
                personal_calendar = calendar
                break

        if personal_calendar is None:
            print("The 'agent' calendar was not found.")
            return

        print(f"Using calendar: {personal_calendar.name}")

        # Create a new calendar event in iCalendar format
        cal = Calendar()
        event = ICalEvent()
        event.add('summary', summary)
        event.add('location', location)
        event.add('dtstart', start_time)
        event.add('dtend', end_time)
        event.add('description', description)
        event.add('uid', f"{datetime.now().timestamp()}@example.com")  # Unique identifier for the event
        event.add('dtstamp', datetime.now())

        # Add the event to the calendar
        cal.add_component(event)

        # Send the event to the CalDAV server
        event_data = cal.to_ical()
        personal_calendar.add_event(event_data)
        print("Event created successfully!")
        return("Event created successfully!")

    except caldav.error.AuthorizationError:
        print("Authorization failed. Check your credentials or app-specific password.")
        return("Event not created")
    except Exception as e:
        print(f"An error occurred: {e}")
        return("Event not created") 

def escalate_to_agent(reason=None):
    return f"Escalating to agent: {reason}" if reason else "Escalating to agent"

def get_tasks():
    tasks = [
        {'name': 'Groceries', 'description': 'Get groceries for the week', 'duration (hours)': 1},
        {'name': 'Blog post', 'description': 'write a blog post about agents', 'duration (hours)': 3},
    ]
    print(tasks)
    return str(tasks)

def escalate_to_henry(event: str, reason: str):
    """This function escalates an event that cannot be booked to Henry. 
        Event should be a string with relevant details of the event in the following format: 
        {summary: str, location: str, start: str, end: str, description: str}
        Reason should be a string with the reason why the event cannot be booked. Specifically 
        which part of the policy is violated (give the specific number and reason)
    """
    print("Event cannot be booked:", event, "reason:", reason)
