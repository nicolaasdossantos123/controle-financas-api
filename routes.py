from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from sqlalchemy import text
from database import engine
from typing import Literal
from datetime import date
from schemas import Usuario, Login, CategoriaCriar, TransacaoCriar
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import bcrypt
import os

router = APIRouter()

security = HTTPBearer()

load_dotenv()

print("SECRET_KEY:", os.getenv("SECRET_KEY"))

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

if SECRET_KEY is None:
    raise RuntimeError("SECRET_KEY não configurada")

@router.post("/usuarios")
def criar_usuario(usuario: Usuario):

    senha_bytes = usuario.senha.encode("utf-8")
    senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
    senha_hash_str = senha_hash.decode("utf-8")

    with engine.begin() as conexao:

        resultado = conexao.execute(
            text(
                """
                SELECT id
                FROM usuarios
                WHERE email = :email
                """
            ),
            {
                "email": usuario.email
            }
        )

        usuario_existente = resultado.mappings().fetchone()

        if usuario_existente is not None:
            raise HTTPException(
                status_code=409,
                detail="Email já cadastrado"
            )

        resultado_usuario = conexao.execute(
            text(
                """
                INSERT INTO usuarios
                (nome, email, senha)
                VALUES
                (:nome, :email, :senha)
                RETURNING id
                """
            ),
            {
                "nome": usuario.nome,
                "email": usuario.email,
                "senha": senha_hash_str
            }
        )

        novo_usuario = resultado_usuario.mappings().fetchone()

    return {
        "mensagem": "Usuário criado!",
        "id": novo_usuario["id"],
        "nome": usuario.nome,
        "email": usuario.email
    }


@router.post("/categorias")
def criar_categoria(categoria: CategoriaCriar, credentials=Depends(security)):
    
    usuario_id = verificar_token(credentials)
    
    with engine.begin() as conexao:
        resultado_categoria = conexao.execute(
            text(
                """
                INSERT INTO categorias
                (nome, usuario_id)
                VALUES
                (:nome, :usuario_id)
                RETURNING id
                """
            ),
            {"nome": categoria.nome, "usuario_id": usuario_id}
        )
        
        novo_id = resultado_categoria.scalar_one()
        
    return {
        "mensagem": "Categoria criada!",
        "id": novo_id,
        "nome": categoria.nome
    }

@router.get("/categorias")
def listar_categorias(credentials=Depends(security)):
    
    lista_categorias = []
    
    usuario_id = verificar_token(credentials)
    
    with engine.connect() as conexao:
        resultado = conexao.execute(
                text(
                    """
                    SELECT id, nome FROM categorias
                    WHERE usuario_id = :usuario_id
                    """
                ),
                {"usuario_id": usuario_id}
            )
        
        categorias = resultado.mappings().fetchall()
        
        for categoria in categorias:
            dados_categoria = {
                "id": categoria["id"],
                "nome": categoria["nome"]
            }
    
            lista_categorias.append(dados_categoria)

    return lista_categorias


@router.get("/categorias/{id}")
def procurar_categoria(id: int, credentials=Depends(security)):
    
    usuario_id = verificar_token(credentials)
    
    with engine.connect() as conexao:
        resultado_categoria = conexao.execute(
            text(
                """
                SELECT id, nome
                FROM categorias
                WHERE id = :id
                AND usuario_id = :usuario_id
                """
            ),
            {"id": id, "usuario_id": usuario_id}
        )
        
        categoria = resultado_categoria.mappings().fetchone()
        
        if categoria is None:
            raise HTTPException(
                status_code=404,
                detail="Categoria não encontrada ou não pertence ao usuário"
            )
        
        return {
            "id": id,
            "usuario_id": usuario_id,
            "nome": categoria["nome"]
        }
        
    
@router.delete("/categorias/{id}")
def deletar_categoria(id: int, credentials=Depends(security)):
    
    usuario_id = verificar_token(credentials)
    
    with engine.begin() as conexao:
        
        resultado_categoria = conexao.execute(
            text(
                """
                DELETE FROM categorias
                WHERE id = :id
                AND usuario_id = :usuario_id
                RETURNING id, usuario_id, nome
                """
            ),
            {"id": id, "usuario_id": usuario_id}
        )
        
        categoria_deletada = resultado_categoria.mappings().fetchone()
        
        if categoria_deletada is None:
            raise HTTPException(
                status_code=404,
                detail="Categoria não encontrada ou não pertence ao usuário"
            )

        return {
            "mensagem": "Categoria deletada!",
            "categoria": {
                "id": categoria_deletada["id"],
                "usuario_id": usuario_id,
                "nome": categoria_deletada["nome"]
            }
        }
    
        
@router.put("/categorias/{id}")
def atualizar_categoria(id: int, categoria: CategoriaCriar, credentials=Depends(security)):
    
    usuario_id = verificar_token(credentials)
    
    with engine.begin() as conexao:
        resultado_categoria = conexao.execute(
            text(
                """
                SELECT id, nome 
                FROM categorias
                WHERE id = :id
                AND usuario_id = :usuario_id
                """
            ),
            {"id": id, "usuario_id": usuario_id,}
        )
        
        categoria_atual = resultado_categoria.mappings().fetchone()
        
        if categoria_atual is None:
            raise HTTPException(
                status_code=404,
                detail="Categoria não encontrada ou não pertence ao usuário"
            )
            
        conexao.execute(
            text(
                """
                UPDATE categorias
                SET nome = :nome
                WHERE id = :id
                AND usuario_id = :usuario_id
                """
            ),
            {
                "id": id,
                "usuario_id": usuario_id,
                "nome": categoria.nome
            }
        )
    
    return {
        "mensagem": "Categoria atualizada!",
        "categoria": {  
            "id": id,
            "usuario_id": usuario_id,
            "nome": categoria.nome
        }
    }

    
@router.post("/transacoes")
def criar_transacao(
    transacao: TransacaoCriar,
    credentials=Depends(security)
):

    usuario_id = verificar_token(credentials)

    with engine.begin() as conexao:

        resultado_categoria = conexao.execute(
            text(
                """
                SELECT id
                FROM categorias
                WHERE id = :categoria_id
                AND usuario_id = :usuario_id
                """
            ),
            {
                "categoria_id": transacao.categoria_id,
                "usuario_id": usuario_id
            }
        )

        categoria = resultado_categoria.mappings().fetchone()

        if categoria is None:
            raise HTTPException(
                status_code=404,
                detail="Categoria não encontrada ou não pertence ao usuário"
            )

        resultado_transacao = conexao.execute(
            text(
                """
                INSERT INTO transacoes
                (categoria_id, usuario_id, descricao, valor, tipo, data)
                VALUES
                (:categoria_id, :usuario_id, :descricao, :valor, :tipo, :data)
                RETURNING id
                """
            ),
            {
                "categoria_id": transacao.categoria_id,
                "usuario_id": usuario_id,
                "descricao": transacao.descricao,
                "valor": transacao.valor,
                "tipo": transacao.tipo,
                "data": transacao.data,
            }
        )

        nova_transacao = resultado_transacao.mappings().fetchone()

    return {
        "mensagem": "Transação criada!",
        "transacao": {
            "id": nova_transacao["id"],
            "categoria_id": transacao.categoria_id,
            "usuario_id": usuario_id,
            "descricao": transacao.descricao,
            "valor": transacao.valor,
            "tipo": transacao.tipo,
            "data": transacao.data,
        }
    }
        
        
@router.get("/transacoes")
def listar_transacoes(
    tipo: Literal["entrada", "saida"] | None = None,
    categoria_id: int | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    credentials=Depends(security)
):

    usuario_id = verificar_token(credentials)

    if (
        data_inicio is not None
        and data_fim is not None
        and data_inicio > data_fim
    ):
        raise HTTPException(
            status_code=400,
            detail="A data inicial não pode ser maior que a data final."
        )

    query = """
        SELECT id, descricao, valor, tipo, data, categoria_id, usuario_id
        FROM transacoes
        WHERE usuario_id = :usuario_id
    """

    params = {
        "usuario_id": usuario_id
    }

    if tipo is not None:
        query += " AND tipo = :tipo"
        params["tipo"] = tipo

    if categoria_id is not None:
        query += " AND categoria_id = :categoria_id"
        params["categoria_id"] = categoria_id

    if data_inicio is not None:
        query += " AND data >= :data_inicio"
        params["data_inicio"] = data_inicio

    if data_fim is not None:
        query += " AND data <= :data_fim"
        params["data_fim"] = data_fim

    query += " ORDER BY data DESC"

    with engine.connect() as conexao:
        resultado_transacao = conexao.execute(
            text(query),
            params
        )

        transacoes = resultado_transacao.mappings().fetchall()

    lista_transacoes = []

    for transacao in transacoes:
        lista_transacoes.append(
            {
                "id": transacao["id"],
                "usuario_id": transacao["usuario_id"],
                "descricao": transacao["descricao"],
                "valor": transacao["valor"],
                "tipo": transacao["tipo"],
                "categoria_id": transacao["categoria_id"],
                "data": transacao["data"],
            }
        )

    return lista_transacoes

@router.get("/transacoes/{id}")
def procurar_transacao(id: int, credentials=Depends(security)):
    
    usuario_id = verificar_token(credentials)
    
    with engine.connect() as conexao:
        resultado_transacao = conexao.execute(
            text(
                """
                SELECT id, descricao, valor, tipo, data, categoria_id, usuario_id
                FROM transacoes
                WHERE id = :id
                AND usuario_id = :usuario_id
                """
            ),
            {"id": id, "usuario_id": usuario_id}
        )
    
        transacao = resultado_transacao.mappings().fetchone()
        
        if transacao is None:
            raise HTTPException(
                status_code=404,
                detail="Transação não encontrada ou não pertence ao usuário"
            )
            
    return {
        "id": transacao["id"],
        "usuario_id": transacao["usuario_id"],
        "categoria_id": transacao["categoria_id"],
        "descricao": transacao["descricao"],
        "valor": transacao["valor"],
        "tipo": transacao["tipo"],
        "data": transacao["data"],   
    }
    
@router.delete("/transacoes/{id}")
def deletar_transacao(id: int, credentials=Depends(security)):
    
    usuario_id = verificar_token(credentials)
    
    with engine.begin() as conexao:
              
        
        resultado_transacao = conexao.execute(
            text(
                """ 
                DELETE FROM transacoes
                WHERE id = :id
                AND usuario_id = :usuario_id
                RETURNING usuario_id, id
                """
            ),
            {"id": id, "usuario_id": usuario_id}
        ) 
        
        transacao = resultado_transacao.mappings().fetchone()
        
        if transacao is None:
            raise HTTPException(
                status_code=404,
                detail="Transação não encontrada ou não pertence ao usuário"
            )  
            
            
        return {
            "mensagem": "Transação deletada!",
            "transacao": {
                "id": transacao["id"],
                "usuario_id": usuario_id
            }   
        }
        

@router.put("/transacoes/{id}")
def atualizar_transacao(id: int, transacao: TransacaoCriar, credentials=Depends(security)):
    
    
    usuario_id = verificar_token(credentials)
    
    with engine.begin() as conexao:   
        
        resultado_categoria = conexao.execute(
            text(
                """
                SELECT id FROM categorias
                WHERE id = :categoria_id
                AND usuario_id = :usuario_id
                """
            ),
            {
                "categoria_id": transacao.categoria_id,
                "usuario_id": usuario_id
            }
        )

        categoria = resultado_categoria.mappings().fetchone()
        
        if categoria is None:
            raise HTTPException(
                status_code=404,
                detail="Categoria não encontrada ou não pertence ao usuário"
            )
            

        resultado_transacao = conexao.execute(
            text(
                """
               UPDATE transacoes
               SET descricao = :descricao,
                    valor = :valor,
                    tipo = :tipo,
                    data = :data,
                    categoria_id = :categoria_id
              WHERE id = :id
              AND usuario_id = :usuario_id
              RETURNING id
                """
            ),
            {
                "id": id,
                "usuario_id": usuario_id,
                "descricao": transacao.descricao,
                "valor": transacao.valor,
                "tipo": transacao.tipo,
                "data": transacao.data,
                "categoria_id": transacao.categoria_id
            }
        )
        
        transacao_atual = resultado_transacao.mappings().fetchone()
        
        
        if transacao_atual is None:
            raise HTTPException(
                status_code=404,
                detail="Transação não encontrada ou não pertence ao usuário"
            )
        
        return {
            "mensagem": "Transação atualizada!",
            "transacao": {
                "id": id,
                "usuario_id": usuario_id,
                "descricao": transacao.descricao,
                "valor": transacao.valor,
                "tipo": transacao.tipo,
                "data": transacao.data,
                "categoria_id": transacao.categoria_id
            }
        }
            
        
@router.post("/login")
def login(login: Login):
    
    agora = datetime.now(timezone.utc)
    exp = agora + timedelta(minutes=30)
    
    with engine.begin() as conexao:
        resultado = conexao.execute(
            text(
            """
            SELECT id, senha FROM usuarios
            WHERE email = :email
            """
            ),
        {"email": login.email}
    )
        
        usuario = resultado.mappings().fetchone()
    
    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Email ou senha inválidos" 
        )
        
    senha_do_banco = usuario["senha"]
    
    senha_valida = bcrypt.checkpw(
        login.senha.encode("utf-8"),
        senha_do_banco.encode("utf-8")
    )
    
    if not senha_valida:
        raise HTTPException(
            status_code=401,
            detail="Email ou senha inválidos"
        )
    
    dados_token = {
        "sub": str(usuario["id"]), 
        "exp": exp
    }

    
    token = jwt.encode(
        dados_token,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "mensagem": "Acesso autorizado",
        "access_token": token,
        "token_type": "bearer"
    }
    
def verificar_token(credentials):
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        usuario_id = payload.get("sub") 
                    
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expirado"
        )
    
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )
        
    if usuario_id is None:
        raise HTTPException(
            status_code=401,
            detail="Token sem identificação do usuário"
        )
    
    return usuario_id