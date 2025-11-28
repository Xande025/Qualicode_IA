"""
Sistema de Codificação IPO Melhorado
- Correção ortográfica antes do agrupamento
- Análise de sentido para agrupamento inteligente
- Relatório detalhado mostrando todos os agrupamentos
"""

import pandas as pd
import re
from typing import Dict, List, Tuple, Any
from collections import defaultdict
import os
import json
from datetime import datetime
from openai import OpenAI

def get_openai_client(api_key):
    return OpenAI(api_key=api_key)
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
import unicodedata
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
import unicodedata
from cache_manager import CacheManager
load_dotenv()

class ImprovedIPOCodingSystem:
    """Sistema de codificação melhorado com relatório detalhado"""
    
    def __init__(self):
        self.corrections = self.load_corrections()
        self.similarity_patterns = self.load_similarity_patterns()
        # Flag indicando se a API do ChatGPT está disponível (True/False/None)
        # None = não testado ainda, True = disponível, False = indisponível
        # Flag indicando se a API do ChatGPT está disponível (True/False/None)
        # None = não testado ainda, True = disponível, False = indisponível
        self.chatgpt_available = None
        self.cache = CacheManager()
    
    def load_corrections(self) -> Dict[str, str]:
        """Carrega correções ortográficas de arquivo JSON ou usa padrão"""
        default_corrections = {
            'nao': 'não',
            'sao': 'são',
            'voce': 'você',
            'esta': 'está',
            'saude': 'saúde',
            'educacao': 'educação',
            'administracao': 'administração',
            'pavimentacao': 'pavimentação',
            'iluminacao': 'iluminação',
            'seguranca': 'segurança',
            'transito': 'trânsito',
            'prefeitura': 'prefeitura',
            'prefeito': 'prefeito',
            'otimo': 'ótimo',
            'pessimo': 'péssimo',
            'muito': 'muito',
            'tambem': 'também',
            'melhor': 'melhor',
            'pior': 'pior',
            'enchente': 'enchente',
            'enchentes': 'enchentes',
            'enche tez': 'enchentes',
            'asfalto': 'asfalto',
            'asfaltamento': 'asfaltamento',
            'calcamento': 'calçamento',
            'calcadas': 'calçadas',
            'cemai': 'Cemai',
            'semae': 'Semae',
            'upa': 'UPA'
        }
        
        try:
            # Tenta carregar do arquivo config/corrections.json
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, 'config', 'corrections.json')
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar correções do arquivo: {e}. Usando padrão.")
            
        return default_corrections
    
    def load_similarity_patterns(self) -> Dict[str, List[str]]:
        """Carrega padrões de similaridade de arquivo JSON ou usa padrão"""
        default_patterns = {
            'saude': ['saúde', 'posto', 'médico', 'hospital', 'atendimento médico', 'consulta'],
            'asfalto': ['asfalto', 'pavimentação', 'pavimentar', 'rua', 'estrada', 'asfaltamento'],
            'educacao': ['educação', 'escola', 'ensino', 'curso', 'qualificação', 'instituto'],
            'enchente': ['enchente', 'enchentes', 'alagamento', 'água', 'inundação'],
            'habitacao': ['casa', 'moradia', 'habitação', 'lote', 'apartamento', 'albergue'],
            'infraestrutura': ['calçada', 'calçamento', 'ponte', 'obra', 'construção'],
            'esporte': ['esporte', 'projeto', 'lazer', 'recreação'],
            'empresa': ['empresa', 'fábrica', 'emprego', 'trabalho', 'desenvolvimento'],
            'nada': ['nada', 'nenhum', 'não fez', 'não tem', 'ruim']
        }
        
        try:
            # Tenta carregar do arquivo config/similarity_patterns.json
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, 'config', 'similarity_patterns.json')
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar padrões de similaridade do arquivo: {e}. Usando padrão.")
            
        return default_patterns
    
    def correct_text(self, text: str) -> str:
        """Corrige ortografia do texto"""
        if pd.isna(text) or not isinstance(text, str):
            return str(text)
        
        corrected = str(text).strip().lower()
        
        # Aplica correções palavra por palavra
        words = corrected.split()
        corrected_words = []
        
        for word in words:
            # Remove pontuação para comparação
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in self.corrections:
                # Substitui mantendo pontuação original
                corrected_word = word.replace(clean_word, self.corrections[clean_word])
                corrected_words.append(corrected_word)
            else:
                corrected_words.append(word)
        
        corrected = ' '.join(corrected_words)
        
        # Capitaliza primeira letra
        if corrected:
            corrected = corrected[0].upper() + corrected[1:] if len(corrected) > 1 else corrected.upper()
        
        # Remove espaços duplos
        corrected = re.sub(r'\s+', ' ', corrected).strip()
        
        return corrected

    def normalize_text(self, text: str) -> str:
        """Normaliza texto para comparações: remove acentos, pontuação, lowercase e espaços extras."""
        if text is None:
            return ''
        s = str(text).strip().lower()
        # remove acentos
        s = unicodedata.normalize('NFKD', s)
        s = ''.join([c for c in s if not unicodedata.combining(c)])
        # remove pontuação
        s = re.sub(r'[^a-z0-9\s]', ' ', s)
        s = re.sub(r'\s+', ' ', s).strip()
        return s

    def canonicalize(self, text: str) -> str:
        """Produz forma canônica para agrupar respostas equivalentes."""
        if not text:
            return ''
        # aplica correções ortográficas primeiro
        corrected = self.correct_text(text)
        norm = self.normalize_text(corrected)

        # regras simples de sinônimos/normalização
        syn_map = {
            'onibus': 'onibus',
            'ônibus': 'onibus',
            'onibis': 'onibus',
            'asfaltmento': 'asfalto',
            'asfalto': 'asfalto',
            'pavimentacao': 'asfalto',
            'pavimentacao/asfalto': 'asfalto',
            'posto de saude': 'posto saude',
            'posto medico': 'posto saude',
            'muito medico': 'medico',
            'mais medicos': 'medico',
            'medicos no posto': 'medico',
            'polisia': 'policia',
            'policia': 'policia',
            'policiamento nas ruas': 'policiamento',
            'policiamento melhor': 'policiamento',
            'seguranca nas ruas': 'seguranca',
            'seguranca publica': 'seguranca',
            'mais seguranca': 'seguranca',
            'egotos': 'esgoto',
            'esgotos emtupidos': 'esgoto',
            'saneamento basico': 'saneamento',
        }

        if norm in syn_map:
            return syn_map[norm]

        # tenta mapear por palavras-chave conhecidas
        for key, keywords in self.similarity_patterns.items():
            for kw in keywords:
                if kw in norm:
                    return key

        return norm
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade entre dois textos"""
        if not text1 or not text2:
            return 0.0
        
        text1_lower = text1.lower()
        text2_lower = text2.lower()
        
        # Similaridade exata
        if text1_lower == text2_lower:
            return 1.0
        
        # Similaridade por palavras-chave
        similarity_score = 0.0
        
        for category, keywords in self.similarity_patterns.items():
            text1_matches = sum(1 for keyword in keywords if keyword in text1_lower)
            text2_matches = sum(1 for keyword in keywords if keyword in text2_lower)
            
            if text1_matches > 0 and text2_matches > 0:
                similarity_score += 0.8  # Alta similaridade por categoria
        
        # Similaridade por palavras comuns
        words1 = set(text1_lower.split())
        words2 = set(text2_lower.split())
        
        if words1 and words2:
            common_words = words1.intersection(words2)
            word_similarity = len(common_words) / max(len(words1), len(words2))
            similarity_score += word_similarity * 0.5
        
        return min(similarity_score, 1.0)
    
    def group_responses_intelligent(self, responses: List[str], existing_codes: Dict[str, int], 
                                  similarity_threshold: float = 0.6) -> Tuple[Dict[str, int], Dict[str, List[str]]]:
        """Agrupa respostas de forma inteligente"""
        # Normaliza e corrige respostas e existing_codes
        corrected_responses = []
        for response in responses:
            if pd.isna(response) or not str(response).strip():
                corrected_responses.append(response)
            else:
                corrected_responses.append(self.correct_text(str(response)))

        # Normaliza existing_codes para comparação (mantém mapa para recuperar descrição original)
        norm_existing_map = {}  # norm_desc -> (original_desc, code)
        for desc, code in existing_codes.items():
            norm = self.correct_text(str(desc)).strip().lower()
            norm_existing_map[norm] = (desc, code)

        # Inicializa grupos com chaves já existentes (usando a descrição original)
        groups = defaultdict(list)
        for desc, code in existing_codes.items():
            groups[desc] = []

        # Próximo código disponível (ignora reservados)
        reserved_codes = [55, 66, 77, 88, 99]
        used_codes = [c for c in existing_codes.values() if c not in reserved_codes]
        next_code = max(used_codes) + 1 if used_codes else 10

        # Processa cada resposta, priorizando códigos do F17
        processed = set()
        for original_response, corrected_response in zip(responses, corrected_responses):
            if pd.isna(original_response) or original_response in processed:
                continue

            resp_str = str(original_response).strip()

            # Se a resposta for número e existir como código, agrupa corretamente
            try:
                resp_num = int(resp_str)
                if resp_num in existing_codes.values():
                    for desc, code in existing_codes.items():
                        if code == resp_num:
                            groups[desc].append(original_response)
                            processed.add(original_response)
                            break
                    continue
            except Exception:
                pass

            # Normaliza e canonicaliza para comparação
            corr_norm = self.canonicalize(corrected_response) if corrected_response is not None else ''

            # 1) Tenta match exato com existing_codes normalizado
            matched = False
            if corr_norm in norm_existing_map:
                desc, code = norm_existing_map[corr_norm]
                groups[desc].append(original_response)
                processed.add(original_response)
                matched = True
                continue

            # 2) Tenta match fuzzy com existing_codes
            best_desc = None
            best_score = 0
            for norm_desc, (orig_desc, code) in norm_existing_map.items():
                score = fuzz.token_set_ratio(corr_norm, norm_desc)
                if score > best_score:
                    best_score = score
                    best_desc = orig_desc
            if best_score >= 85:
                groups[best_desc].append(original_response)
                processed.add(original_response)
                continue

            # 3) Procura grupo novo já criado (usa canonical forms + fuzzy)
            best_match = None
            best_score = 0
            for group_key in list(groups.keys()):
                # ignora grupos que são F17 existentes (já tratados acima)
                if group_key in existing_codes:
                    continue
                key_norm = self.canonicalize(group_key)
                # verificação direta de igualdade canônica
                if key_norm and corr_norm and key_norm == corr_norm:
                    best_match = group_key
                    best_score = 100
                    break
                # fuzzy nas formas normalizadas
                sim = fuzz.token_set_ratio(corr_norm, key_norm)
                if sim > best_score:
                    best_score = sim
                    best_match = group_key
            if best_score >= 82:
                groups[best_match].append(original_response)
                processed.add(original_response)
                continue

            # 4) Cria novo grupo com a forma corrigida padronizada
            # Cria novo grupo usando forma canônica porém apresentável (capitalizada)
            canonical = self.canonicalize(corrected_response) if corrected_response is not None else ''
            display_key = self.correct_text(canonical) if canonical else self.correct_text(str(original_response))
            new_key = display_key
            groups[new_key].append(original_response)
            processed.add(original_response)

        # Mescla grupos similares (usa fuzzy) e reconstrói o mapa de códigos garantindo não duplicar
        merged = self.merge_similar_groups(dict(groups), threshold=85)

        # Reconstrói códigos: prioriza existing_codes; novos começam em next_code
        codes = existing_codes.copy()
        final_groups = {}
        for title, items in merged.items():
            # tenta encontrar se title corresponde (case-insensitive) a alguma existing desc
            found_existing = None
            title_norm = self.correct_text(title).strip().lower()
            for norm_desc, (orig_desc, code) in norm_existing_map.items():
                if title_norm == norm_desc:
                    found_existing = (orig_desc, code)
                    break
            if found_existing:
                orig_desc, code = found_existing
                codes[orig_desc] = code
                # garante que o group key use a descrição original do F17
                final_groups[orig_desc] = list(dict.fromkeys(items))
            else:
                # novo código
                # evita criar duplicata se título já presente no mapa
                if title in codes:
                    assigned_code = codes[title]
                else:
                    assigned_code = next_code
                    codes[title] = assigned_code
                    next_code += 1
                final_groups[title] = list(dict.fromkeys(items))

        return codes, final_groups
    
    def standardize_with_chatgpt(self, phrase: str) -> str:
        """Padroniza frase usando ChatGPT (OpenAI) seguindo regras IPO"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return phrase
        client = get_openai_client(api_key=api_key)
        
        # Prompt mais específico conforme regras IPO
        # Tenta carregar prompt do arquivo
        default_prompt = (
            f"Apply IPO rules to standardize this category title: '{phrase}'.\n"
            "Rules:\n"
            "1. Correct spelling and grammar.\n"
            "2. Capitalize the first letter (Sentence case).\n"
            "3. Keep it concise and descriptive.\n"
            "4. Do not change the meaning.\n"
            "5. Return ONLY the standardized text."
        )
        
        prompt = default_prompt
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            prompt_path = os.path.join(base_dir, 'prompts', 'standardization_prompt.txt')
            if os.path.exists(prompt_path):
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    template = f.read()
                    prompt = template.replace('{phrase}', phrase)
        except Exception as e:
            print(f"Erro ao carregar prompt de padronização: {e}. Usando padrão.")
        
        try:
            # Verifica cache antes de chamar
            cached_response = self.cache.get(prompt, "standardize")
            if cached_response:
                return cached_response

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            # Se chegou aqui, a API respondeu corretamente
            try:
                content = response.choices[0].message.content.strip()
                # Remove aspas se o modelo adicionar
                if content.startswith('"') and content.endswith('"'):
                    content = content[1:-1]
            except Exception:
                content = str(response.choices[0].message.get('content', '')).strip()
            
            # Salva no cache
            self.cache.set(content, prompt, "standardize")
            
            # marca disponibilidade
            try:
                self.chatgpt_available = True
            except Exception:
                pass
            return content
        except Exception:
            # marca indisponibilidade para evitar tentativas repetidas
            try:
                self.chatgpt_available = False
            except Exception:
                pass
            return phrase

    def create_detailed_report(self, codes: Dict[str, int], groups: Dict[str, List[str]], question_name: str, processing_method: str = None) -> str:
        """Cria relatório detalhado de agrupamentos"""
        
        report_lines = []
        report_lines.append(f"RELATÓRIO DE AGRUPAMENTOS – {question_name.upper()}")
        report_lines.append("")
        
        # Adiciona informação sobre o método usado
        if processing_method:
            method_info = {
                'chatgpt': '🤖 Processado com ChatGPT (OpenAI GPT-4o)',
                'fallback_local': '🔧 Processado com Agrupador Local (Fallback)'
            }
            report_lines.append(f"Método de Processamento: {method_info.get(processing_method, processing_method)}")
            report_lines.append("")
        
        # Ordena códigos, reservados por último
        def code_sort_key(item):
            code = item[1]
            if code in [77, 88, 99]:
                return (1, code)
            return (0, code)
        sorted_codes = sorted(codes.items(), key=code_sort_key)
        
        for description, code in sorted_codes:
            # Só tenta padronizar via ChatGPT se soubermos que a API está disponível.
            # Se não estiver disponível (ou ainda não testada), usa a padronização local.
            # Também verifica se o método de processamento foi 'chatgpt'
            use_chatgpt = getattr(self, 'chatgpt_available', False) or (processing_method == 'chatgpt')
            
            if use_chatgpt:
                standardized_desc = self.standardize_with_chatgpt(description)
            else:
                standardized_desc = self.correct_text(description)
            responses_in_group = groups.get(description, [])
            
            report_lines.append(f"Código {code} – {standardized_desc}:")
            
            if responses_in_group:
                for response in responses_in_group:
                    if pd.notna(response) and str(response).strip():
                        report_lines.append(f" - {self.correct_text(str(response))}")
            else:
                report_lines.append(f" - (respostas com código {code})")
            
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    def create_output_columns_detailed(self, original_responses: List[Any], 
                                     codes: Dict[str, int], groups: Dict[str, List[str]]) -> Tuple[List[Any], List[Any]]:
        """Cria colunas de saída com mapeamento detalhado"""
        
        # Cria mapeamento de resposta original para código
        response_to_code = {}
        
        for group_desc, responses_list in groups.items():
            code = codes.get(group_desc)
            if code:
                for response in responses_list:
                    response_to_code[response] = code
        
        code_column = []
        response_column = []
        
        for response in original_responses:
            if pd.isna(response):
                code_column.append("")
                response_column.append("")
            else:
                # Se a resposta é um código reservado, repete
                try:
                    resp_num = int(str(response).strip())
                    if resp_num in codes.values():
                        code_column.append(resp_num)
                        response_column.append(response)
                        continue
                except Exception:
                    pass
                if response in response_to_code:
                    code_column.append(response_to_code[response])
                    response_column.append(response)
                else:
                    # Tenta encontrar por similaridade
                    found_code = None
                    for group_desc, code in codes.items():
                        if self.calculate_similarity(str(response), group_desc) >= 0.8:
                            found_code = code
                            break
                    if found_code:
                        code_column.append(found_code)
                        response_column.append(response)
                    else:
                        code_column.append("ERROR")
                        response_column.append(response)
        
        return code_column, response_column

    def group_with_chatgpt(self, responses: list, f17: list = None, questionario: str = None) -> dict:
        """Agrupa respostas usando o ChatGPT, seguindo o prompt IPO, retornando um dicionário {titulo: [respostas]}"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OPENAI_API_KEY não encontrada no .env")
        client = get_openai_client(api_key=api_key)
        # Usa o prompt fornecido pelo usuário como system prompt para o ChatGPT
        # Carrega prompt do sistema
        default_system_prompt = """
You are a survey coding specialist for the Institute of Opinion Research (IPO). Your objective is to receive data and code survey responses, following the IPO's rules exactly.

CRITICAL: You MUST process EVERY SINGLE response provided. Do not skip any responses. Every response must appear in exactly one group.

Your work must be carried out in mandatory steps. Please confirm the completion of each step before proceeding to the next.

Your objective is to receive data and code survey question responses, following the IPO's rules exactly. You can work in two ways:
1. Receive 3 types of files: • Coding Database (Excel) – Contains the responses and their codes (when they exist). • Form 17 (F17) – The codebook, with a tab for each question, listing responses and their respective codes. • Questionnaire – Shows the text of the questions and indicates if they are closed, semi-open, or open.
2. Receive only the question column from the Coding Database and the corresponding column from the F17, to code only the specific question requested.

Correctly identify the type of question based on the column content:
Closed Question: contains only numeric codes in the response column (e.g., 1,2,3...). Must NEVER be coded — it is already complete.
Semi-open Question: contains some codes and some loose phrases. Create codes only for the new phrases; next code starts at 10 or follows sequence.
Open Question: contains only phrases/words except non-response codes (77,88,99). Search F17 for existing codes; otherwise create new starting at 10.

Mandatory Workflow Steps:
1. Count the total number of responses provided. You MUST process ALL of them.
2. Analyze the question and the F17 to understand existing categories.
3. Analyze ALL open responses, correct spelling, standardize words, identify equivalent meanings.
4. Group responses ONLY when meaning is identical or equivalent.
5. NEVER create duplicate codes for the same meaning.
6. If a response has a unique meaning, assign a unique code.
7. Never use generic grouping like "Others".
8. Mandatory text review: correct spelling/grammar while preserving meaning; capitalize descriptions; standardize names; remove duplicates.
9. If you detect different codes for the same response, mark it as "CHANGES TO (correct code)".
10. If response is out of context or illegible, label it as "MANUAL REVIEW".
11. VERIFY: Count all responses in your groups. The total MUST equal the number of responses provided.

F17 Rules and Critical Rules: follow exactly as described; do not change non-response codes (55,66,77,88,99); do not reorder/insert/delete rows in the database.

Mandatory Output Formatting: Always return two columns: Left: Code, Right: Response. The code column must be filled in every row. Maintain original database right column. Do not reorder or add rows. In F17, texts should be grammatically adjusted without duplicate codes.

Mandatory Outputs:
1. Excel Coding Database (.xlsx) with responses and codes.
2. Excel Form 17 (.xlsx) with codes and responses.
3. Grouping report in TXT explaining group decisions in the required structure.

Working Format: Confirm question type before coding. Group equivalent meanings. Justify groupings. Work exclusively based on files provided and rules above. REMEMBER: Process EVERY response provided.
"""
        system_prompt = default_system_prompt
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            prompt_path = os.path.join(base_dir, 'prompts', 'system_prompt.txt')
            if os.path.exists(prompt_path):
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    system_prompt = f.read()
        except Exception as e:
            print(f"Erro ao carregar prompt do sistema: {e}. Usando padrão.")
        f17_block = ""
        if f17:
            f17_block = "F17 (codebook):\n" + "\n".join([str(x) for x in f17])
        respostas_block = "\n".join([f"{i+1}. {str(x)}" for i, x in enumerate(responses)])
        total_respostas = len(responses)
        # User content pede explicitamente que o modelo retorne uma lista de objetos com codigo/titulo/respostas
        user_content = (
            f"{f17_block}\n\n"
            f"Total de respostas para processar: {total_respostas}\n"
            f"Responses to be coded (do not reorder rows, process ALL {total_respostas} responses):\n{respostas_block}\n\n"
            "CRITICAL REQUIREMENTS:"
            " 1. You MUST process ALL unique responses listed above."
            " 2. Create a Codebook that covers EVERY single response."
            " 3. Use existing F17 codes when a response matches exactly or closely. You MUST return these groups too."
            " 4. If you create new codes, start at 10 or the next available number."
            " 5. Return a JSON array (list) of objects with the exact fields:"
            " [{\"codigo\": <integer>, \"titulo\": <string>, \"respostas\": [<string>, ...]}, ...]."
            " 6. IMPORTANT: Even if a response matches an existing F17 code, you MUST include it in the output JSON with that code."
            " 7. Do NOT skip any response. The goal is to map every input to a code."
        )
        import sys
        import sys
        try:
            # Verifica cache para o agrupamento principal
            # Usa system_prompt e user_content como chave
            cached_grouping = self.cache.get(system_prompt, user_content, "grouping")
            
            if cached_grouping:
                print("[DEBUG] Usando resposta em CACHE para agrupamento!", flush=True)
                # Simula estrutura de resposta para o restante do código processar
                # Precisamos retornar o conteúdo como se fosse o 'content' extraído
                content = cached_grouping
                # Pula a chamada da API
            else:
                print("[DEBUG] Chamando ChatGPT (function-calling)...", flush=True)
                # Define schema para function-calling: lista de objetos {codigo,titulo,respostas}
                functions = [
                    {
                        "name": "return_groups",
                        "description": "Retorna uma lista de grupos codificados seguindo o formato IPO",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "groups": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "codigo": {"type": "integer"},
                                            "titulo": {"type": "string"},
                                            "respostas": {"type": "array", "items": {"type": "string"}}
                                        },
                                        "required": ["codigo", "titulo", "respostas"]
                                    }
                                }
                            },
                            "required": ["groups"]
                        }
                    }
                ]

                # Tenta chamar com function-calling; alguns clientes legados podem rejeitar o parâmetro
                try:
                    # Nova API OpenAI usa 'tools' ao invés de 'functions'
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
                            temperature=0,
                            tools=[{
                                "type": "function",
                                "function": functions[0]
                            }],
                            tool_choice="auto"
                        )
                    except (TypeError, AttributeError):
                        # Tenta com 'functions' (API antiga)
                        try:
                            response = client.chat.completions.create(
                                model="gpt-4o",
                                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
                                temperature=0,
                                functions=functions,
                                function_call="auto"
                            )
                        except (TypeError, AttributeError):
                            # Fallback para chamada normal sem function-calling
                            print("[DEBUG] Function-calling não suportado, usando chamada normal", flush=True)
                            response = client.chat.completions.create(
                                model="gpt-4o",
                                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
                                temperature=0
                            )
                except Exception as api_error:
                    error_str = str(api_error)
                    # Trata erros específicos da API OpenAI
                    if '429' in error_str or 'insufficient_quota' in error_str or 'quota' in error_str.lower():
                        error_msg = "Quota da API OpenAI excedida. Verifique seus créditos e limite de uso em https://platform.openai.com/account/billing"
                        print(f"[DEBUG] {error_msg}", flush=True)
                        raise Exception(error_msg)
                    elif '401' in error_str or 'invalid_api_key' in error_str or 'authentication' in error_str.lower():
                        error_msg = "Chave de API OpenAI inválida ou expirada. Verifique sua chave em https://platform.openai.com/api-keys"
                        print(f"[DEBUG] {error_msg}", flush=True)
                        raise Exception(error_msg)
                    elif 'rate_limit' in error_str.lower() or 'too_many_requests' in error_str.lower():
                        error_msg = "Limite de requisições excedido. Aguarde alguns minutos e tente novamente."
                        print(f"[DEBUG] {error_msg}", flush=True)
                        raise Exception(error_msg)
                    else:
                        error_msg = f"Erro na chamada à API OpenAI: {error_str}"
                        print(f"[DEBUG] {error_msg}", flush=True)
                        raise Exception(error_msg)
                    print("[DEBUG] ChatGPT respondeu!", flush=True)
                    self.chatgpt_available = True # Marca como disponível após sucesso
                import json
                # nova resposta: acesso via response.choices[0].message.content ou via response.choices[0].message['content']
                # adaptamos para ambos formatos
                # Salva raw response para auditoria
                try:
                    raw_path = os.path.join(os.getenv('RESULTS_FOLDER', '/tmp/ipo_results'), f"raw_chatgpt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                    with open(raw_path, 'w', encoding='utf-8') as rf:
                        try:
                            # tenta serializar o objeto de resposta diretamente
                            import json as _json
                            _json.dump(response.__dict__ if hasattr(response, '__dict__') else str(response), rf, ensure_ascii=False, indent=2)
                        except Exception:
                            rf.write(str(response))
                    print(f"[DEBUG] Raw ChatGPT salvo em: {raw_path}", flush=True)
                except Exception:
                    pass

                # Extrai conteúdo: verifica tools (nova API) ou function_call (API antiga) ou content direto
                content = None
                try:
                    msg = response.choices[0].message
                    
                    # Nova API: verifica 'tool_calls' primeiro
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            if hasattr(tool_call, 'function') and hasattr(tool_call.function, 'arguments'):
                                content = tool_call.function.arguments
                                print("[DEBUG] Conteúdo extraído de tool_calls (nova API)", flush=True)
                                break
                    
                    # Se não encontrou em tool_calls, tenta function_call (API antiga)
                    if not content:
                        if isinstance(msg, dict) and 'function_call' in msg and msg['function_call']:
                            func = msg['function_call']
                            content = func.get('arguments') or func.get('args') or ''
                            if content:
                                print("[DEBUG] Conteúdo extraído de function_call (dict)", flush=True)
                        else:
                            # objeto com atributos
                            try:
                                fc = getattr(msg, 'function_call', None)
                                if fc:
                                    content = fc.get('arguments') if isinstance(fc, dict) else getattr(fc, 'arguments', None)
                                    if content:
                                        print("[DEBUG] Conteúdo extraído de function_call (attr)", flush=True)
                            except Exception:
                                pass
                    
                    # Se ainda não encontrou, tenta content direto
                    if not content:
                        content = getattr(msg, 'content', None) or (msg.get('content') if isinstance(msg, dict) else None)
                        if content:
                            print("[DEBUG] Conteúdo extraído de message.content", flush=True)
                            
                except Exception as e_extract:
                    print(f"[DEBUG] Erro ao extrair conteúdo: {e_extract}", flush=True)
                    # fallback para estruturas antigas
                    try:
                        content = response.choices[0].message.content
                    except Exception:
                        try:
                            content = response.choices[0].message['content'] if isinstance(response.choices[0].message, dict) else str(response)
                        except Exception:
                            content = str(response)
                
                # Salva no cache se tiver conteúdo válido
                if content and isinstance(content, str) and content.strip():
                    self.cache.set(content, system_prompt, user_content, "grouping")
            
            if not content or (isinstance(content, str) and not content.strip()):
                error_msg = "ChatGPT retornou resposta sem conteúdo válido. Verifique a resposta da API."
                print(f"[DEBUG] {error_msg}", flush=True)
                # print(f"[DEBUG] Tipo de resposta: {type(response)}", flush=True)
                # print(f"[DEBUG] Estrutura da mensagem: {dir(response.choices[0].message) if response.choices else 'sem choices'}", flush=True)
                raise Exception(error_msg)

            print(f"[DEBUG] Conteúdo bruto retornado pelo ChatGPT:\n{content}", flush=True)
            # Constrói mapa de existing_codes a partir do f17 para priorização (se fornecido)
            existing_codes = {}
            if f17:
                for line in f17:
                    try:
                        parts = str(line).split('|', 1)
                        if len(parts) == 2:
                            code = int(parts[0].strip())
                            desc = parts[1].strip()
                            existing_codes[desc] = code
                    except Exception:
                        continue

            # Tenta extrair JSON da resposta de forma tolerante
            grupos = None
            # busca o primeiro e último colchete/brace que pareçam envelopar um JSON
            possible_jsons = []
            # procura por { ... }
            starts = [m.start() for m in re.finditer(r'\{', content)]
            ends = [m.start() for m in re.finditer(r'\}', content)]
            if starts and ends:
                for s in starts:
                    for e in reversed(ends):
                        if e > s:
                            candidate = content[s:e+1]
                            possible_jsons.append(candidate)
                            break
            # também tenta arrays [...]
            starts_b = [m.start() for m in re.finditer(r'\[', content)]
            ends_b = [m.start() for m in re.finditer(r'\]', content)]
            if starts_b and ends_b:
                for s in starts_b:
                    for e in reversed(ends_b):
                        if e > s:
                            candidate = content[s:e+1]
                            possible_jsons.append(candidate)
                            break

            parsed = False
            for candidate in possible_jsons:
                try:
                    grupos = json.loads(candidate)
                    parsed = True
                    break
                except Exception as e_json:
                    # ignora e tenta próximo
                    print(f"[DEBUG] json.loads falhou para candidato (len={len(candidate)}): {e_json}", flush=True)
                    continue
            if not parsed:
                # última tentativa: tenta carregar todo o conteúdo bruto se ele for um JSON válido
                try:
                    grupos = json.loads(content)
                    parsed = True
                except Exception as e_json:
                    print(f"[DEBUG] Não foi possível parsear JSON do conteúdo retornado pelo ChatGPT: {e_json}", flush=True)
                    grupos = None
            # Agora esperamos que 'grupos' seja uma lista de objetos: [{codigo, titulo, respostas}, ...]
            # OU um dicionário com a chave 'groups': {'groups': [{codigo, titulo, respostas}, ...]}
            # OU um único objeto de grupo: {codigo, titulo, respostas} (caso raro, mas possível)
            
            if isinstance(grupos, dict):
                if 'groups' in grupos:
                    # ChatGPT retornou {'groups': [...]} - extrai a lista
                    grupos = grupos['groups']
                    print("[DEBUG] Extraído 'groups' do dicionário retornado pelo ChatGPT", flush=True)
                elif 'codigo' in grupos and 'titulo' in grupos and 'respostas' in grupos:
                    # ChatGPT retornou um único grupo sem lista
                    print("[DEBUG] ChatGPT retornou um único grupo não envelopado. Convertendo para lista.", flush=True)
                    grupos = [grupos]
                else:
                    # Tenta encontrar lista em outras chaves
                    found_list = False
                    for key in ['data', 'result', 'items']:
                        if key in grupos and isinstance(grupos[key], list):
                            grupos = grupos[key]
                            print(f"[DEBUG] Extraído lista da chave '{key}'", flush=True)
                            found_list = True
                            break
                    
                    if not found_list:
                        # É um dicionário mas não tem estrutura conhecida
                        error_msg = f"Formato inesperado do retorno do ChatGPT (esperava lista ou dict com 'groups'): {type(grupos)} -> {list(grupos.keys()) if grupos else 'vazio'}"
                        print(f"[DEBUG] {error_msg}", flush=True)
                        raise Exception(error_msg)

            if isinstance(grupos, list):
                codes = {}
                groups_map = {}
                for item in grupos:
                    if not isinstance(item, dict):
                        print(f"[DEBUG] Item ignorado (não é dict): {item}", flush=True)
                        continue
                    if 'codigo' in item and 'titulo' in item and 'respostas' in item:
                        try:
                            codigo = int(item['codigo'])
                        except Exception:
                            # pula itens com codigo inválido
                            print(f"[DEBUG] Codigo inválido no item: {item}", flush=True)
                            continue
                        titulo = self.correct_text(str(item['titulo']))
                        respostas_list = [r for r in item.get('respostas', []) if isinstance(r, str) and r.strip()]
                        codes[titulo] = codigo
                        groups_map[titulo] = respostas_list
                    else:
                        print(f"[DEBUG] Item sem campos esperados: {item}", flush=True)
                        continue
                # normaliza e une títulos semelhantes
                groups_map = self.merge_similar_groups(groups_map, threshold=85)
                # garante que não haja códigos duplicados para títulos iguais: se houver conflito, prioriza códigos do F17
                final_codes = {}
                for titulo, respostas in groups_map.items():
                    # se titulo corresponde a existing_codes, use o código existente
                    title_norm = self.correct_text(titulo).strip().lower()
                    used_code = None
                    for desc, code in existing_codes.items():
                        if self.correct_text(desc).strip().lower() == title_norm:
                            used_code = code
                            break
                    if used_code is None:
                        used_code = codes.get(titulo, None)
                    if used_code is None:
                        # atribui novo código sequencial
                        max_existing = max([c for c in existing_codes.values()] + [9])
                        used_code = max_existing + 1
                    final_codes[titulo] = used_code
                if final_codes and groups_map:
                    # Verifica se todas as respostas foram processadas
                    total_respostas_mapeadas = sum(len(resps) for resps in groups_map.values())
                    total_respostas_originais = len(responses)
                    
                    print(f"[DEBUG] ✅ ChatGPT retornou {len(final_codes)} grupos válidos", flush=True)
                    print(f"[DEBUG] Respostas mapeadas: {total_respostas_mapeadas} de {total_respostas_originais} originais", flush=True)
                    
                    if total_respostas_mapeadas < total_respostas_originais:
                        faltando = total_respostas_originais - total_respostas_mapeadas
                        print(f"[DEBUG] ⚠️ ATENÇÃO: {faltando} respostas não foram processadas pelo ChatGPT!", flush=True)
                        print(f"[DEBUG] Respostas originais: {responses[:10]}...", flush=True)
                        print(f"[DEBUG] Respostas mapeadas: {[r for resps in groups_map.values() for r in resps[:10]]}...", flush=True)
                        # Não lança exceção, mas avisa - o sistema vai tentar mapear as faltantes depois
                    
                    return final_codes, groups_map
                else:
                    print(f"[DEBUG] ⚠️ ChatGPT retornou grupos vazios após processamento", flush=True)
                    raise Exception("ChatGPT retornou grupos vazios após processamento. Verifique o formato da resposta.")
            else:
                error_msg = f"Formato inesperado do retorno do ChatGPT (esperava lista): {type(grupos)} -> {grupos}"
                print(f"[DEBUG] {error_msg}", flush=True)
                print(f"[DEBUG] Conteúdo bruto recebido: {content[:500]}...", flush=True)
                raise Exception(f"{error_msg}. Conteúdo recebido: {str(content)[:200]}")
        except Exception as e:
            error_msg = f"Erro ao agrupar com ChatGPT: {str(e)}"
            print(f"[DEBUG] {error_msg}", flush=True)
            if 'content' in locals():
                print(f"[DEBUG] Conteúdo retornado pelo ChatGPT: {content[:500]}...", flush=True)
            try:
                self.chatgpt_available = False
            except Exception:
                pass
            # Re-lança a exceção ao invés de retornar vazio
            raise Exception(error_msg)

    def merge_similar_groups(self, grupos: dict, threshold: int = 85) -> dict:
        """Une grupos com títulos muito semelhantes usando fuzzy matching."""
        keys = list(grupos.keys())
        merged = {}
        used = set()

        # Pré-calc normalizado para chaves
        norm_map = {k: self.normalize_text(k) for k in keys}

        for i, k1 in enumerate(keys):
            if k1 in used:
                continue
            merged[k1] = list(grupos[k1])
            for j, k2 in enumerate(keys):
                if i == j or k2 in used:
                    continue
                n1 = norm_map.get(k1, '')
                n2 = norm_map.get(k2, '')
                # mescla se uma forma for substring da outra (ex: 'posto saude' vs 'posto de saude')
                if n1 and n2 and (n1 in n2 or n2 in n1):
                    merged[k1].extend(grupos[k2])
                    used.add(k2)
                    continue
                sim = fuzz.token_set_ratio(n1, n2)
                if sim >= threshold:
                    merged[k1].extend(grupos[k2])
                    used.add(k2)
            used.add(k1)
        # remove duplicatas em cada grupo e retorna
        for k in list(merged.keys()):
            merged[k] = list(dict.fromkeys(merged[k]))
        return merged

