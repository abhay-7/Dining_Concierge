import json
import time
import os
import dateutil.parser
import logging
import boto3
import datetime

from urllib.request import Request, urlopen

#//------Helper Functions--------//
def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message ,
        }
    }
    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }
    
#//--------My Functions--------//

def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False
        
def isvalid_city(city):
    valid_cities = ['new york','new york city', 'uptown manhattan', 'midtown manhattan', 'downtown manhattan', 'manhattan']
    return city.lower() in valid_cities
    
def isvalid_cuisine(cuisine):
    valid_cuisine = ['indian','chinese','thai','mexican','french','japanese','american','greek','lebanese','afghan','irish']
    return cuisine.lower() in valid_cuisine
        
def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None


def validate(slots):
    location = try_ex(lambda: slots['Location'])
    cuisine = try_ex(lambda: slots['Cuisine'])
    people = try_ex(lambda: slots['No_of_people'])
    date = try_ex(lambda: slots['Date'])
    time = try_ex(lambda: slots['Time'])
    phone = try_ex(lambda: slots['Phone'])
    
    if location and not isvalid_city(location):
        return build_validation_result(
            False,
            'Location',
            'We currently do not support {} as a valid destination. We support Manhattan Areas. Can you try a different city?'.format(location)
        )
        
    if cuisine and not isvalid_cuisine(cuisine):
        return build_validation_result(
            False,
            'Cuisine',
            'We currently do not support {} as a valid cuisine. Can you try a different cuisine?'.format(cuisine)
        )
    
    if date:
        if not isvalid_date(date):
            return build_validation_result(False, 'Date', 'I did not understand your reservation date.  What date would you like to make your reservation for?')
        if datetime.datetime.strptime(date, '%Y-%m-%d').date() < datetime.date.today():
            return build_validation_result(False, 'Date', 'Reservations can only be made for future dates.  Can you try a different date?')
            
    return {'isValid': True}
    

def dining_suggest(intent_request):
    """
    Performs dialog management and fulfillment for gathering user needs for retaurant.

    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of sessionAttributes to pass information that can be used to guide conversation
    """
    
    location = try_ex(lambda: intent_request['currentIntent']['slots']['Location'])
    cuisine = try_ex(lambda: intent_request['currentIntent']['slots']['Cuisine'])
    people = try_ex(lambda: intent_request['currentIntent']['slots']['No_of_people'])
    date = try_ex(lambda: intent_request['currentIntent']['slots']['Date'])
    time = try_ex(lambda: intent_request['currentIntent']['slots']['Time'])
    phone = try_ex(lambda: intent_request['currentIntent']['slots']['Phone'])
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    print(people)
    reservation = json.dumps({
        'Location':location,
        'Cuisine': cuisine,
        'No_of_people': people,
        'Date': date,
        'Time': time,
        'Phone': phone
    })
    
    session_attributes['currentReservation'] = reservation
    
    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, ask for their value
        validation_result = validate(intent_request['currentIntent']['slots'])
        if not validation_result['isValid']:
            slots = intent_request['currentIntent']['slots']
            slots[validation_result['violatedSlot']] = None
    
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )
        else:
            # Otherwise, let native DM rules determine how to elicit for slots and prompt for confirmation.
            session_attributes['currentReservation'] = reservation
            return delegate(session_attributes, intent_request['currentIntent']['slots'])
    
    #do what SQS pushing here
    sqs = boto3.resource('sqs')
    for queue in sqs.queues.all():
        print(queue.url)
    queue = sqs.get_queue_by_name(QueueName='Q1')
    d=dict()
    d["location"]=location
    d["cuisine"]=cuisine
    d["people"]=people
    d["phone"]=phone
    d["date"]=date
    d["time"]=time
    print (people)
    response = queue.send_message(MessageBody=json.dumps(d))
    
    return close(session_attributes,'Fulfilled',{'contentType': 'PlainText','content': 'Thank you! I will get back to with suggestions on your given phone number {}.'.format(phone)})


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    intent_name = intent_request['currentIntent']['name']
    if intent_name == 'DiningSuggestionsIntent':
        return dining_suggest(intent_request)
    
    raise Exception('Intent with name ' + intent_name + ' not supported')

def lambda_handler(event, context):
    # TODO implement
    return dispatch(event)
