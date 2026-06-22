


from decimal import Decimal

from app.models import User, Wallet


def test_add_expense_success(db_session, client):
    # Arrange
    user = User(login="test")
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(name="card", balance=200, user_id=user.id)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    # Act
    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": "card",
            "amount": 50.0,
            "description": "food"

        },

        headers={"Authorization": f"Bearer {user.login}"},
    )
    # Assert
    assert response.status_code==200
    payload = response.json()
    assert payload["message"] == "Expense added"
    assert payload["wallet"] == wallet.name
    assert payload["amount"] == Decimal(50)
    assert payload["new_balance"] == Decimal(150)
    assert response.json()["description"] == "food"



def test_add_expense_negative_amount(db_session, client):
    user = User(login = "test2")
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(name="cash", balance=500, user_id = user.id)

    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    # Act
    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": "cash",
            "amount": -50.0,
            "description": "food"

        },

        headers={"Authorization": f"Bearer {user.login}"},
    )
    # Assert
    assert response.status_code== 422

    payload = response.json()
    assert "detail" in payload

    db_session.refresh(wallet)
    assert wallet.balance == Decimal(500)


def test_add_expense_empty_name(db_session, client):
    user = User(login = "test3")
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(name="cash", balance=500, user_id = user.id)

    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    # Act
    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": "    ",
            "amount": 50.0,
            "description": "food"

        },

        headers={"Authorization": f"Bearer {user.login}"},
    )
    # Assert
    assert response.status_code== 422

    payload = response.json()
    assert "detail" in payload

    db_session.refresh(wallet)
    assert wallet.balance == Decimal(500)



def test_add_expense_wallet_not_exists(db_session, client):
    user = User(login = "test3")
    db_session.add(user)
    db_session.commit()

    # Act
    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": "cash",
            "amount": 50.0,
            "description": "food"

        },

        headers={"Authorization": f"Bearer {user.login}"},
    )
    # Assert
    assert response.status_code== 404

def test_add_expense_unathorized(client):
    
    #Arrange

    # Act
    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": "cash",
            "amount": 50.0,
            "description": "food"

        },

        headers={"Authorization": "Bearer not exist"},
    )
    # Assert
    assert response.status_code== 401



def test_add_expense_not_unough_money(db_session, client):
    # Arrange
    user = User(login="test")
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(name="card", balance=200, user_id=user.id)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    # Act
    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": "card",
            "amount": 500.0,
            "description": "food"

        },

        headers={"Authorization": f"Bearer {user.login}"},
    )
    # Assert
    assert response.status_code==400

    payload = response.json()
    assert "detail" in payload

    db_session.refresh(wallet)
    assert wallet.balance == Decimal(200)
