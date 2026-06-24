from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.enum import CurrencyEnum
from app.models import User
from app.schemas import CreateWalletRequest, TotalBalance, WalletResponse
from app.repository import wallets as wallets_repository
from app.service import exchange_service


async def get_total_balance(db: Session, current_user: User) -> TotalBalance:

    wallets = wallets_repository.get_all_wallets(db, current_user.id)
    total_balance = Decimal(0)
    for wallet in wallets:
        if wallet.currency == CurrencyEnum.RUB:
            total_balance += wallet.balance
        else:
            exchange_rate = await exchange_service.get_exchange_rate(
                wallet.currency, CurrencyEnum.RUB
            )
            total_balance += exchange_rate * wallet.balance
    return TotalBalance(total_balance=total_balance)


def create_wallet(
    db: Session, current_user: User, wallet: CreateWalletRequest
) -> WalletResponse:
    # Проверяем не существует ли уже такой кошелек
    if wallets_repository.is_wallet_exist(db, current_user.id, wallet.wallet_name):
        raise HTTPException(
            status_code=400, detail=f"Wallet '{wallet.wallet_name}' already exists"
        )
    # Создать новый кошелек с начальным балансом
    wallet = wallets_repository.create_wallet(
        db, current_user.id, wallet.wallet_name, wallet.initial_balance, wallet.currency
    )
    db.commit()
    # Возвращать информацию о созданном кошельке
    return WalletResponse.model_validate(wallet)


def delete_wallet(db: Session, current_user: User, wallet_name: str) -> None:
    if not wallets_repository.is_wallet_exist(db, current_user.id, wallet_name):
        raise HTTPException(status_code=404, detail=f"Wallet '{wallet_name}' not found")

    wallets_repository.delete_wallet(db, current_user.id, wallet_name)
    db.commit()
    return {"message": f"Wallet '{wallet_name}' successfully deleted"}


def get_all_wallets(db: Session, current_user: User) -> list[WalletResponse]:
    wallets = wallets_repository.get_all_wallets(db, current_user.id)
    return [WalletResponse.model_validate(wallet) for wallet in wallets]
