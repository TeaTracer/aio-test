"""
Module with database tables declaration
Database: aio
Schema: aio
Tables: remote_managers, local_managers, restaurants,
        orders, dishes, menu, categories, trees
"""

import sqlalchemy as sa

_metadata = sa.MetaData()
_schema = 'aio'
_n = 100  # postgres VARCHAR(_n)
_acc = 10, 2  # postgres NUMERIC(precision, scale) for currency

remote_managers = sa.Table('remote_managers', _metadata,
                           sa.Column('id', sa.Integer, primary_key=True),
                           sa.Column('name', sa.String(_n), nullable=False),
                           sa.Column('restaurant', None,
                                     sa.ForeignKey('restaurants.id')),
                           schema=_schema)

local_managers = sa.Table('local_managers', _metadata,
                          sa.Column('id', sa.Integer, primary_key=True),
                          sa.Column('name', sa.String(_n), nullable=False),
                          schema=_schema)

restaurants = sa.Table('restaurants', _metadata,
                       sa.Column('id', sa.Integer, primary_key=True),
                       sa.Column('name', sa.String(_n), nullable=False),
                       schema=_schema)

orders = sa.Table('orders', _metadata,
                  sa.Column('id', sa.Integer, primary_key=True),
                  sa.Column('manager', None,
                            sa.ForeignKey('remote_managers.id')),
                  sa.Column('tree', None,
                            sa.ForeignKey('trees.id')),
                  sa.Column('order', sa.JSON, nullable=False),
                  schema=_schema)

dishes = sa.Table('dishes', _metadata,
                  sa.Column('id', sa.Integer, primary_key=True),
                  sa.Column('init', sa.Integer),
                  sa.Column('previous', sa.Integer),
                  sa.Column('name', sa.String(_n), nullable=False),
                  sa.Column('discription', sa.TEXT, nullable=False),
                  sa.Column('price', sa.Numeric(*_acc), nullable=False),
                  sa.Column('category', None,
                            sa.ForeignKey('categories.id')),
                  sa.Column('tree', None,
                            sa.ForeignKey('trees.id')),
                  sa.Column('changed_at', sa.TIMESTAMP, nullable=False),
                  sa.Column('changed_by', None,
                            sa.ForeignKey('local_managers.id')),
                  schema=_schema)

menu = sa.Table('menu', _metadata,
                sa.Column('dish', None,
                          sa.ForeignKey('dishes.id')),
                sa.Column('manager', None,
                          sa.ForeignKey('local_managers.id')),
                sa.Column('tree', None,
                          sa.ForeignKey('trees.id')),
                sa.Column('order', sa.JSON, nullable=False),
                schema=_schema)

categories = sa.Table('categories', _metadata,
                      sa.Column('id', sa.Integer, primary_key=True),
                      sa.Column('name', sa.String(_n), nullable=False),
                      sa.Column('changed_at', sa.TIMESTAMP, nullable=False),
                      sa.Column('changed_by', None,
                                sa.ForeignKey('local_managers.id')),
                      schema=_schema)

trees = sa.Table('trees', _metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('tree', sa.JSON, nullable=False),
                 sa.Column('changed_at', sa.TIMESTAMP, nullable=False),
                 sa.Column('changed_by', None,
                           sa.ForeignKey('local_managers.id')),
                 schema=_schema)
