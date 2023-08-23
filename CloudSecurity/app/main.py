"""
This is a simple app for showing and updating items in a web page.
"""

from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    """
    Item class

    Represents an item for sale
    """
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    """
    The function `read_root()` returns a dictionary with the key "Hello" and the value "World".

    :return: A dictionary with the key "Hello" and the value "World" is being returned.
    """
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, info: Union[str, None] = None):
    """
    The function `read_item` takes an item ID and an optional info parameter and returns a 
    dictionary with the item ID and info.

    :param item_id: An integer representing the ID of the item
    :type item_id: int

    :param info: The `info` parameter is an optional parameter that can accept a value of type `str`
    or `None`. If a value is provided for `info`, it will be stored in the returned dictionary with
    the key "info". If no value is provided, the value of "info" in the
    :type info: Union[str, None]

    :return: A dictionary with the keys "item_id" and "info" is being returned. The value of
    "item_id" is the input item_id, and the value of "info" is the input info.
    """
    return {"item_id": item_id, "info": info}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    """
    The function `update_item` takes an item ID and an item object, and returns a dictionary with
    the item name and ID.

    :param item_id: An integer representing the ID of the item to be updated
    :type item_id: int

    :param item: The "item" parameter is an instance of the "Item" class
    :type item: Item

    :return: A dictionary containing the updated item name and item ID.
    """
    return {"item_name": item.name, "item_id": item_id}
