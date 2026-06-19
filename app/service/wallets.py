from fastapi import HTTPException

from app.schemas import CreateWalletRequest
from app.repository import wallets as wallets_repository

def get_wallet(wallet_name: str | None = None):
  # Если имя кошелька не указано - считаем общий баланс
    if wallet_name is None:
        wallets = wallets_repository.get_all_wallets()
        return {"totla_balance": sum(wallets.values())}

    # Проверяем существует ли запрашиваем кошелек
    if not wallets_repository.is_wallet_exist(wallet_name):
        raise HTTPException(status_code=404, detail=f"Wallet '{wallet_name}' not found")
    # Возвращаем баланс конкретного кошелька
    balance = wallets_repository.get_balance_by_name(wallet_name)
    return {"wallet": wallet_name, "balance": balance}


def create_wallet(wallet: CreateWalletRequest):
     # Проверяем не существует ли уже такой кошелек
    if wallets_repository.is_wallet_exist(wallet.wallet_name):
        raise HTTPException(status_code=400, detail=f"Wallet '{wallet.wallet_name}' already exists")
    # Создать новый кошелек с начальным балансом
    new_balance = wallets_repository.create_wallet(wallet.wallet_name, wallet.initial_balance)
    # Возвращать информацию о созданном кошельке
    return {
        "message": f"Wallet '{wallet.wallet_name}' created",
        "wallet": wallet.wallet_name,
        "balance": new_balance,
    }