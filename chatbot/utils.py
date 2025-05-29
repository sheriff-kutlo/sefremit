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
            send_interactive_jobs_message(phone_number)

        elif reply == JA_METER:
            send_interactive_ja_meter_message(phone_number)

        elif reply == ORANGE_SOCIAL_VENTURE_PRICE:
            send_pdf_by_id("1431280267895547", phone_number, "Rules for the 2025 Orange Social Venture Prize (OSVP), detailing eligibility, competition structure, and application process for entrepreneurs in Africa and the Middle East.", "Rules of the OSVP Prize-2025")

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

        elif reply == JOBS_SIMPLE:
            send_interactive_jobs_message(phone_number)

        elif reply == IT:
            send_image_by_id('1865771617324259', phone_number)

        elif reply == FINANCE_ACCOUNTING:
            img_ids = ['1108933161267627', '689359607159211']
            
            for img in img_ids:
                send_image_by_id(img, phone_number)

        elif reply == COMPLIANCE:
            send_image_by_id('1041626037488666', phone_number)

        elif reply == EVENTS:
            send_interactive_events_message(phone_number)

        elif reply == NORTHERN_TRADE_FAIR_2025:
            send_image_by_id("613557838403443", phone_number)

        elif reply == BOTSWANA_NURSES_DAY:
            send_image_by_id("1764990677735677", phone_number)

        elif reply == JOIN_COMPETITION:
            send_message("✅ You’re in! \n\nYour entry to the Ja Meter SMS Competition is successful. 🎉\n\nEnter again to increase your odds!", phone_number)

        elif reply == TERMS_CONDITIONS:
            send_message("*Your Terms & Conditions Here*\n\nLorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum.", phone_number)
        
        elif reply == APPLY_FOR_PROGRAM:
            send_interactive_orange_digital_center_program_form_message(phone_number)

        elif reply == LOCATION:
            send_orange_digital_center_location(phone_number)
        
        elif reply == ORANGE_DIGITAL_CENTER:
            send_interactive_orange_digital_center_message(phone_number)

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
            logger.info(f"welcome message interactive message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send welcome message message. Status Code: {response.status_code}. Response Content: {response.content}")
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
            logger.error(f"Failed to send radio drama/podcasts message. Status Code: {response.status_code}. Response Content: {response.content}")
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
            logger.error(f"Failed to send Seasons message. Status Code: {response.status_code}. Response Content: {response.content}")
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

def send_interactive_jobs_message(phone_number):
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
                "text": "Jobs [Mohiri]"
            },
            "body": {
                "text": "Select a profession area, so we can tailor the experience for you."
            },
            "footer": {
                "text": "You can type *jobs* at any time to return to this screen."
            },
            "action": {
                "button": "Profession Area",
                "sections": [
                    {
                        "title": "Please choose an option",
                        "rows": [
                            {"id": "1", "title": "IT"},
                            {"id": "2", "title": "Compliance"},
                            {"id": "3", "title": "Finance & Accounting"},

                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Jobs interactive message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send Jobs message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def send_pdf_by_id(id, phone_number, caption, filename):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": AUTHORIZATION
    }
    

    json_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "document",
        "document": {
            "id": id,
            "caption": caption,
            "filename": filename
        }
    }
    
    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Document sent successfully. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def send_interactive_events_message(phone_number):
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
                "text": "Events"
            },
            "body": {
                "text": "Check out our upcoming events and be part of something special."
            },
            "footer": {
                "text": "You can type *events* at any time to return to this screen."
            },
            "action": {
                "button": "Profession Area",
                "sections": [
                    {
                        "title": "Please choose an option",
                        "rows": [
                            {"id": "1", "title": "Northern Trade Fair 2025"},
                            {"id": "2", "title": "Botswana Nurses Day"}


                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Jobs interactive message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send Jobs message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def send_image_by_id(id, phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": AUTHORIZATION
    }
    

    # json_data1 = {
    #     "messaging_product": "whatsapp",
    #     "recipient_type": "individual",
    #     "to": phone_number,
    #     "type": "document",
    #     "document": {
    #         "id": id,
    #         "caption": caption,
    #         "filename": filename
    #     }
    # }

    json_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "image",
        "image": {
            "id": id
        }
    }
    
    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Document sent successfully. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def send_interactive_ja_meter_message(phone_number):
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
                "text": "🏆 Ja Meter 🎁💶"
            },
            "body": {
                "text": "Making 1 lucky person a *Millionaire*"
            },
            "footer": {
                "text": "You can type *ja meter* at any time to return to this screen."
            },
            "action": {
                "button": "View",
                "sections": [
                    {
                        "title": "Please choose an option",
                        "rows": [
                            {"id": "1", "title": "Enter Competition", "description": "Join the competition for just P2.50!"},
                            {"id": "2", "title": "Terms & Conditions"},

                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Jobs interactive message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send Jobs message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def send_interactive_orange_digital_center_message(phone_number):
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
                "text": "Orange Digital Center"
            },
            "body": {
                "text": "A network of free & inclusive resources to support local start ups & projects with digital technology"
            },
            "action": {
                "button": "Menu",
                "sections": [
                    {
                        "title": "Please choose an option",
                        "rows": [
                            {"id": "1", "title": "Apply for Program"},
                            {"id": "2", "title": "Location"},

                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Jobs interactive message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send Jobs message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def send_orange_digital_center_location(phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": AUTHORIZATION
    }

    json_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "location",
        "location": {
            "latitude": -24.690091,
            "longitude": 25.879837,
            "name": "Orange Digital Center"
        }
    }
    
    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Location sent successfully. phone: {phone_number}")

            response_data = response.json()

            logger.debug(f"Response JSON: {response_data}")

            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send location. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending Location: {e}", exc_info=True)
        return None

def send_interactive_orange_digital_center_program_form_message(phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": AUTHORIZATION
    }

    json_data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "recipient_type": "individual",
        "type": "interactive",
        "interactive": {
            "type": "flow",
            "header": {
                "type": "text",
                "text": "Our Programs"
            },
            "body": {
                "text": "Fill in the form to apply for one of our programs."
            },
            "action": {
                "name": "flow",
                "parameters": {
                    "flow_message_version": "3",
                    "flow_action": "navigate",
                    "flow_token": "<FLOW_TOKEN>",
                    "flow_id": "1679205382734623",
                    "flow_cta": "Open Form",
                    "flow_action_payload": {
                        "screen": "QUESTION_ONE",
                        "data": {
                            "<CUSTOM_KEY>": "<CUSTOM_VALUE>"
                        }
                    }
                }
            }
        }
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Orange Digital Center interactive message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send Orange Digital Center message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None






