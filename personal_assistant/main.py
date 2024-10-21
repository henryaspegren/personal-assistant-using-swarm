import threading
import telnyx
import time
from event_manager import reply_queue
from configs.agents import *
from swarm.repl import run_demo_loop
from flask import Flask, request, jsonify

context_variables = {
    "customer_context": """Here is what you know about the customer's details:
1. CUSTOMER_ID: customer_12345
2. NAME: John Doe
3. PHONE_NUMBER: (123) 456-7890
4. EMAIL: johndoe@example.com
5. STATUS: Premium
6. ACCOUNT_STATUS: Active
7. BALANCE: $0.00
8. LOCATION: 1234 Main St, San Francisco, CA 94123, USA
""",
    "flight_context": """The customer has an upcoming flight from LGA (Laguardia) in NYC to LAX in Los Angeles.
The flight # is 1919. The flight departure date is 3pm ET, 5/21/2024.""",
}

TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
MESSAGING_PROFILE_ID = os.getenv("MESSAGING_PROFILE_ID")
FROM_NUMBER = os.getenv("TELNYX_NUMBER")

# Initialize Telnyx client
telnyx.api_key = TELNYX_API_KEY

app = Flask(__name__)

def send_message(to, from_, message_body):
    try:
        message = telnyx.Message.create(
            from_=from_,
            to=to,
            text=message_body,
            messaging_profile_id=MESSAGING_PROFILE_ID
        )
        print(f"Message sent: {message_body}")
        return message
    except Exception as e:
        print(f"Failed to send message: {e}")
        return None

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()['data']
    if data['event_type'] == 'message.received':
        payload = data['payload']
        reply_message = payload['text']
        reply_queue.put(reply_message)
        print(f"Webhook reply recieved: {reply_message}")
        return jsonify(status="received"), 200
    return jsonify(status="ignored"), 200

def wait_for_reply(timeout=300):
    # Wait for the reply event to be set by the webhook
    print('Waiting for reply...')
    reply_message = reply_queue.get(block=True, timeout=timeout)
    print(f"Agent reply received: {reply_message}, proceeding...")
    return reply_message
    
def send_and_wait_for_reply(to, from_, message_body, timeout=300):
    message = send_message(to, from_, message_body)
    if message:
        print("Message sent successfully. Waiting for a reply...")
        reply = wait_for_reply(timeout)
        if reply:
            print(f"Reply: {reply}")
            return reply
        else:
            print("No reply received.")
            return None
    else:
        print("Failed to send the initial message.")
        return None

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(port=5000, debug=True, use_reloader=False)).start()
    run_demo_loop(triage_agent, context_variables=context_variables, debug=True)