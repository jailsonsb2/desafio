# ==============================================================================
# PROJETO: Detector de Dados Pessoais (LGPD) - Versão Final (Ouro)
# ==============================================================================

import pandas as pd
import re
import spacy
import argparse
import sys
import os
import logging
from typing import Tuple, List

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')

class DataProtector:
    def __init__(self, model_name: str = "pt_core_news_lg"):
        self.nlp = None
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            try:
                logging.warning("Modelo 'lg' não achado. Usando 'sm'.")
                self.nlp = spacy.load("pt_core_news_sm")
            except:
                logging.error("Nenhum modelo Spacy encontrado.")
                sys.exit(1)

        # 1. Regex Otimizados
        self.regex_cpf = re.compile(r'\b(?:\d{3}\.?\d{3}\.?\d{3}-?\d{2})\b')
        self.regex_email = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        # Regex de Telefone (Forte): Exige DDD ou formato 9xxxx-xxxx. 
        # Aceita fixo sem DDD (xxxx-xxxx) apenas se tiver hífen, para evitar matrículas.
        self.regex_phone = re.compile(r'(?<!\d)(?:(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?(?:9\d{4}[-\s]?\d{4}|\d{4}-\d{4}|(?<=\()\d{4}\d{4}))(?!\d)')
        
        self.regex_rg_context = re.compile(r'(?i)(?:RG|Identidade|R\.G\.)[:\s]*[\d.-]{5,12}')
        
        # 2. Listas de Exclusão (Contexto)
        self.email_blacklist = ['ouvidoria', 'sac', 'atendimento', 'contato', 'admin', 'noreply']
        
        # Termos que, se aparecerem antes de um número, indicam que NÃO é telefone
        self.contexto_negativo_fone = ['matrícula', 'matricula', 'inscrição', 'inscricao', 'nire', 'protocolo', 'processo', 'nº', 'no.', 'nota', 'fiscal']

    def analyze_text(self, text: str) -> dict:
        if not isinstance(text, str): return {"has_data": False, "types": []}

        found_types = []
        text_lower = text.lower()
        
        # --- CPF ---
        if self.regex_cpf.search(text): found_types.append("CPF")
        
        # --- RG ---
        if self.regex_rg_context.search(text): found_types.append("RG")
        
        # --- E-MAIL (Com Blacklist) ---
        for email in self.regex_email.findall(text):
            if not any(x in email.lower() for x in self.email_blacklist):
                found_types.append("EMAIL")
                break

        # --- TELEFONE (Com Análise de Contexto) ---
        # A regex pega os candidatos. Agora filtramos os falsos positivos (Matrícula, NIRE, etc)
        matches_fone = list(self.regex_phone.finditer(text))
        for match in matches_fone:
            numero = match.group()
            start, end = match.span()
            
            # Olhamos os 15 caracteres ANTES do número
            contexto_anterior = text_lower[max(0, start-20):start]
            
            # Se tiver "Matrícula" ou "NIRE" antes, IGNORA.
            eh_falso_positivo = any(termo in contexto_anterior for termo in self.contexto_negativo_fone)
            
            if not eh_falso_positivo:
                # Validação extra: Telefones geralmente têm DDD (10/11 dígitos) ou Hífen
                digits = re.sub(r'\D', '', numero)
                if 8 <= len(digits) <= 11:
                     found_types.append("TELEFONE")
                     break

        # --- NLP (Nomes) ---
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PER":
                # Filtra nomes curtos (ex: "Sol") ou que sejam apenas números
                if len(ent.text.split()) > 1 and not re.match(r'^[\d\W]+$', ent.text):
                    found_types.append("NOME_PESSOA")
                    break

        unique_types = list(set(found_types))
        return {
            "has_data": len(unique_types) > 0,
            "types": unique_types,
            "classification": "Restrito" if unique_types else "Público"
        }

def load_file(filepath):
    if filepath.endswith('.csv'):
        try:
            return pd.read_csv(filepath, sep=None, engine='python', encoding='utf-8')
        except UnicodeDecodeError:
            return pd.read_csv(filepath, sep=None, engine='python', encoding='latin-1')
    elif filepath.endswith(('.xls', '.xlsx')):
        return pd.read_excel(filepath)
    else:
        raise ValueError("Formato não suportado.")

def auto_detect_file():
    files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx', '.xls')) and 'resultado' not in f]
    if files: return files[0]
    return None

def main():
    parser = argparse.ArgumentParser(description="Detector LGPD")
    parser.add_argument("--input", nargs='?', help="Arquivo de entrada")
    parser.add_argument("--output", nargs='?', default="resultado_analise.csv", help="Arquivo de saída")
    args = parser.parse_args()

    input_file = args.input or auto_detect_file()
    if not input_file:
        logging.error("Nenhum arquivo encontrado.")
        sys.exit(1)

    logging.info(f"Processando: {input_file}")
    
    try:
        df = load_file(input_file)
    except Exception as e:
        logging.error(f"Erro ao ler: {e}")
        sys.exit(1)

    target_col = next((c for c in df.columns if any(x in c.lower() for x in ['texto', 'pedido', 'descri'])), None)
    if not target_col:
        logging.error("Coluna de texto não identificada.")
        sys.exit(1)

    protector = DataProtector()
    results = []

    for idx, row in df.iterrows():
        text = str(row[target_col]) if pd.notna(row[target_col]) else ""
        analysis = protector.analyze_text(text)
        
        results.append({
            "ID": row.get('ID', idx),
            "Texto_Snippet": text[:50],
            "Classificacao": analysis["classification"],
            "Dados_Encontrados": ", ".join(analysis["types"])
        })

    try:
        pd.DataFrame(results).to_csv(args.output, index=False, sep=';', encoding='utf-8-sig')
        logging.info(f"Concluído! Salvo em: {args.output}")
    except Exception as e:
        logging.error(f"Erro ao salvar: {e}")

if __name__ == "__main__":
    main()