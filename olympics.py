from json import load
from datetime import datetime, timezone, timedelta
from argparse import ArgumentParser
from os import path
from sys import argv
from typing import List


# http://cdn.espn.com/core/olympics/winter/2022/schedule?xhr=1&render=true&device=desktop&country=us&lang=en&region=us&site=espn&edition-host=espn.com&one-site=true&site-type=full
def process(filepath: str, args: ArgumentParser) -> List[dict]:
    with open(filepath + "olympics.json", "r") as afile:
        schedule = load(afile)

    disciplines = schedule['disciplines']
    allEvents = []
    for i in disciplines:
        name = i['name']
        events = i['events']
        for j in events:
            anEvent = j['competitions']
            for k in anEvent:
                k['name'] = name
                date = datetime.strptime(k['date'], '%Y-%m-%dT%H:%MZ').replace(tzinfo=timezone.utc).astimezone()
                k['date'] = date
                allEvents.append(k)
    allEvents.sort(key=lambda x: x['date'])
    three_hours_ago = (datetime.now() - timedelta(hours=3)).astimezone()
    toprint = [i for i in allEvents if i['date'] > three_hours_ago or args.all_events]
    toprint = event_search(args, toprint)
    for i in toprint[:int(args.count)]:
        print_event(i)
    return allEvents


def event_search(args, event_list):
    if args.search is not None:
        search = args.search.lower()
        event_list = [i for i in event_list if search in (i['name'] + i['description']).lower()]

    if args.exclude is not None:
        exclude = args.exclude.lower()
        event_list = [i for i in event_list if exclude not in (i['name'] + i['description']).lower()]
    return event_list


def print_event(event):
    theDate = event['date'].strftime("On %b %d, at %I:%M%p")
    name = event['name']
    desc = event['description']
    medal = event['finalMedalComp']
    if medal:
        a_medal = " for a medal"
    else:
        a_medal = ""
    print("{} there is a {} event called {}{}".format(theDate, name, desc, a_medal))


if __name__ == '__main__':
    filepath = path.dirname(argv[0])
    if len(filepath) != 0:
        filepath = filepath + "/"

    parser = ArgumentParser(description="prints out olympic events. All data sourced from ESPN via")
    parser.add_argument(
        '-a', '--all', dest='all_events', action='store_true',
        help="If used shows events starting with the first event of the olympics, otherwise only events occuring from "
        "3 hours ago and beyond are shown")
    parser.add_argument('-c', '--count', dest='count', default=900, help="What is the maximum number of events to show,"
                        " defaults to more than the total number of events in the olympics")
    parser.add_argument('-s', '--search', dest='search', default=None, help="Searches the sport and description for the"
                        " exact string ignoring case if it appears it will be printed otherwise it won't.  This filter"
                        " is superceded by count and all")
    parser.add_argument('-e', '--exclude', dest='exclude', default=None, help="Searches the sport and description for"
                        " the exact string ignoring case. If the string is found the event is not displayed. Occurs "
                        "after the search. So the event 'short-track speedskating' with will not show up if 'short' is"
                        " searched for and 'speed' is excluded")
    process(filepath, parser.parse_args())
