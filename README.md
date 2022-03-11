# Notion Calendar Export
Slightly modified version of [notion-export-ics](https://github.com/evertheylen/notion-export-ics).

Modifications include
- Dockerfile for serving iCal subscription
- Migrate to poetry
- Little extra functionality with tags

## Quick usage

- Get your Notion api token by [creating a new integration](https://www.notion.so/my-integrations)
- Share your database with the integration via the share menu
- Get your database ID:
  - Open your database in Notion
  - Open the settings menu (elipses in the top right)
  - Clip copy link
  - Paste the link, the database ID will be the last path component (i.e. `THIS-RIGHT-HERE` in `https://www.notion.so/username/THIS-RIGHT-HERE?v=some-long-string`)

### CLI
```
$> echo '{"token": "secret_t3459384798", "db_id": "b4289r279f8dh", "title_format":"[{Tags[0]}] {Name}"}' > settings.json
$> poetry run python notion_calendar/make_ics.py settings.json > calendar.ics
$> open calendar.ics
```

### Web app

```
$> poetry run python notion_calendar/webapp.py
... serving on 0.0.0.0:8080 ...
```

Dockerfile included, listening on port `8080`.

### Dokku

```
$> git push dokku main:master
```
