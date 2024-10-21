from configs.tools import *
from main import send_and_wait_for_reply
from data.routines.baggage.policies import *
from data.routines.flight_modification.policies import *
from data.routines.prompts import STARTER_PROMPT

from swarm import Agent

today = datetime.today()

def transfer_to_task_agent():
    return task_agent

def transfer_to_calendar_agent():
    return calendar_agent

def transfer_to_appointment_agent():
    return appointment_agent

def transfer_to_triage():
    """Call this function when the user needs to be transferred to a differnt agent and a different policy.
    For instance, if a user is asking about a topic that is not handled by the current agent, call this function.
    """
    return triage_agent

def message_person(name=str, message=str) -> str:
    """Call this function to message a specific person to discuss scheduling an event. The name should be the name of the person
    and the message should be the contents."""
    print("sending", message, "to", name)
    FROM_NUMBER = "+12523567100"
    TO_NUMBER = "+16505098807"
    reply_message = send_and_wait_for_reply(TO_NUMBER, FROM_NUMBER, message)
    print(f"Agent recieved reply: {reply_message}")
    # user_input = input("Please enter your response")
    # print(f"You entered: {user_input}")
    return reply_message

def triage_instructions(context_variables):
    customer_context = context_variables.get("customer_context", None)
    flight_context = context_variables.get("flight_context", None)
    return f"""You are to triage a users request, and call a tool to transfer to the right intent.
    Once you are ready to transfer to the right intent, call the tool to transfer to the right intent.
    You dont need to know specifics, just the topic of the request.
    When you need more information to triage the request to an agent, ask a direct question without explaining why you're asking it.
    Do not share your thought process with the user! Do not make unreasonable assumptions on behalf of user.
    The customer context is here: {customer_context}, and flight context is here: {flight_context}"""

triage_agent = Agent(
    name="Personal Agent",
    instructions="""Your job is to traige his requests and call a tool to transfer to the right intent.
    Once you are ready to transfer to the right intent, call the tool to transfer to the right intent.
    You dont need to know specifics, just the topic of the request.
    When you need more information to triage the request to an agent, ask a direct question without explaining why you're asking it.
    Do not make unreasonable assumptions on behalf of user.""",
    functions=[transfer_to_appointment_agent, transfer_to_task_agent],
)

task_agent = Agent(
    name="Task Agent",
    instructions="""You are responsible for managing Henry's work tasks. 
    You are in charge of getting information about what work he needs to do and how long it will take. 
    Either ask clarifying questions, or call one of your functions, every time.""",
    functions=[transfer_to_triage, get_tasks],
    parallel_tool_calls=False,
)

calendar_agent = Agent(
    name="Calendar Agent",
    instructions=f"""
        You are a helpful assistant for managing Henry's personal calendar. You are in charge of Henry's calendar and can schedule events,
        including with other people. You can also message a person to see when they are available. 
        Either ask clarifying questions, or call one of your functions, every time. 

        If Henry asks you to schedule an event with someone, please find a slot that both the person and Henry are free.
        When messaging someone else, always introduce yourself as Henry's AI assistant. 
        If Henry is not free at that time please message the person again to see if you can find an alternative. 
        Only message Henry if it is not possible to schedule an event, after multiple attempts. 
        
        Use the following policy to determine whether Henry is free. 
        1. Determine what time the event is, how long it is and where it is located.
        2. Check Henry's clanedar to see if he is free during that time. 
        3. If the event is located in a physical location (i.e it isn't online), ensure he has time to commute to the event. 
            You can use the location of Henry's last event on the same day. If it is not, then assume Henry is at home at 4244 Los Palos Place, Palo Alto, CA. 
        4. Henry typically sleeps between 10pm and 7am on weekdays so these are quiet hours. 

        Always check if Henry is free before booking an event. 

        For context the current date is {today}. Do not make additional assumptions.      
        """,
    functions=[get_calendar_events, create_calendar_event, transfer_to_triage, message_person],
    parallel_tool_calls=False,
)

appointment_agent = Agent(
    name="Appointment Agent",
    instructions=f"""
        Your job is to schedule Henry's appointments (e.g. dinner, meetings) with other people. You must use the following steps:
        1. Get Henry's calendar for the time period when the appointment can be scheduled by calling 'get_calendar_events'.
        2. Find a slot on Henry's calender when Henry is free according to the policy below. Henry is free if 
            2a. Henry's clanedar does not have any events at that time
            2b. If the event is located in a physical location (i.e it isn't online), ensure he has time to commute to the event. You can use the location of Henry's last event on the same day. If it is not, then assume Henry is at home at 4244 Los Palos Place, Palo Alto, CA.
            2c. It is not between 10pm and 7am on weekdays, since Henry likes to sleep at those time. 
        3. Message the person to propose a time for the appointment. Always introduce yourself as Henry's AI assistant so they know who you are. 
        4. If the person confirms the appointment then create the event by calling 'create_calendar_event'. Message the person the event details.
        5. If this does not work, repeat steps 2-5 and ask again. 
        
        IMPORANT: Do not message Henry unless you do not have enough information to schedule the appointment.  You don't need to ask him his preferences or confirm if his calendar is free.

        For context the current date is {today}. Do not make additional assumptions.
        Either ask clarifying questions, or call one of your functions, every time. 
        """,
    functions=[get_calendar_events, create_calendar_event, transfer_to_triage, message_person],
    parallel_tool_calls=False,
)

