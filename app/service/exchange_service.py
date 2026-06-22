from decimal import Decimal
from typing import Dict, Tuple  # Типы словаря для резервных курсов

from app.enum import CurrencyEnum

# курсы валют
FALLBACK_RATES: Dict[Tuple[str, str], Decimal] = {
    (CurrencyEnum.USD, CurrencyEnum.RUB): Decimal(str(95.0)),  # Примерный курс USD->RUB
    (CurrencyEnum.USD, CurrencyEnum.EUR): Decimal(str(0.92)),  # Примерный курс USD->EUR
    (CurrencyEnum.EUR, CurrencyEnum.RUB): Decimal(str(103.26)),  # Примерный курс EUR->RUB
    (CurrencyEnum.RUB, CurrencyEnum.USD): Decimal(str(0.0105)),  # Примерный курс RUB->USD
    (CurrencyEnum.EUR, CurrencyEnum.USD): Decimal(str(1.087)),  # Примерный курс EUR->USD
    (CurrencyEnum.RUB, CurrencyEnum.EUR): Decimal(str(0.0097)),  # Примерный курс RUB->EUR
}


def get_exchange_rate(base: CurrencyEnum, target: CurrencyEnum) -> Decimal:
    return FALLBACK_RATES.get((base, target), Decimal(1))
