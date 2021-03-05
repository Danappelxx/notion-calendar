import json
from datetime import datetime

from icalendar import Calendar, Event
from notion.client import NotionClient
from notion.collection import CollectionView, CalendarView as _CalendarView
from notion.block import BasicBlock
from notion.user import User


## Various monkey patching for notion-py
BasicBlock.__repr__ = BasicBlock.__str__ = lambda self: self.title
User.__repr__ = User.__str__ = lambda self: self.given_name or self.family_name

def calendar_build_query_fixed(self):
    calendar_by = self._client.get_record_data("collection_view", self._id)[
        "query2"
    ]["calendar_by"]
    return CollectionView.build_query(self, calendar_by=calendar_by)

import notion
def store_recordmap(self, recordmap):
    for table, records in recordmap.items():
        if records is None: continue
        for id, record in records.items():
            self._update_record(
                table, id, value=record.get("value"), role=record.get("role")
            )
notion.store.RecordStore.store_recordmap = store_recordmap

from tzlocal import get_localzone

import notion
def call_load_page_chunk(self, page_id):

    if self._client.in_transaction():
        self._pages_to_refresh.append(page_id)
        return

    data = {
        "pageId": page_id,
        "limit": 100,
        "cursor": {"stack": []},
        "chunkNumber": 0,
        "verticalColumns": False,
    }

    recordmap = self._client.post("loadPageChunk", data).json()["recordMap"]

    self.store_recordmap(recordmap)

def call_query_collection(
    self,
    collection_id,
    collection_view_id,
    search="",
    type="table",
    aggregate=[],
    aggregations=[],
    filter={},
    sort=[],
    calendar_by="",
    group_by="",
):

    assert not (
        aggregate and aggregations
    ), "Use only one of `aggregate` or `aggregations` (old vs new format)"

    # convert singletons into lists if needed
    if isinstance(aggregate, dict):
        aggregate = [aggregate]
    if isinstance(sort, dict):
        sort = [sort]

    data = {
        "collectionId": collection_id,
        "collectionViewId": collection_view_id,
        "loader": {
            "limit": 1000000,
            "loadContentCover": True,
            "searchQuery": search,
            "userLocale": "en",
            "userTimeZone": str(get_localzone()),
            "type": type,
        },
        "query": {
            "aggregate": aggregate,
            "aggregations": aggregations,
            "filter": filter,
            "sort": sort,
        },
    }

    response = self._client.post("queryCollection", data).json()

    self.store_recordmap(response["recordMap"])

    return response["result"]

def search_pages_with_parent(self, parent_id, search=""):
    data = {
        "query": search,
        "parentId": parent_id,
        "limit": 100,
        "spaceId": self.current_space.id,
    }
    response = self.post("searchPagesWithParent", data).json()
    self._store.store_recordmap(response["recordMap"])
    return response["results"]

notion.store.RecordStore.call_load_page_chunk = call_load_page_chunk
notion.store.RecordStore.call_query_collection = call_query_collection
notion.client.NotionClient.search_pages_with_parent = search_pages_with_parent
##


def get_ical(client, calendar_url, title_format):
    calendar = client.get_block(calendar_url)
    for view in calendar.views:
        if isinstance(view, _CalendarView):
            calendar_view = view
            break
    else:
        raise Exception(f"Couldn't find a calendar view in the following list: {calendar.views}")

    calendar_query = calendar_build_query_fixed(calendar_view)
    calendar_entries = calendar_query.execute()

    collection = calendar.collection

    schema = collection.get_schema_properties()

    properties_by_name = {}
    properties_by_slug = {}
    properties_by_id = {}
    title_prop = None

    for prop in schema:
        name = prop['name']
        if name in properties_by_name:
            print("WARNING: duplicate property with name {}".format(name))
        properties_by_name[name] = prop
        properties_by_slug[prop['slug']] = prop
        properties_by_id[prop['id']] = prop
        if prop['type'] == 'title':
            title_prop = prop

    assert title_prop is not None, "Couldn't find a title property"

    dateprop = properties_by_id[calendar_query.calendar_by]
    #assert dateprop['type'] == 'date', "Property '{}' is not a Date property".format(settings['property'])

    cal = Calendar()
    cal.add("summary", "Imported from Notion, via notion-export-ics.")
    cal.add('version', '2.0')

    for e in calendar_entries:
        date = e.get_property(dateprop['id'])
        if date is None:
            continue

        name = e.get_property(title_prop['id'])
        clean_props = {'NAME': name}

        # Put in ICS file
        event = Event()
        desc = ''
        event.add('dtstart', date.start)
        if date.end is not None:
            event.add('dtend', date.end)
        desc += e.get_browseable_url() + '\n\n'
        desc += 'Properties:\n'
        for k, v in e.get_all_properties().items():
            if k != dateprop['slug']:
                name = properties_by_slug[k]['name']
                desc += "  - {}: {}\n".format(name, v)
                clean_props[name] = v

        try:
            title = title_format.format_map(clean_props)
        except:
            title = clean_props['NAME']
        event.add('summary', title)
        event.add('description', desc)
        cal.add_component(event)

    return cal

