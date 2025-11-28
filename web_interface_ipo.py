"""
Interface Web Intuitiva para Agente IPO
- Upload de arquivos (Banco + F17)
- Questão específica (colar dados)
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import pandas as pd
import os
import tempfile
from datetime import datetime
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import threading
import uuid
import time
import shutil
import zipfile

# Carrega variáveis de ambiente do .env
load_dotenv()

from final_ipo_agent_improved import FinalIPOAgentImproved

app = Flask(__name__)

# Configurações de segurança
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ipo_agent_secret_key_2025_production')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

# Configurações de diretório (compatível Windows/Linux)
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', os.path.join(tempfile.gettempdir(), 'ipo_uploads'))
RESULTS_FOLDER = os.getenv('RESULTS_FOLDER', os.path.join(tempfile.gettempdir(), 'ipo_results'))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

agent = FinalIPOAgentImproved()

# Armazenamento de tarefas em memória (em produção usar Redis/DB)
tasks = {}

def process_batch_task(task_id, banco_path, f17_path):
    """Função executada em thread separada"""
    try:
        tasks[task_id]['state'] = 'PROCESSING'
        tasks[task_id]['status'] = 'Lendo arquivos...'
        tasks[task_id]['progress'] = 5
        
        # Carrega arquivos
        try:
            banco_df = pd.read_excel(banco_path)
            f17_xl = pd.ExcelFile(f17_path)
        except Exception as e:
            raise Exception(f"Erro ao ler arquivos Excel: {str(e)}")
            
        tasks[task_id]['progress'] = 10
        total_cols = len(banco_df.columns)
        processed_count = 0
        
        # Diretório para resultados desta tarefa
        task_dir = os.path.join(RESULTS_FOLDER, task_id)
        os.makedirs(task_dir, exist_ok=True)
        
        results_summary = []
        
        # Itera sobre colunas
        for col_idx, col_name in enumerate(banco_df.columns):
            col_safe = str(col_name).strip()
            tasks[task_id]['status'] = f'Processando questão: {col_safe}'
            
            # Tenta encontrar aba correspondente no F17
            # Procura por match exato ou parcial no nome da aba
            f17_sheet_name = None
            for sheet in f17_xl.sheet_names:
                if str(sheet).strip() == col_safe:
                    f17_sheet_name = sheet
                    break
            
            # Se não achou exato, tenta conter
            if not f17_sheet_name:
                for sheet in f17_xl.sheet_names:
                    if col_safe in str(sheet) or str(sheet) in col_safe:
                        f17_sheet_name = sheet
                        break
            
            question_data = banco_df[col_name].tolist()
            existing_codes = {}
            
            if f17_sheet_name:
                try:
                    df_f17 = pd.read_excel(f17_path, sheet_name=f17_sheet_name)
                    # Assume colunas 0 (código) e 1 (descrição)
                    if len(df_f17.columns) >= 2:
                        for _, row in df_f17.iterrows():
                            try:
                                code = int(row.iloc[0])
                                desc = str(row.iloc[1])
                                existing_codes[desc] = code
                            except:
                                continue
                except Exception as e:
                    print(f"Erro ao ler aba {f17_sheet_name}: {e}")
            
            # Processa a questão
            try:
                result = agent.process_single_question_with_chatgpt(
                    question_data,
                    existing_codes,
                    col_safe
                )
                
                # Salva resultados parciais
                agent.save_improved_outputs(result, task_dir)
                results_summary.append(f"Questão '{col_safe}': Sucesso ({result['question_type']})")
                
            except Exception as e:
                print(f"Erro ao processar questão {col_safe}: {e}")
                results_summary.append(f"Questão '{col_safe}': Erro - {str(e)}")
            
            processed_count += 1
            progress = 10 + (processed_count / total_cols * 80)
            tasks[task_id]['progress'] = progress
            
        # Finalização: Cria ZIP com tudo
        tasks[task_id]['status'] = 'Gerando pacote final...'
        zip_filename = f"resultado_completo_{task_id}.zip"
        zip_path = os.path.join(RESULTS_FOLDER, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(task_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), file)
                    
        # Limpa diretório temporário da tarefa
        shutil.rmtree(task_dir)
        
        tasks[task_id]['result_file'] = zip_filename
        tasks[task_id]['progress'] = 100
        tasks[task_id]['state'] = 'COMPLETED'
        tasks[task_id]['status'] = 'Concluído com sucesso!'
        
    except Exception as e:
        print(f"Erro fatal na tarefa {task_id}: {e}")
        tasks[task_id]['state'] = 'ERROR'
        tasks[task_id]['error'] = str(e)

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_files():
    """Upload de arquivos completos"""
    if request.method == 'GET':
        return render_template('upload.html')
    
    try:
        # Verifica se arquivos foram enviados
        if 'banco_file' not in request.files or 'f17_file' not in request.files:
            return jsonify({'success': False, 'error': 'Arquivos não enviados'})
        
        banco_file = request.files['banco_file']
        f17_file = request.files['f17_file']
        
        if banco_file.filename == '' or f17_file.filename == '':
            return jsonify({'success': False, 'error': 'Selecione os arquivos'})
        
        # Salva arquivos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        banco_path = os.path.join(UPLOAD_FOLDER, f"banco_{timestamp}_{secure_filename(banco_file.filename)}")
        f17_path = os.path.join(UPLOAD_FOLDER, f"f17_{timestamp}_{secure_filename(f17_file.filename)}")
        
        banco_file.save(banco_path)
        f17_file.save(f17_path)
        
        # Cria tarefa
        task_id = str(uuid.uuid4())
        tasks[task_id] = {
            'state': 'PENDING',
            'status': 'Iniciando...',
            'progress': 0,
            'created_at': time.time()
        }
        
        # Inicia thread
        thread = threading.Thread(target=process_batch_task, args=(task_id, banco_path, f17_path))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Processamento iniciado'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/task_status/<task_id>')
def task_status(task_id):
    """Retorna status da tarefa"""
    task = tasks.get(task_id)
    if not task:
        return jsonify({'state': 'ERROR', 'error': 'Tarefa não encontrada'})
    return jsonify(task)

@app.route('/download_batch/<task_id>')
def download_batch(task_id):
    """Download do resultado final"""
    task = tasks.get(task_id)
    if not task or task['state'] != 'COMPLETED':
        flash('Arquivo não disponível', 'error')
        return redirect(url_for('index'))
        
    filename = task.get('result_file')
    return send_file(os.path.join(RESULTS_FOLDER, filename), as_attachment=True)

@app.route('/questao_especifica', methods=['GET', 'POST'])
def questao_especifica():
    """Processamento de questão específica"""
    if request.method == 'GET':
        return render_template('questao_especifica.html')
    print("[DEBUG] Entrou no endpoint /questao_especifica", flush=True)
    try:
        # Recebe dados do formulário
        question_name = request.form.get('question_name', '').strip()
        question_data_text = request.form.get('question_data', '').strip()
        f17_codes_text = request.form.get('f17_codes', '').strip()
        print(f"[DEBUG] Dados recebidos:\nquestion_name: {question_name}\nquestion_data_text: {question_data_text}\nf17_codes_text: {f17_codes_text}", flush=True)
        if not all([question_name, question_data_text, f17_codes_text]):
            print("[DEBUG] Falta algum campo obrigatório", flush=True)
            return jsonify({
                'success': False,
                'error': 'Por favor, preencha todos os campos'
            })
        # Processa dados da questão
        question_data = []
        for line in question_data_text.split('\n'):
            line = line.strip()
            if line:
                try:
                    if '.' in line:
                        question_data.append(float(line))
                    else:
                        question_data.append(int(line))
                except ValueError:
                    question_data.append(line)
        # Processa códigos F17
        existing_codes = {}
        for line in f17_codes_text.split('\n'):
            line = line.strip()
            if line and '|' in line:
                parts = line.split('|', 1)
                if len(parts) == 2:
                    try:
                        code = int(parts[0].strip())
                        description = parts[1].strip()
                        existing_codes[description] = code
                    except ValueError:
                        continue
        print(f"[DEBUG] Dados processados:\nquestion_data: {question_data}\nexisting_codes: {existing_codes}", flush=True)
        if not question_data:
            print("[DEBUG] Nenhum dado válido encontrado na questão", flush=True)
            return jsonify({
                'success': False,
                'error': 'Nenhum dado válido encontrado na questão'
            })
        if not existing_codes:
            print("[DEBUG] Nenhum código F17 válido encontrado", flush=True)
            return jsonify({
                'success': False,
                'error': 'Nenhum código F17 válido encontrado'
            })
        print("[DEBUG] Chamando process_single_question_with_chatgpt", flush=True)
        try:
            result = agent.process_single_question_with_chatgpt(
                question_data, 
                existing_codes,
                question_name
            )
            print("[DEBUG] Retornou do process_single_question_with_chatgpt", flush=True)
        except Exception as e_chatgpt:
            error_str = str(e_chatgpt)
            print(f"[DEBUG] Erro ao processar com ChatGPT: {error_str}", flush=True)
            
            # Se a mensagem já contém instruções específicas (quota, chave inválida, etc), usa ela diretamente
            if 'Quota' in error_str or 'quota' in error_str.lower() or 'billing' in error_str.lower():
                error_message = error_str  # Já tem mensagem específica sobre quota
            elif 'Chave de API' in error_str or 'invalid' in error_str.lower() or 'api-keys' in error_str.lower():
                error_message = f"{error_str}. Verifique sua chave no arquivo .env"
            else:
                error_message = f"{error_str}. Verifique sua chave de API OpenAI no arquivo .env"
            
            return jsonify({
                'success': False,
                'error': error_message
            })
        files_created = agent.save_improved_outputs(result, RESULTS_FOLDER)
        response_data = {
            'success': True,
            'question_name': question_name,
                'total_responses': result['total_responses'],
                'valid_responses': result['valid_responses'],
                'processing_method': result.get('processing_method', 'desconhecido'),
                'question_type': result.get('question_type', 'desconhecido'),
                'statistics': result['statistics'],
            'files_created': {k: os.path.basename(v) for k, v in files_created.items()},
            'detailed_report': result['detailed_report'][:2000] + '...' if len(result['detailed_report']) > 2000 else result['detailed_report'],
            'download_links': {
                'banco': f"/download/{os.path.basename(files_created['banco'])}",
                'f17': f"/download/{os.path.basename(files_created['f17'])}",
                'relatorio': f"/download/{os.path.basename(files_created['relatorio'])}",
                'resumo': f"/download/{os.path.basename(files_created['resumo'])}"
            }
        }
        print("[DEBUG] Enviando resposta JSON de sucesso", flush=True)
        return jsonify(response_data)
    except Exception as e:
        print(f"[DEBUG] Exceção no endpoint /questao_especifica: {e}", flush=True)
        return jsonify({
            'success': False,
            'error': f'Erro ao processar questão: {str(e)}'
        })

@app.route('/download/<filename>')
def download_file(filename):
    """Download de arquivos gerados"""
    try:
        file_path = os.path.join(RESULTS_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            flash('Arquivo não encontrado', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Erro ao baixar arquivo: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/exemplo')
def exemplo():
    """Página com exemplo de uso"""
    return render_template('exemplo.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)

