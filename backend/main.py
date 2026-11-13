from datetime import datetime
from fastapi import FastAPI, HTTPException, Header,Body
from pydantic import BaseModel
import functions    

app = FastAPI()

class PackageCreate(BaseModel):
    name: str
    destination: str
    weight: float
    arrival_date: datetime
    status: str = "pending"
    
class PackageUpdate(BaseModel):
    name: str | None = None
    destination: str | None = None
    weight: float | None = None
    arrival_date: datetime | None = None
    status: str | None = None

class DispatchCreate(BaseModel):
    destination: str
    vehicle_number: str
    dispatch_date: datetime
    package_ids: list[int]

@app.post("/packages")
def register_package(data: PackageCreate,token = Header(None)):
    username=functions.verify_token(token=token,token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    result = functions.register_package(
        name=data.name,
        destination=data.destination,
        weight=data.weight,
        arrival_date=data.arrival_date,
        status=data.status
    )
    return result

@app.get("/packages/{id}")
def get_package(id: int,token = Header(None)):
    username=functions.verify_token(token=token,token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    result = functions.get_one_package(id=id)
    return result

@app.patch("/packages/{id}")
def update_package(id: int, data: PackageUpdate, token=Header(None)):
    username = functions.verify_token(token=token, token_type="access")

    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = functions.update_package(
        id=id,
        name=data.name,
        destination=data.destination,
        weight=data.weight,
        arrival_date=data.arrival_date,
        status=data.status
    )

    return result

@app.delete("/packages/{id}")
def delete_package(id: int,token = Header(None)):
    username=functions.verify_token(token=token,token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    result = functions.delete_package(id=id)
    return result

@app.get("/packages")
def search_packages(destination: str = None, status: str = None, arrival_date: str = None, token = Header(None)):
    username=functions.verify_token(token=token,token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    result = functions.get_all_packages(destination, status, arrival_date)
    return result

@app.get("/dispatch_batches")
def get_dispatch_batches(destination: str = None, vehicle_number: str = None, status: str = None,token = Header(None)):
    username=functions.verify_token(token=token,token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    result = functions.get_all_dispatches(destination, vehicle_number, status)
    return result

@app.get("/packages/status")
def get_statistics(token = Header(None)):
    username=functions.verify_token(token=token,token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    result = functions.get_summary()
    return result

@app.post("/dispatch_batches")
def create_dispatch_batch(data: DispatchCreate, token=Header(None)):
    username = functions.verify_token(token=token, token_type="access")

    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = functions.add_dispatch(
        vehicle_number=data.vehicle_number,
        destination=data.destination,
        dispatch_date=data.dispatch_date
    )

    return result

@app.post("/login")
def login(username= Body(), password= Body()):
    token = functions.verify_login(username=username, password=password)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return token

@app.post("/refresh")
def refresh_token(refresh_token=Header(None)):
    username=functions.verify_token(token=refresh_token, token_type="refresh")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    access_token = functions.create_token(username=username, token_type="access")
    return {"access_token": access_token}

@app.post("/register")
def register_user(user_name= Body(), password=Body()):
    if functions.register_user(user_name=user_name,password=password):
        return{"message":"user registered successfully"}
    raise HTTPException(status_code=400, detail="user already exists")