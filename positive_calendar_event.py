#! /Users/az/anaconda3/bin/python

import os
import pickle
import datetime
import openai
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from openai import OpenAI


#print(dir(openai))
current_dir = os.path.dirname(os.path.abspath(__file__))
credentials_path = os.path.join(current_dir, 'credentials.json')
token_path = os.path.join(current_dir, 'token.pickle')
# os.chdir(script_dir)


# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.


if os.path.exists(token_path):
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)

# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(token_path, 'wb') as token:
        pickle.dump(creds, token)
service = build('calendar', 'v3', credentials=creds)

opeanai_client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def get_todays_events(service):
    # Call the Calendar API to fetch events
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(
        calendarId='primary', timeMin=now,
        maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

def generate_prompt_from_events(events):
    prompt = "I have the following schedule today: "
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        prompt += f"\n- {event['summary']} at {start}"
    prompt += "\nCan you give me one personalized positive and encouraging thoughts based on this schedule? You can leverage the content from famous entrepreneurs, authors, psychologists, politicians etc.\
                Be creative and make it short and sweet, and don't repeat everyday."
    return prompt

def generate_suggestions_from_events(events):
    prompt = "I have the following schedule today: "
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        prompt += f"\n- {event['summary']} at {start}"
    # prompt += "\nCan you give me one personalized positive and encouraging thoughts based on this schedule? You can leverage the content from famous entrepreneurs, authors, psychologists, politicians etc.\
    #             Be creative and make it short and sweet, and don't repeat everyday."
    prompt += "My past week has been super intense and stressed out, and I want to improve my happiness and wellness next week. Based on my schedule next week, I want you to suggest and make adjustments to my Calendar schedule. You can directly reschedule and add events like more yoga sessions, break time, reflective activities etc. And add buffer time before client meetings for me to prepare and watch some motivational speech - you can search online and find some sales motivational speech video and get the link. Don’t change schedule for Hack{h}erthon, daily standup meeting and client meetings."
    prompt += "\nGenerate your suggestions in a JSON output. It's a list of JSON object with key `suggestion` and a value of a string of the reschedule plan. Make sure the output is a VALID JSON!!! Only output JSON!"
    return prompt

def generate_event_suggestions(prompt):
    chat_completion = opeanai_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4",
    )
    message = chat_completion.choices[0].message.content
    print(message)
    return message

def suggestion_to_event_function_call(suggestion_json):
    suggestions = json.loads(suggestion_json)
    for suggestion in suggestions:
        event_body = google_calendar_create_event_openai_function_call(suggestion['suggestion'])
        create_calendar_event_with_body(event_body)


def google_calendar_create_event_openai_function_call(suggestion):
    request = dict(
        messages=[
            {
                "role": "user",
                "content": suggestion,
            }
        ],
        function_call={"name": "create_calendar_event"},
        functions=[
            {
                "name": "create_calendar_event",
                "description": "Create a new event to my calendar",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_title": {
                            "type": "string",
                            "description": "a short title of the event",
                        },
                        "start_time": {
                            "type": "string",
                            "description": "event start time in the format of YYYY-MM-DDTHH:MM:SS (e.g., 2023-12-03T07:00:00)",
                        },
                        "end_time": {
                            "type": "string",
                            "description": "event end time in the format of YYYY-MM-DDTHH:MM:SS (e.g., 2023-12-03T07:30:00)",
                        },
                    },
                    "required": ["event_title", "start_time", "end_time"],
                },
            }
        ],
        model="gpt-4",
    )   
    chat_completion = opeanai_client.chat.completions.create(**request)
    arguments = json.loads(chat_completion.choices[0].message.function_call.arguments)

    event_body = {
        'summary': arguments['event_title'],
        #'summary': 'Your Positive Message for the Day',
       # 'description': message,
        'start': {
            'dateTime': arguments['start_time'],
            'timeZone': 'America/Los_Angeles',  # Change to your time zone if not in PT
        },
        'end': {
            'dateTime': arguments['end_time'],
            'timeZone': 'America/Los_Angeles',
        },
    }
    print(event_body)
    return event_body

def create_calendar_event_with_body(event_body):
    event = service.events().insert(calendarId='primary', body=event_body).execute()
    print(f"Event created: {event.get('htmlLink')}")

# def create_calendar_event(service, message):
#     # Set the time for the event to 7 AM local time
#     today = datetime.date.today()
#     start_time = datetime.datetime.combine(today, datetime.time(7, 0))
#     end_time = start_time + datetime.timedelta(minutes=30)  # Duration of 30 minutes
    
#     clean_message = message.replace('"', '')

#     event_body = {
#         'summary': clean_message,
#         #'summary': 'Your Positive Message for the Day',
#        # 'description': message,
#         'start': {
#             'dateTime': start_time.isoformat(),
#             'timeZone': 'America/Los_Angeles',  # Change to your time zone if not in PT
#         },
#         'end': {
#             'dateTime': end_time.isoformat(),
#             'timeZone': 'America/Los_Angeles',
#         },
#     }
#     print(event_body)

#     event = service.events().insert(calendarId='primary', body=event_body).execute()
#     print(f"Event created: {event.get('htmlLink')}")

def main():
    events = get_todays_events(service)
    # with open('events.pkl', 'rb') as f:
    #     events = pickle.load(f)
    print(events)
    if not events:
        print("No upcoming events found for today.")
    else:
        prompt = generate_suggestions_from_events(events)
        suggestion_json = generate_event_suggestions(prompt)
        suggestion_to_event_function_call(suggestion_json)

if __name__ == '__main__':
    main()




