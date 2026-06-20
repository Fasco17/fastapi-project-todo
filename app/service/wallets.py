from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas import CreateWalletRequest
from app.repository import wallets as wallets_repository


def get_wallet(db: Session, wallet_name: str | None = None):

    # Если имя кошелька не указано - считаем общий баланс
    if wallet_name is None:
        wallets = wallets_repository.get_all_wallets(db)
        return {"totla_balance": sum([w.amount for w in wallets])}

    # Проверяем существует ли запрашиваем кошелек
    if not wallets_repository.is_wallet_exist(db, wallet_name):
        raise HTTPException(status_code=404, detail=f"Wallet '{wallet_name}' not found")
    # Возвращаем баланс конкретного кошелька
    wallet = wallets_repository.get_balance_by_name(db, wallet_name)
    return {"wallet": wallet.name, "balance": wallet.balance}


def create_wallet(db: Session, wallet: CreateWalletRequest):
    # Проверяем не существует ли уже такой кошелек
    if wallets_repository.is_wallet_exist(db, wallet.wallet_name):
        raise HTTPException(
            status_code=400, detail=f"Wallet '{wallet.wallet_name}' already exists"
        )
    # Создать новый кошелек с начальным балансом
    wallet = wallets_repository.create_wallet(
        db, wallet.wallet_name, wallet.initial_balance
    )
    db.commit()
    # Возвращать информацию о созданном кошельке
    return {
        "message": f"Wallet '{wallet.name}' created",
        "wallet": wallet.name,
        "balance": wallet.balance,
    }
