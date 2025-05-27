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
            send_interactive_radio_drama_message(phone_number)

        elif reply == JOBS:
            send_message(JOBS, phone_number)

        elif reply == JA_METER:
            send_message(JA_METER, phone_number)

        elif reply == OSVP:
            send_message(OSVP, phone_number)

        elif reply == DRAMA:
            send_interactive_radio_drama_message(phone_number)

        elif reply == MATSWAKA_BAE:
            send_interactive_seasons_message(phone_number)

        elif reply == SUGAR:
            send_interactive_seasons_message(phone_number)

        elif reply == SEASON_1:
            send_interactive_episodes_message(phone_number)

        elif reply == SEASON_2:
            send_interactive_episodes_message(phone_number)

        elif reply == SEASON_3:
            send_interactive_episodes_message(phone_number)

        elif reply == EPISODE_1:
            send_audio_by_id(625557423882962, phone_number)

        elif reply == EPISODE_2:
            send_audio_by_id(625557423882962, phone_number)

        elif reply == EPISODE_3:
            send_audio_by_id(625557423882962, phone_number)

        elif reply == EPISODE_4:
            send_audio_by_id(625557423882962, phone_number)

        elif reply == JOBS:
            send_message(JOBS, phone_number)
        
        else:
            send_interactive_menu_message(phone_number)

def send_interactive_menu_message(phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": AUTHORIZATION
    }

    json_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Welcome to Orange Botswana WhatsApp 😃"
            },
            "body": {
                "text": "Stay in the loop! Discover current competitions, Orange initiatives, and important updates about our services on WhatsApp."
            },
            "footer": {
                "text": "You can type *menu* at any time to return to this screen."
            },
            "action": {
                "button": "Menu",
                "sections": [
                    {
                        "title": "Please choose an option",
                        "rows": [
                            {"id": "1", "title": "Radio Drama/Podcasts"},
                            {"id": "2", "title": "Jobs [Mohiri]"},
                            {"id": "3", "title": "Ja Meter"},
                            {"id": "4", "title": "OSVP", "description": "Orange Social Venture Prize"},
                            {"id": "5", "title": "Events"},
                            {"id": "6", "title": "Orange Digital Center"}

                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"category interactive message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send category message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def send_interactive_radio_drama_message(phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": AUTHORIZATION
    }

    json_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Radio Drama/Podcasts"
            },
            "body": {
                "text": "Explore our dramas' and podcasts to listen too."
            },
            "footer": {
                "text": "You can type *drama* at any time to return to this screen."
            },
            "action": {
                "button": "Radio Drama/Podcasts",
                "sections": [
                    {
                        "title": "Please choose an option",
                        "rows": [
                            {"id": "1", "title": "Matswaka Bae"},
                            {"id": "2", "title": "Sugar"}

                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"radio drama/podcasts interactive message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send category message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def send_interactive_seasons_message(phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": AUTHORIZATION
    }

    json_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Seasons"
            },
            "body": {
                "text": "Choose a season."
            },
            "action": {
                "button": "Seasons",
                "sections": [
                    {
                        "title": "Please choose an option",
                        "rows": [
                            {"id": "1", "title": "Season 1"},
                            {"id": "2", "title": "Season 2"},
                            {"id": "3", "title": "Season 3"}

                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Seasons interactive message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send category message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def send_interactive_episodes_message(phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": AUTHORIZATION
    }

    json_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Episodes"
            },
            "body": {
                "text": "Choose an episode."
            },
            "action": {
                "button": "Episode",
                "sections": [
                    {
                        "title": "Please choose an episode",
                        "rows": [
                            {"id": "1", "title": "Episode 1"},
                            {"id": "2", "title": "Episode 2"},
                            {"id": "3", "title": "Episode 3"},
                            {"id": "4", "title": "Episode 4"}

                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"episodes interactive message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send episodes message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def send_audio_by_id(id, phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": AUTHORIZATION
    }
    
    json_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "audio",
        "audio": {
            "id": id
        }
    }
    
    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Audio sent successfully. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None






