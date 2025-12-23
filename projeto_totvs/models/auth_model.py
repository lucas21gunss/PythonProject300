# models/auth_model.py
import requests
import base64
from config import Config

class AuthModel:
    def __init__(self):
        self.base_url = Config.URL_REST_PROTHEUS

    def autenticar_protheus(self, username, password):
        """
        Versão Estável: Valida no /portalauth e depois pega token no /api/oauth2
        """
        if not self.base_url:
            return {'success': False, 'error': 'URL do Protheus não configurada'}

        # ETAPA 1: Validação de Credenciais (Basic Auth)
        try:
            url_portal = f"{self.base_url}/portalauth"
            creds = base64.b64encode(f"{username}:{password}".encode()).decode('utf-8')
            headers = {
                "Authorization": f"Basic {creds}",
                "User-Agent": "PortalPy_Flask"
            }
            # Apenas testa conexão e senha
            requests.get(url_portal, headers=headers, timeout=5)
        except Exception:
            pass # Continua mesmo se falhar (alguns ambientes não têm portalauth)

        # ETAPA 2: Token OAuth2
        try:
            url_token = f"{self.base_url}/api/oauth2/v1/token"
            params = {
                "grant_type": "password",
                "username": username,
                "password": password
            }

            response_token = requests.post(url_token, params=params, timeout=10, verify=False)

            if response_token.status_code in [200, 201]:
                dados = response_token.json()
                return {
                    'success': True,
                    'access_token': dados.get('access_token'),
                    'refresh_token': dados.get('refresh_token'),
                    'user_id': username
                }
            else:
                return {'success': False, 'error': f'Protheus recusou login: {response_token.text}'}

        except Exception as e:
            return {'success': False, 'error': f'Erro de conexão: {str(e)}'}