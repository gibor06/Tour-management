from __future__ import annotations

from dataclasses import dataclass

from core.activity_log import write_activity_log
from core.security import password_matches, prepare_password_for_storage
from core.validation import (
    is_valid_fullname,
    is_valid_password,
    is_valid_phone,
    is_valid_username,
    normalize_fullname,
    normalize_phone,
    normalize_username,
)


@dataclass(slots=True)
class ServiceResult:
    success: bool
    message: str
    level: str = "info"
    username: str = ""
    display_name: str = ""
    role: str = ""


class AuthService:
    def __init__(self, datastore):
        self.datastore = datastore

    def authenticate(self, role: str, username: str, password: str) -> ServiceResult:
        normalized_username = normalize_username(username)

        if not normalized_username or not str(password or "").strip():
            return ServiceResult(False, "Vui lòng nhập tài khoản và mật khẩu.", level="warning")

        self.datastore.load()
        record = self._resolve_account(role, normalized_username)

        if not record:
            write_activity_log(
                action="LOGIN",
                actor=normalized_username,
                role=role,
                status="FAILED",
                detail="Không tìm thấy tài khoản.",
                datastore=self.datastore,
            )
            return ServiceResult(False, "Sai tài khoản hoặc mật khẩu!", level="error")

        stored_password = record.get("password", "")
        if not password_matches(stored_password, password):
            write_activity_log(
                action="LOGIN",
                actor=normalized_username,
                role=role,
                status="FAILED",
                detail="Mật khẩu không hợp lệ.",
                datastore=self.datastore,
            )
            return ServiceResult(False, "Sai tài khoản hoặc mật khẩu!", level="error")

        migrated = False
        secured_password = prepare_password_for_storage(stored_password)
        if secured_password and secured_password != stored_password:
            record["password"] = secured_password
            migrated = True

        if migrated:
            self.datastore.save()

        result = ServiceResult(
            True,
            f"Chào mừng {self._display_name(role, record, normalized_username)}!",
            username=normalized_username,
            display_name=self._display_name(role, record, normalized_username),
            role=role,
        )

        write_activity_log(
            action="LOGIN",
            actor=normalized_username,
            role=role,
            status="SUCCESS",
            detail="Đăng nhập thành công.",
            datastore=self.datastore,
        )
        return result

    def register_user(
        self,
        username: str,
        password: str,
        fullname: str,
        phone: str,
    ) -> ServiceResult:
        normalized_username = normalize_username(username)
        normalized_fullname = normalize_fullname(fullname)
        normalized_phone = normalize_phone(phone)

        if not normalized_username or not str(password or "").strip() or not normalized_fullname:
            return ServiceResult(False, "Vui lòng nhập đủ các trường bắt buộc!", level="warning")

        if not is_valid_username(normalized_username):
            return ServiceResult(
                False,
                "Tên đăng nhập phải dài 3-30 ký tự và chỉ gồm chữ, số, dấu chấm, gạch dưới hoặc gạch ngang.",
                level="warning",
            )

        if not is_valid_password(password):
            return ServiceResult(False, "Mật khẩu phải có ít nhất 3 ký tự.", level="warning")

        if not is_valid_fullname(normalized_fullname):
            return ServiceResult(False, "Họ và tên phải có ít nhất 3 ký tự.", level="warning")

        if not is_valid_phone(normalized_phone):
            return ServiceResult(False, "Số điện thoại phải có 10 số và bắt đầu bằng 0.", level="warning")

        self.datastore.load()
        if self.datastore.find_user(normalized_username):
            write_activity_log(
                action="REGISTER_USER",
                actor=normalized_username,
                role="user",
                status="FAILED",
                detail="Tên đăng nhập đã tồn tại.",
                datastore=self.datastore,
            )
            return ServiceResult(False, "Tên đăng nhập đã tồn tại!", level="error")

        self.datastore.data.setdefault("users", []).append(
            {
                "username": normalized_username,
                "password": prepare_password_for_storage(password),
                "fullname": normalized_fullname,
                "sdt": normalized_phone,
            }
        )
        self.datastore.save()

        write_activity_log(
            action="REGISTER_USER",
            actor=normalized_username,
            role="user",
            status="SUCCESS",
            detail="Tạo tài khoản khách hàng mới.",
            datastore=self.datastore,
        )
        return ServiceResult(
            True,
            "Đăng ký tài khoản thành công!",
            username=normalized_username,
            display_name=normalized_fullname,
            role="user",
        )

    def _resolve_account(self, role: str, username: str):
        if role == "admin":
            admin = self.datastore.data.get("admin", {})
            return admin if username == admin.get("username") else None
        if role == "guide":
            return self.datastore.find_hdv(username)
        if role == "user":
            return self.datastore.find_user(username)
        return None

    @staticmethod
    def _display_name(role: str, record: dict, fallback: str) -> str:
        if role == "guide":
            return record.get("tenHDV", fallback)
        if role == "user":
            return record.get("fullname", fallback)
        return fallback
