from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel


app = FastAPI()


BALANCE = {}


class OperationRequest(BaseModel):
    wallet_name: str
    amount: int
    description: str | None = None


@app.get("/balance")
def get_balance(wallet_name: str | None = None):
    # Если имя кошелька не указано - считаем общий баланс
    if wallet_name is None:
        return {"totla_balance": sum(BALANCE.values())}

    # Проверяем существует ли запрашиваем кошелек
    if wallet_name not in BALANCE:
        raise HTTPException(status_code=404, detail=f"Wallet '{wallet_name}' not found")
    # Возвращаем баланс конкретного кошелька
    return {"wallet": wallet_name, "balance": BALANCE[wallet_name]}


@app.post("/wallets/{name}")
def create_wallet(name: str, initial_balance: float = 0):
    # Проверяем не существует ли уже такой кошелек
    if name in BALANCE:
        raise HTTPException(status_code=400, detail=f"Wallet '{name}' already exists")
    # Создать новый кошелек с начальным балансом
    BALANCE[name] = initial_balance
    # Возвращать информацию о созданном кошельке
    return {
        "message": f"Wallet '{name}' created",
        "wallet": name,
        "balance": BALANCE[name],
    }


@app.post("/operations/income")
def add_income(operation: OperationRequest):
    # Проверяем существует ли кошелек
    if operation.wallet_name is None or operation.wallet_name not in BALANCE:
        raise HTTPException(
            status_code=404, detail=f"Wallet '{operation.wallet_name}' not found"
        )
    # Проверяем что сумму положительна
    if operation.amount <= 0:
        raise HTTPException(status_code=400, detail=f"Amount must be positive")
    # Добавить доход к балансу кошелька
    BALANCE[operation.wallet_name] += operation.amount
    #  Возвращаем информацию о балансе
    return {
        "message": "Income added",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "description": operation.description,
        "new_balance": BALANCE[operation.wallet_name]
    }

@app.post("/operations/expense")
def add_expense():
    pass
