# Personal Assistant 

To run
(0) source venv/bin/activate
(1) set up all credentials by running ./set_credentials.sh 
(2) run ngrok http 5000 to set up the webhook
(3) make sure the sms for telnyx webhook is pointed at {link from ngrok}/webhook
(4) python3 swarm/personal_assistant/main.py    
Enjoy! 