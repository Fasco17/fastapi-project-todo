from decimal import Decimal

from app.repository import users as users_repository, wallets as wallets_repository


def auth_headers(login: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {login}"}


def create_test_user(db, login: str = "alice"):
    user = users_repository.create_user(db, login=login)
    db.commit()
    return user


def create_test_wallet(db, user_id: int, wallet_name: str = "cash", balance: Decimal = Decimal("100.00")):
    wallet = wallets_repository.create_wallet(db, user_id, wallet_name, balance)
    db.commit()
    return wallet


def test_add_income_updates_wallet_balance(client, db_session):
    user = create_test_user(db_session, login="alice")
    create_test_wallet(db_session, user.id, wallet_name="cash", balance=Decimal("100.00"))

    response = client.post(
        "/api/v1/operations/income",
        json={
            "wallet_name": "cash",
            "amount": "25.50",
            "description": "Salary deposit",
        },
        headers=auth_headers(user.login),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "Income added"
    assert payload["wallet"] == "cash"
    assert payload["amount"] == "25.50"
    assert payload["new_balance"] == "125.50"

    wallet = wallets_repository.get_balance_by_name(db_session, user.id, "cash")
    assert wallet.balance == Decimal("125.50")


def test_add_expense_decreases_wallet_balance(client, db_session):
    user = create_test_user(db_session, login="bob")
    create_test_wallet(db_session, user.id, wallet_name="travel", balance=Decimal("200.00"))

    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": "travel",
            "amount": "80.00",
            "description": "Taxi fare",
        },
        headers=auth_headers(user.login),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "Expense added"
    assert payload["wallet"] == "travel"
    assert payload["amount"] == "80.00"
    assert payload["new_balance"] == "120.00"

    wallet = wallets_repository.get_balance_by_name(db_session, user.id, "travel")
    assert wallet.balance == Decimal("120.00")


def test_add_income_returns_404_when_wallet_missing(client, db_session):
    user = create_test_user(db_session, login="charlie")

    response = client.post(
        "/api/v1/operations/income",
        json={
            "wallet_name": "missing-wallet",
            "amount": "10.00",
            "description": "Test income",
        },
        headers=auth_headers(user.login),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Wallet 'missing-wallet' not found"


def test_add_expense_returns_400_when_insufficient_funds(client, db_session):
    user = create_test_user(db_session, login="dana")
    create_test_wallet(db_session, user.id, wallet_name="shopping", balance=Decimal("30.00"))

    response = client.post(
        "/api/v1/operations/expense",
        json={
            "wallet_name": "shopping",
            "amount": "50.00",
            "description": "Big purchase",
        },
        headers=auth_headers(user.login),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds. Available: 30.00"
