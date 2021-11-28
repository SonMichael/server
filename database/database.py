import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext

def open():
    if 'database' not in g:
        g.database = sqlite3.connect(
            './database/database.sqlite',
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.database.row_factory = sqlite3.Row

    return g.database


def close():
    database = g.pop('database', None)
    if database is not None:
        database.close()

def init():
    database = open()
    with  current_app.open_resource('database/schema.sql') as f:
        database.executescript(f.read().decode('utf8'))

def init_app(app):
    app.teardown_appcontext(close)
    app.cli.add_command(init_database_command)

@click.command('init-database')
@with_appcontext
def init_database_command():
    """Clear the existing data and create new table."""
    init()
    click.echo("Initialized the datbase.")