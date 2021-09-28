from datetime import datetime
from icalendar import Calendar, Event
from notion_client import Client
from collections import OrderedDict


def get_ical(notion, db_id, title_format):
    schema = notion.databases.retrieve(db_id)["properties"]

    db_query = notion.databases.query(db_id)
    assert not db_query["has_more"]
    calendar_entries = db_query["results"]

    properties_by_id = {}
    title_prop = None
    date_prop = None

    for name in schema:
        properties_by_id[schema[name]['id']] = schema[name]
        if schema[name]['type'] == 'title':
            title_prop = schema[name]
        if schema[name]['type'] == 'date':
            date_prop = schema[name]

    assert title_prop is not None, "Couldn't find a title property"
    assert date_prop is not None, "Couldn't find a date property"

    cal = Calendar()
    cal.add("summary", "Imported from Notion, via notion-export-ics.")
    cal.add('version', '2.0')

    for notion_event in calendar_entries:
        event_props = notion_event["properties"]

        # Put in ICS file
        event = Event()
        desc = ''
        desc += notion_event["url"] + '\n\n'
        desc += 'Properties:\n'

        clean_props = OrderedDict()
        for k, v in event_props.items():
            prop_type = v["type"]
            val = None
            if prop_type == "date":
                date = event_props[date_prop["name"]]["date"]
                event.add('dtstart', datetime.strptime(date["start"], '%Y-%m-%d').date())
                if date.get("end") is not None:
                    event.add('dtend', datetime.strptime(date["end"], '%Y-%m-%d').date())
            elif prop_type == "title":
                val = v["title"][0]["plain_text"]
            elif prop_type == "multi_select":
                val = [t["name"] for t in v["multi_select"]]

            if val is not None:
                desc += "  - {}: {}\n".format(k, val)
                clean_props[k] = val
            # print("type:", v["type"])
            # if k != dateprop['slug']:
            #     name = properties_by_slug[k]['name']
            #     desc += "  - {}: {}\n".format(name, v)
            #     clean_props[name] = v

        try:
            title = title_format.format_map(clean_props)
        except:
            title = clean_props['NAME']
        event.add('summary', title)
        event.add('description', desc)
        cal.add_component(event)

    return cal
