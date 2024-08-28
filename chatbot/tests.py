from django.test import TestCase

# Create your tests here.



import logging

# Sample JSON data
json_data = {
    'object': 'whatsapp_business_account',
    'entry': [
        {
            'id': '428197457039459',
            'changes': [
                {
                    'value': {
                        'messaging_product': 'whatsapp',
                        'metadata': {
                            'display_phone_number': '26772157053',
                            'phone_number_id': '422196440971638'
                        },
                        'contacts': [
                            {
                                'profile': {
                                    'name': 'B. Mangwa'
                                },
                                'wa_id': '26776478882'
                            }
                        ],
                        'messages': [
                            {
                                'from': '26776478882',
                                'id': 'wamid.HBgLMjY3NzY0Nzg4ODIVAgASGCBEMzg5QzMwNkE1OUQ1NjQ4MzA4NURBRkY4Q0MwQTlFQgA=',
                                'timestamp': '1724835215',
                                'type': 'request_welcome'
                            }
                        ]
                    },
                    'field': 'messages'
                }
            ]
        }
    ]
}

# # Setting up logger
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# def handle_reply(request_type, message_id, message_from, name, display_phone_number):
#     logger.info(f"Handling reply for type: {request_type}")
#     logger.info(f"Message ID: {message_id}, From: {message_from}, Name: {name}, Display Phone Number: {display_phone_number}")

# Testing the code
if 'request_welcome' in json_data['entry'][0]['changes'][0]['value']['messages'][0].get('type', ''):
    name = json_data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
    print(f"Request Type: request_welcome")
    print(f"Name: {name}")

    message_id = json_data['entry'][0]['changes'][0]['value']['messages'][0]['id']
    message_from = json_data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    print(f"Message ID: {message_id}")
    print(f"Message From: {message_from}")

    display_phone_number = json_data['entry'][0]['changes'][0]['value']['metadata'].get('display_phone_number', None)
    print(f"Display Phone Number: {display_phone_number}")

    # handle_reply('request_welcome', message_id, message_from, name, display_phone_number)