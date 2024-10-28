from typing import Tuple, Optional
from app import db


class BaseService:
    """
    基礎服務類
    提供共用的資料庫操作方法
    """

    @staticmethod
    def commit() -> Tuple[bool, Optional[str]]:
        """
        提交資料庫變更

        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 錯誤訊息)
        """
        try:
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def save_to_db(model: db.Model) -> Tuple[bool, Optional[str]]:
        """
        保存模型實例到資料庫

        Args:
            model: 資料庫模型實例

        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 錯誤訊息)
        """
        try:
            db.session.add(model)
            return BaseService.commit()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete_from_db(model: db.Model) -> Tuple[bool, Optional[str]]:
        """
        從資料庫刪除模型實例

        Args:
            model: 資料庫模型實例

        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 錯誤訊息)
        """
        try:
            db.session.delete(model)
            return BaseService.commit()
        except Exception as e:
            return False, str(e)
