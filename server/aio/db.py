import asyncio
import aiopg
import os
import binascii
from typing import Dict
from abc import ABCMeta, abstractmethod
from aiopg.sa import create_engine
import sqlalchemy as sa

from datetime import datetime
import secrets
import hashlib

from .settings import settings
from .tables import (metadata, remote_managers, local_managers, categories, restaurants,
                     users, tokens, trees, orders, dishes, menu,
                     create_table_remote_managers, create_table_local_managers,
                     create_table_categories, create_table_restaurants,
                     create_table_users, create_table_tokens, create_table_trees,
                     create_table_orders, create_table_dishes, create_table_menu)

create_tables = (create_table_users, create_table_tokens,
                 create_table_remote_managers, create_table_local_managers,
                 create_table_categories, create_table_restaurants, create_table_trees, create_table_orders,
                 create_table_dishes, create_table_menu)

db = settings["database"]
dbname = db["dbname"]
host = db["host"]
port = db["port"]
dklen = db["hash_len"] // 2
token_n = db["token_len"] // 2
salt_n = db["salt_len"] // 2
token_time = db["token_time"]

dbuser = os.environ["DBUSER"]
dbpassword = os.environ["DBPASSWORD"]

def hashtoken(token_n=token_n):
    btoken = secrets.token_hex(token_n).encode()
    return btoken

def hashpass(password, salt=None, dklen=dklen, salt_n=salt_n, iterations=10000):
    try:
        if salt is None:
            salt = secrets.token_hex(salt_n).encode()
        else:
            salt = salt.encode()
        bpassword = password.encode()
        bhash = binascii.hexlify(
                    hashlib.pbkdf2_hmac("sha256", bpassword, salt,
                                        iterations, dklen=dklen))
    except Exception as err:
        print(err)
    return salt, bhash

class Manager(metaclass=ABCMeta):
    @property
    def dsn(self):
        """ data source name """

        return  f'dbname={dbname} user={dbuser} password={dbpassword} host={host} port={port}'

    @property
    @abstractmethod
    def user_table(self):
        """ table for users of current type """

        pass

    @property
    @abstractmethod
    def manager_type(self):
        pass

    async def verify_credentials(self, login, password):
        """ verify login and password """

        try:
            async with aiopg.create_pool(self.dsn) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        query = f"""
                SELECT id, password, salt
                FROM aio.users
                WHERE aio.users.login = '{login}'"""
                        await cur.execute(query)
                        async for user_id, user_password, user_salt in cur:
                            _, test_hash = hashpass(password, user_salt)
                            if test_hash.decode() == user_password:
                                return user_id
        except Exception as err:
            print(err)
            raise HTTPForbidden()

    async def verify_token(self, token):
        """ verify session token """
        try:
            async with aiopg.create_pool(self.dsn) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        query = f"""
                SELECT aio.{self.manager_type}.id
                FROM aio.tokens JOIN aio.users ON aio.tokens.user_id = aio.users.id
                JOIN aio.{self.manager_type} ON aio.{self.manager_type}.user_id = aio.users.id
                WHERE aio.tokens.token = '{token}'"""
                        await cur.execute(query)
                        async for row in cur:
                            return row[0]
        except Exception as err:
            print(err)
            raise HTTPForbidden()

    async def create_token(self, uid):
        """ get session token by user id """
        try:
            token = hashtoken().decode()
            async with aiopg.create_pool(self.dsn) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        query = f"""
                INSERT INTO aio.tokens (token, user_id)
                VALUES ('{token}', '{uid}') """
                        await cur.execute(query)
                        return token
        except Exception as err:
            print(err)
            raise HTTPForbidden()

    async def _insert(self, table, values_dict):
        """ one value insertion to table """

        async with create_engine(self.dsn) as engine:
            async with engine.acquire() as conn:
                uid = None
                try:
                    uid = await conn.scalar(table.insert().values(**values_dict))
                except Exception as err:
                    print(err)
                return uid

    async def create_all(self):
        """ one value insertion to table """

        async with create_engine(self.dsn) as engine:
            async with engine.acquire() as conn:
                for create_table in create_tables:
                    await create_table(conn)


class RemoteManager(Manager):
    """ local manager with administrative functions """

    @property
    def user_table(self):
        """ table for users of current type """

        return remote_managers

    @property
    def manager_type(self):
        return "remote_managers"

    async def get_menu(self):
        """ fetch all dishes from menu and the most actual tree id """

        async with create_engine(self.dsn) as engine:
            async with engine.acquire() as conn:
                join = sa.join(dishes, menu, dishes.c.id == menu.c.dish)
                query = (sa.select([dishes]).select_from(join))
                dishes_ids = await conn.execute(query).fetchall()
                query = (sa.select([trees.c.id]).order_by(trees.c.id))
                tree_id = await conn.execute(query).first()
                return dishes_ids, tree_id

    async def store_order(self, uid, tree_id, order, ordered_at):
        """ store remote order """

        try:
            async with aiopg.create_pool(self.dsn) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        query = f"""
                INSERT INTO aio.orders(manager, tree, order_data, ordered_at)
                VALUES ('{uid}', '{tree_id}', '{order_data}', '{ordered_at}') """
                        return await cur.scalar(query)
        except Exception as err:
            print(err)
            raise HTTPForbidden()


class LocalManager(Manager):
    """ local manager with administrative functions """

    @property
    def user_table(self):
        """ table for users of current type """

        return local_managers

    @property
    def manager_type(self):
        return "local_managers"

    async def create_user(self, user_table, login, password, **user_data):
        """ create new users """

        salt, hashed_pass = hashpass(password)
        user_dict = {'login': login, 'salt': salt.decode(), 'password': hashed_pass.decode()}
        async with create_engine(self.dsn) as engine:
            async with engine.acquire() as conn:
                trans = await conn.begin()
                query = users.insert().values(**user_dict)
                uid = await conn.scalar(query)
                if not uid:
                    await trans.rollback()
                else:
                    user_table_dict = {'user_id': uid, **user_data}
                    query = user_table.insert().values(**user_table_dict)
                    uid = await conn.scalar(query)
                    if not uid:
                        await trans.rollback()
                    else:
                        await trans.commit()
                        return uid

    async def create_local_user(self, login, password, **user_data):
        """ create new local users """

        return await self.create_user(local_managers, login, password, **user_data)

    async def create_remote_user(self, login, password, **user_data):
        """ create new remote users """

        return await self.create_user(remote_managers, login, password, **user_data)


    async def add_category(self,
                           name: str,
                           changed_by: int):
        """ add new category of dishes """

        values_dict = {'name': name,
                       'changed_by': changed_by}
        return await self._insert(categories, values_dict)

    async def add_tree(self,
                       tree: Dict[int, int],  # json dict
                       changed_by: int):
        """ add tree of categories """

        values_dict = {'tree': tree,
                       'changed_by': changed_by}
        return await self._insert(trees, values_dict)

    async def add_dish_to_menu(self, dish):
        """ add dish to menu """

        values_dict = {'dish': dish}
        async with create_engine(self.dsn) as engine:
            async with engine.acquire() as conn:
                await conn.execute(menu.insert().values(**values_dict))

    async def add_dish(self,
                       name: str,
                       discription: str,
                       price: float,
                       category: int,
                       #  tree: int,
                       changed_by: int
                       ):
        """ add new dish to dish collection """

        values_dict = {'name': name,
                       'discription': discription,
                       'price': price,
                       'category': category,
                       #  'tree': tree,
                       'changed_by': changed_by,
                       }
        return await self._insert(dishes, values_dict)

    async def get_last_orders(self, n):
        """ get list of last orders """

        async with create_engine(self.dsn) as engine:
            async with engine.acquire() as conn:
                query = (sa.select([orders]).order_by(orders.c.ordered_at))
                orders_list = await conn.execute(query).fetchmany(n)
                return orders_list

    async def get_starter_pack(self):
        """ initial database data """

        admin = await self.create_local_user('admin', 'admin', name='Admin')
        admin_token = await self.create_token(admin)
        guest = await self.create_remote_user('guest', 'guest', name='Guest')
        guest_token = await self.create_token(guest)

        tea = await self.add_category("Tea", admin)
        white_tea = await self.add_category("White", admin)
        green_tea = await self.add_category("Green", admin)
        tree = await self.add_tree({tea: {white_tea: None, green_tea: None}}, admin)

        async def init_dish(name, category):
                dish_id = await self.add_dish(name, name, 1.0, category, admin)
                return await self.add_dish_to_menu(dish_id)

        green_tea_tasks = [init_dish(f"green_{i}", green_tea) for i in range(10)]
        white_tea_tasks = [init_dish(f"white_{i}", white_tea) for i in range(10)]
        dish_tasks = green_tea_tasks + white_tea_tasks
        await asyncio.wait(dish_tasks)
