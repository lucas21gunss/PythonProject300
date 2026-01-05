# teste_url.py
# Script para testar a URL do Protheus ANTES de rodar a aplicação

import os
import requests
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()


def testar_configuracao():
    """Testa se a URL está configurada corretamente"""

    print("\n" + "=" * 80)
    print("🔍 TESTE DE CONFIGURAÇÃO - URL DO PROTHEUS")
    print("=" * 80 + "\n")

    # 1. Verifica variável de ambiente
    url_base = os.getenv("URL_REST_PROTHEUS")

    print("📋 Variável de Ambiente:")
    print(f"   URL_REST_PROTHEUS = {url_base}")

    if not url_base:
        print("\n❌ ERRO: Variável URL_REST_PROTHEUS não encontrada no .env")
        return False

    # 2. Monta URL final
    endpoint = "/mmacdw02/ordem_separacao_fabrica/"

    if url_base.endswith("/"):
        url_base = url_base[:-1]

    url_completa = f"{url_base}{endpoint}"

    print(f"\n🔗 URL Final Montada:")
    print(f"   {url_completa}")

    # 3. Verifica duplicação
    if url_completa.count("http://") > 1 or url_completa.count("https://") > 1:
        print("\n❌ ERRO: URL está duplicada!")
        print("   Verifique o arquivo .env")
        return False

    print("\n✅ URL montada corretamente!")

    # 4. Testa conectividade (sem autenticação)
    print("\n🌐 Testando Conectividade...")
    print(f"   Tentando conectar em: {url_base}")

    try:
        # Apenas testa se o servidor responde (pode dar 401, mas está ok)
        response = requests.get(url_base, timeout=5, verify=False)
        print(f"   ✅ Servidor respondeu! (Status: {response.status_code})")

        if response.status_code == 404:
            print("   ⚠️  Aviso: Status 404 - Verifique se o endpoint existe")
        elif response.status_code == 401:
            print("   ✅ Status 401 é esperado (precisa de autenticação)")

        return True

    except requests.exceptions.ConnectionError:
        print(f"   ❌ Não foi possível conectar ao servidor")
        print(f"\n   Possíveis causas:")
        print(f"   1. Servidor Protheus offline")
        print(f"   2. Firewall bloqueando porta 4003")
        print(f"   3. IP/URL incorretos")
        print(f"   4. Rede/VPN desconectada")
        return False

    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout - Servidor não respondeu em 5 segundos")
        return False

    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False


def testar_endpoint_completo():
    """Testa o endpoint completo (precisa de token)"""

    print("\n" + "=" * 80)
    print("🧪 TESTE DO ENDPOINT COMPLETO")
    print("=" * 80 + "\n")

    url_base = os.getenv("URL_REST_PROTHEUS")
    if url_base.endswith("/"):
        url_base = url_base[:-1]

    endpoint = "/mmacdw02/ordem_separacao_fabrica/"
    url_completa = f"{url_base}{endpoint}"

    print(f"📍 URL: {url_completa}")
    print("\n⚠️  NOTA: Este teste vai falhar com 401 (sem token)")
    print("   Isso é NORMAL - significa que o endpoint existe!\n")

    payload = {
        "projeto": "TESTE",
        "celulas": [
            {"celula": "TESTE", "itens": [{"produto": "TESTE", "quantidade": 1}]}
        ],
    }

    try:
        response = requests.post(
            url_completa,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
            verify=False,
        )

        print(f"📊 Status: {response.status_code}")
        print(f"📄 Resposta: {response.text[:200]}")

        if response.status_code == 401:
            print("\n✅ SUCESSO! Endpoint existe (401 = precisa de token)")
            return True
        elif response.status_code == 404:
            print("\n❌ ERRO 404: Endpoint não encontrado!")
            print("   Verifique se o caminho está correto no Protheus")
            return False
        else:
            print(f"\n⚠️  Status inesperado: {response.status_code}")
            return True

    except requests.exceptions.ConnectionError:
        print("\n❌ Erro de conexão - Servidor inacessível")
        return False
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False


def exibir_recomendacoes():
    """Exibe recomendações finais"""

    print("\n" + "=" * 80)
    print("💡 RECOMENDAÇÕES")
    print("=" * 80 + "\n")

    print("1. Seu .env deve estar assim:")
    print("   URL_REST_PROTHEUS=http://172.22.8.25:4003/rest")
    print()
    print("2. NÃO incluir o endpoint completo no .env")
    print()
    print("3. O endpoint é adicionado pelo código:")
    print("   /mmacdw02/ordem_separacao_fabrica/")
    print()
    print("4. URL final deve ser:")
    print("   http://172.22.8.25:4003/rest/")
    print()
    print("5. Sempre reinicie o Flask após alterar o .env")
    print()


if __name__ == "__main__":
    print("\n🚀 Iniciando testes de configuração...\n")

    # Teste 1: Configuração
    config_ok = testar_configuracao()

    if config_ok:
        # Teste 2: Endpoint
        endpoint_ok = testar_endpoint_completo()

        if endpoint_ok:
            print("\n" + "=" * 80)
            print("✅ TODOS OS TESTES PASSARAM!")
            print("=" * 80)
            print("\nSua configuração está correta!")
            print("Agora você pode iniciar o Flask e testar pelo navegador.")
        else:
            print("\n" + "=" * 80)
            print("⚠️  ENDPOINT COM PROBLEMA")
            print("=" * 80)
            exibir_recomendacoes()
    else:
        print("\n" + "=" * 80)
        print("❌ CONFIGURAÇÃO COM PROBLEMA")
        print("=" * 80)
        exibir_recomendacoes()

    print("\n" + "=" * 80 + "\n")
