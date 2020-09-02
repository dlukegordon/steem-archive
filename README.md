# steem-archive

A tool to download comments from the steem blockchain (via the steem api), store them in a sqlite database, and display them.

```
$ python steem_archive.py 
Usage: steem_archive.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  display  Display a thread which is already in the database, specified by a
           link of format "@<user>/<permlink>".
  init-db  Create the database and tables. Any existing data will be wiped.
  thread   Download and save to the database a thread specified by a link of
           format "@<user>/<permlink>".
  user     Download and save to the database all posts which the user has
           contributed to, either by writing the post or commenting. Runs in
           reverse chronological order. Comments which are already in the
           database will be skipped. Do not include a preceding "@"

$ python steem_archive.py user --help
Usage: steem_archive.py user [OPTIONS] USERNAME

Options:
  -s, --start-date TEXT  Start date of history to search (inclusive, format
                         "YYYY-MM-DD").
  -e, --end-date TEXT    End date of history to search (inclusive, format
                         "YYYY-MM-DD").
  -a, --only-authored    Only download posts which the user has authored.
  --help                 Show this message and exit.

```
