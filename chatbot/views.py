from django.shortcuts import render
from django.db import connection
from django.http import HttpResponse, JsonResponse, JsonResponse, Http404
from urllib.parse import urlparse, parse_qs
from django.views.decorators.csrf import csrf_exempt
import json
from .constants import *
from .utils import *
import logging
import bcrypt


# Get an instance of a logger
logger = logging.getLogger(CHATBOT_CATALOG)

@csrf_exempt
def verification(request):
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


                    else:
                        logger.info(f"Status is not 'delivered' or 'read': {status['status']}")

                if 'interactive' in json_data['entry'][0]['changes'][0]['value']['messages'][0]:
                    interactive_data = json_data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']

                    if interactive_data['type'] == 'list_reply':

                        if 'description' in json_data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['list_reply']:
                            description = json_data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['list_reply']['description']
                            
                            name = json_data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']

                            logger.info(f"Description: {description}")
                            
                            message_id = json_data['entry'][0]['changes'][0]['value']['messages'][0]['id']
                            message_from = json_data['entry'][0]['changes'][0]['value']['messages'][0]['from']
                            
                            logger.info(f"Message ID: {message_id}")

                            display_phone_number = json_data['entry'][0]['changes'][0]['value']['metadata'].get('display_phone_number', None)
                            logger.info(f"Display Phone Number from description: {display_phone_number}")

                            handle_reply(description, message_id, message_from, name, display_phone_number)
                    
                        else:

                            title = interactive_data['list_reply']['title']

                            logger.info(f"Title: {title}")

                            message_id = json_data['entry'][0]['changes'][0]['value']['messages'][0]['id']
                            message_from = json_data['entry'][0]['changes'][0]['value']['messages'][0]['from']

                            name = json_data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']

                            logger.info(f"Message ID: {message_id}")

                            display_phone_number = json_data['entry'][0]['changes'][0]['value']['metadata'].get('display_phone_number', None)
                            logger.info(f"Display Phone Number from interactive: {display_phone_number}")

                            handle_reply(title, message_id, message_from, name, display_phone_number)

                    elif interactive_data['type'] == 'nfm_reply':

                        name = json_data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']

                        message = json_data['entry'][0]['changes'][0]['value']['messages'][0]

                        response_str = message['interactive']['nfm_reply']['response_json']
                        message_from = json_data['entry'][0]['changes'][0]['value']['messages'][0]['from']
                        
                        # Convert to dictionary
                        response_data = json.loads(response_str)

                        flow_token = response_data.get('flow_token', '')

                        if flow_token == REGISTER_FLOW_TOKEN:                        
                            # Extract values
                            firstname = response_data.get('screen_0_First_Name_0', '')
                            lastname = response_data.get('screen_0_Last_Name_1', '')
                            email = response_data.get('screen_0_Email_2', '')
                            date_of_birth = response_data.get('screen_0_Date_of_Birth_3', '')
                            pin = response_data.get('screen_0_PIN_code_4', '')
                            confirm_pin = response_data.get('screen_0_Confrim_PIN_code_5', '')

                            # Hash the PIN
                            pin_bytes = pin.encode('utf-8')
                            hashed_pin = bcrypt.hashpw(pin_bytes, bcrypt.gensalt())
                            

                            # Check if PINs are at least 4 digits
                            if len(pin) < 4 or len(confirm_pin) < 4:
                                send_flow_message(message_from, REGISTER_TITLE_ERROR, PIN_TOO_SHORT, REGISTER_FLOW_ID, REGISTER_FLOW_TOKEN, TRY_AGAIN_CTA)
                            # Check if PINs match
                            elif pin != confirm_pin:
                                send_flow_message(message_from, REGISTER_TITLE_ERROR, REGISTER_BODY_ERROR_PIN_NOT_MATCH, REGISTER_FLOW_ID, REGISTER_FLOW_TOKEN, TRY_AGAIN_CTA)
                            else:
                                save_wallet_user({USERNAME: remove_emojis(name), FIRSTNAME: firstname, LASTNAME: lastname, PHONE_NUMBER: message_from, EMAIL: email, DATE_OF_BIRTH: date_of_birth, PIN: hashed_pin})
  
                        elif flow_token == CARD_DETAILS_FLOW_TOKEN:                        
                            # Extract values
                            cardholder_name = response_data.get('screen_0_Cardholder_Name_0', '')
                            card_number = response_data.get('screen_0_Card_Number_1', '')
                            expiry_date = response_data.get('screen_0_Expiry_Date_2', '')
                            cvv = response_data.get('screen_0_CVV_3', '')
                            amount = response_data.get('screen_0_Amount_4', '')

                            save_transaction({USER_ID: get_user_id(message_from), AMOUNT: amount, TRANSACTION_TYPE: ADD_FUNDS, TRANSACTION: ADD_FUNDS, PHONE_NUMBER: message_from})

                        elif flow_token == PAY_MERCHANT_FLOW_TOKEN:
                            # Extract values
                            merchant_id = response_data.get('screen_0_Merchant_ID_0', '')
                            amount = response_data.get('screen_0_Amount_1', '')
                            pin_code = response_data.get('screen_0_PIN_code_2', '')

                            user_pin = get_user_pin(message_from)

                            # Convert both to bytes
                            pin_bytes = pin_code.encode('utf-8')

                            # user_pin might already be bytes (from MySQL varbinary)
                            # If it's a string, decode it first
                            if isinstance(user_pin, str):
                                user_pin = user_pin.encode('utf-8')

                            if bcrypt.checkpw(pin_bytes, user_pin):
                                save_transaction({USER_ID: get_user_id(message_from), AMOUNT: amount, TRANSACTION_TYPE: PAY_MERCHANT, TRANSACTION: merchant_id, PHONE_NUMBER: message_from})
                            else:
                                send_flow_message(message_from, "Incorrect PIN", "The PIN you entered is invalid. Please check and try again.", PAY_MERCHANT_FLOW_ID, PAY_MERCHANT_FLOW_TOKEN, "Try Again")

                        elif flow_token == PAY_FRIEND_FLOW_TOKEN:
                            # Extract values
                            friend_id = response_data.get('screen_0_Phone_Number_0', '')
                            amount = response_data.get('screen_0_Amount_1', '')
                            pin_code = response_data.get('screen_0_PIN_code_2', '')

                            user_pin = get_user_pin(message_from)

                            # Convert both to bytes
                            pin_bytes = pin_code.encode('utf-8')

                            # user_pin might already be bytes (from MySQL varbinary)
                            # If it's a string, decode it first
                            if isinstance(user_pin, str):
                                user_pin = user_pin.encode('utf-8')

                            if bcrypt.checkpw(pin_bytes, user_pin):
                                save_transaction({
                                    USER_ID: get_user_id(message_from),
                                    AMOUNT: amount,
                                    TRANSACTION_TYPE: PAY_FRIEND,
                                    TRANSACTION: friend_id,
                                    PHONE_NUMBER: message_from
                                })

                            else:
                                send_flow_message(message_from, "Incorrect PIN", "The PIN you entered is invalid. Please check and try again.", PAY_FRIEND_FLOW_ID, PAY_FRIEND_FLOW_TOKEN, "Try Again")


            
                if 'location' in json_data['entry'][0]['changes'][0]['value']['messages'][0]:
                    message = json_data['entry'][0]['changes'][0]['value']['messages'][0]
                    latitude = message['location']['latitude']
                    longitude = message['location']['longitude']
                    message_from = message['from']

                    # data = get_customer_order_cache_data(message_from)

                    # save_order_data(data, message_from, latitude, longitude)

                    # order_data = data["order_data"]
                    # order_number = order_data["order_number"]
                    # store_name = data["store_name"]

                    # store_contact = get_store_contact(store_name)

                    # send_message(f"✅ *Order Placed*\n\nYour order has been successfully placed and will be delivered to the address you provided.\n\nIf you have any questions or need assistance, you can contact the store at: *{store_contact}*.\n\nThank you for shopping with us! 🛍️", message_from)

                    # send_message(f"📢 *Order Alert*\n\nOrder *{order_number}* has been sent to the Order Management System.\n\nPlease prepare the order", message_from)

                    # cache.delete_pattern(f"{message_from}_*")

                if 'audio' in json_data['entry'][0]['changes'][0]['value']['messages'][0]:
                    audio_id = json_data['entry'][0]['changes'][0]['value']['messages'][0]['audio']['id']

                    logger.info(f"audio id: {audio_id}")

                    # audio_url = get_audio_url(audio_id)

                    # logger.info(f"logger url: {audio_url}")

                    # name = json_data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
                                        
                    # message_id = json_data['entry'][0]['changes'][0]['value']['messages'][0]['id']
                    # message_from = json_data['entry'][0]['changes'][0]['value']['messages'][0]['from']

                    # display_phone_number = json_data['entry'][0]['changes'][0]['value']['metadata'].get('display_phone_number', None)

                    # logger.info(f"audio_url: {audio_url}")
                    # logger.info(f"message_id: {message_id}")
                    # logger.info(f"message_from: {message_from}")
                    # logger.info(f"name: {name}")
                    # logger.info(f"display_phone_number: {display_phone_number}")

                    # rank_activity = get_rank_activity(message_from)

                    # if rank_activity == CHECK_IN:
                    #     if audio_url:                        
                    #         file_path = download_audio(audio_url)
                    #         if file_path:
                    #             transcription_text = transcribe_audio(file_path)
                    #             logger.info(f"Transcribed Text: {transcription_text}")
                    #             send_sefremit_message(send_chat_msg(message_from, transcription_text)["content"], message_from)
                    
                    # else:
                    #     send_sefremit_message("Head over to *Check In* to use voice")
                                     
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
                
                elif 'order' in json_data['entry'][0]['changes'][0]['value']['messages'][0]:
                    # Extract the name and wa_id
                    name = json_data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']

                    message_id = json_data['entry'][0]['changes'][0]['value']['messages'][0]['id']
                    wa_id = json_data['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
                    logger.info(f"Name: {name}, WhatsApp ID: {wa_id}")
    
                    logger.info(f"Message ID: {message_id}")

                    # Extract display phone number
                    display_phone_number = json_data['entry'][0]['changes'][0]['value']['metadata'].get('display_phone_number', None)
                    logger.info(f"Display Phone Number from text: {display_phone_number}")

                    # Extract product items
                    product_items = json_data['entry'][0]['changes'][0]['value']['messages'][0]['order']['product_items']


                    # # Product ID to Name Mapping
                    # display_products = get_product_title_and_content_id()

                    # order_number = generate_unique_order_number()

                    # # Prepare output
                    # output_lines = []
                    # output_lines.append(f"*Order ID: {order_number}*\n")  # Add Order ID at the top
                    # output_lines.append("\n*Ordered Products:*\n" + "-" * 50)

                    # total_price = 0  # Initialize total price

                    # order_data = []

                    # for item in product_items:
                    #     product_id = item['product_retailer_id']
                    #     quantity = item['quantity']
                    #     item_price = item['item_price']
                    #     currency = "P"  # Botswana Pula (BWP)
                        
                    #     # Get product name from dictionary
                    #     product_name = display_products.get(product_id, "Unknown Product")
                        
                    #     # Calculate total price
                    #     total_price += item_price * quantity
                        
                    #     # Format output
                    #     output_lines.append(f"{product_name}\nQuantity: {quantity}\nPrice: {currency}{item_price}\n")

                    #     # Append total price to output
                    #     output_lines.append("-" * 50)
                    #     # output_lines.append(f"Total Price: {currency}{total_price}")

                    #     formatted_output = "\n".join(output_lines)

                    #     store_name = cache.get(f"{wa_id}_store_name")

                    #     if store_name is None:
                    #         send_stores(wa_id)
                    #     else:
                    #         # Append item to order_data
                    #         order_data.append({
                    #             "content_id": product_id,
                    #             "quantity": quantity,
                    #             "item_price": item_price
                    #         })

                    # # send_message(f"{formatted_output} \n\n*Total: {currency}{round(total_price, 2)}*\n\n", wa_id)
                    # # After calculating total_price and before send_message

                    # if total_price >= 200:
                    #     cache.set(f"{wa_id}_delivery_status", "deliver", timeout=24 * 3600)
                    # else:
                    #     cache.set(f"{wa_id}_delivery_status", "non_deliver", timeout=24 * 3600)

                    # wamid = send_message(f"{formatted_output} \n\n*Total: {currency}{round(total_price, 2)}*\n\n", wa_id)
                    # cache.set(f"{wa_id}_order_data", {
                    #     "products": order_data,
                    #     "order_wamid": wamid,
                    #     "order_number": order_number
                    # }, timeout=24 * 3600)

                    # cache.set(wamid, "follow_up_invoice_btns", timeout=24 * 3600)
                        
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

                # elif 'description' in json_data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['list_reply']:
                #     description = json_data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['list_reply']['description']
                    
                #     name = json_data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']

                #     logger.info(f"Description: {description}")
                    
                #     message_id = json_data['entry'][0]['changes'][0]['value']['messages'][0]['id']
                #     message_from = json_data['entry'][0]['changes'][0]['value']['messages'][0]['from']
                    
                #     logger.info(f"Message ID: {message_id}")

                #     display_phone_number = json_data['entry'][0]['changes'][0]['value']['metadata'].get('display_phone_number', None)
                #     logger.info(f"Display Phone Number from description: {display_phone_number}")

                #     handle_reply(description, message_id, message_from, name, display_phone_number)
              
                # else:
                #     logger.info("Invalid JSON structure")

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

    return HttpResponse(f"Server working as expected!")

