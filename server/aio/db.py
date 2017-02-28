import asyncio
from typing import Dict
from abc import ABCMeta, abstractmethod
from aiopg.sa import create_engine
import secrets
import hashlib

from .settings import settings
from .tables import (metadata, remote_managers, local_managers, restaurants,
                     orders, dishes, menu, categories, trees)

dbname = settings["database"]["dbname"]
host = settings["database"]["host"]
port = settings["database"]["port"] # 1235

dbuser = os.environ["DBUSER"]
dbpassword = os.environ["DBPASSWORD"]

def hashpass(password, bsalt=None):
    if salt is None:
        bsalt = secrets.token_hex(32).encode()
    bpassword = password.encode()
    bhash = binascii.hexlify(hashlib.pbkdf2_hmac("sha256", bpass, bsalt, 10000))
    return bsalt, bhash

class Manager(metaclass=ABCMeta):
    @property
    def dsn(self):
        """ data source name """
        dsn = f'dbmane={dbname} user={dbuser} password={dbpassword} host={host} port={port}'

    @classmethod
    @abstractmethod
    async def verify(self, login, password):
        """ verify login and password """
        pass

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
    pass


class LocalManager:
    """ local manager with administrative functions """

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
