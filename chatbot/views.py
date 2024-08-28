from django.shortcuts import render
from django.db import connection
from django.http import HttpResponse, JsonResponse, JsonResponse, Http404
from urllib.parse import urlparse, parse_qs
from django.views.decorators.csrf import csrf_exempt
import json
from .constants import *
from .sefremit_constants import *
from .utils import *
import logging
from django.conf import settings
import os
from django.http import FileResponse, Http404
import pandas as pd
import re
from datetime import datetime

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

                        value = cache.get(message_id)

                        delete_cache_customer_id(message_id)

                        # Check if the value exists
                        if value is not None:
                            if value == FOLLOW_UP_TO_SEND_PARTICIPATING_STORES_IMAGE:
                                send_template_without_header(recipient_id, PROMOTIONAL_PRODUCTS_OPTIONS_TEMP)
                            elif value == FOLLOW_UP_TO_SEND_PRIZES_IMAGE:
                                handle_prizes(recipient_id)

                    else:
                        logger.info(f"Status is not 'delivered' or 'read': {status['status']}")

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

                elif 'request_welcome' in json_data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['list_reply']:                    
                    name = json_data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
                    
                    message_id = json_data['entry'][0]['changes'][0]['value']['messages'][0]['id']
                    message_from = json_data['entry'][0]['changes'][0]['value']['messages'][0]['from']
                    
                    logger.info(f"Message ID: {message_id}")

                    display_phone_number = json_data['entry'][0]['changes'][0]['value']['metadata'].get('display_phone_number', None)
                    logger.info(f"Display Phone Number from description: {display_phone_number}")

                    handle_reply("options", message_id, message_from, name, display_phone_number)

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

    # handle_reply("sefremit", "wamid: 842892", KUTLO_PHONE_NUMBER, "Joe", SEFREMIT_PHONE_NUMBER)

    # new_broadcast()

    # broadcast()

    # send_template(KUTLO_PHONE_NUMBER, SEF_INTRO_TEMPLATE, )

    # save_valid_customers(sample_phone_numbers)

    # broadcast_to_numbers()

    # send_image_by_id("506570791744802", KUTLO_PHONE_NUMBER)

    # handle_reply(SERVICES, "wamid.7578393", KUTLO_PHONE_NUMBER, "Joe")

    # broadcast_customers = []

    # opted_in_customers_lst = get_customers_opted_in(get_subscription_id(BIRTHDAY_PROMOTION))

    # for customer in opted_in_customers_lst:
    #     broadcast_customers.append(customer)

    # new_customers = get_new_customers()

    # if new_customers:
    #     for customer in new_customers:
    #         broadcast_customers.append(customer)

    # print(len(broadcast_customers))

    # for number in broadcast_customers:
    #     send_document_template_by_id_with_parameter(
    #         number,
    #         SEFALANA_WEEKEND_HYPER_SPECIAL_TEMP,
    #         HYPER_SEFALANA_WEEKEND_SPECIAL_8_11_AUG_2024_ID,
    #         WEEKEND_SPECIAL_DATE,
    #         SEFALANA_HYPER
    #     )

    #     send_document_template_by_id_with_parameter(
    #         number,
    #         SEFALANA_WEEKEND_WHOLESALE_SPECIAL_TEMP,
    #         SEFALANA_WEEKEND_WHOLESALE_SPECIAL_8_11_AUG_2024_ID,
    #         WEEKEND_SPECIAL_DATE,
    #         SEFALANA_WHOLESALE
    #     )

    #     logger.info(f"Sent Weekend Promotion PDFs to {number}")

    # handle_reply(PROMOTIONAL_PRODUCTS, "WAN", KUTLO_PHONE_NUMBER, "JOEs")

    # keys = cache.keys('*')

    # # Initialize an empty list to store key-value pairs containing '_midnight'
    # cached_items = []

    # # Iterate over keys and fetch their corresponding values
    # for key in keys:
    #     value = cache.get(key)
    #     cached_items.append((key, value))

    # # Print or process the list of cached items containing '_midnight'
    # for key, value in cached_items:
    #     # delete_cache_customer_id(key)
    #     print(f"Key: {key}, Value: {value}")
    #     print("------------------------------------------------")

    # print()

    # for img_path in SAMPLE_CATALOGS_PATH:
    #     send_image(f"{DOMAIN_ENDPOINT}{img_path}", KUTLO_PHONE_NUMBER)

    # handle_reply(TRANSACTION_LIMITS, "wamid.75938", KUTLO_PHONE_NUMBER, "Kutlo")

    # for number in board_directors_lst:
    #     send_template_by_image_id(number, SEF_INTRO_TEMPLATE, BIRTHDAY_PROMOTION_IMG_ID)
    #     logger.info(f"Sent Intro template to: {number}")

    return HttpResponse(f"Server working as expected!")

def create_event(request):
    if request.method == 'GET':
        event_name = request.GET.get('event_name')
        subscription_name = request.GET.get('subscription_name')

        if event_name is None or subscription_name is None:
            return JsonResponse({"error": "Missing parameters"}, status=400)

        # You can now use param1 and param2 for your logic  
        add_event(event_name, get_subscription_id(subscription_name))

        return JsonResponse({"event_name": event_name, "subscription_name": subscription_name})

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def add_event_images(request):
    if request.method == 'POST':
        try:
            urls = json.loads(request.body)
            
            add_event_images_to_db(get_event_id("june_2024_birthday_promotion_retail"), urls)
            
            # Optionally, you can respond with a success message
            return JsonResponse({"message": "Data received successfully"})
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)

sample_phone_numbers = [
    "74342078",
    "76478882"
]

def save_valid_customers(sample_phone_numbers):
    
    invalid_phone_numbers = []

    for number in sample_phone_numbers:
        formatted, carrier_name = format_and_get_carrier(number)
        if formatted:
            if not carrier_name:
                logger.error(f"Invalid phone number: {number}")
                invalid_phone_numbers.append(number)
            else:
                send_template_by_image_id(formatted, SEF_INTRO_TEMPLATE, BIRTHDAY_PROMOTION_IMG_ID)
                # send_template_by_image_id(formatted, SEF_INTRO_TEMPLATE, BIRTHDAY_PROMOTION_IMG_ID)
                
                # send_document_template_by_id_with_parameter(
                #     formatted,
                #     SEFALANA_WEEKEND_HYPER_SPECIAL_TEMP,
                #     HYPER_SEFALANA_WEEKEND_SPECIAL_8_11_AUG_2024_ID,
                #     WEEKEND_SPECIAL_DATE,
                #     SEFALANA_HYPER
                # )

                # send_document_template_by_id_with_parameter(
                #     formatted,
                #     SEFALANA_WEEKEND_WHOLESALE_SPECIAL_TEMP,
                #     SEFALANA_WEEKEND_WHOLESALE_SPECIAL_8_11_AUG_2024_ID,
                #     WEEKEND_SPECIAL_DATE,
                #     SEFALANA_WHOLESALE
                # )

                logger.info(f"Sent Welcome message to: {formatted}")

    logger.error(f"invalid phone numbers: {invalid_phone_numbers}")

def other_images(request, category, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, category, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    else:
        raise Http404("Image not found")

def catalog_images(request, category, promotion, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, category, promotion, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    else:
        raise Http404("Image not found")

def serve_pdf(request, filename):
    # Construct the file path
    pdf_path = os.path.join('static', filename)

    # Check if the file exists
    if os.path.exists(pdf_path):
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    else:
        raise Http404("File does not exist")

def add_cache_test(request):
    cache_customer_id(f"{APPEND_TRAFFIC}10", "2024-07-25 21:35:00", use_limit=True)
    cache_customer_id(f"{APPEND_TRAFFIC}11", "2024-07-25 21:37:00", use_limit=True)
    cache_customer_id(f"{APPEND_TRAFFIC}12", "2024-07-22 11:25:00", use_limit=True)
    cache_customer_id(f"{APPEND_TRAFFIC}22", "2024-07-24 12:25:00", use_limit=True)
    cache_customer_id(f"{APPEND_TRAFFIC}25", use_limit=True)
    cache_customer_id(f"{APPEND_TRAFFIC}30", use_limit=True)

    return HttpResponse(f"added cache data")

def get_cache_test(request):
    keys = cache.keys('*')

    # Initialize an empty list to store key-value pairs containing '_midnight'
    cached_items = []

    # Iterate over keys and fetch their corresponding values
    for key in keys:
        value = cache.get(key)
        cached_items.append((key, value))

    # Print or process the list of cached items containing '_midnight'
    for key, value in cached_items:
        # delete_cache_customer_id(key)
        print(f"Key: {key}, Value: {value}")
        print("------------------------------------------------")

    print()

    return HttpResponse(f"get cache data")

def test_update_conversations_limits(request):

    # Get all keys from the cache (this may vary depending on your cache backend)
    keys = cache.keys('*')

    # Initialize an empty list to store key-value pairs containing '_midnight'
    cached_items = []

    # Iterate over keys and fetch their corresponding values
    for key in keys:
        if APPEND_MIDIGHT not in key and f'_{OVER_LIMIT}' not in key:
            value = cache.get(key)
            cached_items.append((key, value))
            print(f"cached: {key} : {value}")

    # Print or process the list of cached items containing '_midnight'
    for key, value in cached_items:
        is_expired = is_difference_more_than_24_hours(value)

        if is_expired:
            is_delete_cache_phone_number = delete_cache_customer_id(key)
            if is_delete_cache_phone_number:
                schedule_for_midnight = f"{key}{APPEND_MIDIGHT}"
                cache_customer_id(schedule_for_midnight, value)

    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    logger.info(f"Ran update_conversations_limits function at: {current_timestamp}")
    print(f"Ran update_conversations_limits function at: {current_timestamp}")

    return HttpResponse(f"test_update_conversations_limits")

def test_save_conversation_limit_data(request):
     # Get all keys from the cache (this may vary depending on your cache backend)
    # Get all keys from the cache (this may vary depending on your cache backend)
    keys = cache.keys('*')

    # Initialize an empty list to store key-value pairs containing '_midnight'
    cached_items = []
    over_limit_items = []

    # Iterate over keys and fetch their corresponding values
    for key in keys:
        if f'{APPEND_MIDIGHT}' in key:
            value = cache.get(key)
            cached_items.append((key, value))

    save_conversation_limit_to_db(cached_items, get_conversation_status_id(IN_LIMIT))

    for key in keys:
        if f'{APPEND_MIDIGHT}' in key:
            delete_cache_customer_id(key)

    for key in keys:
        if f'_{OVER_LIMIT}' in key:
            value = cache.get(key)
            over_limit_items.append((key, value))

    save_conversation_limit_to_db(over_limit_items, get_conversation_status_id(OVER_LIMIT))

    for key in keys:
        if f'_{OVER_LIMIT}' in key:
            delete_cache_customer_id(key)

    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    logger.info(f"Ran save_conversation_limit_data function at: {current_timestamp}")
    print(f"Ran save_conversation_limit_data function at: {current_timestamp}")

def delete_all_cache_test(request):

    keys = cache.keys('*')

    # Initialize an empty list to store key-value pairs containing '_midnight'
    cached_items = []

    # Iterate over keys and fetch their corresponding values
    for key in keys:
        value = cache.get(key)
        cached_items.append((key, value))

    # Print or process the list of cached items containing '_midnight'
    for key, value in cached_items:
        delete_cache_customer_id(key)
        print("------------------------------------------------")

    print()

    return HttpResponse(f"delete cache data")

def broadcast_to_numbers():
    df = pd.read_excel("chatbot_catalog/first_1000_numbers.xlsx")
    phone_numbers_lst = df["Contact No"].astype(str).unique().tolist()

    save_valid_customers(phone_numbers_lst)

    # print(f"Phone numbers: {phone_numbers_lst}")

def broadcast():
    # list of all customers
    broadcast_customers = []

    # opted in customers
    opted_in_customers_lst = get_customers_opted_in(get_subscription_id(BIRTHDAY_PROMOTION))
    for customer in opted_in_customers_lst:
        broadcast_customers.append(customer)

    # new customers
    new_customers = get_new_customers()
    if new_customers:
        for customer in new_customers:
            broadcast_customers.append(customer)

    # append B's to broadcast customers
    broadcast_customers.extend(board_directors_lst)

    # before sending findout which B's already exist to avoid duplicates
    unique_list = list(set(broadcast_customers))
    print(len(unique_list), unique_list)


    # for number in unique_list:
    #     send_document_template_by_id_with_parameter(
    #         number, 
    #         SEFALANA_WEEKEND_HYPER_SPECIAL_TEMP,
    #         HYPER_SEFALANA_WEEKEND_SPECIAL_22_25_AUG_2024_ID,
    #         WEEKEND_SPECIAL_DATE,
    #         SEFALANA_HYPER
    #     )
    
    #     send_document_template_by_id_with_parameter(
    #         number, 
    #         SEFALANA_WEEKEND_WHOLESALE_SPECIAL_TEMP,
    #         SEFALANA_WEEKEND_WHOLESALE_SPECIAL_22_25_AUG_2024_ID,
    #         WEEKEND_SPECIAL_DATE,
    #         SEFALANA_WHOLESALE
    #     )

    #     logger.info(f"Sent Weekend Promotion 22 - 25 August 2024 to: {number}")
    
    #     send_document_template_by_id_with_parameter(
    #         number, 
    #         LIQUOR_WEEKEND_SPECIAL_TEMP,
    #         LIQUOR_WEEKEND_21_27_AUG_SPECIAL_PDF_ID,
    #         LIQUOR_WEEKEND_SPECIAL_DATE,
    #         LIQUOR_WEEKEND_SPECIAL
    #     )

    #     logger.info(f"Sent Weekend Liquor Promotion 21 - 27 August 2024 to: {number}")

def new_broadcast():
    # list of all customers
    broadcast_customers = []

    # opted in customers
    opted_in_customers_lst = get_customers_opted_in(get_subscription_id(BIRTHDAY_PROMOTION))
    for customer in opted_in_customers_lst:
        broadcast_customers.append(customer)

    # new customers
    new_customers = get_new_customers()
    if new_customers:
        for customer in new_customers:
            broadcast_customers.append(customer)

    # append B's to broadcast customers
    broadcast_customers.extend(board_directors_lst)

    # before sending findout which B's already exist to avoid duplicates
    unique_list = list(set(broadcast_customers))

    df = pd.read_excel("chatbot_catalog/first_1000_numbers.xlsx")
    phone_numbers_lst = df["Contact No"].astype(str).unique().tolist()

    phone_number_set = set(phone_numbers_lst)

    # Filter phone_number_lst to remove any number present in unique_list
    filtered_phone_numbers = [number for number in phone_number_set if number not in unique_list]

    first_10_K_df = pd.read_excel("chatbot_catalog/first_10000_numbers.xlsx")
    phone_numbers_lst_10K = first_10_K_df["NUMBER"].astype(str).unique().tolist()

    phone_numbers_lst_10K = set(phone_numbers_lst_10K)

    send_10K_filtered_numbers = [number for number in phone_numbers_lst_10K if number not in filtered_phone_numbers]

    second_10_K_df = pd.read_excel("chatbot_catalog/second_10000_numbers.xlsx")
    second_phone_numbers_lst_10K = second_10_K_df["NUMBER"].astype(str).unique().tolist()

    send_second_10K_numbers = [number for number in second_phone_numbers_lst_10K if number not in send_10K_filtered_numbers]

    print(len(send_second_10K_numbers), send_second_10K_numbers)

    save_valid_customers(send_second_10K_numbers)

    # for number in filtered_phone_numbers:
    #     # send_template_by_image_id(number, SEF_INTRO_TEMPLATE, BIRTHDAY_PROMOTION_IMG_ID)

    #     logger.info(f"Sent Welcome Message to: {number}")

    # invalid_phone_numbers = []

    # for number in sample_phone_numbers:
    #     formatted, carrier_name = format_and_get_carrier(number)
    #     if formatted:
    #         if not carrier_name:
    #             logger.error(f"Invalid phone number: {number}")
    #             invalid_phone_numbers.append(number)
    #         else:
    #             logger.info(f"Sent Welcome message to: {formatted}")

def extract_phone_numbers(target_date):
    # Path to your log file
    log_file_path = '/Users/kutlomangwa/Documents/sefalana/logs/broadcast.log'

    # List to store phone numbers
    phone_numbers = []

    # Regex pattern to match the specific log entry and extract the phone number
    log_pattern = re.compile(r'(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2} INFO Sent Weekend Promotion 22 - 25 August 2024 to: (\d+)')

    # Read and process the log file
    with open(log_file_path, 'r') as file:
        for line in file:
            match = log_pattern.match(line)
            if match:
                log_date = match.group(1)
                if log_date == target_date:
                    phone_number = match.group(2)
                    phone_numbers.append(phone_number)

    return phone_numbers

