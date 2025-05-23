from django.db import connection
from .constants import *
import requests
from django.db import connection, OperationalError
import logging

# Get an instance of a logger
logger = logging.getLogger(CHATBOT_CATALOG)

def send_message(message, phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": AUTHORIZATION
    }
    
    json_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message
        }
    }
    
    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Message sent successfully. message: {message}, phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def handle_reply(reply, message_id, phone_number, username, display_phone_number):

    if display_phone_number == TEST_PHONE_NUMBER:
        reply = reply.lower()

        # customer_id = get_customer_id(phone_number)

        # if not customer_id:
        #     save_customer({USERNAME: remove_emojis(username), PHONE_NUMBER: phone_number})
        #     customer_id = get_customer_id(phone_number)


        if reply == RADIO_DRAMA_PODCASTS:
            send_message(RADIO_DRAMA_PODCASTS, phone_number)

        elif reply == JOBS:
            send_message(JOBS, phone_number)

        elif reply == JA_METER:
            send_message(JA_METER, phone_number)

        elif reply == OSVP:
            send_message(OSVP, phone_number)
