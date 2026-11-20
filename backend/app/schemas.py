from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Literal

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TransactionIn(BaseModel):
    kind: Literal["income", "expense"]
    amount: float = Field(gt=0)
    category: str | None = None
    description: str = ""
    txn_date: date

class BudgetIn(BaseModel):
    category: str
    limit_amount: float = Field(gt=0)
    month: str = Field(pattern=r"^\d{4}-\d{2}$")

class GoalIn(BaseModel):
    title: str
    target_amount: float = Field(gt=0)
    saved_amount: float = Field(default=0, ge=0)
    target_date: date | None = None
