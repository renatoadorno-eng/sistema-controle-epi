import pymysql
import ssl, os
from werkzeug.security import generate_password_hash

# Função de conexão atualizada para o Aiven (com SSL e porta)
def conectar_banco():
    contexto_ssl = ssl.create_default_context()
    contexto_ssl.check_hostname = False
    contexto_ssl.verify_mode = ssl.CERT_NONE

    return pymysql.connect(
        host='mysql-12cadf0a-sistema-controle-epi.h.aivencloud.com',
        user='avnadmin',
        password=os.environ.get('DB_PASS'), # Pode manter aqui temporariamente só para rodar o script no PC
        database='sistema_epi',
        port=26641,
        cursorclass=pymysql.cursors.DictCursor,
        ssl=contexto_ssl
    )

def cadastrar_usuario():
    nome = "Técnico de Segurança"
    email = "tecnico@empresa.com"
    senha_plana = "123456" # Senha que você vai digitar no login
    
    # Gera a senha criptografada (hash segura)
    senha_hash = generate_password_hash(senha_plana)

    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            sql = "INSERT INTO Usuario (Nome, Email, Senha) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nome, email, senha_hash))
            conexao.commit()
            print("Técnico de segurança cadastrado com sucesso!")
    except Exception as e:
        print(f"Erro ao cadastrar (talvez o e-mail já exista): {e}")
    finally:
        conexao.close()

if __name__ == '__main__':
    cadastrar_usuario()