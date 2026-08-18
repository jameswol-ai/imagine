from database.models import User, Role, Permission
from database.connection import SessionLocal

def test_user_role_assignment(db_session):
    # create user
    user = User(email="modeltest@example.com", hashed_password="x", full_name="Model Test")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # create role and permission
    role = Role(name="TestRole")
    perm = Permission(name="test.permission")
    db_session.add_all([role, perm])
    db_session.commit()

    # assign permission to role and role to user
    role.permissions.append(perm)
    user.roles.append(role)
    db_session.add_all([role, user])
    db_session.commit()

    db_session.refresh(user)
    assert any(r.name == "TestRole" for r in user.roles)
    assert any(p.name == "test.permission" for r in user.roles for p in r.permissions)
