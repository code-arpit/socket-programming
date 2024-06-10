import uuid
from typing import Any, Dict, List, TypeVar

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from database import Base

ModelType = TypeVar("ModelType", bound=Base)


async def get(db: Session, id: uuid.UUID, model: ModelType) -> ModelType:
    query = db.query(model).where(model.id == id).first()
    return query


async def get_all(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    model: ModelType,
) -> List[ModelType]:
    return db.query(model).offset(skip).limit(limit).all()


async def create(
    db: Session,
    obj_in: Dict,
    model: ModelType,
) -> ModelType:
    obj_in_data = jsonable_encoder(
        obj_in,
        exclude_unset=True,
        exclude_none=True,
    )
    db_obj = model(
        **obj_in_data,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


async def update(
    db: Session,
    db_obj: ModelType,
    obj_in: Dict[str, Any],
) -> ModelType:
    obj_data = jsonable_encoder(
        db_obj,
    )
    if isinstance(
        obj_in,
        dict,
    ):
        update_data = obj_in
    else:
        update_data = obj_in.dict(
            exclude_unset=True,
        )
    for field in obj_data:
        if field in update_data:
            setattr(
                db_obj,
                field,
                update_data[field],
            )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


async def remove(
    db: Session,
    id: uuid.UUID,
    model: ModelType,
) -> ModelType:
    obj = db.query(model).where(model.id == id).first()
    db.delete(obj)
    db.commit()
    return obj
