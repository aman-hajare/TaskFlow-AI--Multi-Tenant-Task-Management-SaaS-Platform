from app.models.invite import Invite
from app.core.enums import InviteStatusEnum

class InviteRepository:

    @staticmethod
    def create_invite(db, invite_data):
        invite = Invite(**invite_data)

        db.add(invite)
        db.commit()
        db.refresh(invite)

        return invite

    @staticmethod
    def get_by_token(db, token):
        return db.query(Invite).filter(Invite.token == token).first()

    @staticmethod
    def update(db, invite):
        db.commit()
        db.refresh(invite)
        return invite