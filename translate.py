from __future__ import print_function
import urllib.request as req
import json
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'

# your class-code
CLASS = "<code>"

# you can insert conversions here to get better names in your calendar
building_conversion = {
}

def main():

    #get the data from the roosters-api
    with req.urlopen("https://api.roosters.saxion.nl/v2/groups/schedule.json?group=" + CLASS) as page:
        data = json.load(page)

    #get permissions from the google-calendar api
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('creds.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))


    #traverse the schedule as provided by the roosters-api
    for entries in data['days']:
        for classes in entries['entries']:

            #convert timing to the rfc3339 format (note: this only handles CET as of now)
            startTime = classes['date']+'T'+classes['start']+':00+01:00'
            endTime   = classes['date']+'T'+classes['end']  +':00+01:00'

  


            insert_event = {
                # set the summary of the calendar entry
                'summary' : classes['name_en'] + " in " +classes['room'],

                #set the location information of the calendar entry
                'location' : classes['room'] if not classes['room'][0] in building_conversion.keys() else building_conversion[classes['room'][0]],

                #set the class description
                'description' : classes['note'] + ' with ' + classes['teachername'],

                #start time
                'start':{
                    'dateTime': startTime,
                    'timeZone': 'CET'
                },

                #end time
                'end':{
                    'dateTime': endTime,
                    'timeZone': 'CET'
                },

                #how to remind me
                'reminders':{
                    'useDefault': False,
                    'overrides':[{
                        'minutes' : 5,
                        'method' : 'popup'
                    }]
                }
            }

            # Call the Calendar API
            event = service.events().insert(calendarId='primary',body=insert_event).execute()

if __name__ == '__main__':
    main()
