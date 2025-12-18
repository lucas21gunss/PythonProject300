# testar_conexao.py
import pyodbc
import base64

# Suas configurações
DB_SERVER = '172.22.8.25'
DB_DATABASE = 'ZT8HTG_DEV'  # ⚠️ TROQUE PELO SEU BANCO
DB_USERNAME = 'sa'  # ⚠️ TROQUE PELO SEU USUÁRIO
DB_PASSWORD_BASE64 = 'TW90b0B6dDhodGdkYQ=='

# Decodificar senha
senha = base64.b64decode(DB_PASSWORD_BASE64).decode('utf-8')

print("=" * 60)
print("TESTANDO CONEXÃO COM SQL SERVER")
print("=" * 60)
print(f"\n📍 Servidor: {DB_SERVER}")
print(f"📍 Banco: {DB_DATABASE}")
print(f"📍 Usuário: {DB_USERNAME}")
print(f"📍 Senha decodificada: {senha}")
print("\n" + "=" * 60)

# Testar várias formas de conexão
testes = [
    # Teste 1: Conexão básica
    f'DRIVER={{SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={senha}',

    # Teste 2: Com porta explícita
    f'DRIVER={{SQL Server}};SERVER={DB_SERVER},1433;DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={senha}',

    # Teste 3: Named instance
    f'DRIVER={{SQL Server}};SERVER={DB_SERVER}\\SQLEXPRESS;DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={senha}',

    # Teste 4: Trusted connection (Windows Auth)
    f'DRIVER={{SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};Trusted_Connection=yes;',

    # Teste 5: SQL Native Client
    f'DRIVER={{SQL Server Native Client 11.0}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={senha}',
]

for i, conn_str in enumerate(testes, 1):
    print(f"\n🔍 Teste {i}:")
    print(f"   String: {conn_str[:80]}...")

    try:
        conn = pyodbc.connect(conn_str, timeout=5)
        print(f"   ✅ SUCESSO! Conexão estabelecida!")

        # Testar query
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"   ✅ SQL Server Version: {version[:50]}...")

        cursor.execute("SELECT DB_NAME()")
        db = cursor.fetchone()[0]
        print(f"   ✅ Banco atual: {db}")

        conn.close()
        print("\n" + "=" * 60)
        print("🎉 CONEXÃO BEM-SUCEDIDA! Use esta configuração:")
        print("=" * 60)
        print(f"\nDB_SERVER = '{DB_SERVER}'")
        print(f"String de conexão funcionou no Teste {i}")
        break

    except Exception as e:
        print(f"   ❌ Falhou: {str(e)[:100]}...")

print("\n" + "=" * 60)