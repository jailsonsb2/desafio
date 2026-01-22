# EXTREMAMENTE SIMPLES de migrar:
from fastapi import FastAPI
from pydantic import BaseModel
from main import DataProtector # Importa a classe que criamos hoje

app = FastAPI()
protector = DataProtector() # Carrega o modelo Spacy UMA vez na memória

class RequestText(BaseModel):
    texto: str

@app.post("/validar")
def validar_texto(item: RequestText):
    # Reutiliza a mesma lógica
    resultado = protector.analyze_text(item.texto)
    return resultado