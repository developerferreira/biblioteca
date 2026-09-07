from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()

uri = os.getenv("URI")
client = MongoClient(uri)

database = client.get_database("biblioteca") # selecionando o banco de dados
collection = database.get_collection("livros") # selecionando a collection que será utilizada para armazenar os livros

class LivroBase(BaseModel):
    nome: str
    descricao: str
    preco: float

class LivroCreate(LivroBase):
    descricao: str | None = None
    preco: float = None

class LivroUpdate(BaseModel):
    nome: str | None = None
    descricao: str = None
    preco: float = None

@app.get("/")
def read_boot():
    return {
        "Github": "https://github.com/developerferreira"
    }

@app.post("/add/livro")
def add_livro(livro: LivroCreate):
    livro_dicionario = livro.model_dump() # transformando em um dicionario para enviar ao db

    resultado = collection.insert_one(livro_dicionario)

    if resultado.acknowledged: # verifica se o livro foi adicionado (retorna true se foi)
        livro_dicionario["_id"] = str(resultado.inserted_id)

        return {
            "resultado": "Livro adicionado a biblioteca com sucesso.",
            "livro": livro_dicionario
        }
    else:
        raise HTTPException(status_code=500, detail="Ocorreu um erro ao tentar adicionar o livro.")

@app.get("/livros")
def listarLivros():
    biblioteca = collection.find({})
    livros_encontrados = []

    for livro in biblioteca:
        livro["_id"] = str(livro["_id"])
        livros_encontrados.append(livro)
    
    return {
        "livros": livros_encontrados
    }

@app.get("/livro/{livro_id}")
def livro(livro_id: str):
    livro = collection.find_one({ "_id": ObjectId(livro_id) })
    livro["_id"] = str(livro["_id"])
    
    if livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    
    return {
        "resultado": "Livro encontrado!",
        "livro": livro
    }

@app.patch("/atualizar/livro/{livro_id}")
def atualizar_livro(livro_id: str, dados: LivroUpdate):
    biblioteca = collection.find({})

    for livro in biblioteca:
        livro["_id"] = str(livro["_id"])

        if livro["_id"] == livro_id:
            filtro = { "_id": ObjectId(livro_id) }
            atualizar = {
                "$set": {}
            }

            if dados.nome is not None:
                atualizar["$set"]["nome"] = dados.nome
            if dados.descricao is not None:
                atualizar["$set"]["descricao"] = dados.descricao
            if dados.preco is not None:
                atualizar["$set"]["preco"] = dados.preco
            
            collection.update_many(filtro, atualizar)

            # buscando a versão atualizada do livro para retornar
            livro_atualizado = collection.find_one({ "_id": ObjectId(livro_id) })
            livro_atualizado["_id"] = str(livro_atualizado["_id"])
            
            return {
                "resultado": "Livro atualizado com sucesso.",
                "livro": livro_atualizado
            }

    raise HTTPException(status_code=404, detail="Este ID não pertence a nenhum livro da biblioteca")

@app.delete("/livro/deletar/{livro_id}")
def deletar_livro(livro_id: str):
    biblioteca = collection.find({})

    for livro in biblioteca:
        livro["_id"] = str(livro["_id"])

        if livro["_id"] == livro_id:
            livro_deletado = livro # salvando o livro antes de deletar para mostrar no return

            filtro = { "_id": ObjectId(livro_id) }
            collection.delete_one(filtro)

            return {
                "resultado": "Livro deletado com sucesso.",
                "livro": livro_deletado
            }
    
    raise HTTPException(status_code=404, detail="Este ID não pertence a nenhum livro da biblioteca")