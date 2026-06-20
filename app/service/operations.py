from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas import OperationRequest
from app.repository import wallets as wallets_repository


def add_income(db: Session, operation: OperationRequest):
    # Проверяем существует ли кошелек

    if not wallets_repository.is_wallet_exist(db, operation.wallet_name):
        raise HTTPException(
            status_code=404, detail=f"Wallet '{operation.wallet_name}' not found"
        )

    # Добавить доход к балансу кошелька
    wallet = wallets_repository.add_income(db, operation.wallet_name, operation.amount)
    db.commit()
    #  Возвращаем информацию о балансе
    return {
        "message": "Income added",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "description": operation.description,
        "new_balance": wallet.balance,
    }


def add_expense(db: Session, operation: OperationRequest):
    # Проверяем существует ли кошелек
    if not wallets_repository.is_wallet_exist(db, operation.wallet_name):
        raise HTTPException(
            status_code=404, detail=f"Wallet '{operation.wallet_name}' not found"
        )
    # Проверяем что сумму положительна
    if operation.amount <= 0:
        raise HTTPException(status_code=400, detail=f"Amount must be positive")
    # Проверяем достаточно ли средств на кошельке
    wallet = wallets_repository.get_balance_by_name(db, operation.wallet_name)
    if wallet.balance < operation.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Available: {wallet.balance}",
        )
    # Вычитаем расход из баланса кошелька
    wallet = wallets_repository.add_expense(db, operation.wallet_name, operation.amount)

    db.commit()
    # Возвращаем информацию о кошельке
    return {
        "message": "Expense added",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "description": operation.description,
        "new_balance": wallet.balance,
    }
