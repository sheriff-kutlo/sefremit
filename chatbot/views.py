from django.shortcuts import render
from django.db import connection
from django.http import HttpResponse, JsonResponse, JsonResponse, Http404
from urllib.parse import urlparse, parse_qs
from django.views.decorators.csrf import csrf_exempt
import json
from .constants import *
from .utils import *
import logging

# Get an instance of a logger
logger = logging.getLogger(CHATBOT_CATALOG)

@csrf_exempt
def sefremit_verification(request):
    if request.method == 'GET':
        hub_mode = request.GET.get('hub.mode')
        hub_verify_token = request.GET.get('hub.verify_token')
        hub_challenge = request.GET.get('hub.challenge')
        
        if hub_mode == 'subscribe' and hub_verify_token == HUB_KEY_VERIFICATION:
            return HttpResponse(hub_challenge, status=200)
        else:
            return JsonResponse({}, status=400)
    
    elif request.method == 'POST':
        # Retrieve the value of the "X-Hub-Signature-256" header from the request
        # header_value = request.headers.get("X-Hub-Signature-256")

        # if header_value is None:
        #     return JsonResponse({'error': 'Missing X-Hub-Signature-256 header'}, status=400)
        
        # return JsonResponse({'header_value': header_value})
        
        try:
            json_data = json.loads(request.body.decode('utf-8'))  # Deserialize JSON data from the request body
            logger.info(json_data) # Print JSON data for debugging
            
            try:

                # Check and handle the response only if status is 'delivered'
                if 'statuses' in json_data['entry'][0]['changes'][0]['value']:
                    status = json_data['entry'][0]['changes'][0]['value']['statuses'][0]

                    # Extract display phone number
                    display_phone_number = json_data['entry'][0]['changes'][0]['value']['metadata'].get('display_phone_number', None)
                    
                    if status['status'] == 'delivered' or status['status'] == 'read':
                        message_id = status['id']
                        message_status = status['status']
                        recipient_id = status['recipient_id']
                        timestamp = status['timestamp']
                        conversation_id = status['conversation']['id']

                        logger.info(f"Message ID: {message_id}")
                        logger.info(f"Status: {message_status}")
                        logger.info(f"Recipient ID: {recipient_id}")
                        logger.info(f"Timestamp: {timestamp}")
                        logger.info(f"Conversation ID: {conversation_id}")
                        logger.info(f"Display Phone Number from status: {display_phone_number}")

                        # value = cache.get(message_id)

                        # delete_cache_customer_id(message_id)

                        # Check if the value exists
                        # if value is not None:
                        #     if value == FOLLOW_UP_TO_SEND_PARTICIPATING_STORES_IMAGE:
                        #         send_template_without_header(recipient_id, PROMOTIONAL_PRODUCTS_OPTIONS_TEMP)
                        #     elif value == FOLLOW_UP_TO_SEND_PRIZES_IMAGE:
                        #         handle_prizes(recipient_id)
                        #     elif value == FOLLOW_UP_TO_SEND_EVENTS_IMAGE:
                        #         handle_upcoming_events(recipient_id)

                    else:
                        logger.info(f"Status is not 'delivered' or 'read': {status['status']}")

                if 'request_welcome' in json_data['entry'][0]['changes'][0]['value']['messages'][0].get('type', ''):
                    name = json_data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
                    logger.info(f"Request Type: request_welcome")
                    logger.info(f"Name: {name}")

                    message_id = json_data['entry'][0]['changes'][0]['value']['messages'][0]['id']
                    message_from = json_data['entry'][0]['changes'][0]['value']['messages'][0]['from']
                    logger.info(f"Message ID: {message_id}")
                    logger.info(f"Message From: {message_from}")

                    display_phone_number = json_data['entry'][0]['changes'][0]['value']['metadata'].get('display_phone_number', None)
                    logger.info(f"Display Phone Number: {display_phone_number}")

                    handle_reply('options', message_id, message_from, name, display_phone_number)

                # Check if the JSON data follows structure 1
                if 'text' in json_data['entry'][0]['changes'][0]['value']['messages'][0]:
                    # Extract the name and wa_id
                    name = json_data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']

                    body = json_data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']

                    logger.info(f"Message Body: {body}")
                    
                    message_id = json_data['entry'][0]['changes'][0]['value']['messages'][0]['id']
                    message_from = json_data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    
                    logger.info(f"Message ID: {message_id}")

                    # Extract display phone number
                    display_phone_number = json_data['entry'][0]['changes'][0]['value']['metadata'].get('display_phone_number', None)
                    logger.info(f"Display Phone Number from text: {display_phone_number}")

                    handle_reply(body, message_id, message_from, name, display_phone_number)
                
                # Check if the JSON data follows structure 2
                elif 'button' in json_data['entry'][0]['changes'][0]['value']['messages'][0]:
                    text = json_data['entry'][0]['changes'][0]['value']['messages'][0]['button']['text']
                    logger.info(f"Text: {text}")
                    
                     # Extracting id from context object
                    message_id = json_data['entry'][0]['changes'][0]['value']['messages'][0]['context']['id']
                    message_from = json_data['entry'][0]['changes'][0]['value']['messages'][0]['from']

                    name = json_data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
    
                    logger.info(f"Context ID: {message_id}")

                    display_phone_number = json_data['entry'][0]['changes'][0]['value']['metadata'].get('display_phone_number', None)
                    logger.info(f"Display Phone Number from button: {display_phone_number}")
                    
                    handle_reply(text, message_id, message_from, name, display_phone_number)

                elif 'description' in json_data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['list_reply']:
                    description = json_data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['list_reply']['description']
                    
                    name = json_data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']

                    logger.info(f"Description: {description}")
                    
                    message_id = json_data['entry'][0]['changes'][0]['value']['messages'][0]['id']
                    message_from = json_data['entry'][0]['changes'][0]['value']['messages'][0]['from']
                    
                    logger.info(f"Message ID: {message_id}")

                    display_phone_number = json_data['entry'][0]['changes'][0]['value']['metadata'].get('display_phone_number', None)
                    logger.info(f"Display Phone Number from description: {display_phone_number}")

                    handle_reply(description, message_id, message_from, name, display_phone_number)

                elif 'interactive' in json_data['entry'][0]['changes'][0]['value']['messages'][0]:
                    interactive_data = json_data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']
                    if interactive_data['type'] == 'list_reply':
                        title = interactive_data['list_reply']['title']

                        logger.info(f"Title: {title}")

                        message_id = json_data['entry'][0]['changes'][0]['value']['messages'][0]['id']
                        message_from = json_data['entry'][0]['changes'][0]['value']['messages'][0]['from']

                        name = json_data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']

                        logger.info(f"Message ID: {message_id}")

                        display_phone_number = json_data['entry'][0]['changes'][0]['value']['metadata'].get('display_phone_number', None)
                        logger.info(f"Display Phone Number from interactive: {display_phone_number}")

                        handle_reply(title, message_id, message_from, name, display_phone_number)

                else:
                    logger.info("Invalid JSON structure")

            except KeyError as e:
                logger.info(f"Error: Key not found -: {e}")
            except IndexError as e:
                logger.info(f"Error: Index out of range -: {e}", exc_info=True)
            except Exception as e:
                logger.info(f"An unexpected error occurred: {e}", exc_info=True)

            return JsonResponse({'message': 'Received JSON data'}, status=200)
        
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

def hello(request):

    send_message("some message", KUTLO_PHONE_NUMBER)

    return HttpResponse(f"Server working as expected!")

