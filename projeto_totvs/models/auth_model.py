# models/auth_model.py
import requests
import base64
from config import Config


class AuthModel:
    def __init__(self):
        self.base_url = Config.URL_REST_PROTHEUS

    def autenticar_protheus(self, username, password):
        """
        Autenticação usando endpoint customizado /auth
        - Usa OAuth2PasswordRequestForm (application/x-www-form-urlencoded)
        - Senha codificada em base64
        - Header X-Cliente-Token obrigatório
        """
        import logging

        logger = logging.getLogger("AuthModel")

        # Valida configurações
        auth_url = Config.get_auth_endpoint()
        chave_coletor = Config.CHAVE_COLETOR

        logger.info(f"🔐 Tentando autenticar usuário: {username}")
        logger.info(f"📍 URL de autenticação: {auth_url}")
        logger.info(
            f"🔑 Chave coletor configurada: {'Sim' if chave_coletor else 'Não'}"
        )

        if not auth_url:
            return {"success": False, "error": "URL de autenticação não configurada"}

        if not chave_coletor:
            logger.error("❌ CHAVE_COLETOR não configurada no .env")
            return {
                "success": False,
                "error": "CHAVE_COLETOR não configurada no .env",
            }

        try:
            # Codifica a senha em base64
            senha_base64 = base64.b64encode(password.encode()).decode()

            # Prepara headers - OAuth2 usa application/x-www-form-urlencoded
            headers = {
                "X-Cliente-Token": chave_coletor,
                "Content-Type": "application/x-www-form-urlencoded",
            }

            # OAuth2PasswordRequestForm espera 'username' e 'password' como form fields
            data = {"username": username, "password": senha_base64}

            logger.info(f"📤 Enviando requisição OAuth2 para {auth_url}")
            logger.debug(f"Headers: X-Cliente-Token presente")
            logger.debug(f"Data: username={username}, password=[BASE64_REDACTED]")

            # Faz a requisição
            response = requests.post(
                url=auth_url, headers=headers, data=data, timeout=10, verify=False
            )

            logger.info(f"📥 Status Code: {response.status_code}")
            logger.info(f"📥 Response: {response.text[:500]}")  # Primeiros 500 chars

            # Processa resposta
            if response.status_code in [200, 201]:
                dados = response.json()
                logger.info(f"✅ Autenticação bem-sucedida para {username}")

                # O endpoint retorna 'dados_autenticacao' com 'token'
                if "dados_autenticacao" in dados:
                    return {
                        "success": True,
                        "access_token": dados["dados_autenticacao"].get("token", ""),
                        "refresh_token": dados["dados_autenticacao"].get(
                            "refresh_token", ""
                        ),
                        "user_id": username,
                    }
                else:
                    # Fallback para estrutura antiga
                    return {
                        "success": True,
                        "access_token": dados.get("access_token", ""),
                        "refresh_token": dados.get("refresh_token", ""),
                        "user_id": username,
                    }
            else:
                logger.error(
                    f"❌ Autenticação falhou - Status: {response.status_code}"
                )
                logger.error(f"❌ Resposta: {response.text}")
                return {
                    "success": False,
                    "error": f"Autenticação falhou (Status {response.status_code}): {response.text}",
                }

        except requests.exceptions.Timeout:
            logger.error("❌ Timeout na autenticação")
            return {"success": False, "error": "Timeout na autenticação"}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Erro de conexão: {str(e)}")
            return {"success": False, "error": "Erro de conexão com servidor de auth"}
        except Exception as e:
            logger.exception("❌ Erro inesperado na autenticação")
            return {"success": False, "error": f"Erro inesperado: {str(e)}"}
