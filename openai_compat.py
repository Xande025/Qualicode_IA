"""Compatibilidade entre versões do SDK OpenAI.

Fornece get_openai_client(api_key=None) que retorna um objeto com a
interface utilizada pelo projeto: client.chat.completions.create(...).

Suporta a nova interface (from openai import OpenAI) quando disponível,
e também suporta a interface legada (import openai; openai.ChatCompletion.create).
"""
import os

def get_openai_client(api_key: str = None):
    try:
        # Tenta usar a nova API (openai.OpenAI)
        from openai import OpenAI as NewOpenAI

        if api_key:
            return NewOpenAI(api_key=api_key)
        return NewOpenAI()
    except Exception:
        # Fallback para a API legada
        try:
            import openai as legacy_openai
        except Exception:
            raise ImportError("Nenhuma biblioteca 'openai' disponível")

        # Ajusta api_key se fornecido
        if api_key:
            try:
                legacy_openai.api_key = api_key
            except Exception:
                os.environ.setdefault('OPENAI_API_KEY', api_key)

        # Cria um cliente compatível que expõe client.chat.completions.create
        class _LegacyCompletions:
            def create(self, **kwargs):
                return legacy_openai.ChatCompletion.create(**kwargs)

        class _LegacyChat:
            def __init__(self):
                self.completions = _LegacyCompletions()

        class _LegacyClient:
            def __init__(self):
                self.chat = _LegacyChat()

        return _LegacyClient()
