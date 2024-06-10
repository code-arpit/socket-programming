from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    HTTPException,
    Header,
)
import asyncio
from fastapi.responses import HTMLResponse
from connection import connection_manager
import uuid
from settings import settings
import models
from database import get_db, engine
from contextlib import asynccontextmanager
from validators import *
from web_chat import web_chat_html
from sqlalchemy.orm import Session
import services
import json
from fastapi_pagination import Page, add_pagination, paginate
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination.utils import disable_installed_extensions_check
from auth import JWTBearer, get_current_user, decode_jwt
from datetime import datetime

disable_installed_extensions_check()


@asynccontextmanager
async def lifespan(application: FastAPI):
    yield models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
)

origins = [
    "*",
    "localhost",
    "127.0.0.1",
    "https://xdr.zerohack.in/",
    "https://dev-xdr.zerohack.in",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def get_client():
    return HTMLResponse(web_chat_html)


@app.get("/root/")
async def get_root_client():
    html_response = (
        web_chat_html.replace(
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzEyNTcyMTk4LCJpYXQiOjE3MTI1NjQ5OTgsImp0aSI6ImQxMGJlM2Q1YWE4MjQ4ODJiZDNjNzk0NWJlMDgzYjc2IiwidXNlcl9pZCI6IjgwYzJkYTcxLWQwNzUtNGNkZS1iNzgxLThlNWI3NmU3NzIzNyJ9.hI3CvOKHeuATu6rO9kZFSvppM_102pA5sn_4kLP81Mg",
            "root/",
        )
        .replace("User: root/", "User: ROOT")
        .replace("b62b3790-7601-4acb-8f43-6e2dda389fee", "ROOT")
    )
    return HTMLResponse(html_response)


@app.websocket(
    "/ws/{token}",
)
async def websocket_endpoint(
    connection: WebSocket,
    token: str,
    db: Session = Depends(get_db),
):
    try:
        decoded = await decode_jwt(token.replace("Bearer ", ""))
        client_id = uuid.UUID(decoded["user_id"])
    except Exception as e:
        raise HTTPException(status_code=400, detail="Not authenticated.")
    client_port = str(connection.scope.get("client")[1])

    await connection_manager.connect(
        websocket=connection,
        client_id=str(client_id),
        client_port=client_port,
    )

    try:
        while True:
            data = await asyncio.wait_for(connection_manager.receive(connection), timeout=600)
            json_data = json.loads(data)
            conversation_db_obj = None
            conversation_id = json_data.get("conversation_id", None)
            message = json_data.get("message", None)

            if conversation_id:
                conversation_db_obj = await services.get(
                    db=db,
                    id=conversation_id,
                    model=models.Conversation,
                )
            else:
                conversation_obj = ConversationRequestModel(
                    user_id=client_id, title=message, started_on=datetime.now()
                )
                conversation_db_obj = await services.create(
                    db=db,
                    obj_in=conversation_obj.model_dump(),
                    model=models.Conversation,
                )
                conversation_id = conversation_db_obj.id

            if conversation_db_obj:
                await connection_manager.update_connection(
                    client_id=str(client_id),
                    conversation_id=str(conversation_db_obj.id),
                    client_port=client_port,
                )

                message_obj = MessageRequestModel(
                    conversation_id=conversation_db_obj.id,
                    question=message,
                    question_time=datetime.now(),
                )
                message_db_obj = await services.create(
                    db=db,
                    obj_in=message_obj.model_dump(),
                    model=models.Message,
                )

            try:
                await connection_manager.send_root(
                    data={
                        "message": message,
                        "conversation_id": str(conversation_db_obj.id),
                        "message_id": str(message_db_obj.id),
                        "client_id": str(client_id),
                        "client_port": client_port,
                        "time": int(datetime.now().timestamp() * 1000),
                        "sender": "CLIENT",
                    },
                )
            except Exception:
                message = "Root Connection Not Established! Please Try Again Later."

            await connection_manager.send_personal_json(
                client_id=str(client_id),
                conversation_id=str(conversation_id),
                client_port=client_port,
                data={
                    "message": message,
                    "conversation_id": str(conversation_db_obj.id),
                    "message_id": str(message_db_obj.id),
                    "client_id": str(client_id),
                    "client_port": client_port,
                    "time": int(datetime.now().timestamp() * 1000),
                    "sender": "CLIENT",
                },
                websocket=connection,
            )
    # except Exception as e:
    #     raise e
    except WebSocketDisconnect as e:
        print("----------------------------Closing Client----------------------")
        await connection_manager.disconnect(
            connection,
        )
    
    except asyncio.TimeoutError:
        print("Timeout while waiting for data")
        await connection_manager.disconnect(
            connection,
        )


@app.websocket(
    "/ws/root/",
)
async def websocket_endpoint_root(
    connection: WebSocket,
):
    await connection_manager.connect(connection, type="root")
    if connection_manager.root_connection:
       await connection_manager.send_root(
           data={
               "message": "You are now connected as a root user.",
           },
       )
    try:
        while True:
            data = await connection_manager.receive_root()
            print(data, "-------------RECEIVE ROOT 1--------------------")
            json_data = json.loads(data)
            if json_data.get("message") == "PING":
                continue
            conversation_id = json_data.get("conversation_id", None)
            message = json_data.get("message", None)
            message_id = json_data.get("message_id", None)
            client_id = json_data.get("client_id", None)
            client_port = json_data.get("client_port", None)
            status = json_data.get("status", "FAILED")

            await connection_manager.send_personal_json(
                client_id=str(client_id),
                conversation_id=str(conversation_id),
                client_port=client_port,
                status=status,
                data={
                    "message": message,
                    "conversation_id": str(conversation_id),
                    "message_id": message_id,
                    "client_id": str(client_id),
                    "client_port": client_port,
                    "time": int(datetime.now().timestamp() * 1000),
                    "sender": "AI",
                },
                websocket=connection,
            )

    except WebSocketDisconnect:
        print("----------------------------Closing Root----------------------")
        await connection_manager.disconnect(connection)


@app.get(
    "/conversation",
    response_model=Page[ConversationResponseModel],
    dependencies=[
        Depends(JWTBearer()),
    ],
)
async def get_conversation(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation_query = db.query(models.Conversation)
    if user_id:
        conversation_query = conversation_query.filter(
            models.Conversation.user_id == user_id,
            models.Conversation.is_deleted == False
        )
    conversation_objs = conversation_query.order_by(
        models.Conversation.started_on.desc()
    ).all()
    return paginate(conversation_objs)


@app.get(
    "/message",
    response_model=Page[MessageResponseModel],
    dependencies=[
        Depends(JWTBearer()),
    ],
)
async def get_message(
    conversation_id: uuid.UUID | None = None,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation_query = (
        db.query(models.Conversation.id)
        .filter(models.Conversation.user_id == user_id)
        .order_by(models.Conversation.started_on.desc())
        .all()
    )
    conversation_ids = []
    if conversation_query:
        conversation_ids = [id[0] for id in conversation_query]

    if conversation_id not in conversation_ids:
        raise HTTPException(
            status_code=404,
            detail="Conversation not Found for the current user.",
        )

    if conversation_ids:
        message_objs = (
            db.query(models.Message)
            .filter(models.Message.conversation_id == conversation_id)
            .order_by(models.Message.question_time.asc())
            .all()
        )
    return paginate(message_objs)


@app.patch(
    "/conversation/{conversation_id}",
    response_model=ConversationResponseModel,
    dependencies=[
        Depends(JWTBearer()),
    ],
)
async def soft_delete_conversation(
    conversation_id: uuid.UUID | None = None,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation_query = (
        db.query(models.Conversation.id)
        .filter(models.Conversation.user_id == user_id)
        .order_by(models.Conversation.started_on.desc())
        .all()
    )
    conversation_ids = []
    if conversation_query:
        conversation_ids = [id[0] for id in conversation_query]

    if conversation_id not in conversation_ids:
        raise HTTPException(
            status_code=404,
            detail="Conversation not Found for the current user.",
        )

    conversation_obj = await services.get(
        db=db,
        id=conversation_id,
        model=models.Conversation
    )
    
    if conversation_obj:
        try:
            delete_conversation = await services.update(
                db=db,
                db_obj=conversation_obj,
                obj_in={
                    "is_deleted": True,
                },
            )
            return delete_conversation
        
        except Exception:
            raise HTTPException(
                status_code=404,
                detail="Conversation Not Found. Failed to Delete."
            ) 


add_pagination(app)