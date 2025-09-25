from django.db import connection
from .constants import *
import requests
from django.db import connection, OperationalError
import logging
import re
from django.core.cache import cache
import math
from datetime import datetime



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

# def handle_reply(reply, message_id, phone_number, username, display_phone_number):

#     if display_phone_number == TEST_PHONE_NUMBER:

#         if phone_number == INVALID_PHONE_NUMBER:
#             reply = reply.lower()
            
#             user_id = get_user_id_tx(phone_number)

#             if not user_id:
#                 save_user_tx({USERNAME: remove_emojis(username), PHONE_NUMBER: phone_number})
#                 user_id = get_user_id_tx(phone_number)
#                 cache.set(f"{phone_number}_action", ROUTE, timeout=24 * 3600)


#             action = cache.get(f"{phone_number}_action")

#             if action is None:
#                 send_routes(phone_number)
#                 cache.set(f"{phone_number}_action", ROUTE, timeout=24 * 3600)

#             else:
#                 if action == ROUTE:
#                     if not verify_route(reply):
#                         send_message("Please enter a valid route", phone_number)

#                     else:
#                         send_hotspots(reply, phone_number)
#                         cache.set(f"{phone_number}_action", HOTSPOTS, timeout=24 * 3600)

#                 elif action == HOTSPOTS:
#                     if verify_hotspot(reply) == None:
#                         send_message(f"Please enter a valid hotspot", phone_number)

#                     else:
#                         send_template_with_parameter(phone_number, CONFIRM_SEND_REQUEST, reply)
#                         cache.set(f"{phone_number}_action", CONFIRM_REQUEST, timeout=24 * 3600)

#                 elif action == CONFIRM_REQUEST:
#                     if reply == YES:
#                         send_message("send request", phone_number)
#                         pass

#                     elif reply == CANCEL:
#                         cache.delete_pattern(f"{phone_number}_*")
#                         send_message("Request Canceled", phone_number)

#                     else:
#                         send_message("Please enter a valid response", phone_number)





            
#             # send_flow_message(KUTLO_PHONE_NUMBER, SIMPE_USER_DATA_HEADER, SIMPE_USER_DATA_BODY, SIMPE_USER_DATA_FLOW_ID, SIMPE_USER_DATA_FLOW_TOKEN, SIMPE_USER_DATA_CTA)


#             # store_name = cache.get(f"{phone_number}_store_name")

#             # if store_name is None:
#             #     send_stores(phone_number)
#             # else:
#             #     products_lst = get_products(store_name, PET_CARE)

#             #     if not products_lst:
#             #         send_message(f"We currently don't have any {PET_CARE} products", phone_number)
#             #     else:
#             #         send_catalog_template_message(phone_number, products_lst, PET_CARE_CAMEL_CASE, PET_CARE_CAMEL_CASE)
       
       
#         elif phone_number == KUTLO_PHONE_NUMBER:
#             reply = reply.lower()
            
#             user_id = get_user_id_tx(phone_number)

#             if not user_id:
#                 save_user_tx({USERNAME: remove_emojis(username), PHONE_NUMBER: phone_number})
#                 user_id = get_user_id_tx(phone_number)
#                 cache.set(f"{phone_number}_action", ROUTE, timeout=24 * 3600)

#             action = cache.get(f"{phone_number}_action")

#             if action is None:
#                 send_routes(phone_number)
#                 cache.set(f"{phone_number}_action", ROUTE, timeout=24 * 3600)

#             else:
#                 if action == ROUTE:
#                     if not verify_route(reply):
#                         send_message("Please enter a valid route", phone_number)

#                     else:
#                         send_hotspots(reply, phone_number)
#                         cache.set(f"{phone_number}_action", HOTSPOTS, timeout=24 * 3600)

#                 elif action == HOTSPOTS:
#                     if verify_hotspot(reply) == None:
#                         send_message(f"Please enter a valid hotspot", phone_number)

#                     else:
#                         send_template_with_parameter(phone_number, CONFIRM_SEND_REQUEST, reply)
#                         cache.set(f"{phone_number}_action", CONFIRM_REQUEST, timeout=24 * 3600)

#                 elif action == CONFIRM_REQUEST:
#                     if reply == YES:
#                         send_message("send request", phone_number)
#                         pass

#                     elif reply == CANCEL:
#                         cache.delete_pattern(f"{phone_number}_*")
#                         send_message("Request Canceled", phone_number)

#                     else:
#                         send_message("Please enter a valid response", phone_number)




            





#         else:
#             reply = reply.lower()

#             user_id = get_user_id(phone_number)

#             if not user_id:
#                 save_user({USERNAME: remove_emojis(username), PHONE_NUMBER: phone_number})
#                 user_id = get_user_id(phone_number)


#             if reply == RADIO_DRAMA_PODCASTS:
#                 send_interactive_radio_drama_message(phone_number)
#                 update_interactions({INTERACTION_TYPE: RADIO_DRAMA_PODCASTS, USER_ID: user_id})

#             elif reply == JOBS:
#                 send_interactive_jobs_message(phone_number)
#                 update_interactions({INTERACTION_TYPE: JOBS, USER_ID: user_id})

#             elif reply == JA_METER:
#                 send_interactive_ja_meter_message(phone_number)
#                 update_interactions({INTERACTION_TYPE: JA_METER, USER_ID: user_id})

#             elif reply == ORANGE_SOCIAL_VENTURE_PRICE:
#                 send_pdf_by_id("1431280267895547", phone_number, "Rules for the 2025 Orange Social Venture Prize (OSVP), detailing eligibility, competition structure, and application process for entrepreneurs in Africa and the Middle East.", "Rules of the OSVP Prize-2025")
#                 update_interactions({INTERACTION_TYPE: ORANGE_SOCIAL_VENTURE_PRICE, USER_ID: user_id})

#             elif reply == DRAMA:
#                 send_interactive_radio_drama_message(phone_number)
#                 update_interactions({INTERACTION_TYPE: DRAMA, USER_ID: user_id})

#             elif reply == MATSWAKA_BAE:
#                 send_interactive_seasons_message(phone_number)
#                 update_interactions({INTERACTION_TYPE: MATSWAKA_BAE, USER_ID: user_id})

#             elif reply == SUGAR:
#                 send_interactive_seasons_message(phone_number)
#                 update_interactions({INTERACTION_TYPE: SUGAR, USER_ID: user_id})

#             elif reply == SEASON_1:
#                 send_interactive_episodes_message(phone_number)
#                 update_interactions({INTERACTION_TYPE: SEASON_1, USER_ID: user_id})

#             elif reply == SEASON_2:
#                 send_interactive_episodes_message(phone_number)
#                 update_interactions({INTERACTION_TYPE: SEASON_2, USER_ID: user_id})

#             elif reply == SEASON_3:
#                 send_interactive_episodes_message(phone_number)
#                 update_interactions({INTERACTION_TYPE: SEASON_3, USER_ID: user_id})

#             elif reply == EPISODE_1:
#                 send_audio_by_id(625557423882962, phone_number)
#                 update_interactions({INTERACTION_TYPE: EPISODE_1, USER_ID: user_id})

#             elif reply == EPISODE_2:
#                 send_audio_by_id(625557423882962, phone_number)
#                 update_interactions({INTERACTION_TYPE: EPISODE_2, USER_ID: user_id})

#             elif reply == EPISODE_3:
#                 send_audio_by_id(625557423882962, phone_number)
#                 update_interactions({INTERACTION_TYPE: EPISODE_3, USER_ID: user_id})

#             elif reply == EPISODE_4:
#                 send_audio_by_id(625557423882962, phone_number)
#                 update_interactions({INTERACTION_TYPE: EPISODE_4, USER_ID: user_id})

#             elif reply == JOBS_SIMPLE:
#                 send_interactive_jobs_message(phone_number)
#                 update_interactions({INTERACTION_TYPE: JOBS_SIMPLE, USER_ID: user_id})

#             elif reply == IT:
#                 send_image_by_id('1865771617324259', phone_number)
#                 update_interactions({INTERACTION_TYPE: IT, USER_ID: user_id})

#             elif reply == FINANCE_ACCOUNTING:
#                 img_ids = ['1108933161267627', '689359607159211']
                
#                 for img in img_ids:
#                     send_image_by_id(img, phone_number)

#                 update_interactions({INTERACTION_TYPE: FINANCE_ACCOUNTING, USER_ID: user_id})

#             elif reply == COMPLIANCE:
#                 send_image_by_id('1041626037488666', phone_number)
#                 update_interactions({INTERACTION_TYPE: COMPLIANCE, USER_ID: user_id})

#             elif reply == EVENTS:
#                 send_interactive_events_message(phone_number)
#                 update_interactions({INTERACTION_TYPE: EVENTS, USER_ID: user_id})

#             elif reply == NORTHERN_TRADE_FAIR_2025:
#                 send_image_by_id("613557838403443", phone_number)
#                 update_interactions({INTERACTION_TYPE: NORTHERN_TRADE_FAIR_2025, USER_ID: user_id})

#             elif reply == BOTSWANA_NURSES_DAY:
#                 send_image_by_id("1764990677735677", phone_number)
#                 update_interactions({INTERACTION_TYPE: BOTSWANA_NURSES_DAY, USER_ID: user_id})

#             elif reply == JOIN_COMPETITION:
#                 send_message("✅ You’re in! \n\nYour entry to the Ja Meter SMS Competition is successful. 🎉\n\nEnter again to increase your odds!", phone_number)
#                 update_interactions({INTERACTION_TYPE: JOIN_COMPETITION, USER_ID: user_id})

#             elif reply == TERMS_CONDITIONS:
#                 send_message("*Your Terms & Conditions Here*\n\nLorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum.", phone_number)
#                 update_interactions({INTERACTION_TYPE: TERMS_CONDITIONS, USER_ID: user_id})
            
#             elif reply == APPLY_FOR_PROGRAM:
#                 send_interactive_orange_digital_center_program_form_message(phone_number)
#                 update_interactions({INTERACTION_TYPE: APPLY_FOR_PROGRAM, USER_ID: user_id})

#             elif reply == LOCATION:
#                 send_orange_digital_center_location(phone_number)
#                 update_interactions({INTERACTION_TYPE: LOCATION, USER_ID: user_id})
            
#             elif reply == ORANGE_DIGITAL_CENTER:
#                 send_interactive_orange_digital_center_message(phone_number)
#                 update_interactions({INTERACTION_TYPE: ORANGE_DIGITAL_CENTER, USER_ID: user_id})

#             else:
#                 send_interactive_menu_message(phone_number)

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
                "button": "Events",
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

def get_user_id(phone_number):
    query = "SELECT user_id FROM users WHERE phone_number = %s;"

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (phone_number,))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                # Handle case where no customer is found
                # Example: You might want to register the user here
                # register_user(phone_number)
                return None

    except OperationalError as e:
        logger.error(f'Operational error occurred in get_user_id: {e}', exc_info=True)
        # Handle or raise the exception as needed
        return None
    except Exception as e:
        logger.error(f'An error occurred in get_user_id: {e}', exc_info=True)
        # Handle or raise the exception as needed
        return None

def save_user(save_user_dict):
    try:
        query = """
            INSERT INTO users (username, phone_number, created_at) 
            VALUES (%s, %s, CURRENT_TIMESTAMP());
        """
        
        with connection.cursor() as cursor:
            cursor.execute(query, (save_user_dict[USERNAME], save_user_dict[PHONE_NUMBER]))
            connection.commit()
            logger.info(f"Customer saved successfully. username: {save_user_dict[USERNAME]}, phone: {save_user_dict[PHONE_NUMBER]}")

    except Exception as e:
        connection.rollback()
        logger.error(f'An error occurred saving user: {e}', exc_info=True)

def remove_emojis(text):
    """
    Function to remove emojis from a string.

    :param text: The input string potentially containing emojis.
    :return: The string with emojis removed.
    """
    # Define a regex pattern to match emojis
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Misc Symbols and Pictographs
        "\U0001F680-\U0001F6FF"  # Transport and Map Symbols
        "\U0001F700-\U0001F77F"  # Alchemical Symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed Characters
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

def update_interactions(interaction_dict):
    try:
        # Use context manager to get cursor from connection
        with connection.cursor() as cursor:
            query = "INSERT INTO interactions(interaction_type, timestamp, user_id) VALUES(%s, current_timestamp(), %s);"
            cursor.execute(query, (interaction_dict[INTERACTION_TYPE], interaction_dict[USER_ID]))
            
            # Commit the transaction
            connection.commit()

            logger.info(f"Successfully updated customer interaction: interaction_type: {interaction_dict[INTERACTION_TYPE]}, customer_id: {interaction_dict[USER_ID]}")
        
    except Exception as e:
        logger.error(f"An unexpected error occurred in update_interactions: {e}", exc_info=True)

def send_welcome_interactive_menu_message(phone_number):
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
                "text": "Welcome to Ride Finder 😃"
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

def send_flow_message(phone_number, header, body, flow_id, flow_token, cta = "Enter Details"):

    json_data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "recipient_type": "individual",
        "type": "interactive",
        "interactive": {
            "type": "flow",
            "header": {
                "type": "text",
                "text": header
            },
            "body": {
                "text": body
            },
            "action": {
                "name": "flow",
                "parameters": {
                    "flow_message_version": "3",
                    "flow_action": "navigate",
                    "flow_token": flow_token,
                    "flow_id": flow_id,
                    "flow_cta": cta,
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


    headers = {
        "Authorization": AUTHORIZATION,
        "Content-Type": APPLICATION_JSON
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"flow sent successfully: flow_id: {flow_id}, phone_number: {phone_number}")
            
            response_data = response.json()
            
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send flow message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending flow message: {e}", exc_info=True)
        return None
 
def save_user_tx(save_user_dict):
    try:
        query = """
            INSERT INTO users (username, phone, role, reliability_score, is_banned, created_at) 
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP());
        """
        
        with connection.cursor() as cursor:
            cursor.execute(query, (
                save_user_dict[USERNAME],        
                save_user_dict[PHONE_NUMBER],    
                "customer",                        
                100,                               
                0                                  
            ))

            connection.commit()
            logger.info(f"Customer saved successfully. username: {save_user_dict[USERNAME]}, phone: {save_user_dict[PHONE_NUMBER]}")
    
    except Exception as e:
        connection.rollback()
        logger.error(f'An error occurred saving user: {e}', exc_info=True)

def get_user_id_tx(phone_number):
    query = "SELECT user_id FROM users WHERE phone = %s;"

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (phone_number,))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                # Handle case where no customer is found
                # Example: You might want to register the user here
                # register_user(phone_number)
                return None

    except OperationalError as e:
        logger.error(f'Operational error occurred in get_user_id: {e}', exc_info=True)
        # Handle or raise the exception as needed
        return None
    except Exception as e:
        logger.error(f'An error occurred in get_user_id: {e}', exc_info=True)
        # Handle or raise the exception as needed
        return None

def send_routes(phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": AUTHORIZATION
    }

    routes = get_routes()

    # Build the "rows" for the WhatsApp list dynamically
    route_rows = [{"id": str(index + 1), "title": route} for index, route in enumerate(routes)]

    if not route_rows:
        logger.warning(f"Routes not found")
        return None

    json_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "Share Your Route 🚕"
            },
            "body": {
                "text": "Pick your route to help nearby combis find you."
            },
            "action": {
                "button": "Choose My Route",
                "sections": [
                    {
                        "title": "Choose your Route",
                        "rows": route_rows  # Use dynamically generated rows
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Routes message successfully sent. Phone Number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def get_routes():
    query = """
        SELECT name 
        FROM routes;
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = [row[0] for row in cursor.fetchall()]

            if results:
                return results
            else:
                # Handle case where no customer is found
                # Example: You might want to register the user here
                # register_user(phone_number)
                return None

    except OperationalError as e:
        logger.error(f'Operational error occurred in get_routes: {e}', exc_info=True)
        # Handle or raise the exception as needed
        return None
    except Exception as e:
        logger.error(f'An error occurred in get_routes: {e}', exc_info=True)
        # Handle or raise the exception as needed
        return None

def send_hotspots(route, phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": AUTHORIZATION
    }

    hotspots = get_hotspots(route)

    if hotspots is None:
        logger.info(f"Hotspots not available for route: {route}")

    else:
    
        # Build the "rows" for the WhatsApp list dynamically
        hotspot_rows = [{"id": str(index + 1), "title": hotspot} for index, hotspot in enumerate(hotspots)]

        if not hotspot_rows:
            logger.warning(f"Hotspots not found")
            return None

        json_data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "Choose a Pickup Spot 📍"
                },
                "body": {
                    "text": "Select the nearest hotspot so a combi can pick you up faster."
                },
                "action": {
                    "button": "Show Hotspot",
                    "sections": [
                        {
                            "title": "Choose your Hotspot",
                            "rows": hotspot_rows  # Use dynamically generated rows
                        }
                    ]
                }
            }
        }

        try:
            response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"Hotspots message successfully sent. Phone Number: {phone_number}")
                response_data = response.json()
                logger.debug(f"Response JSON: {response_data}")
                return response_data.get("messages", [{}])[0].get("id")
            else:
                logger.error(f"Failed to send message. Status Code: {response.status_code}. Response Content: {response.content}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending message: {e}", exc_info=True)
            return None

def verify_route(route):
    query = """
        SELECT name 
        FROM routes where name = %s;
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (route,))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                # Handle case where no customer is found
                # Example: You might want to register the user here
                # register_user(phone_number)
                return None

    except OperationalError as e:
        logger.error(f'Operational error occurred in verify_route: {e}', exc_info=True)
        # Handle or raise the exception as needed
        return None
    except Exception as e:
        logger.error(f'An error occurred in verify_route: {e}', exc_info=True)
        # Handle or raise the exception as needed
        return None

def get_hotspots(route):
    query = """
        SELECT 
            h.name
        FROM 
            hotspots h
        JOIN 
            routes r ON h.route_id = r.route_id
        WHERE 
            r.name = %s;
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (route,))
            results = [row[0] for row in cursor.fetchall()]

            if results:
                return results
            else:
                # Handle case where no customer is found
                # Example: You might want to register the user here
                # register_user(phone_number)
                return None

    except OperationalError as e:
        logger.error(f'Operational error occurred in get_hotspots: {e}', exc_info=True)
        # Handle or raise the exception as needed
        return None
    except Exception as e:
        logger.error(f'An error occurred in get_hotspots: {e}', exc_info=True)
        # Handle or raise the exception as needed
        return None
    
def verify_hotspot(hotspot):
    query = """
        SELECT h.name 
        FROM hotspots h
        JOIN routes r ON h.route_id = r.route_id
        WHERE h.name = %s;
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (hotspot,))
            result = cursor.fetchone()

            if result:
                return result[0]  # hotspot name
            else:
                return None

    except OperationalError as e:
        logger.error(f'Operational error in verify_hotspot: {e}', exc_info=True)
        return None
    except Exception as e:
        logger.error(f'Unexpected error in verify_hotspot: {e}', exc_info=True)
        return None

def send_template_with_parameter(phone_number, template_name, hotspot):
    json_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": "en_US"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": hotspot
                        }
                    ]
                }
            ]
        }
    }

    headers = {
        "Authorization": AUTHORIZATION,
        "Content-Type": APPLICATION_JSON
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"template sent successfully: template_name: {template_name}, phone_number: {phone_number}")
            
            response_data = response.json()
            
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send document template message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending template message: {e}", exc_info=True)
        return None
 






















def send_search_catalog_message(phone_number, product_list, search):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": AUTHORIZATION
    }
    
    batch_size = 30
    total_batches = math.ceil(len(product_list) / batch_size)
    
    for batch_index in range(total_batches):
        batch_start = batch_index * batch_size
        batch_end = batch_start + batch_size
        batch_products = product_list[batch_start:batch_end]
        
        product_items = [{"product_retailer_id": product_id} for product_id in batch_products]
        page_info = f"Page [{batch_index + 1} of {total_batches}]"

        json_data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "product_list",
                "header": {
                    "type": "TEXT",
                    "text": "Find Products"
                },
                "body": {
                    "text": f"Searched: *{search}*"
                },
                "action": {
                    "catalog_id": "1148125030695385",
                    "sections": [
                        {
                            "title": f"Results for: {search}",
                            "product_items": product_items

                        }
                    ]
                }
            }
        }
        
       
        try:
            response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"Catalog message successfully sent. Phone number: {phone_number}, Page: {page_info}")
                response_data = response.json()
                logger.debug(f"Response JSON: {response_data}")
            else:
                logger.error(f"Failed to send Catalog message. Status Code: {response.status_code}. Response Content: {response.content}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending message: {e}", exc_info=True)

def send_welcome_message(phone_number):
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
                "text": "👋 Welcome to Royal Property Valuers"
            },
            "body": {
                "text": "What would you like to do today?"
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
                            {"id": "1", "title": "🏠 Buy"},
                            {"id": "2", "title": "🏡 Rent"},

                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"send_welcome_message interactive message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send send_welcome_message message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def send_property_type_message(phone_number):
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
                "text": "Property Type"
            },
            "body": {
                "text": "What type of property are you looking for?"
            },
            "action": {
                "button": "Type",
                "sections": [
                    {
                        "title": "Please choose an option",
                        "rows": [
                            {"id": "1", "title": "🏘️ Residential"},
                            {"id": "2", "title": "🏢 Commercial"},
                            {"id": "3", "title": "🌾 Agricultural"},

                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"send_welcome_message interactive message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send send_welcome_message message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None






############### PAY ###############


######### DB #########
def get_user_id(phone_number):
    query = "SELECT user_id FROM users WHERE phone_number = %s;"

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (phone_number,))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                # Handle case where no customer is found
                # Example: You might want to register the user here
                # register_user(phone_number)
                return None

    except OperationalError as e:
        logger.error(f'Operational error occurred in get_user_id: {e}', exc_info=True)
        # Handle or raise the exception as needed
        return None
    except Exception as e:
        logger.error(f'An error occurred in get_user_id: {e}', exc_info=True)
        # Handle or raise the exception as needed
        return None

def save_wallet_user(save_user_dict):
    try:
        query = """
            INSERT INTO users (username, first_name, last_name, phone_number, email, date_of_birth, pin, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP());
        """

        with connection.cursor() as cursor:
            # 1️⃣ Save user
            cursor.execute(query, (
                save_user_dict[USERNAME],
                save_user_dict[FIRSTNAME],
                save_user_dict[LASTNAME],
                save_user_dict[PHONE_NUMBER],
                save_user_dict[EMAIL],
                save_user_dict[DATE_OF_BIRTH],
                save_user_dict[PIN]
            ))
            # Get the inserted user_id
            user_id = cursor.lastrowid

            # 2️⃣ Initialize balance for new user
            cursor.execute(
                "INSERT INTO balances (balance, user_id) VALUES (%s, %s);",
                (0.0, user_id)
            )

            connection.commit()

            # 3️⃣ Logging and sending messages
            logger.info(f"User saved successfully. username: {save_user_dict[USERNAME]}, phone: {save_user_dict[PHONE_NUMBER]}")
            send_message("Account Successfully Created!", save_user_dict[PHONE_NUMBER])
            menu_message(save_user_dict[PHONE_NUMBER])

    except Exception as e:
        connection.rollback()
        logger.error(f'An error occurred saving user or initializing balance: {e}', exc_info=True)

# def save_transaction(save_transaction_dict):
#     try:
#         user_id = save_transaction_dict[USER_ID]
#         amount = float(save_transaction_dict[AMOUNT])  # make sure it's numeric
#         transaction_type = save_transaction_dict[TRANSACTION_TYPE]
#         phone_number = save_transaction_dict[PHONE_NUMBER]
#         transaction = save_transaction_dict[TRANSACTION]

#         with connection.cursor() as cursor:
#             # 1️⃣ Get current balance
#             select_balance_query = "SELECT balance FROM balances WHERE user_id = %s FOR UPDATE;"
#             cursor.execute(select_balance_query, (user_id,))
#             result = cursor.fetchone()

#             if result:
#                 current_balance = float(result[0])
#             else:
#                 # If user has no balance yet, assume 0 and create record
#                 current_balance = 0.0
#                 cursor.execute(
#                     "INSERT INTO balances (balance, user_id) VALUES (%s, %s);",
#                     (current_balance, user_id)
#                 )

#             # 2️⃣ Check if payment would make balance negative
#             if transaction_type.lower() in [PAY_FRIEND, PAY_MERCHANT]:
#                 if amount > current_balance:
#                     send_message(
#                         f"⚠️ Insufficient funds! Your current balance is P{current_balance:.2f}.",
#                         phone_number
#                     )
#                     return  # Stop the transaction

#             # 3️⃣ Insert transaction
#             insert_query = """
#                 INSERT INTO transactions (transaction_type, amount, transaction, created_at, user_id)
#                 VALUES (%s, %s, %s, CURRENT_TIMESTAMP(), %s);
#             """
#             cursor.execute(insert_query, (transaction_type, amount, transaction, user_id))

#             # 4️⃣ Update balance
#             if transaction_type.lower() in [ADD_FUNDS, RECEIVE]:
#                 new_balance = current_balance + amount
#             else:  # deduct for PAY, SPLIT_BILL, REQUEST, PAY_MERCHANT
#                 new_balance = current_balance - amount

#             update_balance_query = "UPDATE balances SET balance = %s WHERE user_id = %s;"
#             cursor.execute(update_balance_query, (new_balance, user_id))

#             connection.commit()

#             # 5️⃣ Send confirmation messages
#             if transaction_type.lower() == ADD_FUNDS:
#                 send_message(
#                     f"Funds added successfully! 🎉\n\nYour new wallet balance is: P{new_balance:.2f}",
#                     phone_number
#                 )
#             elif transaction_type.lower() == PAY_MERCHANT:
#                 send_message(
#                     f"✅ Payment Successful!\n\nYou have paid Merchant ID: *{transaction}*\n\nAmount: P{amount:.2f}\n\nNew Balance: *P{new_balance:.2f}*",
#                     phone_number
#                 )
#             elif transaction_type.lower() == PAY_FRIEND:
#                 send_message(
#                     f"✅ Payment Successful!\n\nYou have paid Friend: *{transaction}*\n\nAmount: P{amount:.2f}\n\nNew Balance: *P{new_balance:.2f}*",
#                     phone_number
#                 )

#             logger.info(f"Transaction saved and balance updated successfully for user {user_id}.")

#     except Exception as e:
#         connection.rollback()
#         logger.error(f'An error occurred saving transaction or updating balance: {e}', exc_info=True)

def save_transaction(save_transaction_dict):
    try:
        user_id = save_transaction_dict[USER_ID]
        amount = float(save_transaction_dict[AMOUNT]) 
        transaction_type = save_transaction_dict[TRANSACTION_TYPE].lower()
        phone_number = save_transaction_dict[PHONE_NUMBER]
        transaction = save_transaction_dict[TRANSACTION]

        with connection.cursor() as cursor:
            # 1️⃣ Get sender's current balance
            select_balance_query = "SELECT balance FROM balances WHERE user_id = %s FOR UPDATE;"
            cursor.execute(select_balance_query, (user_id,))
            result = cursor.fetchone()

            if result:
                sender_balance = float(result[0])
            else:
                sender_balance = 0.0
                cursor.execute(
                    "INSERT INTO balances (balance, user_id) VALUES (%s, %s);",
                    (sender_balance, user_id)
                )

            # 2️⃣ Check if payment would make balance negative
            if transaction_type in [PAY_FRIEND, PAY_MERCHANT]:
                if amount > sender_balance:
                    send_message(
                        f"⚠️ Insufficient funds! Your current balance is P{sender_balance:.2f}.",
                        phone_number
                    )
                    return  # Stop the transaction

            # 3️⃣ Insert sender's transaction
            insert_query = """
                INSERT INTO transactions (transaction_type, amount, transaction, created_at, user_id)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP(), %s);
            """
            cursor.execute(insert_query, (transaction_type, amount, transaction, user_id))

            # 4️⃣ Update sender's balance
            if transaction_type in [ADD_FUNDS, RECEIVE]:
                new_balance = sender_balance + amount
            else:  # deduct for PAY, SPLIT_BILL, REQUEST, PAY_MERCHANT, PAY_FRIEND
                new_balance = sender_balance - amount

            update_balance_query = "UPDATE balances SET balance = %s WHERE user_id = %s;"
            cursor.execute(update_balance_query, (new_balance, user_id))

            # 5️⃣ If PAY_FRIEND, update recipient's balance and send them a message
            if transaction_type == PAY_FRIEND:
                # Look up friend's user_id by phone number
                cursor.execute("SELECT user_id, balance FROM balances WHERE user_id = (SELECT user_id FROM users WHERE phone_number = %s) FOR UPDATE;", (transaction,))
                friend_result = cursor.fetchone()

                if friend_result:
                    friend_id, friend_balance = friend_result
                    friend_new_balance = friend_balance + amount
                    cursor.execute("UPDATE balances SET balance = %s WHERE user_id = %s;", (friend_new_balance, friend_id))
                    # Optionally log the transaction for the friend
                    cursor.execute(
                        insert_query,
                        ("RECEIVE", amount, f"From Friend ID {user_id}", friend_id)
                    )
                    # Send message to friend
                    send_message(
                        f"💸 You have received P{amount:.2f} from a friend!\nYour new balance is: P{friend_new_balance:.2f}",
                        transaction  # friend's phone number
                    )
                else:
                    # Handle case where friend doesn't exist
                    # send_message(
                    #     f"⚠️ Could not find a wallet for {transaction}. Payment recorded but recipient not notified.",
                    #     phone_number
                    # )

                    send_message(
                    f"✅ Payment Successful!\n\nYou have paid Friend: *{transaction}*\n\nAmount: P{amount:.2f}\n\nNew Balance: *P{new_balance:.2f}*",
                    phone_number
                )

            connection.commit()

            # 6️⃣ Send confirmation message to sender
            send_message(
                f"✅ Payment Successful!\n\nYou have paid Friend: *{transaction}*\nAmount: P{amount:.2f}\nNew Balance: P{new_balance:.2f}",
                phone_number
            )

            logger.info(f"Transaction saved and balance updated successfully for user {user_id}.")

    except Exception as e:
        connection.rollback()
        logger.error(f'An error occurred saving transaction or updating balance: {e}', exc_info=True)


def get_user_pin(phone_number):
    query = "SELECT pin FROM users WHERE phone_number = %s;"

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (phone_number,))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                # Handle case where no customer is found
                # Example: You might want to register the user here
                # register_user(phone_number)
                return None

    except OperationalError as e:
        logger.error(f'Operational error occurred in get_user_pin: {e}', exc_info=True)
        # Handle or raise the exception as needed
        return None
    except Exception as e:
        logger.error(f'An error occurred in get_user_pin: {e}', exc_info=True)
        # Handle or raise the exception as needed
        return None

def get_user_transactions(user_id, limit=5):
    """
    Fetch recent transactions for a user, limited to 'limit' rows.
    """
    query = """
        SELECT transaction_id, transaction_type, amount, transaction, created_at
        FROM transactions
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s;
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (user_id, limit))
            results = cursor.fetchall()
            return results
    except Exception as e:
        logger.error(f"Error fetching transactions for user {user_id}: {e}", exc_info=True)
        return []
    




######## FLOW ########
def send_flow_message(phone_number, header, body, flow_id, flow_token, cta):

    json_data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "recipient_type": "individual",
        "type": "interactive",
        "interactive": {
            "type": "flow",
            "header": {
                "type": "text",
                "text": header
            },
            "body": {
                "text": body
            },
            "action": {
                "name": "flow",
                "parameters": {
                    "flow_message_version": "3",
                    "flow_action": "navigate",
                    "flow_token": flow_token,
                    "flow_id": flow_id,
                    "flow_cta": cta,
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


    headers = {
        "Authorization": AUTHORIZATION,
        "Content-Type": APPLICATION_JSON
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"flow sent successfully: flow_id: {flow_id}, phone_number: {phone_number}")
            
            response_data = response.json()
            
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send flow message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending flow message: {e}", exc_info=True)
        return None


######## METHODS #########
def handle_reply(reply, message_id, phone_number, username, display_phone_number):

    if display_phone_number == TEST_PHONE_NUMBER:
        reply = reply.lower()

        user_id = get_user_id(phone_number)

        if not user_id:
            send_flow_message(phone_number, REGISTER_TITLE, REGISTER_BODY, REGISTER_FLOW_ID, REGISTER_FLOW_TOKEN, REGISTER_CTA)
            return

        if reply == MENU:
            menu_message(phone_number)

        elif reply == MY_BALANCE:
            balance = get_user_balance(get_user_id(phone_number))
            if balance is not None:
                send_message(f"Your current balance is: *P{balance:.2f}*", phone_number)
            else:
                send_message("No balance record found for your account.", phone_number)

        elif reply == ADD_FUNDS:
            send_flow_message(phone_number, CARD_DETAILS_FLOW_TITLE, CARD_DETAILS_FLOW_BODY, CARD_DETAILS_FLOW_ID, CARD_DETAILS_FLOW_TOKEN, CARD_DETAILS_FLOW_CTA)

        elif reply == PAY:
            pay_options_message(phone_number)

        elif reply == PAY_MERCHANT:
            send_flow_message(phone_number, PAY_MERCHANT_FLOW_TITLE, PAY_MERCHANT_FLOW_BODY, PAY_MERCHANT_FLOW_ID, PAY_MERCHANT_FLOW_TOKEN, PAY_MERCHANT_FLOW_CTA)

        elif reply == RECEIVE:
            send_message(f'💡 To receive a payment, share this number with the payer: {phone_number}\n\nThey will use it to send money directly to your wallet.', phone_number)

        elif reply == TRANSACTIONS:
            user_id = get_user_id(phone_number)
            transactions = get_user_transactions(user_id)
            message = format_transactions(transactions)
            send_message(message, phone_number)

        elif reply == PAY_FRIEND:
            send_flow_message(phone_number, PAY_FRIEND_FLOW_TITLE, PAY_FRIEND_FLOW_BODY, PAY_FRIEND_FLOW_ID, PAY_FRIEND_FLOW_TOKEN, PAY_FRIEND_FLOW_CTA)

        else:
            menu_message(phone_number)
        
def menu_message(phone_number):
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
                "text": "👋 Welcome to Your Wallet"
            },
            "body": {
                "text": "Manage your money and explore features. Tap below to see the menu."
            },
            "footer": {
                "text": "You can type *menu* at any time to return to this screen."
            },
            "action": {
                "button": "Open Menu",
                "sections": [
                    {
                        "title": "Please choose an option",
                        "rows": [
                            {"id": "1", "title": "My Balance"},
                            {"id": "2", "title": "Pay"},
                            {"id": "3", "title": "Receive"},
                            # {"id": "4", "title": "Request"},
                            # {"id": "5", "title": "Split Bill"},
                            {"id": "6", "title": "Add Funds"},
                            {"id": "7", "title": "Transactions"},

                        ]
                    },
                ]
            }
        }
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"send_welcome_message interactive message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send send_welcome_message message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def pay_options_message(phone_number):
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
                "text": "Payment Options"
            },
            "body": {
                "text": "Select who you’d like to pay"
            },
            "action": {
                "button": "Options",
                "sections": [
                    {
                        "title": "Please choose an option",
                        "rows": [
                            {"id": "1", "title": "Pay Merchant"},
                            {"id": "2", "title": "Pay Friend"},

                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"pay_options_message interactive message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send pay_options_message message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def get_user_balance(user_id):
    """
    Fetch the current wallet balance for a given user.
    Returns a float balance or None if not found.
    """
    query = "SELECT balance FROM balances WHERE user_id = %s;"
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            if result:
                return float(result[0])  # Convert balance from varchar to float
            else:
                return None  # User has no balance record yet
    except Exception as e:
        logger.error(f"An error occurred fetching balance for user {user_id}: {e}", exc_info=True)
        return None

def format_transactions(transactions):
    if not transactions:
        return "📜 No recent transactions found."

    message = "📜 Transaction History\n\n"
    for txn in transactions:
        txn_id, txn_type, amount, txn_detail, created_at = txn
        # Format date cleanly: 23 Sep 2025, 12:48
        formatted_date = datetime.strftime(created_at, "%d %b %Y, %H:%M")
        message += (
            f"#{txn_id} | {txn_type.title()}"
            + (f" ({txn_detail})" if txn_detail else "")
            + f"\nAmount: P{float(amount):.2f}\nDate: {formatted_date}\n\n"
        )
    return message.strip()





        