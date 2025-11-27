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

agent = FinalIPOAgentImproved()

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
            flash('Por favor, envie tanto o Banco quanto o F17', 'error')
            return redirect(url_for('upload_files'))
        
        banco_file = request.files['banco_file']
        f17_file = request.files['f17_file']
        
        if banco_file.filename == '' or f17_file.filename == '':
            flash('Por favor, selecione os arquivos', 'error')
            return redirect(url_for('upload_files'))
        
        # Salva arquivos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        banco_path = os.path.join(UPLOAD_FOLDER, f"banco_{timestamp}_{secure_filename(banco_file.filename)}")
        f17_path = os.path.join(UPLOAD_FOLDER, f"f17_{timestamp}_{secure_filename(f17_file.filename)}")
        
        banco_file.save(banco_path)
        f17_file.save(f17_path)
        
        # Processa arquivos (implementação simplificada)
        flash('Arquivos enviados com sucesso! Funcionalidade de processamento completo em desenvolvimento.', 'success')
        return redirect(url_for('upload_files'))
        
    except Exception as e:
        flash(f'Erro ao processar arquivos: {str(e)}', 'error')
        return redirect(url_for('upload_files'))

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

