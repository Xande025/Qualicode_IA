from dotenv import load_dotenv
from openai_compat import get_openai_client
import os

load_dotenv()

class ChatGPTClient:
    """Cliente para consultas ao ChatGPT/OpenAI usando a nova API"""
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = get_openai_client(api_key=self.api_key)

    def ask(self, prompt, model="gpt-3.5-turbo"):
        resp = self.client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}])
        # compatibilidade com estrutura antiga e nova
        try:
            return resp.choices[0].message.content
        except Exception:
            try:
                return resp.choices[0].message.get('content')
            except Exception:
                return str(resp)
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
    
    def process_single_question_improved(self, question_data: List[Any], 
                                       existing_codes: Dict[str, int],
                                       question_name: str) -> Dict[str, Any]:
        """Processa uma questão específica com sistema melhorado"""
        
        print(f"🔧 PROCESSANDO QUESTÃO: {question_name}")
        print("=" * 60)
        
        # Estatísticas iniciais
        total_responses = len(question_data)
        valid_responses = [r for r in question_data if pd.notna(r) and str(r).strip()]
        text_responses = [r for r in valid_responses if isinstance(r, str)]
        numeric_responses = [r for r in valid_responses if isinstance(r, (int, float))]
        
        print(f"📊 Estatísticas iniciais:")
        print(f"   - Total de respostas: {total_responses}")
        print(f"   - Respostas válidas: {len(valid_responses)}")
        print(f"   - Respostas em texto: {len(text_responses)}")
        print(f"   - Respostas numéricas: {len(numeric_responses)}")
        
        # Mostra amostra dos dados
        print(f"\n📝 Amostra das respostas originais:")
        for i, response in enumerate(valid_responses[:15], 1):
            print(f"   {i:2d}. {response}")
        if len(valid_responses) > 15:
            print(f"   ... e mais {len(valid_responses) - 15} respostas")
        
        # Mostra códigos existentes
        print(f"\n📋 Códigos existentes no F17:")
        for desc, code in sorted(existing_codes.items(), key=lambda x: x[1]):
            print(f"   {code:2d} | {desc}")
        
        # Processa com sistema melhorado
        print(f"\n🔧 Processando com sistema melhorado...")
        codes, groups, detailed_report = self.coding_system.process_responses_improved(
            question_data, existing_codes, question_name
        )
        
        # Cria colunas de saída
        code_column, response_column = self.coding_system.create_output_columns_detailed(
            question_data, codes, groups
        )
        
        # Estatísticas finais
        new_codes = {desc: code for desc, code in codes.items() if desc not in existing_codes}
        
        print(f"\n✅ Processamento concluído!")
        print(f"   - Códigos existentes utilizados: {len(existing_codes)}")
        print(f"   - Novos códigos criados: {len(new_codes)}")
        print(f"   - Total de códigos finais: {len(codes)}")
        print(f"   - Grupos com agrupamentos: {len([g for g in groups.values() if len(g) > 1])}")
        
        # Mostra novos códigos criados
        if new_codes:
            print(f"\n🆕 Novos códigos criados:")
            for desc, code in sorted(new_codes.items(), key=lambda x: x[1]):
                group_size = len(groups.get(desc, []))
                print(f"   {code:2d} | {desc} ({group_size} respostas)")
        
        return {
            'question_name': question_name,
            'total_responses': total_responses,
            'valid_responses': len(valid_responses),
            'existing_codes': existing_codes,
            'final_codes': codes,
            'new_codes': new_codes,
            'groups': groups,
            'detailed_report': detailed_report,
            'code_column': code_column,
            'response_column': response_column,
            'statistics': {
                'total_codes': len(codes),
                'new_codes_count': len(new_codes),
                'groups_with_multiple': len([g for g in groups.values() if len(g) > 1]),
                'largest_group_size': max([len(g) for g in groups.values()]) if groups else 0
            }
        }
    
    def process_single_question_with_chatgpt(self, question_data: list, existing_codes: dict, question_name: str) -> dict:
        print(f"[DEBUG] Entrou em process_single_question_with_chatgpt para: {question_name}", flush=True)
        print(f"[DEBUG] Dados recebidos: question_data={question_data}, existing_codes={existing_codes}", flush=True)
        # Converte códigos existentes para lista de strings para o prompt
        f17_list = [f"{code} | {desc}" for desc, code in existing_codes.items()]
        try:
            # Agora group_with_chatgpt retorna (codes_dict, groups_dict) ou ({}, {}) em caso de erro
            codes_ret, groups_ret = self.coding_system.group_with_chatgpt(question_data, f17=f17_list)
        except Exception as e_gpt:
            print(f"[DEBUG] group_with_chatgpt lançou exceção: {e_gpt}. Usando fallback local.", flush=True)
            codes_ret, groups_ret = {}, {}

        if not codes_ret or not groups_ret:
            print(f"[DEBUG] group_with_chatgpt retornou inválido/vazio. Fazendo fallback para agrupador local.", flush=True)
            codes, groups, detailed_report = self.coding_system.process_responses_improved(
                question_data, existing_codes, question_name
            )
        else:
            # Usa diretamente o retorno do ChatGPT (mapeando para existing_codes quando aplicável)
            codes = codes_ret.copy()
            groups = groups_ret.copy()
            # se alguma descrição do ChatGPT corresponder ao F17, ajuste para usar a descrição do F17
            normalized_map = {self.coding_system.correct_text(desc).strip().lower(): desc for desc in existing_codes.keys()}
            adjusted_codes = {}
            adjusted_groups = {}
            for titulo, respostas in groups.items():
                titulo_norm = self.coding_system.correct_text(titulo).strip().lower()
                if titulo_norm in normalized_map:
                    f17_desc = normalized_map[titulo_norm]
                    adjusted_codes[f17_desc] = existing_codes[f17_desc]
                    adjusted_groups[f17_desc] = respostas
                else:
                    adjusted_codes[titulo] = codes.get(titulo, None)
                    adjusted_groups[titulo] = respostas
            codes = adjusted_codes
            groups = adjusted_groups
            detailed_report = self.coding_system.create_detailed_report(codes, groups, question_name)
        code_column = []
        response_column = []
        for resp in question_data:
            found = False
            for titulo, respostas in groups.items():
                if resp in respostas:
                    code_column.append(codes[titulo])
                    response_column.append(resp)
                    found = True
                    break
            if not found:
                code_column.append('ERROR')
                response_column.append(resp)
        new_codes = {desc: code for desc, code in codes.items() if desc not in existing_codes}
        print(f"[DEBUG] Saída de process_single_question_with_chatgpt: codes={codes}, new_codes={new_codes}", flush=True)
        return {
            'question_name': question_name,
            'total_responses': len(question_data),
            'valid_responses': len(question_data),
            'existing_codes': existing_codes,
            'final_codes': codes,
            'new_codes': new_codes,
            'groups': groups,
            'detailed_report': detailed_report,
            'code_column': code_column,
            'response_column': response_column,
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
        # Apenas código e título do grupo (frase corrigida)
        f17_df = pd.DataFrame([
            {'Código': code, 'Descrição': desc}
            for desc, code in sorted(result['final_codes'].items(), key=lambda x: x[1])
        ])
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
        
        # Estatísticas gerais
        lines.append("ESTATÍSTICAS GERAIS:")
        lines.append(f"- Total de respostas: {result['total_responses']}")
        lines.append(f"- Respostas válidas: {result['valid_responses']}")
        lines.append(f"- Códigos existentes (F17): {len(result['existing_codes'])}")
        lines.append(f"- Novos códigos criados: {result['statistics']['new_codes_count']}")
        lines.append(f"- Total de códigos finais: {result['statistics']['total_codes']}")
        lines.append("")
        
        # Análise de agrupamentos
        lines.append("ANÁLISE DE AGRUPAMENTOS:")
        lines.append(f"- Grupos com múltiplas respostas: {result['statistics']['groups_with_multiple']}")
        lines.append(f"- Maior grupo: {result['statistics']['largest_group_size']} respostas")
        lines.append("")
        
        # Códigos existentes utilizados
        existing_used = []
        for desc, code in result['existing_codes'].items():
            group_size = len(result['groups'].get(desc, []))
            if group_size > 0:
                existing_used.append((desc, code, group_size))
        
        if existing_used:
            lines.append("CÓDIGOS EXISTENTES UTILIZADOS:")
            for desc, code, size in sorted(existing_used, key=lambda x: x[1]):
                lines.append(f"- Código {code}: {desc} ({size} respostas)")
            lines.append("")
        
        # Novos códigos criados
        if result['new_codes']:
            lines.append("NOVOS CÓDIGOS CRIADOS:")
            for desc, code in sorted(result['new_codes'].items(), key=lambda x: x[1]):
                group_size = len(result['groups'].get(desc, []))
                lines.append(f"- Código {code}: {desc} ({group_size} respostas)")
            lines.append("")
        
        # Grupos com múltiplas respostas
        multi_groups = [(desc, responses) for desc, responses in result['groups'].items() if len(responses) > 1]
        if multi_groups:
            lines.append("PRINCIPAIS AGRUPAMENTOS:")
            for desc, responses in sorted(multi_groups, key=lambda x: len(x[1]), reverse=True)[:10]:
                code = result['final_codes'].get(desc, '?')
                lines.append(f"- Código {code} ({len(responses)} respostas): {desc}")
                for resp in responses[:3]:
                    lines.append(f"  • {resp}")
                if len(responses) > 3:
                    lines.append(f"  • ... e mais {len(responses) - 3} respostas")
                lines.append("")
        
        return "\n".join(lines)

def demo_agent_improved():
    """Demonstração do agente melhorado"""
    print("🚀 DEMONSTRAÇÃO DO AGENTE IPO MELHORADO")
    print("=" * 70)
    
    # Dados de exemplo com erros ortográficos (simulando dados reais)
    question_data = [
        "Melhorou a saude",
        "Melhorou a saúde do bairro", 
        "Saude melhorou muito",
        "Melhorou os postos de saude",
        "Arrumou as estradas",
        "Consertou as ruas", 
        "Asfalto novo",
        "Pavimentacao das ruas",
        "Estradas melhores",
        "Asfaltamento da cidade",
        "Nao fez nada",
        "Nada foi feito",
        "Não vejo melhoria",
        "Construiu escola nova",
        "Escola reformada",
        "Cursos no instituto",
        "Atuacao nas enchentes",
        "Ajudou na enchente",
        "Durante as enchentez foi prestativo",
        "Apoio na enchente",
        "Suporte nas enchentes",
        "Cemai",
        "Obra do cemai",
        "Centro Cemai",
        77,
        88,
        99
    ]
    
    # Códigos existentes no F17
    existing_codes = {
        "Melhoria na área da saúde": 1,
        "Pavimentação/asfalto": 2,
        "Educação": 3,
        "Revitalização do calçadão": 4,
        "Iluminação de led": 5,
        "Atrair novas empresas/desenvolvimento": 6,
        "Revitalização da Avenida Ruperti Filho": 7,
        "Cursos de qualificação": 8,
        "Não fez nada": 9
    }
    
    # Processa com agente melhorado
    agent = FinalIPOAgentImproved()
    result = agent.process_single_question_improved(
        question_data, 
        existing_codes,
        "QUESTÃO 15 - PRINCIPAL REALIZAÇÃO DO GOVERNO"
    )
    
    # Salva arquivos
    print(f"\n💾 Salvando arquivos...")
    files_created = agent.save_improved_outputs(result)
    
    print(f"\n📁 Arquivos criados:")
    for tipo, caminho in files_created.items():
        print(f"   - {tipo.upper()}: {os.path.basename(caminho)}")
    
    print(f"\n📋 AMOSTRA DO RELATÓRIO DETALHADO:")
    print("=" * 50)
    print(result['detailed_report'][:800] + "..." if len(result['detailed_report']) > 800 else result['detailed_report'])
    
    print(f"\n🎉 DEMONSTRAÇÃO CONCLUÍDA!")
    print(f"   ✅ {result['statistics']['total_codes']} códigos finais")
    print(f"   ✅ {result['statistics']['new_codes_count']} novos códigos criados")
    print(f"   ✅ {result['statistics']['groups_with_multiple']} grupos com agrupamentos")
    print(f"   ✅ Relatório detalhado como modelo fornecido")
    
    return result, files_created

if __name__ == "__main__":
    demo_agent_improved()

