import asyncio
from typing import Dict
from abc import ABCMeta, abstractmethod
from aiopg.sa import create_engine
from datetime import datetime
import secrets
import hashlib

from .settings import settings
from .tables import (metadata, remote_managers, local_managers, restaurants,
                     users, tokens, orders, dishes, menu, categories, trees)

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

def hashpass(password, bsalt=None, dklen=dklen, salt_n=salt_n, iterations=10000):
    if salt is None:
        bsalt = secrets.token_hex(salt_n).encode()
    bpassword = password.encode()
    bhash = binascii.hexlify(
                hashlib.pbkdf2_hmac("sha256", bpass, bsalt,
                                    iterations, dklen=dklen))
    return bsalt, bhash

class Manager(metaclass=ABCMeta):
    @property
    def dsn(self):
        """ data source name """

        dsn = f'dbmane={dbname} user={dbuser} password={dbpassword} host={host} port={port}'

    @property
    @abstractmethod
    def user_table(self):
        """ table for users of current type """

        pass

    async def verify_credentials(self, login, password):
        """ verify login and password """

        async with create_engine(self.dsn) as engine:
            async with engine.acquire() as conn:
                join = sa.join(self.user_table, users, self.user_table.c.user == users.c.id)
                query = (users.select([self.user_table.c.id, users])
                         .select_from(join)
                         .where(users.c.login == login))
                async for uid, users in conn.execute(query):
                    test_hash = hashpass(password, row.salt)
                    if test_hash == row.password:
                        return uid

    async def get_token(self, uid):
        """ get session token by user id """

        token = hashtoken()
        values_dict = {'token': token, 'user': uid}
        tid = await self._insert(tokens, values_dict)
        if not tid:
            raise Exception("wrong token insertion")
        return token

    async def verify_token(self, token):
        """ verify session token """

        async with create_engine(self.dsn) as engine:
            async with engine.acquire() as conn:
                join = sa.join(self.user_table, tokens, self.user_table.c.id == tokens.c.user)
                query = (users.select([self.user_table.c.id, tokens])
                         .select_from(join)
                         .where(tokens.c.token == token))
                async for uid, token in conn.execute(query):
                    session_time = datetime.now() - token.c.inserted_at
                    if session_time.total_seconds() < token_time:
                        return uid

    async def _insert(self, table, values_dict):
        """ one value insertion to table """

        async with create_engine(self.dsn) as engine:
            async with engine.acquire() as conn:
                uid = await conn.scalar(table.insert().values(**values_dict))
                return uid

    async def create_all(self, metadata):
        """ one value insertion to table """

        async with create_engine(self.dsn) as engine:
            await metadata.create_all(engine)


class RemoteManager:
    """ local manager with administrative functions """

    @property
    def user_table(self):
        """ table for users of current type """

        return remote_managers

    async def verify_credentials(self, login, password, user_table=None):
        super().verify_credentials(self, login, password, user_table=remote_managers)


class LocalManager:
    """ local manager with administrative functions """

    @property
    def user_table(self):
        """ table for users of current type """

        return local_managers

    async def verify_credentials(self, login, password, user_table=None):
        super().verify_credentials(self, login, password, user_table=local_managers)

    async def add_local_manager(self,
                                name: str):
        """ add local administrative manager account """

        values_dict = {'name': name}
        return await self._insert(local_managers, values_dict)

    async def add_remote_manager(self,
                                 name: str):
        """ add remote restaurant manager account """

        values_dict = {'name': name}
        return await self._insert(remote_managers, values_dict)

    async def add_category(self,
                           name: str,
                           changed_by: int):
        """ add new category of dishes """

        values_dict = {'name': name, 'changed_by': changed_by}
        return await self._insert(categories, values_dict)

    async def add_tree(self,
                       tree: Dict[int, int],  # json dict
                       changed_by: int):
        """ add remote restaurant manager account """

        values_dict = {'tree': tree, 'changed_by': changed_by}
        return await self._insert(trees, values_dict)

    async def add_dish(self,
                       name: str,
                       discription: str,
                       price: float,
                       category: int,
                       tree: int,
                       changed_by: int
                       ):
        """ add new dish to dish collection """

        values_dict = {'name': name,
                       'discription': discription,
                       'price': price,
                       'category': category,
                       'tree': tree,
                       'changed_by': changed_by,
                       }
        return await self._insert(dishes, values_dict)

    async def go(self):
        manager = await self.add_local_manager('Alex')
        category = await self.add_category("Fruits", manager)
        tree = await self.add_tree({category: None}, manager)
        dish = await self.add_dish('Apple', 'Fresh apple.',
                                   1.0, category, tree, manager)
