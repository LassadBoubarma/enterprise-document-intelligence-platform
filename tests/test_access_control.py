from src.access_control import can_access

def test_allowed_role():
    assert can_access("engineering", ["engineering", "security"])

def test_disallowed_role():
    assert not can_access("hr", ["engineering", "security"])

def test_admin_can_access_everything():
    assert can_access("admin", ["hr"])

def test_all_is_public_to_roles():
    assert can_access("risk", ["all"])
