from django.db import connection
from .constants import *
import requests
import math
from django.db import connection, OperationalError
import logging
import phonenumbers
from phonenumbers import carrier
from django.core.cache import cache
from datetime import datetime
import time
import re
from barcode import Code128 
from barcode.writer import ImageWriter 
from io import BytesIO
import uuid
from collections import defaultdict
from whois import whois



# Get an instance of a logger
logger = logging.getLogger(CHATBOT_CATALOG)

def handle_reply(reply, message_id, phone_number, username, display_phone_number):

    if display_phone_number == "26776448866":

        reply = reply.lower()

        # user_id = get_user_id(phone_number)


        # if not user_id:
        #     save_user({USERNAME: remove_emojis(username), PHONE_NUMBER: phone_number})               
        
        if reply == "menu":
            pass

        else:
            pass
                
            
    
def send_interactive_services(phone_number):
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
                "text": "BOCRA WhatsApp channel!"
            },
            "body": {
                "text": "Welcome to the BOCRA WhatsApp service. Get quick help with licensing, regulations, and consumer information anytime."
            },
            "footer": {
                "text": "You can type *Services* at any time to return to this screen."
            },
            "action": {
                "button": "Services",
                "sections": [
                    {
                        "title": "Complaints",
                        "rows": [
                            {"id": "8", "title": "File a Complaint"},
                            {"id": "9", "title": "Track a Complaint"},

                        ]
                    },
                    {
                        "title": "Domains",
                        "rows": [
                            {"id": "6", "title": ".bw Registration"},
                            {"id": "7", "title": "Become a Register"},

                        ]
                    },
                    {
                        "title": "Licensing",
                        "rows": [
                            {"id": "1", "title": "Apply for a Licence"},
                            {"id": "2", "title": "Verify a Licence"},
                        ]
                    },
                    {
                        "title": "Type Approval",
                        "rows": [
                            {"id": "3", "title": "Apply for Type Approval"},
                            {"id": "4", "title": "Type Approval Registry"},
                            {"id": "5", "title": "Device Verification"},

                        ]
                    },
                    {
                        "title": "Help",
                        "rows": [
                            {"id": "10", "title": "FAQs"},

                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"bocra intro message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def send_interactive_select_licence(phone_number):
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
                "text": "What licence do you need?"
            },
            "body": {
                "text": "Which sector does your business fall under?"
            },
            "action": {
                "button": "Sectors",
                "sections": [
                    {
                        "title": "Sector",
                        "rows": [
                            {"id": "1", "title": "Telecommunications"},
                            {"id": "2", "title": "Broadcasting"},
                            {"id": "3", "title": "Internet & ICT"},
                            {"id": "4", "title": "Postal"},
                            {"id": "5", "title": "Radio Spectrum"},
                            {"id": "6", "title": "Other / Not sure"},
                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def send_interactive_type_of_licence(phone_number):
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
                "text": "Type of License"
            },
            "body": {
                "text": "What type of license are you applying for??"
            },
            "action": {
                "button": "Type",
                "sections": [
                    {
                        "title": "Types",
                        "rows": [
                            {"id": "1", "title": "Aircraft Radio Licence"},
                            {"id": "2", "title": "Amateur Radio Licence"},
                            {"id": "3", "title": "Cellula Mobile Licence"},
                            {"id": "4", "title": "P2MP Licence"},
                            {"id": "5", "title": "P2P Licence"},
                            {"id": "6", "title": "Satellite Licence"},
                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def send_flow_message(phone_number, header, body, flow_id, flow_token, cta="Enter Details"):

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
 
def get_domain_info(domain):
    try:
        info = whois(domain)
        return {
            "success": True,
            "data": str(info)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def save_complaint(complaint_dict):
    try:
        query = """
            INSERT INTO complaints 
            (sector, fullname, email, operator, primary_complaint, complaint_text, has_reference)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    complaint_dict["sector"],
                    complaint_dict["fullname"],
                    complaint_dict["email"],
                    complaint_dict["operator"],
                    complaint_dict["primary_complaint"],
                    complaint_dict["complaint_text"],
                    complaint_dict["has_reference"]
                )
            )
            connection.commit()
            
            # Get the generated complaint_ref for this row
            cursor.execute("SELECT complaint_ref FROM complaints WHERE complaint_id = LAST_INSERT_ID();")
            complaint_ref = cursor.fetchone()[0]

            logger.info(
                f"Complaint saved successfully. fullname: {complaint_dict['fullname']}, sector: {complaint_dict['sector']}, ref: {complaint_ref}"
            )

            return complaint_ref

    except Exception as e:
        connection.rollback()
        logger.error(f"An error occurred saving complaint: {e}", exc_info=True)
        return None

def get_complaint_by_ref(complaint_ref):
    try:
        query = """
            SELECT complaint_id, complaint_ref, sector, fullname, email, operator, 
                   primary_complaint, complaint_text, has_reference
            FROM complaints
            WHERE complaint_ref = %s;
        """
        
        with connection.cursor() as cursor:
            cursor.execute(query, (complaint_ref,))
            result = cursor.fetchone()
            
            if result:
                # Convert result to a dictionary
                columns = [col[0] for col in cursor.description]
                complaint_data = dict(zip(columns, result))
                return complaint_data
            else:
                return None  # No complaint found

    except Exception as e:
        logger.error(f"An error occurred fetching complaint: {e}", exc_info=True)
        return None
    
    