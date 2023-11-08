#! /Users/az/anaconda3/bin/python

import os
import pickle
import datetime
import openai
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


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

openai.api_key = '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'

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

def generate_positive_message(prompt):
    #response = client.chat.completions.create(
    response = openai.completions.create(
        model="gpt-3.5-turbo-instruct",  # Update with the correct model
        prompt=prompt,
        max_tokens=150,
        temperature=0.9
    )
    message = response.choices[0].text
    return message

def create_calendar_event(service, message):
    # Set the time for the event to 7 AM local time
    today = datetime.date.today()
    start_time = datetime.datetime.combine(today, datetime.time(7, 0))
    end_time = start_time + datetime.timedelta(minutes=30)  # Duration of 30 minutes
    
    clean_message = message.replace('"', '')

    event_body = {
        'summary': clean_message,
        #'summary': 'Your Positive Message for the Day',
       # 'description': message,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'America/Los_Angeles',  # Change to your time zone if not in PT
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'America/Los_Angeles',
        },
    }

    event = service.events().insert(calendarId='primary', body=event_body).execute()
    print(f"Event created: {event.get('htmlLink')}")

def main():
    events = get_todays_events(service)
    if not events:
        print("No upcoming events found for today.")
    else:
        prompt = generate_prompt_from_events(events)
        positive_message = generate_positive_message(prompt)
        create_calendar_event(service, positive_message)

if __name__ == '__main__':
    main()




