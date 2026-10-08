from flask import Flask, render_template, request, redirect, url_for
import pymysql

app = Flask(__name__)

def conectar_banco():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='1234',
        database='sistema_epi',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/colaboradores', methods=['GET', 'POST'])
def colaboradores():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    #Se o usuario enviou formulario, insere no banco de dados
    if request.method == 'POST':
        nome = request.form['nome']
        setor = request.form['setor']

        cursor.execute("INSERT INTO Colaborador (Nome, Setor) VALUES (%s, %s)", (nome, setor))
        conexao.commit()

        cursor.close()
        conexao.close()
        return redirect(url_for('colaboradores'))

    #Se apenas acesso, busca todos os colaboradores
    cursor.execute("SELECT * FROM Colaborador")
    lista_colaboradores = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template('colaboradores.html', colaboradores=lista_colaboradores)

@app.route('/colaboradores/editar/<int:id>', methods=['GET', 'POST'])
def editar_colaborador(id):
    conexao = conectar_banco()
    try:
        if request.method == 'POST':
            nome = request.form['nome']
            setor = request.form['setor']
 
            print(f"DEBUG -> A atualizar ID: {id} | Novo Nome: {nome} | Novo Setor: {setor}")

            with conexao.cursor() as cursor:
                sql = "UPDATE Colaborador SET Nome = %s, Setor = %s WHERE ID = %s"
                cursor.execute(sql, (nome, setor, id))
                conexao.commit()
            return redirect(url_for('colaboradores'))

        #Se for GET, busca dados atuais para preencher formulario
        with conexao.cursor() as cursor:
            sql = "SELECT * FROM Colaborador WHERE ID = %s"
            cursor.execute(sql, (id,))
            colaborador = cursor.fetchone()

            return render_template('editar_colaborador.html', colaborador=colaborador)
    finally:
        conexao.close()

@app.route('/colaboradores/excluir/<int:id>', methods=['GET'])
def excluir_colaborador(id):
    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            # Como configuramos ON DELETE CASCADE, apagar o colaborador 
            # vai apagar automaticamente os empréstimos e os itens associados
            sql = "DELETE FROM Colaborador WHERE ID = %s"
            cursor.execute(sql, (id,))
            conexao.commit()
    finally:
        conexao.close()
    return redirect(url_for('colaboradores'))

@app.route('/equipamentos', methods=['GET', 'POST'])
def equipamentos():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        qtd_estoque = request.form['qtd_estoque']
        print(f"DEBUG EQUIPAMENTO -> Nome: {nome} | Estoque: {qtd_estoque}")

        cursor.execute("INSERT INTO Equipamento (Nome, QTD_estoque) VALUES (%s, %s)", (nome, qtd_estoque))
        conexao.commit()

        cursor.close()
        conexao.close()
        return redirect(url_for('equipamentos'))

    cursor.execute("SELECT * FROM Equipamento")
    lista_equipamentos = cursor.fetchall()
    print(f"{lista_equipamentos}")
    cursor.close()
    conexao.close()

    return render_template('equipamentos.html', equipamentos=lista_equipamentos)


@app.route('/equipamentos/editar/<int:id>', methods=['GET', 'POST'])
def editar_equipamento(id):
    conexao = conectar_banco()

    try:
        if request.method == 'POST':
            nome = request.form['nome']
            qtd_estoque = request.form['qtd_estoque']

            with conexao.cursor() as cursor:
                sql = "UPDATE Equipamento SET Nome = %s, QTD_estoque = %s WHERE ID = %s"
                cursor.execute(sql, (nome, qtd_estoque, id))
                conexao.commit()
            return redirect(url_for('equipamentos'))
        
        with conexao.cursor() as cursor:
            sql = "SELECT * FROM Equipamento WHERE ID = %s"
            cursor.execute(sql, (id,))
            equipamento = cursor.fetchone()
            return render_template('editar_equipamento.html', equipamento=equipamento)

    finally:
        conexao.close()

@app.route('/equipamentos/excluir/<int:id>', methods=['GET'])
def exlcuir_equipamento(id):
    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            sql = "DELETE FROM Equipamento WHERE ID = %s"
            cursor.execute(sql, (id,))
            conexao.commit()
    except pymysql.err.IntegrityError:
        # Mensagem orientada para o utilizador indicando o bloqueio por estar em uso
        return "Erro: Não é possível apagar este equipamento porque ele está envolvido num registo de empréstimo."
    finally:
        conexao.close()
    return redirect(url_for('equipamentos'))

@app.route('/emprestimos')
def emprestimos():
    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            # Consulta para buscar os empréstimos juntamente com o nome do colaborador
            sql = """
                SELECT e.ID, e.Data, e.Situacao, c.Nome AS Colaborador 
                FROM Emprestimo e 
                JOIN Colaborador c ON e.idColaborador = c.ID
            """
            cursor.execute(sql)
            lista_emprestimos = cursor.fetchall()
            return render_template('emprestimos.html', emprestimos=lista_emprestimos)
    finally:
        conexao.close()

@app.route('/emprestimos/novo', methods=['GET', 'POST'])
def novo_emprestimo():
    conexao = conectar_banco()
    try:
        if request.method == 'POST':
            id_colaborador = request.form['id_colaborador']
            id_equipamento = request.form['id_equipamento']
            quantidade = int(request.form['quantidade']) # Garantir que é número inteiro

            with conexao.cursor() as cursor:
                # 1. Cria o empréstimo (Situação 1 = Ativo)
                sql_emp = "INSERT INTO Emprestimo (Data, idColaborador, Situacao) VALUES (NOW(), %s, 1)"
                cursor.execute(sql_emp, (id_colaborador,))
                id_emprestimo = cursor.lastrowid

                # 2. Insere na tabela associativa 'contem'
                sql_contem = "INSERT INTO contem (idEmprestimo, idEquipamento, Quantidade) VALUES (%s, %s, %s)"
                cursor.execute(sql_contem, (id_emprestimo, id_equipamento, quantidade))
                
                # 3. Diminui a quantidade do EPI no estoque
                sql_estoque = "UPDATE Equipamento SET QTD_estoque = QTD_estoque - %s WHERE ID = %s"
                cursor.execute(sql_estoque, (quantidade, id_equipamento))

                conexao.commit()
            return redirect(url_for('emprestimos'))

        # Se for GET, busca colaboradores e equipamentos para preencher os selects do formulário
        with conexao.cursor() as cursor:
            cursor.execute("SELECT * FROM Colaborador")
            colaboradores = cursor.fetchall()

            cursor.execute("SELECT * FROM Equipamento WHERE QTD_estoque > 0")
            equipamentos = cursor.fetchall()

            return render_template('novo_emprestimo.html', colaboradores=colaboradores, equipamentos=equipamentos)
    finally:
        conexao.close()

@app.route('/emprestimos/finalizar/<int:id>', methods=['GET'])
def finalizar_emprestimo(id):
    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            # 1. Buscar os equipamentos e quantidades vinculados a este empréstimo
            sql_itens = "SELECT idEquipamento, Quantidade FROM contem WHERE idEmprestimo = %s"
            cursor.execute(sql_itens, (id,))
            itens = cursor.fetchall()
            
            # 2. Devolver a quantidade de cada EPI de volta ao estoque
            for item in itens:
                id_equipamento = item['idEquipamento']
                quantidade = item['Quantidade']
                
                sql_devolve_estoque = "UPDATE Equipamento SET QTD_estoque = QTD_estoque + %s WHERE ID = %s"
                cursor.execute(sql_devolve_estoque, (quantidade, id_equipamento))

            # 3. Altera a situação do empréstimo para finalizado (ex: 0)
            sql_emp = "UPDATE Emprestimo SET Situacao = 0 WHERE ID = %s"
            cursor.execute(sql_emp, (id,))
            
            conexao.commit()
    finally:
        conexao.close()
    return redirect(url_for('emprestimos'))

@app.route('/emprestimos/visualizar/<int:id>')
def visualizar_emprestimo(id):
    conexao = conectar_banco()
    try:
        with conexao.cursor() as cursor:
            # 1. Buscar dados gerais do empréstimo, colaborador e setor
            sql_emp = """
                SELECT e.ID, e.Data, e.Situacao, c.ID AS IdColaborador, c.Nome AS Colaborador, c.Setor 
                FROM Emprestimo e 
                JOIN Colaborador c ON e.idColaborador = c.ID 
                WHERE e.ID = %s
            """
            cursor.execute(sql_emp, (id,))
            emprestimo = cursor.fetchone()
            
            # 2. Buscar os equipamentos e quantidades associados a este empréstimo
            sql_itens = """
                SELECT eq.ID AS IdEquipamento, eq.Nome, co.Quantidade 
                FROM contem co 
                JOIN Equipamento eq ON co.idEquipamento = eq.ID 
                WHERE co.idEmprestimo = %s
            """
            cursor.execute(sql_itens, (id,))
            itens = cursor.fetchall()
            
            return render_template('visualizar_emprestimo.html', emprestimo=emprestimo, itens=itens)
    finally:
        conexao.close()

if __name__ == '__main__':
    app.run(debug=True)