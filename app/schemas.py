



from pydantic import BaseModel, Field, field_validator


class OperationRequest(BaseModel):
    wallet_name: str = Field(..., max_length=127)
    amount: float
    description: str | None = Field(None, max_length=255)

    @field_validator('amount')
    def amount_must_be_positive(cls, v: float) -> float:
        # Значение больше нуля
        if v <= 0:
            raise ValueError("Amount must be positive")
        
        return v
    
    @field_validator('wallet_name')
    def wallet_name_not_empty(cls, v: str) -> str:
        #  Убираем пробелы по краям
        v = v.strip()

        # Проверяем что строка не пустая
        if not v:
            raise ValueError("Wallet name cannot by empty")
        # Возвращаем очищенное значение
        return v
    
class CreateWalletRequest(BaseModel):
     wallet_name: str = Field(..., max_length=127)
     initial_balance: float = 0
     
     @field_validator('wallet_name')
     def name_not_empty(cls, v: str) -> str:
        #  Убираем пробелы по краям
        v = v.strip()

        # Проверяем что строка не пустая
        if not v:
            raise ValueError("Wallet name cannot by empty")
        # Возвращаем очищенное значение
        return v
     @field_validator('initial_balance')
     def balance_not_negative(cls, v: float) -> float:
         # Значение больше нуля
        if v < 0:
            raise ValueError("Initial balance cantto be negative")
        return v