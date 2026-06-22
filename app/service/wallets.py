from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User
from app.schemas import CreateWalletRequest, WalletResponse
from app.repository import wallets as wallets_repository


def get_wallet(db: Session, current_user: User, wallet_name: str | None = None):

    # Если имя кошелька не указано - считаем общий баланс
    if wallet_name is None:
        wallets = wallets_repository.get_all_wallets(
            db,
            current_user.id,
        )
        return {"totla_balance": sum([w.balance for w in wallets])}

    # Проверяем существует ли запрашиваем кошелек
    if not wallets_repository.is_wallet_exist(db, current_user.id, wallet_name):
        raise HTTPException(status_code=404, detail=f"Wallet '{wallet_name}' not found")
    # Возвращаем баланс конкретного кошелька
    wallet = wallets_repository.get_balance_by_name(db, current_user.id, wallet_name)
    return {"wallet": wallet.name, "balance": wallet.balance}


def create_wallet(db: Session, current_user: User, wallet: CreateWalletRequest) -> WalletResponse:
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
