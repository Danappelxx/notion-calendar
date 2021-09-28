from notion_client import Client
from notion_ics import get_ical
import json
import sys

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        settings = json.load(f)

    client = Client(auth=settings['token'])
    cal = get_ical(client, settings['db_id'], settings['title_format'])

    print(cal.to_ical().decode("utf-8"))
