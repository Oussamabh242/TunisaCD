from pydantic import BaseModel
from typing import Union
import datetime

class signup(BaseModel) : 
    email : str 
    password : str 
    nom: str 
    adresse : str 
    nbcarte : Union[int , None] = 0

class signin(BaseModel) : 
    email : str 
    password : str

class tokenReturn(BaseModel): 
    email : str 
    expire : datetime.datetime