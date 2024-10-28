from app import db


class BaseService:
    @staticmethod
    def commit():
        try:
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
