# -*- coding: utf-8 -*-
"""
This Code Imports a specified Google Calendar and adds up the 
total amount of time that each department uses our shared research 
spaces. The time window must be specified by the user running the 
script. 

Note this is the beta version of a script that has been expanded and 
updated by the UW Ability and Innovation lab.
"""

from icalendar import Calendar
from datetime import timedelta
from datetime import date
from datetime import datetime
from itertools import groupby
from operator import itemgetter
import unicodedata
from dateutil.rrule import rrulestr
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *


def calculate_time(event):
    start = event['DTSTART'].dt
    end = event['DTEND'].dt
    return end - start


def summary_String(event):
    summary = str(event['SUMMARY'])
    for ID in summaryIDs:
        if ID in summary:
            return ID
    
          
def uni2StrConverter(rRule):
    RRule_Comp_Str = {}
    for key in rRule:
    #access keys and values in RRULE, modify both to create strings, create 
    #new dict with strings instead of unicode
        modKey = unicodedata.normalize('NFKD', key).encode('ascii','ignore')
        elements = []
    
        for element in rRule[key]:
            #elements are actually iCal objects, not unicode objects
            strElem = (str(element))
            elements.append(strElem)
            
            RRule_Comp_Str[modKey] = elements
    return RRule_Comp_Str



#Build out an rruleStr that we can use to generate a rule string
def strParser(modRRule):
    rruleStr = ""
    numKeys = len(modRRule)
    keyCount = 0
    #print(numKeys)
    
    #for each key in modRRule, we want to add this to our rule string
    for key in modRRule:
        keyCount = keyCount + 1
        rruleStr = rruleStr + key + "="
        
        #Gives us num of vals within each key
        numVals = len(modRRule[key])
        valCount = 0
        
        for val in modRRule[key]: 
            valCount = valCount + 1
            #if key = UNTIL, only take 1st 10 characters
            #need to change from hard count to variable. 10 = length of date value.
            if len(val) > 10:
                valSubStr = val[0:10]
                rruleStr = rruleStr + valSubStr
            else:
                rruleStr = rruleStr + val
            if valCount < numVals:
                rruleStr = rruleStr + ","
                
        #add a semicolon to the end of the key + value string, unless we're on the last key
        if keyCount < numKeys:
            rruleStr = rruleStr + ";"
    
    return rruleStr



def multiplyAndCount(rule):
    newRule = rule
    startDate = "20170401" #(we want this to be a constant provided by our user)
    expandRecurEv = list(rrulestr(newRule, dtstart=parse(startDate)))
    
    futureDate = datetime(2017,06,01) #(we want this to be a constant provided by our user)
    
    recurCount = 0
    for recurEve in expandRecurEv:
        if futureDate >= recurEve:
            recurCount = recurCount + 1
    
    return recurCount


#Function to determine whether or not an RRULE exists. 
def RRULE_Verify(events):
    for element in events:
        strElement = unicodedata.normalize('NFKD', element).encode('ascii','ignore')
        if strElement == 'RRULE':
            ContainsRRULE = True
            break
        else:
            ContainsRRULE = False
        
    return ContainsRRULE


#Grabs RRULEs from events and turns them into rule strings that can be used by other functions
def append_repeats(events):
    
    repeatBool = RRULE_Verify(events)
    
    if repeatBool == True:
        
        rRule = events['RRULE']
        modRRule = uni2StrConverter(rRule)
        
        rule = strParser(modRRule)
        
        numEventRepeats = multiplyAndCount(rule)
        
        return numEventRepeats 
    
    else:
        
        singleEvent = 1
        return singleEvent
    
    
#Sorts events by depot. name. (Will want to augment functionality to names / team names.)
    #Augment by saving an index to a variable name and then plugging variable nmae into 
    #function.
#After keys are sorted, group them by that same variable (i.e. depot., team, or name.)
#After grouping, sum all of the times together. All times correspond to depot., team, or,...
    #name within the specified time frame.
def sort_and_sum(mod_events):
    sorted_events = sorted(mod_events, key=itemgetter(0))
    for key, group in groupby(sorted_events, itemgetter(0)):
        yield (key, sum(map(itemgetter(1), group), timedelta()))    

#build summary IDs for sorting
summaryIDs = ['ME, MoCap', 'ME, Small MoCap', 'EE, MoCap', 'EE, Small MoCap']

#load in AMP calendar file
file = open('/Users/darrinhowell/Documents/iCalPyScripts/pyTestCal_UntilCheck_uw.edu_a1ckdp6feimsr2456h3qkg58c0@group.calendar.google.com.ics')
cal = Calendar.from_ical(file.read())

###############################################################################


#Implement methods

#build events list w/ repeats
events = []
for e in cal.walk('vevent'):
    #want to add the following functionality... 
        #if e occurs within the time window specified..., then add to the events list
        #if event['DTSTART'].dt && event['DTEND] between specified window add!
    newEvent = ((summary_String(e), calculate_time(e), append_repeats(e)))
    events.append(newEvent)
    events = [e for e in events if e[0] != None] 
print(events) 


#multiply numRepeats by duration of single calendar event
muted_events = events
mute_index = 0
for sublist in muted_events:
    sublist = list(sublist)    
    sublist[1] = sublist[1] * int(sublist[2])
    muted_events[mute_index] = sublist
    mute_index = mute_index + 1
 
    
#sort events by common summary ID name. Calculate total time    
used_time_updated = dict(sort_and_sum(muted_events))
total_time_updated = sum(used_time_updated.values(), timedelta())

for summaryID, time in used_time_updated.items():
    print('{}\t{}h'.format(summaryID, time.total_seconds() / 3600))

print('=============')
print('TOTAL\t{}h'.format(total_time_updated.total_seconds() / 3600))

