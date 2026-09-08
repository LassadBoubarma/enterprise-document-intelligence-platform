from __future__ import annotations
from typing import Iterable

def normalise_roles(roles: Iterable[str]) -> set[str]:
    return {str(role).strip().lower() for role in roles if str(role).strip()}

def can_access(user_role: str, allowed_roles: Iterable[str]) -> bool:
    role = (user_role or "").strip().lower()
    allowed = normalise_roles(allowed_roles)
    if role == "admin":
        return True
    if "all" in allowed:
        return True
    return role in allowed
