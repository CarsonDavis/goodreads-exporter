# goodreads-exporter
## What?
Simple script to export goodreads data as csv.

## Why?
Doesn't goodreads already have csv export?

yes...but it has a known bug for about 4 years where it fails to export the read date, and it seems like the staff have no plans to fix it.

## How to Run
1. Make a python env with the requirements
2. Edit the config.py with your username
3. Run exporter.py

This will make a csv, `goodreads_export-YYYYMMDD.csv`

## Known Limitations
This isn't meant to fully replace the goodreads exporter, just fill in the data that it misses.
- Since you aren't logged it, it won't export private notes.

This was mostly just a quick script to make sure I had dates backed up, but if there is demand for more functionality feel free to leave an issue.
