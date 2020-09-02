from termcolor import colored

import db
from fetch import get_key, get_root_key
from helpers import get_header_string, get_link_string

# Print a representation of a thread
def display_thread(author, permlink):
    result = list(db.select(db.comment, dict(author=author, permlink=permlink)))
    if not result:
        print(f'Could not find thread "{get_link_string(author, permlink)}" in the database')
        return
    comment = result[0]

    root_author, root_permlink = get_root_key(comment)
    post_comments = list(db.select(
        db.comment,
        dict(root_author=root_author, root_permlink=root_permlink)
    ))
    parent_groups = group_comments_by_parent(post_comments)
    comment_tree = build_comment_tree(comment, parent_groups)
    display_comment_tree(comment_tree)

def group_comments_by_parent(comments):
    parent_groups = {}
    for c in comments:
        key = c['parent_author'], c['parent_permlink']
        if key not in parent_groups:
            parent_groups[key] = []
        parent_groups[key].append(c)
    return parent_groups

# Recursively build a tree of comments
def build_comment_tree(comment, parent_groups):
    return dict(
        comment=comment,
        children=[
            build_comment_tree(c, parent_groups)
            for c in parent_groups.get((comment['author'], comment['permlink']), [])
        ],
    )

# Recursively print the comment tree
def display_comment_tree(tree, depth=0):
    print_comment(tree['comment'], depth)
    for t in tree['children']:
        display_comment_tree(t, depth + 1)

def print_comment(c, depth):
    indent = ' ' * 4 * depth
    header_message = f'@{c["author"]}: {c["created"]}'[:-3]
    if c['was_deleted']:
        header_message += ' (deleted)'
    header = indent + get_header_string(header_message)
    body = indent + c['body'].replace('\n', '\n' + indent) + '\n\n'

    if depth == 0:
        if c['title']:
            print('\n' + colored(get_header_string(c['title']), 'green', attrs=['bold']))
        print(colored(
            get_header_string(get_link_string(*get_key(c))) + '\n\n',
            'green',
            attrs=['bold']
        ))
    print(colored(header, 'green'))
    print(body)
