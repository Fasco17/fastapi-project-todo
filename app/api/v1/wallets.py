from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependency import get_current_user, get_db
from app.models import User
from app.schemas import CreateWalletRequest, WalletResponse
from app.service import wallets as wallets_service


router = APIRouter()


@router.get("/balance")
async def get_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await wallets_service.get_total_balance(db, current_user, )


@router.post("/wallets", response_model=WalletResponse)
def create_wallet(
    wallet: CreateWalletRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return wallets_service.create_wallet(db, current_user, wallet)


@router.delete("/wallets/{wallet_name}")
def delete_wallet(
    wallet_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return wallets_service.delete_wallet(db, current_user, wallet_name)


@router.get("/wallets", response_model=list[WalletResponse])
def get_all_wallets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return wallets_service.get_all_wallets(db, current_user)