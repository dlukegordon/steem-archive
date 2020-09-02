from sqlalchemy import Boolean, Column, DateTime, create_engine, Integer, MetaData, String, Table

from fetch import get_key
from helpers import parse_datetime

engine = create_engine('sqlite:///steem_archive.sqlite')
metadata = MetaData()

def init_db():
    metadata.drop_all(engine)
    metadata.create_all(engine)

def get_conn():
    return engine.connect()

def insert_or_ignore(table, rows, conn=get_conn()):
    return conn.execute(table.insert(rows).prefix_with('OR IGNORE'))

def select(table, wherecols, conn=get_conn()):
    stmt = table.select()
    for col, value in wherecols.items():
        stmt = stmt.where(table.c[col] == value)
    return rows_to_dicts(conn.execute(stmt))

def get_comment_keys(conn=get_conn()):
    return set([get_key(row) for row in list(select(comment, {}))])

# Convert the ReultProxy object returned by sqlalchemy to a generator of python dicts
def rows_to_dicts(rows):
    return (dict(row.items()) for row in rows)

# Format a dict so that it's ready to insert into a table
def format_row(table, row_raw):
    row = {}
    for col in table.columns:
        value = row_raw.get(col.name, None)
        if value is None:
            continue
        if isinstance(col.type, DateTime):
            value = parse_datetime(value)
        row[col.name] = value
    return row

# Determines whether a comment is a top level comment, aka a post
def is_post(context):
    params = context.get_current_parameters()
    return params['root_permlink'] == params['permlink'] and params['parent_author'] == ''

# Stores the comments/posts. Note that all columns except the last three
# are named the same as they appear in the steem api.
comment = Table(
    'comment', metadata,
    Column('author', String, primary_key=True, nullable=False),
    Column('permlink', String, primary_key=True, nullable=False),
    Column('parent_author', String, nullable=False),
    Column('parent_permlink', String, nullable=False),
    Column('root_author', String, nullable=False),
    Column('root_permlink', String, nullable=False),
    Column('title', String, nullable=False),
    Column('category', String, nullable=False),
    Column('created', DateTime, nullable=False),
    Column('last_update', DateTime, nullable=False),
    Column('depth', Integer, nullable=False),
    Column('body', String, nullable=False),
    Column('is_post', Boolean, nullable=False, default=is_post),
    Column('was_deleted', Boolean, nullable=False, default=False),
)
