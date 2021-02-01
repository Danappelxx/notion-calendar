from notion.client import NotionClient
from notion_ics import get_ical
import json
import sys

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        settings = json.load(f)

    client = NotionClient(settings['token'], monitor=False)
    cal = get_ical(client, settings['calendar_url'], settings['title_format'])

    print(cal.to_ical())
