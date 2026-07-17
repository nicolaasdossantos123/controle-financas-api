from pydantic import BaseModel, EmailStr
from datetime import date
from decimal import Decimal
from typing import Literal

class Usuario(BaseModel):
    nome: str
    email: EmailStr
    senha: str

class Login(BaseModel):
    email: EmailStr
    senha: str

class CategoriaCriar(BaseModel):
    nome: str
    
class TransacaoCriar(BaseModel):
    descricao: str
    valor: Decimal
    tipo: Literal['entrada', 'saida']
    data: date
    data_inicio: date
    data_fim: date
    categoria_id: int 