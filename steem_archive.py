#!/usr/bin/env python3

# This is the entrypoint for the application. CLI commands are handled via click.

import click
from datetime import datetime

import archive
from display import display_thread
from helpers import parse_date
import db

STEEM_START_DATE = datetime(2016, 7, 4).date()

@click.group()
def cli():
    pass

@cli.command(short_help='Create the database and tables. Any existing data will be wiped.')
def init_db():
    click.confirm('Are you sure? Any existing data will be wiped.', abort=True)
    db.init_db()

@cli.command(short_help='Download and save to the database all posts which the user has contributed to, ' +
    'either by writing the post or commenting. Runs in reverse chronological order. Comments which are ' +
    'already in the database will be skipped. Do not include a preceding "@"')
@click.argument('username')
@click.option('-s', '--start-date', default='',
    help='Start date of history to search (inclusive, format "YYYY-MM-DD").')
@click.option('-e', '--end-date', default='',
    help='End date of history to search (inclusive, format "YYYY-MM-DD").')
@click.option('-a', '--only-authored', is_flag=True, help='Only download posts which the user has authored.')
def user(username, start_date, end_date, only_authored):
    try:
        if start_date == '':
            start_date = STEEM_START_DATE
        else:
            start_date = parse_date(start_date)

        if end_date == '':
            end_date = datetime.now().date()
        else:
            end_date = parse_date(end_date)
    except ValueError:
        print('Invalid date format, must be "YYYY-MM-DD"')
        exit()
    archive.archive_user_history(username, start_date, end_date, only_authored)

@cli.command(short_help='Download and save to the database a thread specified by a link of format "@<user>/<permlink>".')
@click.argument('link')
def thread(link):
    author, permlink = parse_link(link)
    archive.archive_thread(author, permlink)

@cli.command(short_help='Display a thread which is already in the database, specified by a link of format "@<user>/<permlink>".')
@click.argument('link')
def display(link):
    author, permlink = parse_link(link)
    display_thread(author, permlink)

def parse_link(link):
    try:
        assert(link[0]) == '@'
        splitted = link[1:].split('/')
        assert(len(splitted) == 2)
        return splitted
    except AssertionError:
        print('Invalid format, must be "@<user>/<permlink>"')
        exit()


if __name__ == '__main__':
    cli()
