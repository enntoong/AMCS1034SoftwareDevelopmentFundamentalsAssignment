# File: room_booking/helpers.py

def user_in_booking(b: dict, current_user: str) -> bool:
    """检查当前用户是否在 booking 里（Owner 或 Member）"""
    me = str(current_user).strip().upper()

    # Owner 匹配
    if b.get("owner_name", "").strip().upper() == me or b.get("owner_id", "").strip() == str(current_user).strip():
        return True

    # Members 匹配
    members = b.get("members", "").strip()
    for m in members.split(";"):
        m = m.strip()
        if not m:
            continue
        sid, sep, name = m.partition("|")
        if sid.strip() == str(current_user).strip() or name.strip().upper() == me:
            return True
    return False
