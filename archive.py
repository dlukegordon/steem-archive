import db
import fetch
from helpers import get_link_string, print_with_timestamp, timer

def archive_user_history(username, start_date, end_date, only_authored):
    message = f'Archive history for user "{username}" from {start_date} to {end_date}'
    if only_authored:
        message += ' (only self-authored posts)'
    with timer(message):
        comment_keys = db.get_comment_keys() # Keep track of the comments we've already fetched
        for post_comments in fetch.fetch_user_history_rows(
            username, start_date, end_date, comment_keys, only_authored
        ):
            if post_comments:
                insert_comments(post_comments)

def archive_thread(author, permlink):
    with timer(f'Archive thread "{get_link_string(author, permlink)}"'):
        thread_comments = fetch.fetch_thread_rows(author, permlink)
        if thread_comments:
            insert_comments(thread_comments)

def insert_comments(rows):
    result = db.insert_or_ignore(db.comment, rows)
    num_inserted = result.rowcount
    num_skipped = len(rows) - num_inserted
    message = f'Inserted {num_inserted} rows into "{db.comment.name}"'
    if num_skipped:
        message += f' ({num_skipped} skipped)'
    print_with_timestamp(message)
