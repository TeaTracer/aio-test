"""
Module with database tables declaration
Database: aio
Schema: aio
Tables: tokens, users, remote_managers, local_managers, restaurants,
        orders, dishes, menu, categories, trees
"""

import sqlalchemy as sa

from .settings import settings

metadata = sa.MetaData()

db = settings["database"]
n = db["string_len"]
acc = db["currency_acc"]
schema = db["schema"]
hash_n = db["hash_len"]
salt_n = db["salt_len"]
token_n = db["token_len"]

users = sa.Table('users', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('login', sa.String(n), nullable=False),
                 sa.Column('password', sa.String(hash_n), nullable=False),
                 sa.Column('salt', sa.String(salt_n), nullable=False),
                 schema=schema)

async def create_table_users(conn):
    await conn.execute(f'''CREATE TABLE IF NOT EXISTS users (
                                        id serial PRIMARY KEY,
                                        login varchar({n}) not null,
                                        password varchar({hash_n}) not null,
                                        salt varchar({salt_n}) not null
                                        )''')

tokens = sa.Table('tokens', metadata,
                  sa.Column('token', sa.String(token_n), nullable=False),
                  sa.Column('user_id', sa.Integer,
                             sa.ForeignKey('users.id')),
                  sa.Column('inserted_at', sa.TIMESTAMP,
                            default=sa.func.current_timestamp(), nullable=False),
                  schema=schema)

async def create_table_tokens(conn):
    await conn.execute(f'''CREATE TABLE IF NOT EXISTS tokens (
                                        token varchar({token_n}) not null,
                                        user_id int references users(id),
                                        inserted_at timestamp default current_timestamp
                                        )''')


remote_managers = sa.Table('remote_managers', metadata,
                           sa.Column('id', sa.Integer, primary_key=True),
                           sa.Column('user_id', sa.Integer,
                                      sa.ForeignKey('users.id')),
                           sa.Column('name', sa.String(n), nullable=False),
                           #  sa.Column('restaurant', sa.Integer,
                                     #  sa.ForeignKey('restaurants.id')),
                           schema=schema)

async def create_table_remote_managers(conn):
    await conn.execute(f'''CREATE TABLE IF NOT EXISTS remote_managers (
                                        id serial PRIMARY KEY,
                                        user_id int references users(id),
                                        name varchar({n}) not null
                                        )''')

local_managers = sa.Table('local_managers', metadata,
                          sa.Column('id', sa.Integer, primary_key=True),
                          sa.Column('user_id', sa.Integer,
                                     sa.ForeignKey('users.id')),
                          sa.Column('name', sa.String(n), nullable=False),
                          schema=schema)

async def create_table_local_managers(conn):
    await conn.execute(f'''CREATE TABLE IF NOT EXISTS local_managers (
                                        id serial PRIMARY KEY,
                                        user_id int references users(id),
                                        name varchar({n}) not null
                                        )''')

categories = sa.Table('categories', metadata,
                      sa.Column('id', sa.Integer, primary_key=True),
                      sa.Column('name', sa.String(n), nullable=False),
                      sa.Column('changed_at', sa.TIMESTAMP,
                                default=sa.func.current_timestamp(), nullable=False),
                      sa.Column('changed_by', sa.Integer,
                                sa.ForeignKey('local_managers.id')),
                      schema=schema)

async def create_table_categories(conn):
    await conn.execute(f'''CREATE TABLE IF NOT EXISTS categories (
                                        id serial PRIMARY KEY,
                                        name varchar({n}) not null,
                                        changed_at timestamp default current_timestamp,
                                        changed_by int references local_managers(id)
                                        )''')

restaurants = sa.Table('restaurants', metadata,
                       sa.Column('id', sa.Integer, primary_key=True),
                       sa.Column('name', sa.String(n), nullable=False),
                       schema=schema)

async def create_table_restaurants(conn):
    await conn.execute(f'''CREATE TABLE IF NOT EXISTS restaurants (
                                        id serial PRIMARY KEY,
                                        name varchar({n}) not null
                                        )''')

trees = sa.Table('trees', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('tree', sa.JSON, nullable=False),
                 sa.Column('changed_at', sa.TIMESTAMP,
                           default=sa.func.current_timestamp(), nullable=False),
                 sa.Column('changed_by', sa.Integer,
                           sa.ForeignKey('local_managers.id')),
                 schema=schema)

async def create_table_trees(conn):
    await conn.execute(f'''CREATE TABLE IF NOT EXISTS trees (
                                        id serial PRIMARY KEY,
                                        tree json not null,
                                        changed_at timestamp default current_timestamp,
                                        changed_by int references local_managers(id)
                                        )''')

orders = sa.Table('orders', metadata,
                  sa.Column('id', sa.Integer, primary_key=True),
                  sa.Column('manager', sa.Integer,
                            sa.ForeignKey('remote_managers.id')),
                  sa.Column('tree', sa.Integer,
                            sa.ForeignKey('trees.id')),
                  sa.Column('order_data', sa.JSON, nullable=False),
                  sa.Column('ordered_at', sa.TIMESTAMP, nullable=False),
                  schema=schema)

async def create_table_orders(conn):
    await conn.execute(f'''CREATE TABLE IF NOT EXISTS orders (
                                        id serial PRIMARY KEY,
                                        manager int references remote_managers(id),
                                        tree int references trees(id),
                                        order_data json not null,
                                        ordered_at timestamp not null
                                        )''')

dishes = sa.Table('dishes', metadata,
                  sa.Column('id', sa.Integer, primary_key=True),
                  #  sa.Column('init', sa.Integer),
                  #  sa.Column('previous', sa.Integer),
                  sa.Column('name', sa.String(n), nullable=False),
                  sa.Column('discription', sa.TEXT, nullable=False),
                  sa.Column('price', sa.Numeric(*acc), nullable=False),
                  sa.Column('category', sa.Integer,
                            sa.ForeignKey('categories.id')),
                  #  sa.Column('tree', sa.Integer,
                            #  sa.ForeignKey('trees.id')),
                  sa.Column('changed_at', sa.TIMESTAMP,
                            default=sa.func.current_timestamp(), nullable=False),
                  sa.Column('changed_by', sa.Integer,
                            sa.ForeignKey('local_managers.id')),
                  schema=schema)

async def create_table_dishes(conn):
    await conn.execute(f'''CREATE TABLE IF NOT EXISTS dishes (
                                        id serial PRIMARY KEY,
                                        name varchar({n}) not null,
                                        discription text not null,
                                        price numeric({acc[0]}, {acc[1]}) not null,
                                        category int references categories(id),
                                        changed_at timestamp default current_timestamp,
                                        changed_by int references local_managers(id)
                                        )''')

menu = sa.Table('menu', metadata,
                sa.Column('dish', sa.Integer,
                          sa.ForeignKey('dishes.id')),
                #  sa.Column('manager', sa.Integer,
                          #  sa.ForeignKey('local_managers.id')),
                #  sa.Column('tree', sa.Integer,
                          #  sa.ForeignKey('trees.id')),
                #  sa.Column('order_data', sa.JSON, nullable=False),
                schema=schema)

async def create_table_menu(conn):
    await conn.execute(f'''CREATE TABLE IF NOT EXISTS menu (
                                        dish int references dishes(id)
                                        )''')

