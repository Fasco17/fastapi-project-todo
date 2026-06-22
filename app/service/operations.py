from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.enum import OperationType
from app.models import User
from app.schemas import OperationRequest, OperationResponse
from app.repository import wallets as wallets_repository
from app.repository import operations as operations_repository
from app.service.exchange_service import get_exchange_rate


def add_income(
    db: Session, current_user: User, operation: OperationRequest
) -> OperationResponse:
    # Проверяем существует ли кошелек

    if not wallets_repository.is_wallet_exist(
        db, current_user.id, operation.wallet_name
    ):
        raise HTTPException(
            status_code=404, detail=f"Wallet '{operation.wallet_name}' not found"
        )

    # Добавить доход к балансу кошелька
    wallet = wallets_repository.add_income(
        db, current_user.id, operation.wallet_name, operation.amount
    )
    operation = operations_repository.create_operation(
        db=db,
        wallet_id=wallet.id,
        type=OperationType.INCOME,
        amount=operation.amount,
        currency=wallet.currency,
        category=operation.description,
    )
    db.commit()
    #  Возвращаем информацию о балансе
    return OperationResponse.model_validate(operation)


def add_expense(
    db: Session, current_user: User, operation: OperationRequest
) -> OperationResponse:
    # Проверяем существует ли кошелек
    if not wallets_repository.is_wallet_exist(
        db, current_user.id, operation.wallet_name
    ):
        raise HTTPException(
            status_code=404, detail=f"Wallet '{operation.wallet_name}' not found"
        )
    # Проверяем что сумму положительна
    if operation.amount <= 0:
        raise HTTPException(status_code=400, detail=f"Amount must be positive")
    # Проверяем достаточно ли средств на кошельке
    wallet = wallets_repository.get_balance_by_name(
        db, current_user.id, operation.wallet_name
    )
    if wallet.balance < operation.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Available: {wallet.balance}",
        )
    # Вычитаем расход из баланса кошелька
    wallet = wallets_repository.add_expense(
        db, current_user.id, operation.wallet_name, operation.amount
    )
    operation = operations_repository.create_operation(
        db=db,
        wallet_id=wallet.id,
        type=OperationType.EXPENSE,
        amount=operation.amount,
        currency=wallet.currency,
        category=operation.description,
    )

    db.commit()
    # Возвращаем информацию о кошельке
    return OperationResponse.model_validate(operation)


def get_operations_list(
    db: Session,
    current_user: User,
    wallet_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[OperationResponse]:

    if wallet_id:
        wallet = wallets_repository.get_wallet_by_id(db, current_user.id, wallet_id)
        if not wallet:
            raise HTTPException(
                status_code=404, detail=f"Wallet '{wallet_id}' not found"
            )
        wallets_ids = [wallet_id]
    else:
        wallets = wallets_repository.get_all_wallets(db, current_user.id)
        wallets_ids = [w.id for w in wallets]

    operations = operations_repository.get_operations_list(
        db, wallets_ids, date_from, date_to
    )

    result = []

    for operation in operations:
        result.append(OperationResponse.model_validate(operation))

    return result



def transfer_between_wallets(
        db: Session, user_id: int, from_wallet_id: int, to_wallet_id: int, amount: Decimal
) -> OperationResponse:
    from_wallet = wallets_repository.get_wallet_by_id(db=db, user_id=user_id, wallet_id=from_wallet_id)
    to_wallet = wallets_repository.get_wallet_by_id(db=db, user_id=user_id, wallet_id=to_wallet_id)

    if not from_wallet or not to_wallet:
        raise HTTPException(status_code= 404, detail=f"Wallet not Found: {from_wallet_id} {to_wallet_id}")
    
    if from_wallet.balance < amount:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough money: {from_wallet.balance} {from_wallet.currency}"

        )
    target_amount = amount  # Сколько придёт получателю
    exchange_rate = 1.0  # Курс по умолчанию (одинаковые валюты)
    if from_wallet.currency != to_wallet.currency:  # Разные валюты — нужна конв
        exchange_rate = get_exchange_rate(
            from_wallet.currency, to_wallet.currency
        )  # Получаем курс асинхронно
        target_amount = round(amount * exchange_rate, 2)
        
    from_wallet.balance = round(from_wallet.balance - amount, 2)  # Списываем
    to_wallet.balance = round(to_wallet.balance + target_amount, 2)  # Зачисляем
    operation = operations_repository.create_operation(
        db=db,
        wallet_id=from_wallet.id,
        type=OperationType.TRANSFER,
        amount=target_amount,
        currency=from_wallet.currency,
        category="перевод",
    )

    db.add(from_wallet)
    db.add(to_wallet)
    db.add(operation)
    db.commit()  # Сохраняем изменения в БД
    return OperationResponse.model_validate(operation)