from django.db import connection
from .constants import *
from .sefremit_constants import *
from .sefremit_utils import *
import requests
from django.db import connection, OperationalError
import logging
import phonenumbers
from phonenumbers import carrier
from django.core.cache import cache
from datetime import datetime
import time
import re

# Get an instance of a logger
logger = logging.getLogger(CHATBOT_CATALOG)

def get_customer_id(phone_number):
    query = "SELECT customer_id FROM customers WHERE phone_number = %s;"

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
        logger.error(f'Operational error occurred in get_customer_id: {e}', exc_info=True)
        # Handle or raise the exception as needed
        return None
    except Exception as e:
        logger.error(f'An error occurred in get_customer_id: {e}', exc_info=True)
        # Handle or raise the exception as needed
        return None

def save_customer(save_customer_dict):
    try:
        query = """
            INSERT INTO customers (username, phone_number, created_at, opt_out_all) 
            VALUES (%s, %s, CURRENT_TIMESTAMP(), False);
        """
        
        with connection.cursor() as cursor:
            cursor.execute(query, (save_customer_dict[USERNAME], save_customer_dict[PHONE_NUMBER]))
            connection.commit()
            logger.info(f"Customer saved successfully. username: {save_customer_dict[USERNAME]}, phone: {save_customer_dict[PHONE_NUMBER]}")

    except Exception as e:
        connection.rollback()
        logger.error(f'An error occurred saving customer: {e}', exc_info=True)

def update_customer_subscriptions(customer_subscription_param):
    try:
        if CUSTOMER_SUBSCRIPTION_ID in customer_subscription_param:
            query = """
                REPLACE INTO customer_subscriptions (customer_subscription_id, customer_id, subscription_id, opt_in_status) 
                VALUES (%s, %s, %s, %s);
            """
            params = (
                customer_subscription_param[CUSTOMER_SUBSCRIPTION_ID],
                customer_subscription_param[CUSTOMER_ID],
                customer_subscription_param[SUBSCRIPTION_ID],
                customer_subscription_param[OPT_IN_STATUS]
            )
        else:
            query = """
                REPLACE INTO customer_subscriptions (customer_id, subscription_id, opt_in_status) 
                VALUES (%s, %s, %s);
            """
            params = (
                customer_subscription_param[CUSTOMER_ID],
                customer_subscription_param[SUBSCRIPTION_ID],
                customer_subscription_param[OPT_IN_STATUS]
            )

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            connection.commit()
            logger.info(f"Successfully updated customer_subscriptions. customer_id: {customer_subscription_param[CUSTOMER_ID]}, subscription_id: {customer_subscription_param[SUBSCRIPTION_ID]}, opt_in_status: {customer_subscription_param[OPT_IN_STATUS]}")
            
    except Exception as e:
        connection.rollback()
        logger.error(f'An error occurred updating customer_subscriptions: {e}', exc_info=True)

def get_customer_subscriptions(customer_id):
    query = """
        SELECT customer_subscription_id, customer_id, subscription_id, opt_in_status 
        FROM customer_subscriptions 
        WHERE customer_id = %s;
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (customer_id,))
            results = cursor.fetchall()

            subscriptions_dict_lst = [
                {
                    CUSTOMER_SUBSCRIPTION_ID: customer_subscription_id,
                    CUSTOMER_ID: customer_id,
                    SUBSCRIPTION_ID: subscription_id,
                    OPT_IN_STATUS: opt_in_status
                }

                for customer_subscription_id, customer_id, subscription_id, opt_in_status in results
            ]
            
            return subscriptions_dict_lst

    except Exception as e:
        logger.error(f'An error occurred in get_customer_subscriptions: {e}', exc_info=True)
        return []

def get_customers_opted_in(subscription_id):
    query = """
        SELECT c.phone_number 
        FROM customers AS c
        JOIN customer_subscriptions AS cs ON c.customer_id = cs.customer_id
        WHERE c.opt_out_all = '0' 
        AND cs.opt_in_status = '1' 
        AND cs.subscription_id = %s;
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (subscription_id,))
            results = [row[0] for row in cursor.fetchall()]
            return results

    except Exception as e:
        logger.error(f'An error occurred in get_customers_opted_in: {e}', exc_info=True)
        return []

def send_template(phone_number, template_name, image_url):
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
                    "type": "header",
                    "parameters": [
                        {
                            "type": "image",
                            "image": {
                                "link": image_url
                            }
                        }
                    ]
                },
                {
                    "type": "body"
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
            logger.info(f"Template send successfully: template_name: {template_name}, phone_number: {phone_number}, image_url: {image_url}")
            
            response_data = response.json()
            
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def opt_customer_in_all(customer_id):
    query = "UPDATE customers SET opt_out_all = 0 WHERE customer_id = %(customer_id)s;"

    try:
        # Use context manager to get cursor from connection
        with connection.cursor() as cursor:
            # Execute the query with provided parameters
            cursor.execute(query, {"customer_id": customer_id})
            
            # Commit the transaction
            connection.commit()

        logger.info(f"Successfully opted in customer {customer_id} for all promotions.")
        
    except Exception as e:
        # Rollback any changes if an error occurs
        connection.rollback()
        logger.error(f"An error occurred while opting in customer {customer_id}: {e}", exc_info=True)

def send_image(url, phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": AUTHORIZATION
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
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
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

def get_new_customers():
    query = """
        SELECT customers.phone_number
        FROM customers
        LEFT JOIN customer_subscriptions ON customers.customer_id = customer_subscriptions.customer_id
        WHERE customer_subscriptions.customer_id IS NULL
        AND customers.opt_out_all = 0;
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = [x[0] for x in cursor.fetchall()]
            return results

    except Exception as e:
        logger.error(f"An error occurred in get_new_customers: {e}", exc_info=True)
        return []

def send_interactive_message_birthday_promo(phone_number):
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
                "text": "Welcome to Sefalana WhatsApp channel!"
            },
            "body": {
                "text": "Discover more about the competition."
            },
            "footer": {
                "text": "You can type *options* at any time to return to this screen."
            },
            "action": {
                "button": "Options",
                "sections": [
                    {
                        "title": "Please choose an option",
                        "rows": [
                            {"id": "1", "title": "Register my rewards card"},
                            {"id": "2", "title": "Prizes"},
                            {"id": "3", "title": "BIG-50 Birthday T&Cs"},
                            {"id": "4", "title": "How to enter"},
                            {"id": "7", "title": "Report Fraud"},
                            {"id": "8", "title": "Promotional Products"}
                        ]
                    },
                    {
                        "title": "Opt Out Of?",
                        "rows": [
                            {
                                "id": "5",
                                "title": "BIG-50 Birthday Bonanza",
                                "description": "Opt out of just the BIG-50 Birthday Bonanza"
                            },
                            {
                                "id": "6",
                                "title": "All Promotions",
                                "description": "Opt Out Of All Messages"
                            }
                        ]
                    }
                ]
            }
        }
    }

    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"birthday promo interactive message successfully sent. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def opt_out_options(phone_number):
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
                "text": "Opt Out Options"
            },
            "body": {
                "text": "Decide which promotions you wish to stop receiving."
            },
            "action": {
                "button": "Options",
                "sections": [
                    {
                        "title": "Opt Out Of?",
                        "rows": [
                            {
                                "id": "1",
                                "title": "BIG-50 Birthday Bonanza",
                                "description": "Opt out of just the BIG-50 Birthday Bonanza"
                            },
                            {
                                "id": "2",
                                "title": "All Promotions",
                                "description": "Opt Out Of All Messages"
                            }
                        ]
                    }
                ]
            }
        }
    }
 
    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Opt-out options message sent successfully. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send opt-out options message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending opt-out options message: {e}", exc_info=True)
        return None

def opt_in_options(phone_number):
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
                "text": "Opt In Options"
            },
            "body": {
                "text": "Decide which promotions you wish to start receiving."
            },
            "footer": {
                "text": "You can type *Opt In* at any time to return to this screen."
            },
            "action": {
                "button": "Options",
                "sections": [
                    {
                        "title": "Opt In For?",
                        "rows": [
                            {
                                "id": "1",
                                "title": "BIG-50 Birthday Bonanza",
                                "description": "Opt in for the BIG-50 Birthday Bonanza"
                            },
                            {
                                "id": "2",
                                "title": "All Promotions",
                                "description": "Opt In for All Promotions"
                            }
                        ]
                    }
                ]
            }
        }
    }
 
    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Opt-in options message sent successfully. phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send opt-in options message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending opt-in options message: {e}", exc_info=True)
        return None

def opt_customer_in_for_birthday_promotion(customer_id, subscription_id):
    query = "UPDATE customer_subscriptions SET opt_in_status = 1 WHERE subscription_id = %(subscription_id)s and customer_id = %(customer_id)s;"
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, {SUBSCRIPTION_ID: subscription_id, CUSTOMER_ID: customer_id})
            connection.commit()
            logger.info(f"Successfully opted customer in for birthday promotion. subscription_id: {subscription_id}, customer id: {customer_id}")
        
    except Exception as e:
        connection.rollback()
        logger.error("An error occurred while opting customer in for birthday promotion:", exc_info=True)

def opt_customer_out_all(phone_number):
    query = "UPDATE customers SET opt_out_all = 1 WHERE phone_number = %(phone_number)s;"
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, {"phone_number": phone_number})
            connection.commit()
            logger.info(f"Successfully opted customer out of all promotions. phone_number: {phone_number}")
        
    except Exception as e:
        connection.rollback()
        logger.error("An error occurred while opting customer out of all promotions:", exc_info=True)

def get_subscriptions():
    query = "SELECT subscription_id FROM subscriptions;"
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = [x[0] for x in cursor.fetchall()]
            
            if results:
                return results
            else:
                logger.info("No subscriptions found.")
                return []
                
    except Exception as e:
        logger.error("An error occurred in get_subscriptions:", exc_info=True)
        return []

def opt_customer_in_all_subscriptions(customer_id, subscriptions_lst):
    query = """
        UPDATE customer_subscriptions 
        SET opt_in_status = '1' 
        WHERE customer_id = %(customer_id)s 
        AND subscription_id = %(subscription_id)s;
    """
    
    try:
        with connection.cursor() as cursor:
            for subscription_id in subscriptions_lst:
                cursor.execute(query, {
                    CUSTOMER_ID: customer_id,
                    SUBSCRIPTION_ID: subscription_id
                })
            connection.commit()
            logger.info(f"Successfully opted customer in for all subscriptions. customer_id: {customer_id}, subscriptions: {subscriptions_lst}")
            
    except Exception as e:
        connection.rollback()
        logger.error("An error occurred in opt_customer_in_all_subscriptions:", exc_info=True)

def get_subscription_id(subscription_name):
    query = "SELECT subscription_id FROM subscriptions WHERE subscription_name = %(subscription_name)s;"

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, {SUBSCRIPTION_NAME: subscription_name})
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                logger.info(f"No subscription found with the given name. subscription_name: {subscription_name}")
                return None

    except Exception as e:
        logger.error("An error occurred in get_subscription_id:", exc_info=True)
        return None

def update_opt_out_all_customer_subscriptions(customer_id, sub_lst):
    try:
        # Use context manager to get cursor from connection
        with connection.cursor() as cursor:
            for sub_id in sub_lst:
                query = "REPLACE INTO customer_subscriptions(customer_id, subscription_id, opt_in_status) VALUES(%s, %s, '0');"
                cursor.execute(query, (customer_id, sub_id))
            
            # Commit the transaction
            connection.commit()

            logger.info(f"Successfully updated customer_subscriptions opt all out. customer_id: {customer_id}, subscription_lst: {sub_lst}")
        
    except Exception as e:
        logger.error(f"An unexpected error occurred in update_opt_out_all_customer_subscriptions: {e}", exc_info=True)

def update_opt_in_all_customer_subscriptions(customer_id, sub_lst):

    try:
        # Use context manager to get cursor from connection
        with connection.cursor() as cursor:
            for sub_id in sub_lst:
                query = "REPLACE INTO customer_subscriptions(customer_id, subscription_id, opt_in_status) VALUES(%(customer_id)s, %(sub_id)s, '1');"
                
                # Execute the query with provided parameters
                cursor.execute(query, {CUSTOMER_ID: customer_id, "sub_id": sub_id})
            
            # Commit the transaction
            connection.commit()
            
            logger.info(f"Successfully updated opt-in status for customer_id: {customer_id} in subscriptions: {sub_lst}")
        
    except Exception as e:
        logger.error(f"An error occurred in update_opt_in_all_customer_subscriptions: {e}", exc_info=True)
        # Rollback any changes if an error occurs
        connection.rollback()

def send_template_without_header(phone_number, template_name):
    json_data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": "en_US"
            }
        }
    }

    headers = {
        "Authorization": AUTHORIZATION,
        "Content-Type": APPLICATION_JSON
    }

    try:
        url = MESSAGES_ENDPOINT
        response = requests.post(url, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Successfully sent message to {phone_number}. Response: {response.json()}")
            return response.json()["messages"][0]["id"]
        else:
            logger.error(f"Failed to send message to {phone_number}. Status Code: {response.status_code}, Response Content: {response.content}")
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message to {phone_number}: {e}", exc_info=True)

def handle_reply(reply, message_id, phone_number, username, display_phone_number):

    reply = reply.lower()
       
    if reply == SERVICES:
        send_interactive_sefremit_services_menu_message(phone_number)

    elif reply == TODAYS_RATES:
        send_sefremit_image(SEFREMIT_TODAYS_RATES_URL, phone_number)

    elif reply == OPERATING_HOURS:
        send_sefremit_image(SEFREMIT_OPERATING_HOURS_URL, phone_number)

    elif reply == OUR_BRANCHES:
        send_sefremit_image(SEFREMIT_BRANCHES_URL, phone_number)

    elif reply == TRANSACTION_LIMITS:
        send_sefremit_message("The maximum transaction limit is BWP 10,000.00", phone_number)

    elif reply == KYC_REQUIREMENTS:
        send_sefremit_message(KYC_REQUIREMENTS_MESSAGE, phone_number)

    elif reply == EVENTS:
        send_sefremit_image(SEFREMIT_UPCOMING_EVENT, phone_number)

    elif reply == PARTNERS:
        send_sefremit_image(SEFREMIT_PARTNERS_URL, phone_number)

    elif reply == CASH_PICKUP:
        send_image_with_description(SEFREMIT_PARTNERS_URL, phone_number, CASH_PICKUP_CAPTION)

    elif reply == STANDARD_CHARTERED:
        send_sefremit_message(STANDARD_CHARTERED_REQUIREMENTS_MESSAGE, phone_number)

    elif reply == AGENCY_BANKING:
        send_interactive_sefremit_agency_banking_menu_message(phone_number)

    elif reply == "sefremit":
        send_interactive_sefremit_menu_message(phone_number)

    elif reply == FOREIGN_CURRECY_EXCHANGE:
        send_sefremit_message(FOREIGN_CURRECY_EXCHANGE_MESSAGE, phone_number)

    elif reply == GLOBAL_MONEY_TRANSER:
        send_image_with_description(SEFREMIT_TRANSFER_FEES, phone_number, GLOBAL_MONEY_TRANSER_MESSAGE)

    else:
        send_interactive_sefremit_menu_message(phone_number)

def handle_opt_out_big_50_birthday_bonanza(customer_id, phone_number):
    sub_id = get_subscription_id(BIRTHDAY_PROMOTION)
    customer_subscriptions_dict_lst = get_customer_subscriptions(customer_id)

    if customer_subscriptions_dict_lst:
        for customer_subscriptions_dict in customer_subscriptions_dict_lst:
            if CUSTOMER_SUBSCRIPTION_ID in customer_subscriptions_dict:
                if customer_subscriptions_dict[SUBSCRIPTION_ID] == sub_id:
                    update_customer_subscriptions({
                        CUSTOMER_SUBSCRIPTION_ID: customer_subscriptions_dict[CUSTOMER_SUBSCRIPTION_ID],
                        CUSTOMER_ID: customer_subscriptions_dict[CUSTOMER_ID],
                        SUBSCRIPTION_ID: customer_subscriptions_dict[SUBSCRIPTION_ID],
                        OPT_IN_STATUS: False
                    })
            else:
                update_customer_subscriptions({
                    CUSTOMER_ID: customer_id,
                    SUBSCRIPTION_ID: sub_id,
                    OPT_IN_STATUS: False
                })

    message = OPT_OUT_BIG_50_MESSAGE
    send_message(message, phone_number)

def handle_opt_out_all_messages(customer_id, phone_number):
    opt_customer_out_all(phone_number)
    customer_subscriptions_dict_lst = get_customer_subscriptions(customer_id)
    
    if customer_subscriptions_dict_lst:
        for customer_subscriptions_dict in customer_subscriptions_dict_lst:
            update_customer_subscriptions({
                CUSTOMER_SUBSCRIPTION_ID: customer_subscriptions_dict.get(CUSTOMER_SUBSCRIPTION_ID),
                CUSTOMER_ID: customer_subscriptions_dict[CUSTOMER_ID],
                SUBSCRIPTION_ID: customer_subscriptions_dict[SUBSCRIPTION_ID],
                OPT_IN_STATUS: False
            })
    else:
        update_opt_out_all_customer_subscriptions(customer_id, get_subscriptions())
    
    message = OPT_OUT_ALL_PROMOTIONS_MESSAGE
    send_message(message, phone_number)

def handle_prizes(phone_number):
    message = PRIZES_MESSAGE
    send_message(message, phone_number)

def handle_join(customer_id, phone_number):
    sub_id = get_subscription_id(BIRTHDAY_PROMOTION)
    customer_subscriptions_dict_lst = get_customer_subscriptions(customer_id)
    
    if customer_subscriptions_dict_lst:
        for customer_subscriptions_dict in customer_subscriptions_dict_lst:
            update_customer_subscriptions({
                CUSTOMER_SUBSCRIPTION_ID: customer_subscriptions_dict.get(CUSTOMER_SUBSCRIPTION_ID),
                CUSTOMER_ID: customer_subscriptions_dict[CUSTOMER_ID],
                SUBSCRIPTION_ID: customer_subscriptions_dict[SUBSCRIPTION_ID],
                OPT_IN_STATUS: True
            })
    else:
        update_customer_subscriptions({
            CUSTOMER_ID: customer_id,
            SUBSCRIPTION_ID: sub_id,
            OPT_IN_STATUS: True
        })
    
    send_interactive_message_birthday_promo(phone_number)

def handle_opt_in_big_50_birthday_bonanza(customer_id, phone_number):
    subscription_id = get_subscription_id(BIRTHDAY_PROMOTION)
    opt_customer_in_for_birthday_promotion(customer_id, subscription_id)
    opt_customer_in_all(customer_id)
    send_message(OPT_IN_BIG_50_MESSAGE, phone_number)

def handle_opt_in_all_promotions(customer_id, phone_number):
    opt_customer_in_all_subscriptions(customer_id, get_subscriptions())
    opt_customer_in_all(customer_id)
    send_message(OPT_IN_ALL_PROMOTION_MESSAGE, phone_number)

def handle_leaflets(event_name, phone_number):
    for path in get_image_urls(event_name):
        url = f"{DOMAIN_ENDPOINT}/{path}"
        send_image(url, phone_number)
        time.sleep(1)

def handle_default(customer_id, phone_number):
    new_customers = get_new_customers()
    if new_customers:
        customer_subscriptions_dict_lst = get_customer_subscriptions(customer_id)
        
        if customer_subscriptions_dict_lst:
            send_interactive_message_birthday_promo(phone_number)
        else:
            update_opt_in_all_customer_subscriptions(get_customer_id(phone_number), get_subscriptions())
            send_interactive_message_birthday_promo(phone_number)
    else:
        send_interactive_message_birthday_promo(phone_number)

def handle_opt_out_options(customer_id, phone_number):
    new_customers = get_new_customers()
    if new_customers:
        customer_subscriptions_dict_lst = get_customer_subscriptions(customer_id)
        
        if customer_subscriptions_dict_lst:
            opt_out_options(phone_number)
        else:
            update_opt_in_all_customer_subscriptions(get_customer_id(phone_number), get_subscriptions())
            opt_out_options(phone_number)
    else:
        opt_out_options(phone_number)

def update_interactions(interaction_dict):
    try:
        # Use context manager to get cursor from connection
        with connection.cursor() as cursor:
            query = "REPLACE INTO interactions(interaction_type, timestamp, customer_id) VALUES(%s, current_timestamp(), %s);"
            cursor.execute(query, (interaction_dict[INTERACTION_TYPE], interaction_dict[CUSTOMER_ID]))
            
            # Commit the transaction
            connection.commit()

            logger.info(f"Successfully updated customer interaction: interaction_type: {interaction_dict[INTERACTION_TYPE]}, customer_id: {interaction_dict[CUSTOMER_ID]}")
        
    except Exception as e:
        logger.error(f"An unexpected error occurred in update_interactions: {e}", exc_info=True)

def add_event(event_name, subscription_id):
    try:
        # Use context manager to get cursor from connection
        with connection.cursor() as cursor:
            query = "REPLACE INTO events(event_name, event_timestamp, subscription_id) VALUES(%s, current_timestamp(), %s);"
            cursor.execute(query, (event_name, subscription_id))
            
            # Commit the transaction
            connection.commit()

            logger.info(f"Successfully added event. event_name: {event_name}, subscription_id: {subscription_id}")
        
    except Exception as e:
        logger.error(f"An unexpected error occurred in add_event: {e}", exc_info=True)

def get_event_id(event_name):
    query = "SELECT event_id FROM events WHERE event_name = %s;"

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (event_name,))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                logger.info(f"{event_name} not found")
                return None

    except Exception as e:
        logger.error(f'An error occurred in get_event_id: {e}', exc_info=True)
        # Handle or raise the exception as needed
        return None

def add_event_images_to_db(event_id, url_dict_lst):
    try:
        # Use context manager to get cursor from connection
        with connection.cursor() as cursor:
            # Iterate through the list of items
            for url_dict in url_dict_lst:
                query = "REPLACE INTO event_images(event_id, url) VALUES(%s, %s);"
                url = url_dict.get('url')

                cursor.execute(query, (event_id, url))

                logger.info(f"Successfully added image url. event_id: {event_id}, url: {url}")
            
            # Commit the transaction
            connection.commit()
        
    except Exception as e:
        logger.error(f"An unexpected error occurred in add_event_images_to_db: {e}", exc_info=True)

def get_image_urls(event_name):
    query = "select ei.path from event_images as ei, events as e where e.event_id = ei.event_id and e.event_name = %s;"
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (event_name,))
            results = [x[0] for x in cursor.fetchall()]
            
            if results:
                return results
            else:
                logger.info(f"No image urls found for event_name: {event_name}.")
                return []
                
    except Exception as e:
        logger.error("An error occurred in get_image_urls:", exc_info=True)
        return []

def format_and_get_carrier(phone_number):
    try:
        # Parse the phone number with default region set to Botswana ("BW")
        parsed_number = phonenumbers.parse(phone_number, "BW")

        # Format the phone number to E164 format (including country code)
        formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)

        # Get the carrier name
        carrier_name = carrier.name_for_number(parsed_number, "en")

        if carrier_name is None:
            carrier_name = "Carrier information not available"

        return formatted_number[1:], carrier_name  # Return formatted number without '+'

    except phonenumbers.phonenumberutil.NumberParseException as e:
        logger.error(f"Error parsing {phone_number}: {e}")
        return None, "Error parsing number"

    except Exception as e:
        logger.error(f"Error processing {phone_number}: {e}")
        return None, "Error processing number"

def delete_cache_customer_id(customer_id):
    # Remove the cached item by phone_number
    cache.delete(customer_id)

    # Verify removal
    if cache.get(customer_id) is None:
        logger.info(f"Cache entry with key '{customer_id}' has been successfully removed.")
        return True
    else:
        logger.info(f"Failed to remove cache entry with key '{customer_id}'.")
        return False

def is_customer_id_cached(customer_id):
    cached_value = cache.get(customer_id)
    return cached_value is not None

def is_difference_more_than_24_hours(timestamp_str):
    # Parse the timestamp string into a datetime object
    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

    # Get the current time
    current_time = datetime.now()

    # Calculate the difference
    time_difference = current_time - timestamp

    # Check if the difference is more than or equal to 24 hours
    if time_difference.total_seconds() >= 24 * 3600:  # 24 hours in seconds
        return True
    else:
        return False
 
def save_conversation_limit_to_db(conversation_limit_lst, conversation_status_id):

    try:
        query = """
            INSERT INTO conversation_limit_cache (timestamp, customer_id, limit_status_id) 
            VALUES (%s, %s, %s);
        """
        
        with connection.cursor() as cursor:
            for key, value in conversation_limit_lst:
                match = re.search(r'\d+', key)

                if match:
                    customer_id = int(match.group())
                    cursor.execute(query, (value, customer_id, conversation_status_id))

            connection.commit()

            logger.info(f"Saved conversation limit caches")

    except Exception as e:
        connection.rollback()
        logger.error(f'An error occurred save_conversation_limit_to_db: {e}', exc_info=True)
    
def get_conversation_status_id(status):
    query = "SELECT limit_status_id FROM limit_status WHERE status = %s;"

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (status,))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                # Handle case where no customer is found
                # Example: You might want to register the user here
                # register_user(phone_number)
                return None

    except Exception as e:
        logger.error(f'An error occurred in get_conversation_status_id: {e}', exc_info=True)
        # Handle or raise the exception as needed
        return None

def cache_customer_id(customer_id, current_timestamp=None, cache_timeout=26 * 3600, use_limit=False):
    if current_timestamp is None:
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if use_limit and is_cache_limit_reached():
        return handle_over_limit_cache(customer_id, current_timestamp, cache_timeout)
    
    return handle_standard_cache(customer_id, current_timestamp, cache_timeout)

def is_cache_limit_reached():
    # Get all keys starting with "TRAFFIC_"
    traffic_keys = cache.keys(f'{APPEND_TRAFFIC}*')
    return len(traffic_keys) >= 3 # make it 10 000

def handle_over_limit_cache(customer_id, current_timestamp, cache_timeout):
    cus_id = f"{customer_id}_{OVER_LIMIT}"
    existing_value = cache.get(cus_id)
    
    if existing_value is not None:
        logger.info(f"Over limit Customer ID {cus_id} already exists in the cache with value: {existing_value}")
        return None
    else:
        cache.set(cus_id, current_timestamp, timeout=cache_timeout)
        logger.info(f"Over limit Customer ID {cus_id} has been cached with value: {current_timestamp} for 26 hours")
        return None

def handle_standard_cache(customer_id, current_timestamp, cache_timeout):
    existing_value = cache.get(customer_id)
    
    if existing_value is not None:
        logger.info(f"Customer ID {customer_id} already exists in the cache with value: {existing_value}")
        return existing_value
    else:
        cache.set(customer_id, current_timestamp, timeout=cache_timeout)
        logger.info(f"Customer ID {customer_id} has been cached with value: {current_timestamp} for 26 hours")
        return cache.get(customer_id)
    
def send_pdf(filename, link, phone_number):
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
            "filename": filename,
            "link": link
        }
    }
    
    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Document sent successfully. filename: {filename}, phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def send_image_by_id(id, phone_number):
    headers = {
        "Content-Type": APPLICATION_JSON,
        "Authorization": AUTHORIZATION
    }
    
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
            logger.info(f"Image sent successfully. id: {id}, phone: {phone_number}")

            response_data = response.json()

            logger.debug(f"Response JSON: {response_data}")

            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send image. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending Image: {e}", exc_info=True)
        return None

def send_pdf_by_id(filename, id, phone_number):
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
            "filename": filename,
            "id": id
        }
    }
    
    try:
        response = requests.post(MESSAGES_ENDPOINT, json=json_data, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Document sent successfully. filename: {filename}, phone_number: {phone_number}")
            response_data = response.json()
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

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

def send_template_by_image_id(phone_number, template_name, image_id):
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
                    "type": "header",
                    "parameters": [
                        {
                            "type": "image",
                            "image": {
                                "id": image_id
                            }
                        }
                    ]
                },
                {
                    "type": "body"
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
            logger.info(f"Template send successfully: template_name: {template_name}, phone_number: {phone_number}, image_id: {image_id}")
            
            response_data = response.json()
            
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}", exc_info=True)
        return None

def send_document_template_by_id_with_parameter(phone_number, template_name, document_id, date_parameter, filename):
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
                    "type": "header",
                    "parameters": [
                        {
                            "type": "document",
                            "document": {
                                "id": document_id,
                                "filename": filename
                            }
                        }
                    ]
                },
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": date_parameter
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
            logger.info(f"Document template sent successfully: template_name: {template_name}, phone_number: {phone_number}, filename: {filename}")
            
            response_data = response.json()
            
            logger.debug(f"Response JSON: {response_data}")
            return response_data.get("messages", [{}])[0].get("id")
        else:
            logger.error(f"Failed to send document template message. Status Code: {response.status_code}. Response Content: {response.content}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending document template message: {e}", exc_info=True)
        return None

