from datetime import datetime

import steem

import db
from helpers import get_link_string, parse_date, print_with_timestamp, timer

steemd = steem.Steem()
UNIX_DATE_0 = datetime(1970, 1, 1).date()

def fetch_thread_rows(author, permlink):
    comment = fetch_comment((author, permlink))
    if comment_is_not_found(comment):
        print(f'Could not find thread "{get_link_string(author, permlink)}"')
        return []
    return format_comment_rows(fetch_thread(comment))

def fetch_user_history_rows(username, start_date, end_date, comment_keys, only_authored):
    num_posts = 0
    num_comments = 0
    current_date = None

    # Iterate through the user history. Note that the comment operations returned from the history
    # api call are not the same as the full comments, they are missing certain information such as
    # root author and root permlink.
    for comment_op in fetch_user_comment_ops(username):
        op_date = parse_date(comment_op['timestamp'])
        if op_date > end_date:
            continue
        if op_date < start_date:
            break

        if op_date != current_date:
            current_date = op_date
            print_with_timestamp(f'Searching history for {current_date}')

        post_comments = fetch_comment_op_thread(comment_op, comment_keys, username, only_authored)
        num_posts += 1
        num_comments += len(post_comments)
        yield format_comment_rows(post_comments)
    
    print_with_timestamp(f'Fetched {num_posts} posts with {num_comments} comments')

def fetch_comment_op_thread(comment_op, comment_keys, username, only_authored):
    # Skip comments we've already fetched
    op_key = get_key(comment_op)
    if op_key in comment_keys:
        return []
    
    post_comments = []

    # We can't fetch deleted comments from the api, so try to use the parent
    # to fill in the information missing from the operation
    comment = fetch_comment(op_key)
    if comment_is_not_found(comment):
        parent_comment = fetch_comment(get_parent_key(comment_op))
        if comment_is_not_found(parent_comment):
            print_with_timestamp(f'Could not find "{get_link_string(*op_key)}", skipping...')
            return []
        post_comments.append(make_comment_from_parent(comment_op, parent_comment))
        print_with_timestamp(
            f'Comment "{get_link_string(*op_key)}" was deleted'
            ' but was able to fill in information from parent'
        )
        # Now that the deleted comment was added, find the root comment from the parent
        comment = parent_comment

    if only_authored and comment['root_author'] != username:
        return []

    # If this isn't the root comment, fetch it
    comment_key = get_key(comment)
    root_key = get_root_key(comment)
    root_comment = comment if root_key == comment_key else fetch_comment(root_key)

    with timer(f'Fetching post "{get_link_string(*root_key)}"'):
        post_comments.extend(fetch_thread(root_comment, comment_keys))
    return post_comments

# Add the information missing from the comment operation from the parent comment
def make_comment_from_parent(comment_op, parent_comment):
    comment_op = dict(comment_op)
    comment_op['root_author'] = parent_comment['root_author']
    comment_op['root_permlink'] = parent_comment['root_permlink']
    comment_op['category'] = ''
    comment_op['created'] = comment_op['timestamp']
    comment_op['last_update'] = comment_op['timestamp']
    comment_op['depth'] = int(parent_comment['depth']) + 1
    comment_op['was_deleted'] = True
    return comment_op

# Given a comment, recursively fetch all its children and return the comment and children 
def fetch_thread(comment, comment_keys=set()):
    all_comments = [comment]
    comment_key = get_key(comment)
    comment_keys.add(comment_key)
    for comment_reply in fetch_comment_replies(comment_key):
        all_comments.extend(fetch_thread(comment_reply, comment_keys))
    return all_comments

def fetch_user_comment_ops(username):
    return (
        steem.account
        .Account(username, steemd)
        .history_reverse(filter_by='comment', batch_size=3000)
    )

def fetch_comment(key):
    return steemd.get_content(*key)

def fetch_comment_replies(key):
    return steemd.get_content_replies(*key)

def get_key(c):
    return c['author'], c['permlink']

def get_root_key(c):
    return c['root_author'], c['root_permlink']

def get_parent_key(c):
    return c['parent_author'], c['parent_permlink']

# When the api can't find a comment, it returns a JSON object with filler values
def comment_is_not_found(comment):
    return parse_date(comment['created']) == UNIX_DATE_0

# Turn the raw JSON objects returned from the api into dicts ready to insert into the comment table
def format_comment_rows(rows):
    return [db.format_row(db.comment, row) for row in rows]
