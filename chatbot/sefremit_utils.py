from django.db import connection
from .sefremit_constants import *
import requests
from django.db import connection, OperationalError
import logging

logger = logging.getLogger(CHATBOT_CATALOG)

def send_image_with_description(url, phone_number, caption):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": SEFREMIT_AUTHORIZATION
    }
    
    json_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "image",
        "image": {
            "link": url,
            "caption": caption
        }
    }
    
    try:
        response = requests.post(SEFREMIT_MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Image sent successfully. url: {url}, phone: {phone_number}")

            response_data = response.json()

            logger.debug(f"Response JSON: {response_data}")

            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send image. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending Image: {e}", exc_info=True)
        return None

def send_sefremit_message(message, phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": SEFREMIT_AUTHORIZATION
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
        response = requests.post(SEFREMIT_MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
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

def send_interactive_sefremit_menu_message(phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": SEFREMIT_AUTHORIZATION
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
                "text": "Welcome to SefRemit Money transfer | Bureau de Change"
            },
            "body": {
                "text": "SefRemit is diversified global provider of financial services and solutions. It facilitates the seamless movement of money across geographies, currencies, and channels via multiple customer touch points including retail stores."
            },
            "footer": {
                "text": "You can type *SefRemit* at any time to return to this screen."
            },
            "action": {
                "button": "Options",
                "sections": [
                    {
                        "title": "Please choose an option",
                        "rows": [
                            {"id": "1", "title": "Services"},
                            {"id": "2", "title": "Todays Rates"},
                            {"id": "3", "title": "Branch Hours"},
                            {"id": "5", "title": "Transaction Limits"},
                            {"id": "6", "title": "KYC Requirements"},
                            {"id": "7", "title": "Upcoming Events"},
                            {"id": "8", "title": "Promotions"}
                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(SEFREMIT_MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"send_interactive_sefremit_menu_message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send send_interactive_sefremit_menu_message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending send_interactive_sefremit_menu_message: {e}", exc_info=True)
        return None

def send_interactive_sefremit_services_menu_message(phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": SEFREMIT_AUTHORIZATION
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
                "text": "Our Services"
            },
            "body": {
                "text": "SefRemit Bureau de Change offers multiple financial solutions designed to meet your needs."
            },
            "action": {
                "button": "Services",
                "sections": [
                    {
                        "title": "Please choose an option",
                        "rows": [
                            {"id": "1", "title": "Cash Pickup"},
                            {"id": "2", "title": "Foreign CurrencyExchange"},
                            {"id": "3", "title": "Global Money Transfer"}
                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(SEFREMIT_MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"send_interactive_sefremit_services_menu_message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send send_interactive_sefremit_services_menu_message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending send_interactive_sefremit_services_menu_message: {e}", exc_info=True)
        return None

def send_interactive_sefremit_agency_banking_menu_message(phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": SEFREMIT_AUTHORIZATION
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
                "text": "Agency Banking"
            },
            "body": {
                "text": "You can make deposits or withdrawals at these banks using our SefRemit service."
            },
            "action": {
                "button": "Banks",
                "sections": [
                    {
                        "title": "Please choose an option",
                        "rows": [
                            {"id": "1", "title": "Standard Chartered"}
                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(SEFREMIT_MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"send_interactive_sefremit_agency_banking_menu_message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send send_interactive_sefremit_agency_banking_menu_message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending send_interactive_sefremit_agency_banking_menu_message: {e}", exc_info=True)
        return None

def send_sefremit_image(url, phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": SEFREMIT_AUTHORIZATION
    }
    
    json_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "image",
        "image": {
            "link": url
        }
    }
    
    try:
        response = requests.post(SEFREMIT_MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Image sent successfully. url: {url}, phone: {phone_number}")

            response_data = response.json()

            logger.debug(f"Response JSON: {response_data}")

            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send image. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending Image: {e}", exc_info=True)
        return None

def send_survey_flow(phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": "Bearer EAAGEVZB3PErsBO0su0lexA8f56akL6C9rXC5Ba4suLXQnwYkoFutROdO7mXEfKfRQN8C0kZCziHusufSe1MmDj3vKxaIL6yUfkBofb26Pg2kE9O6eMz0sjhf4jnm3hiWpgpURhORNk27hQZBjAT1PaZAPpljezHZBQQIfE0a8I5hPfRX2ZA0ezEG2HtOb6IwUU"
    }

    json_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": "poll_template_test_2",
            "language": {
                "code": "en_US"
            },
            "components": [
                {
                    "type": "button",
                    "sub_type": "flow",
                    "index": "0",
                    "parameters": [
                        {
                            "type": "action",
                            "action": {
                                "flow_token": "1067499460905066"
                            }
                        }
                    ]
                }
            ]
        }
    }
        
    try:
        response = requests.post("https://graph.facebook.com/v20.0/286939801179582/messages", json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Flow template sent successfully. flow: survey flow, phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None



