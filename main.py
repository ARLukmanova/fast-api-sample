
import fastapi
from fastapi import FastAPI, Query, Path,   HTTPException
from enum import Enum
from pydantic import BaseModel
import random
from typing import Optional
from typing import List


app = FastAPI()


class DogType(str, Enum):
    terrier = "terrier"
    bulldog = "bulldog"
    dalmatian = "dalmatian"


class Dog(BaseModel):
    name: str
    pk: int
    kind: DogType


class Timestamp(BaseModel):
    id: int
    timestamp: int


dogs_db = {
    0: Dog(name='Bob', pk=0, kind='terrier'),
    1: Dog(name='Marli', pk=1, kind="bulldog"),
    2: Dog(name='Snoopy', pk=2, kind='dalmatian'),
    3: Dog(name='Rex', pk=3, kind='dalmatian'),
    4: Dog(name='Pongo', pk=4, kind='dalmatian'),
    5: Dog(name='Tillman', pk=5, kind='bulldog'),
    6: Dog(name='Uga', pk=6, kind='bulldog')
}

post_db = [
    Timestamp(id=0, timestamp=12),
    Timestamp(id=1, timestamp=10)
]


@app.get("/")
def root():
    return {"You're welcome!"}

@app.post("/post")
def get_post() -> Timestamp:
    max_id = max(post_db, key=lambda x: x.id).id
    new_timestamp = Timestamp(id=max_id + 1, timestamp=random.randint(10,20))
    post_db.append(new_timestamp)
    return new_timestamp

@app.get("/dog")
def get_dogs(kind: str = Query(default=None, title = 'Breed name')) -> List[Dog]:
    if (kind is not None) and (kind not in DogType.__members__):
        raise HTTPException(
            status_code=422,
            detail={
                "items":
                    [{
                        "loc": [
                            {"kind": "Invalid value"}],
                            "msg": "Input should be " + ', '.join(DogType.__members__.keys()),
                        "type": "ValidationError"
                    }]})
    elif kind is not None and DogType.__members__:
        return [dog for dog in dogs_db.values() if dog.kind == kind]
    else:
        return dogs_db.values()

@app.post("/dog")
def create_dog(dog: Dog= fastapi.Body()) ->Dog:
    if dog.pk in list(dogs_db.keys()):
        raise HTTPException(status_code=409,
                            detail='The specified PK already exists.')
    elif dog.pk<0:
        raise HTTPException(status_code=422,
                            detail='The PK should  not be less than 0')
    dogs_db[dog.pk] = dog
    return dog

@app.get("/dog/{pk}")
def get_dog_by_pk(pk: int = Path(title="The PK of the dog to get", ge=0)) ->Dog:
    if pk in dogs_db:
        return dogs_db[pk]
    else:
        return {"message": "Dog is not found"}

@app.patch("/dog/{pk}")
def update_dog(dog: Dog = fastapi.Body(), pk: int = Path(title="The PK of the dog to update", ge=0)) ->Dog:
    if pk in dogs_db and pk == dog.pk:
        dogs_db[pk] = dog
        return dog
    elif pk!= dog.pk:
        raise HTTPException(status_code=422,
                            detail="The PK can't be changed.")
    else:
        return {"detail": "Dog is not found"}
