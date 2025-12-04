import sqlite3
import hashlib
import json
import os
from datetime import datetime

class CacheManager:
    def __init__(self, db_path='cache.db'):
        """Inicializa o gerenciador de cache com SQLite"""
        # Garante que o caminho seja absoluto em relação à raiz do projeto se não for fornecido
        if not os.path.isabs(db_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, db_path)
            
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Cria a tabela de cache se não existir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_cache (
                    hash_key TEXT PRIMARY KEY,
                    response TEXT,
                    created_at TIMESTAMP,
                    model TEXT
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[CACHE] Erro ao inicializar banco de cache: {e}")

    def _generate_hash(self, *args):
        """Gera um hash SHA-256 único para os argumentos fornecidos"""
        content = ""
        for arg in args:
            if isinstance(arg, (list, dict)):
                content += json.dumps(arg, sort_keys=True)
            else:
                content += str(arg)
        
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def get(self, *args):
        """Recupera uma resposta do cache baseada nos argumentos de entrada"""
        hash_key = self._generate_hash(*args)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT response FROM api_cache WHERE hash_key = ?', (hash_key,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
        except Exception as e:
            print(f"[CACHE] Erro ao ler do cache: {e}")
            return None

    def set(self, response, *args, model="gpt-4o"):
        """Salva uma resposta no cache"""
        hash_key = self._generate_hash(*args)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO api_cache (hash_key, response, created_at, model)
                VALUES (?, ?, ?, ?)
            ''', (hash_key, json.dumps(response), datetime.now(), model))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[CACHE] Erro ao salvar no cache: {e}")
