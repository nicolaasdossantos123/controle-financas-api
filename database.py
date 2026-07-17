from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:night@localhost:5432/api-financas"

print(DATABASE_URL)

engine = create_engine(
    "postgresql+psycopg2://postgres:night@127.0.0.1:5432/postgres"
)

with engine.begin() as conexao:

    conexao.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                
                id SERIAL PRIMARY KEY,
                
                nome VARCHAR(100) NOT NULL,
                
                email VARCHAR(100) NOT NULL UNIQUE,
                
                senha VARCHAR(100) NOT NULL
            )
            """
        )
    )


with engine.begin() as conexao:
    
    conexao.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS categorias (
                
            id SERIAL PRIMARY KEY,
            
            nome VARCHAR(100) NOT NULL,
            
            usuario_id INTEGER NOT NULL
                REFERENCES usuarios(id)
                ON DELETE CASCADE
            )
            """
        )
    )
    
with engine.begin() as conexao:
        
    conexao.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS transacoes (
            
            id SERIAL PRIMARY KEY,
            
            descricao TEXT NOT NULL,
            
            valor NUMERIC(10, 2) NOT NULL,
            
            tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('entrada', 'saida')),
            
            data DATE NOT NULL,
            
            categoria_id INTEGER
            REFERENCES categorias(id)
            ON DELETE CASCADE, 
            
            usuario_id INTEGER NOT NULL
            REFERENCES usuarios(id)
            ON DELETE CASCADE 
                
            )
            """
        )
    )
