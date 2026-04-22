from fastapi import APIRouter, WebSocket
from app.core.database import SessionLocal
from app.core.enums import RoleEnum
from app.models.user import User
from app.websocket.manager import manager

router = APIRouter()
   
@router.websocket("/ws/notifications/{user_id}/{company_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, company_id: int):

    db = SessionLocal()
    try:
        user = db.query(User.id, User.role).filter(User.id == user_id).first()
        is_super_admin = bool(user and user.role == RoleEnum.super_admin)
    finally:
        db.close()

    await manager.connect(
        user_id=user_id,
        company_id=company_id,
        websocket=websocket,
        is_super_admin=is_super_admin,
    )

    try:
        while True:
            await websocket.receive_text()
    except:
        manager.disconnect(user_id, websocket)