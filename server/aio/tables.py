"""
Module with database tables declaration
Database: aio
Schema: aio
Tables: remote_managers, local_managers, restaurants,
        orders, dishes, menu, categories, trees
"""

import sqlalchemy as sa

from .settings import settings

metadata = sa.MetaData()
schema = settings["database"]["schema"]
n = settings["database"]["string_len"]  # postgres VARCHAR(n)
acc = settings["database"]["currencyacc"]  # postgres NUMERIC(precision, scale) for currency
#  schema = 'aio'
#  n = 100  # postgres VARCHAR(n)
#  acc = 10, 2  # postgres NUMERIC(precision, scale) for currency

users = sa.Table('users', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('login', sa.String(n), nullable=False),
                 sa.Column('login', sa.String(n), nullable=False),
                 schema=schema)

remote_managers = sa.Table('remote_managers', metadata,
                           sa.Column('id', sa.Integer, primary_key=True),
                           sa.Column('name', sa.String(n), nullable=False),
                           sa.Column('restaurant', None,
                                     sa.ForeignKey('restaurants.id')),
                           schema=schema)

local_managers = sa.Table('local_managers', metadata,
                          sa.Column('id', sa.Integer, primary_key=True),
                          sa.Column('name', sa.String(n), nullable=False),
                          schema=schema)

restaurants = sa.Table('restaurants', metadata,
                       sa.Column('id', sa.Integer, primary_key=True),
                       sa.Column('name', sa.String(n), nullable=False),
                       schema=schema)

orders = sa.Table('orders', metadata,
                  sa.Column('id', sa.Integer, primary_key=True),
                  sa.Column('manager', None,
                            sa.ForeignKey('remote_managers.id')),
                  sa.Column('tree', None,
                            sa.ForeignKey('trees.id')),
                  sa.Column('order', sa.JSON, nullable=False),
                  schema=schema)

dishes = sa.Table('dishes', metadata,
                  sa.Column('id', sa.Integer, primary_key=True),
                  sa.Column('init', sa.Integer),
                  sa.Column('previous', sa.Integer),
                  sa.Column('name', sa.String(n), nullable=False),
                  sa.Column('discription', sa.TEXT, nullable=False),
                  sa.Column('price', sa.Numeric(*acc), nullable=False),
                  sa.Column('category', None,
                            sa.ForeignKey('categories.id')),
                  sa.Column('tree', None,
                            sa.ForeignKey('trees.id')),
                  sa.Column('changed_at', sa.TIMESTAMP, nullable=False),
                  sa.Column('changed_by', None,
                            sa.ForeignKey('local_managers.id')),
                  schema=schema)

menu = sa.Table('menu', metadata,
                sa.Column('dish', None,
                          sa.ForeignKey('dishes.id')),
                sa.Column('manager', None,
                          sa.ForeignKey('local_managers.id')),
                sa.Column('tree', None,
                          sa.ForeignKey('trees.id')),
                sa.Column('order', sa.JSON, nullable=False),
                schema=schema)

categories = sa.Table('categories', metadata,
                      sa.Column('id', sa.Integer, primary_key=True),
                      sa.Column('name', sa.String(n), nullable=False),
                      sa.Column('changed_at', sa.TIMESTAMP, nullable=False),
                      sa.Column('changed_by', None,
                                sa.ForeignKey('local_managers.id')),
                      schema=schema)

trees = sa.Table('trees', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('tree', sa.JSON, nullable=False),
                 sa.Column('changed_at', sa.TIMESTAMP, nullable=False),
                 sa.Column('changed_by', None,
                           sa.ForeignKey('local_managers.id')),
                 schema=schema)
