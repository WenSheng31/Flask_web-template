import re
from typing import Tuple


class PasswordValidator:
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        驗證密碼強度
        規則：
        - 至少8個字符
        - 至少包含一個英文字母
        """
        if len(password) < 8:
            return False, "密碼長度必須至少8個字符"

        if not re.search(r"[a-zA-Z]", password):
            return False, "密碼必須包含至少一個英文字母"

        return True, "密碼符合要求"
