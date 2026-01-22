# api.py - Interface de API para o Detector LGPD
# Execução: uvicorn api:app --reload

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from main import DataProtector, load_file
import shutil
import os
import pandas as pd

app = FastAPI(
    title="API Detector LGPD - Participa DF",
    description="Microserviço para detecção de dados pessoais em textos e arquivos.",
    version="1.0.0"
)

# Instancia o modelo UMA vez na memória (Singleton)
protector = DataProtector()

# Modelo de entrada JSON
class TextoInput(BaseModel):
    id_pedido: str
    texto: str

@app.get("/")
def home():
    return {"status": "online", "docs": "/docs"}

# Endpoint 1: Validação em Tempo Real (JSON)
@app.post("/analisar_texto")
def analisar_texto(entrada: TextoInput):
    resultado = protector.analyze_text(entrada.texto)
    return {
        "id": entrada.id_pedido,
        "classificacao": resultado["classification"],
        "dados_encontrados": resultado["types"],
        "contem_dados_pessoais": resultado["has_data"]
    }

# Endpoint 2: Upload de Arquivo (CSV/Excel)
@app.post("/analisar_arquivo")
async def analisar_arquivo(file: UploadFile = File(...)):
    temp_filename = f"temp_{file.filename}"
    
    # Salva o arquivo temporariamente
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Usa sua função de leitura inteligente (detecta ; ou ,)
        df = load_file(temp_filename)
        
        # Detecta coluna
        target_col = next((c for c in df.columns if any(x in c.lower() for x in ['texto', 'pedido', 'descri'])), None)
        if not target_col:
            raise HTTPException(status_code=400, detail="Coluna de texto não encontrada no arquivo.")

        results = []
        for idx, row in df.iterrows():
            text = str(row[target_col]) if pd.notna(row[target_col]) else ""
            analysis = protector.analyze_text(text)
            results.append({
                "ID": row.get('ID', idx),
                "Classificacao": analysis["classification"],
                "Tipos": analysis["types"]
            })
            
        return {"total_processado": len(df), "resultados": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename) # Limpa a sujeira