from fastapi import HTTPException

from app.schemas import OperationRequest
from app.repository import wallets as wallets_repository


def add_income(operation: OperationRequest):
    # Проверяем существует ли кошелек
    if not wallets_repository.is_wallet_exist(operation.wallet_name):
        raise HTTPException(
            status_code=404, detail=f"Wallet '{operation.wallet_name}' not found"
        )

    # Добавить доход к балансу кошелька
    new_balance = wallets_repository.add_income(operation.wallet_name, operation.amount)
    #  Возвращаем информацию о балансе
    return {
        "message": "Income added",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "description": operation.description,
        "new_balance": new_balance,
    }


def add_expense(operation: OperationRequest):
    # Проверяем существует ли кошелек
    if not wallets_repository.is_wallet_exist(operation.wallet_name):
        raise HTTPException(
            status_code=404, detail=f"Wallet '{operation.wallet_name}' not found"
        )
    # Проверяем что сумму положительна
    if operation.amount <= 0:
        raise HTTPException(status_code=400, detail=f"Amount must be positive")
    # Проверяем достаточно ли средств на кошельке
    balance = wallets_repository.get_balance_by_name(operation.wallet_name)
    if balance < operation.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Available: {balance}",
        )
    # Вычитаем расход из баланса кошелька
    new_balance = wallets_repository.add_expense(operation.wallet_name, operation.amount)

    # Возвращаем информацию о кошельке
    return {
        "message": "Expense added",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "description": operation.description,
        "new_balance": new_balance,
    }
