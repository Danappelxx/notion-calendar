# Notion Calendar Export
Slightly modified version of [notion-export-ics](https://github.com/evertheylen/notion-export-ics).

Modifications include
- Dockerfile for serving iCal subscription
- Migrate to poetry
- Little extra functionality with tags

Keeping private because `settings.json` has credentials and I'm too lazy to scrub.

## Quick usage
```
$> poetry run python notion_calendar/make_ics.py settings.json > calendar.ics
$> poetry run python notion_calendar/webapp.py
... serving on 0.0.0.0:8080 ...
```
