# controllers/projeto_controller.py
from models.projeto_model import ProjetoModel
from flask import g
import requests
import json
import logging
from config import Config

logger = logging.getLogger('ProtheusIntegration')


class ProjetoController:
    def __init__(self):
        self.model = ProjetoModel()

    # --- LEITURAS (MANTIDAS IGUAIS) ---
    def listar_projetos(self):
        if not self.model.conectar():
            return {'success': False, 'error': 'Erro Banco'}
        try:
            return {'success': True, 'data': self.model.get_projetos()}
        finally:
            self.model.desconectar()

    def listar_celulas(self, projeto, revisao):
        if not self.model.conectar():
            return {'success': False, 'error': 'Erro Banco'}
        try:
            return {'success': True, 'data': self.model.get_celulas(projeto, revisao)}
        finally:
            self.model.desconectar()

    def listar_produtos(self, projeto, revisao, celula):
        if not self.model.conectar():
            return {'success': False, 'error': 'Erro Banco'}
        try:
            dados = self.model.get_produtos(projeto, revisao, celula)
            total_nec = sum(d['AFA_QUANT'] for d in dados)
            total_ent = sum(d['CP_XQUPR'] for d in dados)
            perc = round((total_ent / total_nec * 100)) if total_nec > 0 else 0
            return {
                'success': True,
                'data': dados,
                'estatisticas': {
                    'total_necessidade': total_nec,
                    'total_entregue': total_ent,
                    'percentual_geral': perc
                }
            }
        finally:
            self.model.desconectar()

    # --- MÉTODO PARA ENVIAR ORDEM DE SEPARAÇÃO
    def enviar_ordem_separacao(self, payload):
        """
        Envia a ordem de separação para o endpoint do Protheus

        Args:
            payload (dict): Estrutura com projeto, celulas e itens

        Returns:
            dict: {'success': bool, 'mensagem': str, 'dados_protheus': dict/str}
        """

        # 1. Recupera o token OAuth2 do Protheus que foi salvo no login
        token_protheus = getattr(g, 'protheus_token', None)

        if not token_protheus:
            logger.error("❌ Tentativa de envio sem token na sessão")
            print("\n❌ ERRO CRÍTICO: Token não encontrado na sessão!", flush=True)
            print("   → Faça logout e login novamente\n", flush=True)
            return {
                'success': False,
                'error': 'Sessão expirada. Faça login novamente.'
            }

        try:
            # 2. MONTA A URL CORRETA (VERIFICAÇÃO CRÍTICA)
            base_url = Config.URL_REST_PROTHEUS

            # Remove barras duplicadas
            if base_url.endswith('/'):
                base_url = base_url[:-1]

            # Endpoint específico
            endpoint = ""

            # URL final
            url_completa = f"{base_url}{endpoint}"

            # VALIDAÇÃO: Verifica se a URL não está duplicada
            if url_completa.count('http://') > 1 or url_completa.count('https://') > 1:
                logger.error(f"❌ URL DUPLICADA DETECTADA: {url_completa}")
                print(f"\n❌ ERRO: URL está duplicada!", flush=True)
                print(f"   Base URL: {base_url}", flush=True)
                print(f"   Endpoint: {endpoint}", flush=True)
                print(f"   URL Final: {url_completa}", flush=True)
                return {
                    'success': False,
                    'error': 'Erro de configuração de URL. Verifique o arquivo .env'
                }

            # 3. Configura os headers
            headers = {
                'Authorization': f'Bearer {token_protheus}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            # --- LOGS DETALHADOS NO TERMINAL ---
            print("\n" + "=" * 80, flush=True)
            print("🚀 [ENVIO ORDEM SEPARAÇÃO] Iniciando requisição ao Protheus", flush=True)
            print("=" * 80, flush=True)
            print(f"🌐 BASE URL do .env: {Config.URL_REST_PROTHEUS}", flush=True)
            print(f"📍 ENDPOINT: {endpoint}", flush=True)
            print(f"🔗 URL FINAL: {url_completa}", flush=True)
            print("-" * 80, flush=True)
            print(f"📦 Projeto: {payload.get('projeto')}", flush=True)
            print(f"🏭 Total de Células: {len(payload.get('celulas', []))}", flush=True)

            # Log detalhado de cada célula
            for idx, celula_data in enumerate(payload.get('celulas', []), 1):
                print(f"   └─ Célula {idx}: {celula_data.get('celula')} "
                      f"({len(celula_data.get('itens', []))} itens)", flush=True)

            print(f"🔑 Token (primeiros 30 chars): {token_protheus[:30]}...", flush=True)
            print(f"📋 Payload Completo:", flush=True)
            print(json.dumps(payload, indent=2, ensure_ascii=False), flush=True)
            print("-" * 80, flush=True)

            logger.info(f"POST {url_completa} | Projeto: {payload.get('projeto')}")

            # 4. Faz a requisição POST (timeout de 60 segundos)
            print("⏳ Enviando requisição para o Protheus...", flush=True)

            response = requests.post(
                url_completa,
                json=payload,
                headers=headers,
                timeout=60,
                verify=False  # Desabilita SSL para IPs internos
            )

            # --- ANÁLISE DO RETORNO ---
            print("=" * 80, flush=True)
            print("📥 [RESPOSTA DO PROTHEUS]", flush=True)
            print("=" * 80, flush=True)
            print(f"📊 Status HTTP: {response.status_code}", flush=True)
            print(f"⏱️  Tempo de Resposta: {response.elapsed.total_seconds():.2f}s", flush=True)
            print(f"📄 Content-Type: {response.headers.get('Content-Type', 'N/A')}", flush=True)
            print("-" * 80, flush=True)

            # Tenta imprimir o corpo da resposta de forma formatada
            try:
                resposta_json = response.json()
                print("📄 Corpo da Resposta (JSON):", flush=True)
                print(json.dumps(resposta_json, indent=2, ensure_ascii=False), flush=True)
            except ValueError:
                print("📄 Corpo da Resposta (Texto):", flush=True)
                print(response.text[:1000], flush=True)  # Limita a 1000 chars
                if len(response.text) > 1000:
                    print("... (truncado)", flush=True)

            print("=" * 80 + "\n", flush=True)

            logger.info(f"Resposta | Status: {response.status_code} | Body: {response.text[:500]}")

            # 5. Tratamento da resposta baseado no status HTTP
            if response.status_code in [200, 201]:
                # Sucesso - processa o retorno
                print("✅ Requisição processada com sucesso pelo Protheus!", flush=True)

                try:
                    dados_retorno = response.json()

                    # Extrai informações relevantes se disponíveis
                    mensagem_sucesso = "✅ Ordem de separação gerada com sucesso!"

                    # Verifica estruturas comuns de resposta
                    if isinstance(dados_retorno, dict):
                        if 'numero_ordem' in dados_retorno:
                            mensagem_sucesso += f" | Ordem: {dados_retorno['numero_ordem']}"
                        elif 'mensagem' in dados_retorno:
                            mensagem_sucesso = dados_retorno['mensagem']
                        elif 'message' in dados_retorno:
                            mensagem_sucesso = dados_retorno['message']

                    return {
                        'success': True,
                        'mensagem': mensagem_sucesso,
                        'dados_protheus': dados_retorno
                    }

                except ValueError:
                    # Resposta não é JSON válido, mas teve sucesso
                    print("⚠️  Resposta não é JSON, retornando como texto", flush=True)
                    return {
                        'success': True,
                        'mensagem': 'Ordem enviada com sucesso!',
                        'dados_protheus': response.text
                    }

            elif response.status_code == 401:
                logger.error("❌ Token inválido ou expirado no Protheus")
                print("❌ ERRO 401: Token inválido ou expirado", flush=True)
                return {
                    'success': False,
                    'error': 'Sessão expirada no Protheus. Faça login novamente.'
                }

            elif response.status_code == 400:
                logger.error(f"❌ Dados inválidos enviados: {response.text}")
                print(f"❌ ERRO 400: Dados inválidos", flush=True)
                return {
                    'success': False,
                    'error': f'Dados inválidos: {response.text}'
                }

            elif response.status_code == 404:
                logger.error(f"❌ Endpoint não encontrado: {url_completa}")
                print(f"❌ ERRO 404: Endpoint não encontrado", flush=True)
                print(f"   Verifique se a URL está correta: {url_completa}", flush=True)
                return {
                    'success': False,
                    'error': f'Endpoint não encontrado (404). URL: {url_completa}'
                }

            elif response.status_code == 500:
                logger.error(f"❌ Erro interno do Protheus: {response.text}")
                print(f"❌ ERRO 500: Erro interno do servidor Protheus", flush=True)
                return {
                    'success': False,
                    'error': f'Erro interno do Protheus: {response.text}'
                }

            else:
                # Qualquer outro erro
                logger.error(f"❌ Erro HTTP {response.status_code}: {response.text}")
                print(f"❌ ERRO HTTP {response.status_code}", flush=True)
                return {
                    'success': False,
                    'error': f'Erro no Protheus (HTTP {response.status_code}): {response.text}'
                }

        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Erro de conexão com Protheus: {e}")
            print("\n" + "=" * 80, flush=True)
            print("❌ ERRO DE CONEXÃO", flush=True)
            print("=" * 80, flush=True)
            print(f"Não foi possível conectar ao servidor: {url_completa}", flush=True)
            print("\nPossíveis causas:", flush=True)
            print("  1. Servidor Protheus está offline", flush=True)
            print("  2. Firewall bloqueando a porta 4003", flush=True)
            print("  3. IP/URL incorretos", flush=True)
            print("  4. Rede/VPN desconectada", flush=True)
            print("=" * 80 + "\n", flush=True)
            return {
                'success': False,
                'error': 'Servidor Protheus inacessível. Verifique a rede ou se o servidor está ativo.'
            }

        except requests.exceptions.Timeout:
            logger.error("❌ Timeout na requisição ao Protheus")
            print("\n❌ TIMEOUT: Protheus demorou mais de 60 segundos para responder\n", flush=True)
            return {
                'success': False,
                'error': 'Timeout: O Protheus não respondeu em tempo hábil. Tente novamente.'
            }

        except Exception as e:
            logger.exception(f"❌ Erro inesperado ao enviar ordem: {e}")
            print(f"\n❌ ERRO INTERNO: {type(e).__name__}", flush=True)
            print(f"   Mensagem: {str(e)}\n", flush=True)
            return {
                'success': False,
                'error': f'Erro interno: {str(e)}'
            }