from configs.tools import *
from data.routines.baggage.policies import *
from data.routines.flight_modification.policies import *
from data.routines.prompts import STARTER_PROMPT

from swarm import Agent

today = datetime.today()

def transfer_to_task_agent():
    return task_agent

def transfer_to_calendar_agent():
    return calendar_agent

def transfer_to_triage():
    """Call this function when the user needs to be transferred to a differnt agent and a different policy.
    For instance, if a user is asking about a topic that is not handled by the current agent, call this function.
    """
    return triage_agent

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
    instructions="""You are a helpful personal assistant for Henry. You can help him plan and manage his daily life.
    You have access to other agents that can help you. Call the right tools to get information about his calendar or what tasks he 
    needs to perform.""",
    functions=[transfer_to_calendar_agent, transfer_to_task_agent],
)

task_agent = Agent(
    name="Task Agent",
    instructions="""You are a helpful assitant for managing Henry's work. 
    You are in charge of getting information about what work he needs to do and how long it will take. 
    Either ask clarifying questions, or call one of your functions, every time.""",
    functions=[transfer_to_triage, get_tasks],
    parallel_tool_calls=False,
)

calendar_agent = Agent(
    name="Calendar Agent",
    instructions=f"""
        You are a helpful assistant for managing Henry's personal calendar. You are in charge of Henry's calendar and are responsible for scheduling new events.
        Either ask clarifying questions, or call one of your functions, every time. 

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
    functions=[get_calendar_events, create_calendar_event, escalate_to_henry, transfer_to_triage],
    parallel_tool_calls=False,
)
