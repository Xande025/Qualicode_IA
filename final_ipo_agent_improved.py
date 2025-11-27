"""
Agente IPO Final Melhorado
- Correção ortográfica antes do agrupamento
- Análise inteligente de sentido
- Relatório detalhado como modelo fornecido
"""

import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple

from improved_coding_system import ImprovedIPOCodingSystem

class FinalIPOAgentImproved:
    """Agente IPO final com sistema melhorado"""
    
    def __init__(self):
        self.coding_system = ImprovedIPOCodingSystem()
    
    def analyze_question_type(self, data: list) -> str:
        """
        Analisa o tipo de questão conforme regras do IPO:
        - Fechada: Apenas códigos numéricos (exceto 98/99 etc que são NS/NR)
        - Semi-aberta: Mistura de códigos numéricos e texto
        - Aberta: Predominância de texto
        """
        total = len(data)
        if total == 0:
            return "vazia"
            
        numeric_count = 0
        text_count = 0
        
        for item in data:
            try:
                # Tenta converter para float/int
                float(item)
                numeric_count += 1
            except (ValueError, TypeError):
                # Se tem texto e não é vazio/espaço
                if str(item).strip():
                    text_count += 1
                    
        # Regras de decisão IPO
        if text_count == 0 and numeric_count > 0:
            return "fechada"
        elif text_count > 0 and numeric_count > 0:
            return "semi-aberta"
        else:
            return "aberta"

    def process_single_question_with_chatgpt(self, question_data: list, existing_codes: dict, question_name: str) -> dict:
        print(f"[DEBUG] Entrou em process_single_question_with_chatgpt para: {question_name}", flush=True)
        
        # 1. Análise do Tipo de Questão (Lógica IPO)
        q_type = self.analyze_question_type(question_data)
        print(f"[DEBUG] Tipo de questão detectado: {q_type.upper()}", flush=True)
        
        if q_type == "fechada":
            # Questões fechadas não passam pelo GPT
            return {
                'question_name': question_name,
                'total_responses': len(question_data),
                'valid_responses': len(question_data),
                'existing_codes': existing_codes,
                'final_codes': existing_codes,
                'new_codes': {},
                'groups': {},
                'detailed_report': "Questão identificada como FECHADA. Nenhum processamento de IA necessário.",
                'code_column': question_data, # Retorna os próprios dados como códigos
                'response_column': question_data,
                'processing_method': 'ignorado_fechada',
                'statistics': {'total_codes': 0, 'new_codes_count': 0, 'groups_with_multiple': 0, 'largest_group_size': 0}
            }

        # Para semi-abertas, filtramos apenas os textos para enviar ao GPT
        items_to_process = []
        indices_to_process = []
        
        if q_type == "semi-aberta":
            print("[DEBUG] Processando como SEMI-ABERTA: filtrando apenas textos.", flush=True)
            for i, item in enumerate(question_data):
                is_text = False
                try:
                    float(item)
                except ValueError:
                    if str(item).strip():
                        is_text = True
                
                if is_text:
                    items_to_process.append(item)
                    indices_to_process.append(i)
        else:
            # Aberta: processa tudo (exceto vazios ou códigos de NS/NR se estiverem misturados, mas assumimos tudo como texto)
            items_to_process = question_data
            # Mapeamento 1:1
        
        # OTIMIZAÇÃO IPO: Extrai respostas únicas para criar o Codebook
        # Isso evita enviar respostas repetidas e garante que o modelo foque em criar categorias
        unique_items = sorted(list(set([str(x).strip() for x in items_to_process if str(x).strip()])))
        
        print(f"[DEBUG] Dados para processar na IA: {len(items_to_process)} itens totais -> {len(unique_items)} itens ÚNICOS", flush=True)

        print(f"[DEBUG] Dados recebidos: question_data={len(question_data)} itens, existing_codes={len(existing_codes)}", flush=True)
        # Converte códigos existentes para lista de strings para o prompt
        f17_list = [f"{code} | {desc}" for desc, code in existing_codes.items()]
        processing_method = "chatgpt"
        
        # Usa APENAS ChatGPT - sem fallback local
        try:
            # group_with_chatgpt retorna (codes_dict, groups_dict) ou ({}, {}) em caso de erro
            # Passamos apenas os itens ÚNICOS para criar o Codebook
            codes_ret, groups_ret = self.coding_system.group_with_chatgpt(unique_items, f17=f17_list)
            
            # --- LÓGICA DE RETRY PARA ITENS NÃO MAPEADOS ---
            # Verifica quais itens únicos NÃO foram cobertos por nenhum grupo retornado nem pelo F17
            
            # Cria conjunto de tudo que foi coberto
            covered_items = set()
            # 1. Coberto pelo retorno do GPT
            for respostas_grupo in groups_ret.values():
                for r in respostas_grupo:
                    covered_items.add(str(r).strip())
                    # Normalização agressiva
                    covered_items.add(self.coding_system.normalize_text(str(r)))
            
            # 2. Coberto pelo F17 existente (backup local)
            # Normaliza chaves do F17 para garantir match
            normalized_f17 = {self.coding_system.normalize_text(k): v for k, v in existing_codes.items()}
            
            items_missing = []
            for item in unique_items:
                item_str = str(item).strip()
                item_norm = self.coding_system.normalize_text(item_str)
                
                # Verifica cobertura
                is_covered = False
                
                # Checa match exato ou normalizado nos grupos do GPT
                if item_str in covered_items or item_norm in covered_items:
                    is_covered = True
                
                # Checa match no F17 (exato ou normalizado)
                if not is_covered:
                    if item_str in existing_codes:
                        is_covered = True
                    elif item_norm in normalized_f17:
                        is_covered = True
                
                # Se não coberto, adiciona para retry
                if not is_covered:
                    items_missing.append(item_str)
            
            if items_missing:
                print(f"[DEBUG] ⚠️ {len(items_missing)} itens não foram processados na primeira passada. Tentando RETRY...", flush=True)
                print(f"[DEBUG] Itens faltando para Retry: {items_missing}", flush=True)
                
                # Segunda chamada APENAS para os faltantes
                try:
                    # Prompt específico para o retry - FORÇA a criação de códigos
                    retry_prompt_suffix = "\n\nIMPORTANT: You MUST provide a code for EACH of these remaining items. Do not skip any."
                    
                    # Usa uma chamada dedicada para o retry se possível, ou a mesma função
                    # Aqui usamos a mesma função mas passando apenas os faltantes
                    codes_retry, groups_retry = self.coding_system.group_with_chatgpt(items_missing, f17=f17_list)
                    
                    if codes_retry and groups_retry:
                        print(f"[DEBUG] ✅ Retry bem sucedido! Recuperados {len(codes_retry)} novos códigos.", flush=True)
                        
                        # Calcula o próximo código disponível com segurança
                        used_codes = set(codes_ret.values()) | set(existing_codes.values())
                        max_code = max(used_codes) if used_codes else 9
                        
                        for titulo, respostas in groups_retry.items():
                            # Se o título já existe, mescla respostas
                            if titulo in groups_ret:
                                for r in respostas:
                                    if r not in groups_ret[titulo]:
                                        groups_ret[titulo].append(r)
                            else:
                                # Novo código
                                novo_cod = codes_retry[titulo]
                                # Se conflitar, incrementa
                                if novo_cod in used_codes:
                                    max_code += 1
                                    novo_cod = max_code
                                    used_codes.add(novo_cod)
                                
                                codes_ret[titulo] = novo_cod
                                groups_ret[titulo] = respostas
                    else:
                         print(f"[DEBUG] ❌ Retry retornou vazio.", flush=True)

                except Exception as e_retry:
                    print(f"[DEBUG] Erro no retry: {e_retry}", flush=True)
                
                # --- FALLBACK FINAL (Última Milha) ---
                # Se ainda sobraram itens sem código após o retry, cria códigos novos automaticamente
                # Isso garante que NUNCA retornamos 'ERROR' para itens válidos
                
                # Recalcula o que ainda falta
                still_missing = []
                covered_now = set()
                for resps in groups_ret.values():
                    for r in resps:
                        covered_now.add(str(r).strip())
                        covered_now.add(self.coding_system.normalize_text(str(r)))
                
                # Atualiza com F17
                normalized_f17 = {self.coding_system.normalize_text(k): v for k, v in existing_codes.items()}
                
                for item in items_missing:
                    item_str = str(item).strip()
                    item_norm = self.coding_system.normalize_text(item_str)
                    if item_str not in covered_now and item_norm not in covered_now:
                        if item_str not in existing_codes and item_norm not in normalized_f17:
                            still_missing.append(item_str)
                
                if still_missing:
                    print(f"[DEBUG] ⚠️ Ainda restam {len(still_missing)} itens após retry. Criando códigos automáticos...", flush=True)
                    
                    # Determina próximo código seguro
                    used_codes = set(codes_ret.values()) | set(existing_codes.values())
                    next_code = (max(used_codes) + 1) if used_codes else 10
                    if next_code < 10: next_code = 10 # Garante mínimo 10 para novos
                    
                    for missing_item in still_missing:
                        # Cria um grupo novo para cada item faltante
                        # Usa o próprio texto como título (capitalizado)
                        title = missing_item.capitalize()
                        
                        # Verifica se já existe grupo com esse título (improvável mas possível)
                        if title in groups_ret:
                            groups_ret[title].append(missing_item)
                        else:
                            while next_code in used_codes:
                                next_code += 1
                            
                            codes_ret[title] = next_code
                            groups_ret[title] = [missing_item]
                            used_codes.add(next_code)
                            
                    print(f"[DEBUG] ✅ {len(still_missing)} códigos automáticos criados.", flush=True)

            else:
                 print(f"[DEBUG] ✅ Todos os itens únicos foram cobertos na primeira passada (ou estão no F17).", flush=True)

            # -----------------------------------------------

        except Exception as e_gpt:
            # Propaga a exceção diretamente - a mensagem já foi formatada no group_with_chatgpt
            # Não adiciona mais contexto para evitar duplicação
            raise e_gpt

        if not codes_ret or not groups_ret:
            error_msg = "ChatGPT retornou resultado vazio ou inválido. Verifique sua chave de API e tente novamente."
            print(f"[DEBUG] {error_msg}", flush=True)
            raise Exception(error_msg)
        
        # Usa diretamente o retorno do ChatGPT (mapeando para existing_codes quando aplicável)
        codes = codes_ret.copy()
        groups = groups_ret.copy()
        
        # GARANTIA DE F17: Adiciona códigos existentes ao dicionário de códigos se não estiverem lá
        # Isso garante que respostas que o GPT ignorou (por já existirem) sejam encontradas
        for desc, code in existing_codes.items():
             # Normaliza a chave do F17 para garantir match
             desc_norm = self.coding_system.correct_text(desc).strip()
             if desc_norm not in codes:
                 codes[desc_norm] = code
                 # Cria grupo fictício se não existir, para o relatório
                 if desc_norm not in groups:
                     groups[desc_norm] = []

        # se alguma descrição do ChatGPT corresponder ao F17, ajuste para usar a descrição do F17
        normalized_map = {self.coding_system.correct_text(desc).strip().lower(): desc for desc in existing_codes.keys()}
        
        # Mapa reverso de códigos F17 para evitar conflitos
        # code -> description
        existing_codes_reverse = {v: k for k, v in existing_codes.items()}
        
        # Encontra o maior código em uso para gerar novos
        if existing_codes:
            max_existing_code = max(existing_codes.values())
        else:
            max_existing_code = 9
            
        adjusted_codes = {}
        adjusted_groups = {}
        
        # Processa retorno do ChatGPT validando conflitos
        for titulo, respostas in groups.items():
            titulo_norm = self.coding_system.correct_text(titulo).strip().lower()
            
            # Caso 1: Título bate com F17 (ex: "Tubarão") -> Usa código F17
            if titulo_norm in normalized_map:
                f17_desc = normalized_map[titulo_norm]
                code_to_use = existing_codes[f17_desc]
                
                adjusted_codes[f17_desc] = code_to_use
                adjusted_groups[f17_desc] = respostas
                
            else:
                # Caso 2: Título Novo (ex: "Chapecó")
                proposed_code = codes.get(titulo)
                
                # Verifica se o código proposto já existe no F17 para OUTRA coisa
                if proposed_code in existing_codes_reverse:
                    # Conflito! O código 1 é "Tubarão", mas GPT quer usar para "Chapecó"
                    # Gera novo código
                    max_existing_code += 1
                    final_code = max_existing_code
                else:
                    # Código livre ou é novo
                    # Mas cuidado: se GPT retornou 1 e não existe no F17, ok. 
                    # Mas se retornou 10, ok.
                    # Melhor garantir que seja > max do F17 se for novo
                    if proposed_code is not None and proposed_code <= max(existing_codes.values() or [0]) and proposed_code not in existing_codes.values():
                         # GPT inventou um código baixo livre? Aceita.
                         final_code = proposed_code
                    elif proposed_code is not None and proposed_code > max(existing_codes.values() or [0]):
                         final_code = proposed_code
                         if final_code > max_existing_code: max_existing_code = final_code
                    else:
                         # Sem código ou conflito, gera novo
                         max_existing_code += 1
                         final_code = max_existing_code
                
                adjusted_codes[titulo] = final_code
                adjusted_groups[titulo] = respostas
        
        # Re-adiciona F17 que podem ter sido perdidos no loop acima se não estavam em 'groups'
        for desc, code in existing_codes.items():
             if desc not in adjusted_codes:
                 adjusted_codes[desc] = code
                 adjusted_groups[desc] = []

        codes = adjusted_codes
        groups = adjusted_groups
        detailed_report = self.coding_system.create_detailed_report(codes, groups, question_name, processing_method)
        print(f"[DEBUG] ✅ Processamento concluído usando: CHATGPT (OpenAI)", flush=True)
        
        # CONSOLIDAÇÃO FINAL DOS CÓDIGOS
        # Garante que 'codes' (usado para o loop de classificação) e 'final_codes' (retorno)
        # contenham a união de tudo: F17 + GPT + Retry + Auto
        
        # Adiciona F17
        for desc, code in existing_codes.items():
            if desc not in codes:
                codes[desc] = code
        
        # Garante que novos códigos do Auto/Retry estejam em 'codes'
        # (já foram adicionados a codes_ret que é a base de codes, mas reforçando)
        
        print(f"[DEBUG] Códigos finais consolidados: {len(codes)} itens", flush=True)
        # print(f"[DEBUG] Amostra de códigos: {list(codes.items())[:5]}", flush=True)

        # Cria mapeamento de respostas para códigos (com normalização)
        response_to_code = {}
        total_respostas_mapeadas = 0
        
        # Reconstrói response_to_code com base no dicionário consolidado 'codes' e 'groups'
        # Se um código está em 'codes' mas não em 'groups', cria entrada dummy no loop
        
        all_keys = set(groups.keys()) | set(codes.keys())
        
        for titulo in all_keys:
            code = codes.get(titulo)
            respostas = groups.get(titulo, [])
            
            if code:
                # Adiciona o próprio título do grupo como chave de busca
                titulo_str = str(titulo).strip()
                titulo_norm = self.coding_system.normalize_text(titulo_str)
                response_to_code[titulo_str] = (code, titulo_str)
                response_to_code[titulo_norm] = (code, titulo_str)
                
                for resposta in respostas:
                    resp_norm = self.coding_system.normalize_text(str(resposta))
                    response_to_code[str(resposta).strip()] = (code, resposta)
                    response_to_code[resp_norm] = (code, resposta)
                    total_respostas_mapeadas += 1
                    
        print(f"[DEBUG] Mapeamento criado: {len(all_keys)} grupos, {total_respostas_mapeadas} respostas mapeadas, {len(response_to_code)} chaves no dicionário", flush=True)
        print(f"[DEBUG] Total de respostas originais para processar: {len(question_data)}", flush=True)
        
        code_column = []
        response_column = []
        
        # Se for semi-aberta, precisamos reconstruir a coluna misturando os originais numéricos com os codificados
        if q_type == "semi-aberta":
             # Inicializa com os valores originais (assumindo que são códigos)
            code_column = [x for x in question_data]
            response_column = [x for x in question_data]
            
            # Processa apenas os itens que foram para a IA
            # Mapeamento inverso dos grupos para encontrar códigos
            text_to_code = {}
            # Normaliza chaves do groups_ret/codes_ret para busca
            for titulo, respostas in groups.items():
                 c = codes.get(titulo)
                 if c:
                     for r in respostas:
                         text_to_code[self.coding_system.normalize_text(str(r))] = c
                         text_to_code[str(r).strip()] = c # Original também
            
            # Atualiza apenas os índices que eram texto
            for idx, original_resp in zip(indices_to_process, items_to_process):
                # Tenta encontrar o código
                resp_norm = self.coding_system.normalize_text(str(original_resp))
                found_code = text_to_code.get(resp_norm) or text_to_code.get(str(original_resp).strip())
                
                # Tenta fuzzy se não achou (reuso da lógica abaixo seria ideal, mas simplificando aqui)
                if not found_code:
                     # Tenta achar no response_to_code criado anteriormente (se existir) ou busca direta
                     # Por hora, marca ERROR se não achar, ou usa a lógica de match completa
                     pass

                # ATENÇÃO: A lógica abaixo de loop principal já faz o match robusto.
                # Vamos deixar o loop principal rodar APENAS para os items_to_process se for semi-aberta?
                # Não, o loop principal espera iterar sobre 'question_data'.
                # Vamos ajustar o loop principal para lidar com o tipo de questão.
                pass 

        # REFAZENDO O LOOP PRINCIPAL PARA SUPORTAR OS TIPOS
        code_column = []
        response_column = []
        
        for i, resp in enumerate(question_data):
            # Se for semi-aberta e este índice NÃO foi processado (era número), mantém original
            if q_type == "semi-aberta" and i not in indices_to_process:
                code_column.append(resp) # Mantém o número original
                response_column.append(resp)
                continue
                
            found = False
            
            # Se for código numérico explícito (NS/NR) em questão aberta, mantém
            if isinstance(resp, (int, float)):
                resp_num = int(resp)
                if resp_num in [55, 66, 77, 88, 98, 99]:
                    code_column.append(resp_num)
                    response_column.append(resp)
                    found = True
            
            if not found:
                # Normaliza resposta original para busca
                resp_str = str(resp).strip()
                resp_norm = self.coding_system.normalize_text(resp_str)
                
                # Tenta match exato (sem normalização primeiro)
                if resp_str in response_to_code:
                    code, resp_original = response_to_code[resp_str]
                    code_column.append(code)
                    response_column.append(resp)
                    found = True
                # Tenta match exato normalizado
                elif resp_norm in response_to_code:
                    code, resp_original = response_to_code[resp_norm]
                    code_column.append(code)
                    response_column.append(resp)
                    found = True
                else:
                    # Tenta match parcial/fuzzy
                    best_match = None
                    best_score = 0
                    for resp_norm_key, (code, resp_original) in response_to_code.items():
                        # Match exato após normalização
                        if resp_norm == resp_norm_key:
                            best_match = (code, resp)
                            best_score = 100
                            break
                        # Match parcial (substring)
                        if resp_norm in resp_norm_key or resp_norm_key in resp_norm:
                            score = min(len(resp_norm), len(resp_norm_key)) / max(len(resp_norm), len(resp_norm_key), 1)
                            if score > best_score:
                                best_score = score
                                best_match = (code, resp)
                    
                    if best_match and best_score >= 0.8:  # Threshold de 80%
                        code, resp_original = best_match
                        code_column.append(code)
                        response_column.append(resp)
                        found = True
                    else:
                        # Tenta fuzzy matching como último recurso
                        from fuzzywuzzy import fuzz
                        for resp_norm_key, (code, resp_original) in response_to_code.items():
                            score = fuzz.ratio(resp_norm, resp_norm_key)
                            if score > best_score:
                                best_score = score
                                best_match = (code, resp)
                        
                        if best_match and best_score >= 85:  # Threshold de 85% para fuzzy
                            code, resp_original = best_match
                            code_column.append(code)
                            response_column.append(resp)
                            found = True
            
            if not found:
                # Não encontrou match - marca como ERROR
                resp_debug = str(resp).strip()
                resp_norm_debug = self.coding_system.normalize_text(resp_debug)
                print(f"[DEBUG] Resposta não mapeada: '{resp_debug}' (normalizada: '{resp_norm_debug}')", flush=True)
                if len(response_to_code) > 0:
                     # Debug limitado
                     pass
                code_column.append('ERROR')
                response_column.append(resp)
        new_codes = {desc: code for desc, code in codes.items() if desc not in existing_codes}
        print(f"[DEBUG] Saída de process_single_question_with_chatgpt: codes={codes}, new_codes={new_codes}", flush=True)
        
        # RECONSTRUÇÃO DO DICIONÁRIO 'GROUPS' PARA RELATÓRIO COMPLETO
        # O 'groups' atual tem apenas a amostra do GPT. Precisamos de TODAS as respostas originais agrupadas
        # para que o relatório mostre todas as variações (ex: Tubara, Tubarao, Tubarão)
        
        full_groups = {}
        # Inicializa com as chaves conhecidas
        for desc in codes.keys():
            full_groups[desc] = []
            
        # Itera sobre o resultado classificado (resposta -> código)
        # Precisa do mapeamento reverso código -> descrição
        code_to_desc = {v: k for k, v in codes.items()}
        
        for resp, code in zip(response_column, code_column):
            if code != 'ERROR' and code in code_to_desc:
                desc = code_to_desc[code]
                # Adiciona TODAS as respostas para auditoria completa (Opção B)
                # Se preferir lista limpa, descomente o if abaixo
                # if resp not in full_groups[desc]:
                full_groups[desc].append(resp)
        
        # Atualiza o objeto groups para o relatório
        groups = full_groups
        
        # Regera o relatório com os dados completos
        detailed_report = self.coding_system.create_detailed_report(codes, groups, question_name, processing_method)
        
        return {
            'question_name': question_name,
            'total_responses': len(question_data),
            'valid_responses': len(question_data),
            'existing_codes': existing_codes,
            'final_codes': codes,
            'new_codes': new_codes,
            'groups': groups, # Agora contém TODAS as respostas originais agrupadas
            'detailed_report': detailed_report,
            'code_column': code_column,
            'response_column': response_column,
            'processing_method': processing_method or 'desconhecido',
            'question_type': q_type,
            'statistics': {
                'total_codes': len(codes),
                'new_codes_count': len(new_codes),
                'groups_with_multiple': len([g for g in groups.values() if len(g) > 1]),
                'largest_group_size': max([len(g) for g in groups.values()]) if groups else 0
            }
        }
    
    def save_improved_outputs(self, result: Dict[str, Any], output_dir: str = ".") -> Dict[str, str]:
        """Salva arquivos de saída melhorados"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = result['question_name'].replace('/', '_').replace('?', '').replace(':', '')[:30]
        base_name = f"{safe_name}_{timestamp}"
        
        files_created = {}
        
        # 1. Banco codificado
        banco_path = os.path.join(output_dir, f"{base_name}_banco_codificado.xlsx")
        banco_df = pd.DataFrame({
            'Código': result['code_column'],
            'Resposta': result['response_column']
        })
        banco_df.to_excel(banco_path, index=False)
        files_created['banco'] = banco_path
        
        # 2. F17 atualizado
        f17_path = os.path.join(output_dir, f"{base_name}_f17_atualizado.xlsx")
        
        # Padroniza descrições antes de salvar
        # Separa o que é do F17 original (confiável) do que é novo (precisa de revisão)
        original_f17_descs = set(result['existing_codes'].keys())
        
        final_f17_list = []
        for desc, code in sorted(result['final_codes'].items(), key=lambda x: x[1]):
            final_desc = desc
            # Se é um código novo (não estava no F17 original), tenta corrigir a grafia
            if desc not in original_f17_descs:
                # Usa o corretor do sistema (que pode usar GPT se disponível ou local)
                # A função standardize_with_chatgpt já verifica disponibilidade
                try:
                    # Remove aspas extras se houver
                    clean_desc = desc.strip('"').strip("'")
                    # Tenta padronizar via GPT ou corretor local
                    if hasattr(self.coding_system, 'standardize_with_chatgpt') and getattr(self.coding_system, 'chatgpt_available', False):
                         final_desc = self.coding_system.standardize_with_chatgpt(clean_desc)
                    else:
                         final_desc = self.coding_system.correct_text(clean_desc)
                except Exception:
                    final_desc = desc # Mantém original em caso de erro
            
            final_f17_list.append({'Código': code, 'Descrição': final_desc})

        f17_df = pd.DataFrame(final_f17_list)
        f17_df.to_excel(f17_path, index=False)
        files_created['f17'] = f17_path
        
        # 3. Relatório detalhado de agrupamentos
        relatorio_path = os.path.join(output_dir, f"{base_name}_relatorio_agrupamentos.txt")
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            f.write(result['detailed_report'])
        files_created['relatorio'] = relatorio_path
        
        # 4. Resumo estatístico
        resumo_path = os.path.join(output_dir, f"{base_name}_resumo_estatistico.txt")
        resumo_content = self.create_statistical_summary(result)
        with open(resumo_path, 'w', encoding='utf-8') as f:
            f.write(resumo_content)
        files_created['resumo'] = resumo_path
        
        return files_created
    
    def create_statistical_summary(self, result: Dict[str, Any]) -> str:
        """Cria resumo estatístico do processamento"""
        
        lines = []
        lines.append(f"RESUMO ESTATÍSTICO - {result['question_name']}")
        lines.append("=" * 60)
        lines.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        lines.append("")
        
        # Método de processamento
        processing_method = result.get('processing_method', 'desconhecido')
        method_display = {
            'chatgpt': '🤖 ChatGPT (OpenAI GPT-4o)',
            'fallback_local': '🔧 Agrupador Local (Fallback)',
            'desconhecido': '❓ Método Desconhecido'
        }
        lines.append("MÉTODO DE PROCESSAMENTO:")
        lines.append(f"- {method_display.get(processing_method, f'❓ {processing_method}')}")
        lines.append("")
        
        # Calcula frequências REAIS baseadas na coluna de códigos final
        # (result['groups'] tem apenas exemplos únicos, não serve para contagem estatística)
        code_counts = {}
        for code in result['code_column']:
            if code != 'ERROR':
                code_counts[code] = code_counts.get(code, 0) + 1
                
        # Estatísticas gerais
        lines.append("ESTATÍSTICAS GERAIS:")
        lines.append(f"- Total de respostas: {result['total_responses']}")
        lines.append(f"- Respostas válidas: {result['valid_responses']}")
        lines.append(f"- Códigos existentes (F17): {len(result['existing_codes'])}")
        lines.append(f"- Novos códigos criados: {result['statistics']['new_codes_count']}")
        lines.append(f"- Total de códigos finais: {result['statistics']['total_codes']}")
        lines.append("")
        
        # Análise de agrupamentos
        # Recalcula métricas com base nas frequências reais
        groups_with_multiple = len([c for c, count in code_counts.items() if count > 1])
        largest_group_size = max(code_counts.values()) if code_counts else 0
        
        lines.append("ANÁLISE DE AGRUPAMENTOS:")
        lines.append(f"- Grupos com múltiplas respostas: {groups_with_multiple}")
        lines.append(f"- Maior grupo: {largest_group_size} respostas")
        lines.append("")
        
        # Códigos existentes utilizados
        existing_used = []
        for desc, code in result['existing_codes'].items():
            count = code_counts.get(code, 0)
            if count > 0:
                existing_used.append((desc, code, count))
        
        if existing_used:
            lines.append("CÓDIGOS EXISTENTES UTILIZADOS:")
            for desc, code, size in sorted(existing_used, key=lambda x: x[1]):
                lines.append(f"- Código {code}: {desc} ({size} respostas)")
            lines.append("")
        
        # Novos códigos criados
        if result['new_codes']:
            lines.append("NOVOS CÓDIGOS CRIADOS:")
            for desc, code in sorted(result['new_codes'].items(), key=lambda x: x[1]):
                count = code_counts.get(code, 0)
                lines.append(f"- Código {code}: {desc} ({count} respostas)")
            lines.append("")
        
        # Grupos com múltiplas respostas (Top 10)
        # Usa a contagem real para ordenar
        multi_groups = []
        for desc, code in result['final_codes'].items():
            count = code_counts.get(code, 0)
            if count > 1:
                # Pega exemplos do grupo para exibição
                examples = result['groups'].get(desc, [])
                multi_groups.append((desc, code, count, examples))
                
        if multi_groups:
            lines.append("PRINCIPAIS AGRUPAMENTOS:")
            for desc, code, count, examples in sorted(multi_groups, key=lambda x: x[2], reverse=True)[:10]:
                lines.append(f"- Código {code} ({count} respostas): {desc}")
                for resp in examples[:3]:
                    lines.append(f"  • {resp}")
                if len(examples) > 3:
                    lines.append(f"  • ... e mais {len(examples) - 3} variações")
                lines.append("")
        
        return "\n".join(lines)

