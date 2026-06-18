from fastapi import FastAPI, HTTPException
from fastapi.responses import Response


app = FastAPI()


BALANCE = {}


@app.get("/balance")
def get_balance(wallet_name: str | None = None):
    # Если имя кошелька не указано - считаем общий баланс
    if wallet_name is None:
        return {"totla_balance": sum(BALANCE.values())}

    # Проверяем существует ли запрашиваем кошелек
    if wallet_name not in BALANCE:
        raise HTTPException(
            status_code=404,
            detail=f"Wallet '{wallet_name}' not found"
            )
    # Возвращаем баланс конкретного кошелька
    return {"wallet": wallet_name, "balance": BALANCE[wallet_name]}


@app.post("wallets/{name}")
def receive_money(name: str, amount: int):
    # Если кошелька с таким именем еще нет - создаем его с балансем 0
    if name not in BALANCE:
        BALANCE[name] = 0

    # Если есть - то добавляем сумму к балансу
    BALANCE[name] += amount
    # Возвращаем информацию о кошельке
    return {
        "message": f"Added {amount} to {name}",
        "wallet": name,
        "new_balance": BALANCE[name]
    }