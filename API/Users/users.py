from datetime import timedelta 
import datetime
import sys 
sys.path.append(r"../")


from fastapi import APIRouter , HTTPException , status , Depends
from fastapi.security import OAuth2PasswordRequestForm , OAuth2PasswordBearer
from . import users_schemas as US
router = APIRouter(prefix="/user" , tags=["users"]) 
import database as db
from passlib.context import  CryptContext
import jwt  
from jose import jwt , JWTError
from typing import Annotated

import pytz
utc= pytz.UTC


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")


def getuser(email:str) : 
    db.cur.execute("SELECT * FROM visiteur WHERE email = %s" , (email,))
    res = dict(db.cur.fetchone())
    return US.signup(**res)




def hash(plain_password): 
    return pwd_context.hash(plain_password) 

def verify(plain_password , hash_password) : 
    return pwd_context.verify(plain_password , hash_password)

def auhtenticate(user : OAuth2PasswordRequestForm) : 
    real_user = getuser(user.username) 
    if not real_user: 
        return False 
    if not verify(user.password , real_user.password ): 
        return False 
    return  real_user 

def create_access_token(data : dict , expires_delta : timedelta) : 
    to_encode = data.copy()
    if expires_delta : 
        expire = datetime.datetime.utcnow() + expires_delta 
    else : 
        expire= datetime.datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp" : expire})
    encoded_jwt = jwt.encode(to_encode , SECRET_KEY , ALGORITHM)
    return encoded_jwt

def current_user(token :str = Depends(oauth2_scheme)): 
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try : 
        payload = jwt.decode(token , SECRET_KEY , algorithms=[ALGORITHM]) 
        email = payload.get("sub")
        if not email : 
            raise credentials_exception 
    except JWTError : 
        raise credentials_exception
    ret = US.tokenReturn(email=email , expire=payload.get("exp"))
    return ret

    

def current_active_user(current_user = Annotated[US.tokenReturn ,Depends(current_user) ]) : 
    print(current_user.expire)

#signup
@router.post("/signup")
def signup(user :US.signup ) : 
    db.cur.execute("SELECT * FROM visiteur WHERE email = %s" , (user.email,))
    if db.cur.fetchone() : 
        return {"erorr" : "email in use "}
    db.cur.execute("""INSERT INTO visiteur(email , password , nom , adresse , nbcarte ) values
    (%s , %s , %s , %s , %s )""" , (user.email , hash(user.password) , user.nom , user.adresse , user.nbcarte))
    db.commit()
    return HTTPException(status_code= status.HTTP_201_CREATED)

#signin 
@router.post("/signin")
def signin(user: Annotated[OAuth2PasswordRequestForm, Depends()]) : 
    db_user = auhtenticate(user)
    if not user : 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"sub" : db_user.email}
    access_token = create_access_token(data , access_token_expires)
    return {"token" : access_token , "type" : "bearer"}


@router.get("/me")
def me(token = Depends(current_user)) : 
    print(token.expire> utc.localize(datetime.datetime.utcnow()) )
    return token

print(datetime.datetime.utcnow()+timedelta(minutes=15) > datetime.datetime.utcnow())