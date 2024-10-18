from datetime import datetime
from swarm import Agent
from examples.calendar_agent.calendar_tools import get_calendar_events, create_calendar_event


def escalate_to_henry(event: str, reason: str):
    """This function escalates an event that cannot be booked to Henry. 
        Event should be a string with relevant details of the event in the following format: 
        {summary: str, location: str, start: str, end: str, description: str}
        Reason should be a string with the reason why the event cannot be booked. Specifically 
        which part of the policy is violated (give the specific number and reason)
    """
    print("Event cannot be booked:", event, "reason:", reason)

# Get today's date
today = datetime.today()

calendar_agent = Agent(
    name="Calendar Agent",
    instructions=f"""
        You are a helpful assistant for managing Henry's personal calendar. Your job is to check if Henry can attend events and, if so, add them to his calendar. 
        Use the following policy to determine whether Henry is available for an event. 
        1. Determine what time the event is, how long it is and where it is located
        2. Check Henry's schedule is free during that slot. Henry is free if theere are no events at that time. Do not make additional assumptions. 
        3. If the event is located in a physical location (i.e it isn't online), ensure he has time to commute to the event. You can use the location of Henry's last event on the same day. 
            If it is not, then assume Henry is at home at 4244 Los Palos Place, Palo Alto, CA. 
        4. Henry typically sleeps between 10pm and 7am on weekdays so these are quiet hours. 
        5. If Henry is free, able to commute and it isn't during his quiet hours book the event. 
        6. If it is not possible to book, please try to find another time. 
        7. If that is not possible please escalate to Henry.

        For context the current date is {today}.      
        """,
    functions=[get_calendar_events, create_calendar_event, escalate_to_henry],
)

