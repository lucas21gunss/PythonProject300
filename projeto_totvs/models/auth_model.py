# models/auth_model.py
import requests
import base64
from config import Config


class AuthModel:
    def __init__(self):
        self.base_url = Config.URL_REST_PROTHEUS

    def autenticar_protheus(self, username, password):
        """
        Realiza autenticação em duas etapas conforme padrão do PortalPy:
        1. Basic Auth em /portalauth
        2. OAuth2 Password Grant em /api/oauth2/v1/token
        """
        if not self.base_url:
            return {'success': False, 'error': 'URL do Protheus não configurada'}

        # ETAPA 1: Validação Basic Auth (/portalauth)
        try:
            url_portal = f"{self.base_url}/portalauth"
            creds = base64.b64encode(f"{username}:{password}".encode()).decode('utf-8')
            headers = {
                "Authorization": f"Basic {creds}",
                "User-Agent": "PortalPy_Flask"
            }

            # Timeout curto para teste de conexão
            response_portal = requests.get(url_portal, headers=headers, timeout=10)

            if response_portal.status_code != 200:
                return {
                    'success': False,
                    'error': f'Falha na autenticação (PortalAuth): {response_portal.status_code}'
                }

        except Exception as e:
            return {'success': False, 'error': f'Erro de conexão com Protheus: {str(e)}'}

        # ETAPA 2: Obtenção do Token OAuth2
        try:
            url_token = f"{self.base_url}/api/oauth2/v1/token?grant_type=password"
            # O Protheus geralmente espera os dados no header ou form-data para esse endpoint específico
            headers_token = {
                "password": password,
                "username": username
            }

            response_token = requests.post(url_token, headers=headers_token, timeout=10)

            if response_token.status_code == 201:  # 201 Created é o padrão esperado
                dados = response_token.json()
                return {
                    'success': True,
                    'access_token': dados.get('access_token'),
                    'refresh_token': dados.get('refresh_token'),
                    'user_id': username
                }
            else:
                return {
                    'success': False,
                    'error': f'Erro ao gerar token: {response_token.text}'
                }

        except Exception as e:
            return {'success': False, 'error': f'Erro na etapa de Token: {str(e)}'}