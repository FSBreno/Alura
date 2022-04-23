from flask import Flask, render_template, request, session, flash, redirect, jsonify
from flask_session import Session
import banco as banco

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
Session(app)
app.secret_key = 'alura'

@app.route('/')
def index():
    return render_template('index.html', titulo='Alura')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html', titulo='Cadastro')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():    
    comando1 = ("""select * from alunos where usuario=%s""")
    comando2 = ("""select * from empresas where usuario=%s""")
    condicao = request.form['usuario'] 
    cadastra = int(request.form['cadastra'])
    telefone = request.form.get('telefone')
    endereco = request.form.get('endereco')
    print (telefone)
    print(endereco)
    if not (banco.consultabd(comando1, condicao) or banco.consultabd(comando2, condicao)):
        if cadastra == 1:
            banco.cadastrarUsuario(request.form['usuario'],
            request.form['nome'],
            request.form['senha']
            )
            if telefone:
                banco.alterabd("""update alunos set telefone=%s where usuario=%s;""", (telefone,condicao))
            if endereco:
                banco.alterabd("""update alunos set endereco=%s where usuario=%s;""", (endereco,condicao))
            if banco.autenticaUsuario(request.form['usuario'],request.form['senha']):
                flash(request.form['usuario'] + ' foi cadastrado!')
            else:
                flash(request.form['usuario'] + ' não cadastrado!')
            return redirect('/')
        elif cadastra == 2:
            banco.cadastrarEmpresa(request.form['usuario'],
            request.form['nome'],
            request.form['senha']
            )
            if banco.autenticaEmpresa(request.form['usuario'],request.form['senha']):
                flash(request.form['usuario'] + ' cadastrada!')
            else:
                flash(request.form['usuario'] + ' não cadastrada!')
            return redirect('/')  
    else:
        flash(request.form['usuario'] + ' já existe!')
        return redirect('/cadastro')      

@app.route('/entrar', methods=['POST'])
def entrar():
    if request.args.get('usuario') and request.args.get('senha'):
        session['usuario'] = request.args['usuario']
        session['senha'] = request.args['senha']
    else:
        session['usuario'] = request.form['usuario']
        session['senha'] = request.form['senha']
    usuario = session['usuario']
    senha = session['senha']    
    if (banco.autenticaUsuario(usuario, senha) or banco.adm(usuario, senha) or banco.autenticaEmpresa(usuario, senha)):
        return redirect('/entrar')
    else:
        flash('Usuário ou senha incorretos')        
        return redirect('/')

@app.route('/entrar')
def carregaLogin():
    usuario = session.get('usuario')
    senha = session.get('senha')
    if banco.autenticaUsuario(usuario, senha):
        nome = banco.retornabd("""select nome from alunos where usuario=%s""",usuario)
        id = banco.retornabd("""select id from alunos where usuario=%s""",usuario)
        matriculas = banco.retornasbd("""select cursos.nome,matriculas.status,matriculas.id_matricula from cursos INNER JOIN matriculas on cursos.id_curso = matriculas.id_curso where id_aluno=%s""",id)
        plano = banco.retornabd("""select planos.id_plano,empresas.nome from planos INNER JOIN empresas INNER JOIN alunos on empresas.id_empresa=planos.id_empresa && planos.id_plano = alunos.id_plano where alunos.id=%s""",id)
        if not plano:
            plano = banco.retornabd("""select planos.id_plano,planos.tipo from planos INNER JOIN alunos on planos.id_plano = alunos.id_plano where alunos.id=%s""",id)
        planos1 = banco.retornasbd("""select planos.id_plano, planos.tipo from planos where padrao=1;""",0)
        planos2 = banco.retornasbd("""select planos.id_plano, planos.tipo, empresas.nome from planos inner join empresas on planos.id_empresa=empresas.id_empresa;""",0)
        cursos = banco.retornasbd("""select cursos.id_curso,cursos.nome from cursos""",0)
        return render_template('login.html',titulo="Meu Espaço",nome=nome,matriculas=matriculas,plano=plano,planos1=planos1, planos2=planos2,cursos=cursos)
    elif banco.autenticaEmpresa(usuario, senha):
        nome = banco.retornabd("""select nome from empresas where usuario=%s""",usuario)
        id = banco.retornabd("""select id_empresa from empresas where usuario=%s""",usuario)
        plano = banco.retornabd("""select empresas.nome,planos.tipo,planos.id_plano from planos inner join empresas on planos.id_empresa=empresas.id_empresa where planos.id_empresa=%s;""", id)
        planos = banco.retornasbd("""select planos.id_plano, planos.tipo from planos where padrao = %s;""",1)
        alunos = []
        inativas = []
        ativas = []
        empresa_ativa = bool(banco.retornabd("""select * from empresas where usuario=%s && ativa=true;""", usuario))
        print("A empresa", usuario, "está ativa!",empresa_ativa)
        if plano:
            alunos = banco.retornasbd("""select nome,id from alunos where id_plano=%s;""", plano[2])
            if empresa_ativa:
                inativas = banco.retornasbd("""select matriculas.id_matricula, cursos.nome, alunos.nome from matriculas inner join cursos inner join alunos on matriculas.id_curso=cursos.id_curso && matriculas.id_aluno=alunos.id where status='inativo' && alunos.id_plano=%s;""",plano[2])
                ativas = banco.retornasbd("""select matriculas.id_matricula, cursos.nome, alunos.nome from matriculas inner join cursos inner join alunos on matriculas.id_curso=cursos.id_curso && matriculas.id_aluno=alunos.id where status='ativo' && alunos.id_plano=%s;""",plano[2])
            
        return render_template('login.html',titulo="Meu Espaço",nome=nome,plano=plano,planos1=planos,alunos=alunos,ativas=ativas,inativas=inativas)
    elif (banco.adm(usuario, senha)):
        nome = banco.retornabd("""select nome from administrador where usuario=%s""",usuario)           
        inativas = []
        ativas = []
        empresa_ativa = bool(banco.retornabd("""select * from empresas where ativa=%s;""", True))
        if empresa_ativa:
                inativas = banco.retornasbd("""select id_empresa, nome, usuario from empresas where ativa=false;""",0)
                ativas = banco.retornasbd("""select id_empresa, nome, usuario from empresas where ativa=true;""",0)            
        return render_template('login.html',titulo="Administração do Sistema",nome=nome,empresa_ativa=ativas,empresa_inativa=inativas,area=1)
    else:
        flash('Sem usuário logado!')
        return redirect('/')

@app.route('/contrataplano', methods=['POST'])
def contrataplano():
    usuario = str(session['usuario'])
    senha = session.get('senha')
    plano = request.form['plano']
    if banco.autenticaUsuario(usuario, senha):       
        if banco.contrataplano(plano,usuario):
            flash('Plano contratado!')
            return redirect('/entrar')
        else:
            flash('Erro ao contratar plano selecionado')
            return redirect('/entrar')
    elif banco.autenticaEmpresa(usuario, senha):
        id = banco.retornabd("""SELECT id_empresa FROM empresas WHERE usuario = %s;""", usuario)
        tipo = banco.retornabd("""SELECT tipo FROM planos WHERE id_plano = %s;""", plano)
        banco.alterabd("""INSERT INTO planos (tipo,id_empresa) VALUES (%s,%s);""", (tipo[0], id))
        flash('Plano contratado!')
        return redirect('/entrar')
    else:
        flash('Sem usuário logado!')
        return redirect('/')


@app.route('/adicionacurso', methods=['POST'])
def adicionacurso():
    id_curso = int(request.form['curso'])
    usuario = str(session['usuario'])
    if banco.adicionacurso(id_curso,usuario):
        flash('Curso adicionado!')
        return redirect('/entrar')
    else:
        flash('Erro ao adicionar curso selecionado')
        return redirect('/entrar')

@app.route('/removermatricula', methods=['POST'])
def removermatricula():
    matricula = request.form['matricula']
    print(matricula)
    if banco.alterabd("""delete from matriculas where id_matricula=%s""", matricula):
        flash('Erro ao ativar matricula!')
        return redirect('/entrar')
    else:
        flash('Matricula excluida')
        return redirect('/entrar')

@app.route('/ativarmatricula', methods=['POST'])
def ativarmatricula():
    matricula = request.form['matricula']
    if banco.alterabd("""update matriculas set status='ativo' where id_matricula=%s""", matricula):
        flash('Erro ao ativar matricula!')
        return redirect('/entrar')
    else:
        flash('Matricula ativada')
        return redirect('/entrar')

@app.route('/desativarmatricula', methods=['POST'])
def desativarmatricula():
    matricula = request.form['matricula']
    print(matricula)
    if banco.alterabd("""update matriculas set status='inativo' where id_matricula=%s""", matricula):
        flash('Erro ao desativar matricula!')
        return redirect('/entrar')
    else:
        flash('Matricula desativada')
        return redirect('/entrar')

@app.route('/ativarempresa', methods=['POST'])
def ativarempresa():
    empresa = request.form['empresa']
    if banco.alterabd("""update empresas set ativa=true where id_empresa=%s""", empresa):
        flash('Erro ao ativar empresa!')
        return redirect('/entrar')
    else:
        flash('Empresa ativada')
        return redirect('/entrar')

@app.route('/desativarempresa', methods=['POST'])
def desativarempresa():
    empresa = request.form['empresa']
    if banco.alterabd("""update empresas set ativa=false where id_empresa=%s""", empresa):
        flash('Erro ao desativar empresa!')
        return redirect('/entrar')
    else:
        flash('Empresa desativada')
        return redirect('/entrar')

@app.route('/sair', methods=['GET', 'POST'])
def sair():
    session['usuario'] = None
    session['senha'] = None
    return redirect('/')

#------------------------------------------------------------------------------------------------------------------
#Rotas para iteração administrativa

@app.route('/alunos')
def alunos():
    usuario = session.get('usuario')
    senha = session.get('senha')
    if banco.adm(usuario, senha):
        if request.args.get('nome'):
            nome = request.args['nome']
            dados = banco.retornasbd("""select * from alunos where nome=%s;""",nome)
        elif request.args.get('id'):
            id = request.args['id']
            dados = banco.retornasbd("""select * from alunos where id=%s;""",id)
        elif request.args.get('id_plano'):
            id_plano = request.args['id_plano']
            dados = banco.retornasbd("""select * from alunos where id_plano=%s;""",id_plano)
        elif request.args.get('senha'):
            senha = request.args['senha']
            dados = banco.retornasbd("""select * from alunos where senha=%s;""",senha)
        elif request.args.get('usuario'):
            usuario = request.args['usuario']
            dados = banco.retornasbd("""select * from alunos where usuario=%s;""",usuario)
        elif request.args.get('telefone'):
            telefone = request.args['telefone']
            dados = banco.retornasbd("""select * from alunos where telefone=%s;""",telefone)
        elif request.args.get('endereco'):
            endereco = request.args['endereco']
            dados = banco.retornasbd("""select * from alunos where endereco=%s;""",endereco)
        else:
            dados = banco.retornasbd("""select * from alunos;""",0)    
        alunos = []
        for i in dados:
            alunos.append( { "id" : i[0], "usuario" : i[1], "nome" : i[2], "senha": i[3], "id_plano": i[4], "telefone": i[5], "endereco": i[6]})
        return jsonify(alunos)
    elif session.get('usuario') == None:
        return redirect('/entrar')
    else:
        flash('Acesso restrito aos administradores!')
        return redirect('/entrar')

@app.route('/alunos', methods=['POST'])
def novoalunos(): 
    if banco.consultabd("""select * from alunos where usuario=%s;""", (request.args.get('usuario'))):
        return jsonify('Usuario já existe!')
    elif request.args.get('usuario') and request.args.get('nome') and request.args.get('senha'):
        usuario1 = request.args.get('usuario')
        nome1 = request.args['nome']
        senha1 = request.args['senha']
        banco.cadastrarUsuario(usuario1,nome1,senha1)
        if request.args.get('id_plano'):
            plano = request.args['id_plano']
            banco.alterabd("""update alunos set id_plano=%s where usuario=%s;""", (plano,usuario1))        
        if request.args.get('telefone'):
            telefone = request.args['telefone']
            banco.alterabd("""update alunos set telefone=%s where usuario=%s;""", (telefone,usuario1)) 
        if request.args.get('endereco'):
            endereco = request.args['endereco']
            banco.alterabd("""update alunos set endereco=%s where usuario=%s;""", (endereco,usuario1)) 
        return jsonify('Aluno adicionado!')
    else:        
        return jsonify('Faltam argumentos!')

@app.route('/alunos/<int:id>', methods=['PUT'])
def alteraalunos(id):
    usuario = session.get('usuario')
    senha = session.get('senha')
    alterados = []
    if banco.adm(usuario, senha):
        if request.args.get('usuario'):
            usuario = request.args['usuario']
            banco.alterabd("""UPDATE alunos SET usuario=%s WHERE id=%s;""",(usuario,id))
            alterados.append('Usuario')
        if request.args.get('nome'):
            nome = request.args['nome']
            banco.alterabd("""UPDATE alunos SET nome=%s WHERE id=%s;""",(nome,id))
            alterados.append('Nome')
        if request.args.get('senha'):
            senha = request.args['senha']
            banco.alterabd("""UPDATE alunos SET senha=%s WHERE id=%s;""",(senha,id))
            alterados.append('Senha')
        if request.args.get('id_plano'):
            plano = request.args['id_plano']
            banco.alterabd("""UPDATE alunos SET id_plano=%s WHERE id=%s;""",(plano,id))
            alterados.append('Plano')
        if request.args.get('telefone'):
            telefone = request.args['telefone']
            banco.alterabd("""UPDATE alunos SET telefone=%s WHERE id=%s;""",(telefone,id))
            alterados.append('Telefone')
        if request.args.get('endereco'):
            endereco = request.args['endereco']
            banco.alterabd("""UPDATE alunos SET endereco=%s WHERE id=%s;""",(endereco,id))
            alterados.append('Endereço')
        if alterados:
            if len(alterados) > 1:
                alterados[-1] += (' alterados') 
            else:
                alterados[-1] += (' alterado')           
            return jsonify(alterados)
        else:            
            return jsonify('Nenhuma alteração realizada')       
    elif session.get('usuario') == None:
        return redirect('/entrar')
    else:
        flash('Acesso restrito aos administradores!')
        return redirect('/entrar')

@app.route('/alunos/<int:id>', methods=['DELETE'])
def deletealunos(id):
    usuario = session.get('usuario')
    senha = session.get('senha')
    if banco.adm(usuario, senha):
        banco.alterabd("""DELETE FROM alunos WHERE id=%s;""",id)        
        return jsonify('Aluno excluido')
    elif session.get('usuario') == None:
        return redirect('/entrar')
    else:
        flash('Acesso restrito aos administradores!')
        return redirect('/entrar')

@app.route('/matriculas')
def matriculas():
    usuario = session.get('usuario')
    senha = session.get('senha')
    if banco.adm(usuario, senha):
        if request.args.get('id_matricula'):
            matricula = request.args['id_matricula']
            dados = banco.retornasbd("""select * from matriculas where id_matricula=%s;""",matricula)
        elif request.args.get('id_aluno'):
            aluno = request.args['id_aluno']
            dados = banco.retornasbd("""select * from matriculas where id_aluno=%s;""",aluno)
        elif request.args.get('id_curso'):
            curso = request.args['id_curso']
            dados = banco.retornasbd("""select * from matriculas where id_curso=%s;""",curso)
        elif request.args.get('status'):
            status = request.args['status']
            dados = banco.retornasbd("""select * from matriculas where status=%s;""",status)
        else:
            dados = banco.retornasbd("""select * from matriculas;""",0)    
        matriculas = []
        for i in dados:
            matriculas.append( {"id_matricula": i[0], "id_aluno": i[1], "id_curso": i[2], "status": i[3]})
        return jsonify(matriculas)
    elif session.get('usuario') == None:
        return redirect('/entrar')
    else:
        flash(usuario + ' não é uma empresa!')
        return redirect('/entrar')

@app.route('/matriculas', methods=['POST'])
def novamatriculas():
    usuario = session.get('usuario')
    senha = session.get('senha')
    if banco.adm(usuario, senha):
        if request.args.get('id_aluno') and request.args.get('id_curso'):
            id_aluno = request.args['id_aluno']
            id_curso = request.args['id_curso']
            status = "inativo"
            banco.alterabd("""insert into matriculas (id_aluno,id_curso,status) values (%s,%s,%s);""", (id_aluno,id_curso,status))
            if request.args.get('status'):
                status = request.args['status']
                banco.alterabd("""update matriculas set status='ativo' where id_aluno=%s && id_curso=%s;""", (id_aluno,id_curso))            
            return jsonify('Matricula adicionada!')
        else:
            return jsonify('Faltam argumentos!')
    elif session.get('usuario') == None:
        return redirect('/entrar')
    else:
        flash('Acesso restrito aos administradores!')
        return redirect('/entrar')

@app.route('/matriculas/<int:id>', methods=['PUT'])
def alteramatriculas(id):
    usuario = session.get('usuario')
    senha = session.get('senha')
    alterados = []
    if banco.adm(usuario, senha):
        if request.args.get('id_aluno'):
            aluno = request.args['id_aluno']
            banco.alterabd("""UPDATE matriculas SET id_aluno=%s WHERE id_matricula=%s;""",(aluno,id))
            alterados.append('Aluno')
        if request.args.get('id_curso'):
            curso = request.args['id_curso']
            banco.alterabd("""UPDATE matriculas SET id_curso=%s WHERE id_matricula=%s;""",(curso,id))
            alterados.append('Curso')
        if request.args.get('status'):
            status = request.args['status']
            banco.alterabd("""UPDATE matriculas SET status=%s WHERE id_matricula=%s;""",(status,id))
            alterados.append('status')
        if alterados:
            if len(alterados) > 1:
                alterados[-1] += (' alterados') 
            else:
                alterados[-1] += (' alterado')           
            return jsonify(alterados)
        else:
            return jsonify(('Nenhuma alteração realizada'))
    elif session.get('usuario') == None:
        return redirect('/entrar')
    else:
        flash('Acesso restrito aos administradores!')
        return redirect('/entrar')

@app.route('/matriculas/<int:id>', methods=['DELETE'])
def deletematriculas(id):
    usuario = session.get('usuario')
    senha = session.get('senha')
    if banco.adm(usuario, senha):
        banco.alterabd("""DELETE FROM matriculas WHERE id_matricula=%s;""",id)
        return jsonify('Matricula excluida!')
    elif session.get('usuario') == None:
        return redirect('/entrar')
    else:
        flash('Acesso restrito aos administradores!')
        return redirect('/entrar')

@app.route('/cursos')
def cursos():
    usuario = session.get('usuario')
    senha = session.get('senha')
    if banco.autenticaUsuario(usuario, senha) or banco.autenticaEmpresa(usuario, senha) or banco.adm(usuario, senha):
        if request.args.get('id_curso'):
            curso = request.args['id_curso']
            dados = banco.retornasbd("""select * from cursos where id_curso=%s;""",curso)
        elif request.args.get('nome'):
            nome = request.args['nome']
            dados = banco.retornasbd("""select * from cursos where nome=%s;""",nome)
        elif request.args.get('carga_horaria'):
            carga_horaria = request.args['carga_horaria']
            dados = banco.retornasbd("""select * from cursos where carga_horaria=%s;""",carga_horaria)
        elif request.args.get('investimento'):
            investimento = request.args['investimento']
            dados = banco.retornasbd("""select * from cursos where investimento=%s;""",investimento)
        elif request.args.get('trilha'):
            trilha = request.args['trilha']
            dados = banco.retornasbd("""select * from cursos where trilha=%s;""",trilha)
        else:
            dados = banco.retornasbd("""select * from cursos;""",0)    
        cursos = []
        for i in dados:
            cursos.append( {"id_curso": i[0], "nome": i[1], "carga_horaria": i[2], "investimento": i[3]})
        return jsonify(cursos)
    elif session.get('usuario') == None:
        return redirect('/entrar')
    else:
        flash(usuario + ' não é uma empresa!')
        return redirect('/entrar')

@app.route('/cursos', methods=['POST'])
def novocurso():
    usuario = session.get('usuario')
    senha = session.get('senha')
    if banco.autenticaEmpresa(usuario, senha) or banco.adm(usuario, senha):
        if request.args.get('id_curso') and request.args.get('nome'):
            id_curso = request.args['id_curso']
            nome = request.args['nome']
            banco.alterabd("""insert into cursos (id_curso,nome) values (%s,%s);""", (id_curso,nome))
            if request.args.get('carga_horaria'):
                carga_horaria = request.args['carga_horaria']
                banco.alterabd("""update cursos set carga_horaria=%s where id_curso=%s;""", (carga_horaria, id_curso))
            if request.args.get('investimento'):
                investimento = request.args['investimento']
                banco.alterabd("""update cursos set investimento=%s where id_curso=%s;""", (investimento, id_curso))
            if request.args.get('trilha'):
                trilha = request.args['trilha']
                banco.alterabd("""update cursos set trilha=%s where id_curso=%s;""", (trilha, id_curso))
            return jsonify('curso adicionado!')
        else:
            return jsonify('Faltam argumentos!')
    elif session.get('usuario') == None:
        return redirect('/entrar')
    else:
        flash('Acesso restrito aos administradores!')
        return redirect('/entrar')

@app.route('/cursos/<int:id>', methods=['PUT'])
def alteracursos(id):
    usuario = session.get('usuario')
    senha = session.get('senha')
    alterados = []
    if banco.adm(usuario, senha):
        if request.args.get('nome'):
            nome = request.args['nome']
            banco.alterabd("""UPDATE cursos SET nome=%s WHERE id_curso=%s;""",(nome,id))
            alterados.append('Nome')
        if request.args.get('carga_horaria'):
            carga_horaria = request.args['carga_horaria']
            banco.alterabd("""UPDATE cursos SET carga_horaria=%s WHERE id_curso=%s;""",(carga_horaria,id))
            alterados.append('carga_horaria')
        if request.args.get('investimento'):
            investimento = request.args['investimento']
            banco.alterabd("""UPDATE cursos SET investimento=%s WHERE id_curso=%s;""",(investimento,id))
            alterados.append('investimento')
        if request.args.get('trilha'):
            trilha = request.args['trilha']
            banco.alterabd("""UPDATE cursos SET trilha=%s WHERE id_curso=%s;""",(trilha,id))
            alterados.append('investimento')
        if alterados:
            if len(alterados) > 1:
                alterados[-1] += (' alterados') 
            else:
                alterados[-1] += (' alterado')           
            return jsonify(alterados)
        else:
            return jsonify('Nenhuma alteração realizada')
    elif session.get('usuario') == None:
        return redirect('/entrar')
    else:
        flash('Acesso restrito aos administradores!')
        return redirect('/entrar')

@app.route('/cursos/<int:id>', methods=['DELETE'])
def deletecursos(id):
    usuario = session.get('usuario')
    senha = session.get('senha')
    if banco.adm(usuario, senha):
        banco.alterabd("""DELETE FROM cursos WHERE id_curso=%s;""",id)
        return jsonify('Curso excluido!')
    elif session.get('usuario') == None:
        return redirect('/entrar')
    else:
        flash('Acesso restrito aos administradores!')
        return redirect('/entrar')

@app.route('/planos')
def planos():
    usuario = session.get('usuario')
    senha = session.get('senha')
    if banco.adm(usuario, senha):
        if request.args.get('id_plano'):
            plano = request.args['id_plano']
            dados = banco.retornasbd("""select * from planos where id_plano=%s;""",plano)
        elif request.args.get('tipo'):
            tipo = request.args['tipo']
            dados = banco.retornasbd("""select * from planos where tipo=%s;""",tipo)
        elif request.args.get('id_empresa'):
            id_empresa = request.args['id_empresa']
            dados = banco.retornasbd("""select * from planos where id_empresa=%s;""",id_empresa)
        elif request.args.get('padrao'):
            padrao = request.args['padrao']
            dados = banco.retornasbd("""select * from planos where padrao=%s;""",padrao)
        else:
            dados = banco.retornasbd("""select * from planos;""",0)    
        planos = []
        for i in dados:
            planos.append( {"id_plano": i[0], "tipo": i[1], "id_empresa": i[2], "padrao": i[3]})
        return jsonify(planos)
    elif session.get('usuario') == None:
        return redirect('/entrar')
    else:
        flash(usuario + ' não é uma empresa!')
        return redirect('/entrar')

@app.route('/planos', methods=['POST'])
def novoplano():
    usuario = session.get('usuario')
    senha = session.get('senha')
    if banco.adm(usuario, senha):
        if request.args.get('id_plano') and request.args.get('tipo'):
            id_plano = request.args['id_plano']
            tipo = request.args['tipo']
            banco.alterabd("""insert into planos (id_plano,tipo) values (%s,%s);""", (id_plano,tipo))
            if request.args.get('id_empresa'):
                id_empresa = request.args['id_empresa']
                banco.alterabd("""update planos set id_empresa=%s where id_plano=%s;""", (id_empresa, id_plano))
            if request.args.get('padrao'):
                padrao = request.args['padrao']
                banco.alterabd("""update planos set padrao=%s where id_plano=%s;""", (padrao, id_plano))
            return jsonify('plano adicionado!')
        else:
            return jsonify('Faltam argumentos!')
    elif session.get('usuario') == None:
        return redirect('/entrar')
    else:
        flash('Acesso restrito aos administradores!')
        return redirect('/entrar')

@app.route('/planos/<int:id>', methods=['PUT'])
def alteraplanos(id):
    usuario = session.get('usuario')
    senha = session.get('senha')
    alterados = []
    if banco.adm(usuario, senha):
        if request.args.get('tipo'):
            tipo = request.args['tipo']
            banco.alterabd("""UPDATE planos SET tipo=%s WHERE id_plano=%s;""",(tipo,id))
            alterados.append('Tipo')
        if request.args.get('id_empresa'):
            id_empresa = request.args['id_empresa']
            banco.alterabd("""UPDATE planos SET id_empresa=%s WHERE id_plano=%s;""",(id_empresa,id))
            alterados.append('Id da empresa')
        if request.args.get('padrao'):
            padrao = request.args['padrao']
            banco.alterabd("""UPDATE planos SET padrao=%s WHERE id_plano=%s;""",(padrao,id))
            alterados.append('Padrão')
        if alterados:
            if len(alterados) > 1:
                alterados[-1] += (' alterados') 
            else:
                alterados[-1] += (' alterado')           
            return jsonify(alterados)
        else:
            return jsonify('Nenhuma alteração realizada')
    elif session.get('usuario') == None:
        return redirect('/entrar')
    else:
        flash('Acesso restrito aos administradores!')
        return redirect('/entrar')

@app.route('/planos/<int:id>', methods=['DELETE'])
def deleteplanos(id):
    usuario = session.get('usuario')
    senha = session.get('senha')
    if banco.adm(usuario, senha):
        banco.alterabd("""DELETE FROM planos WHERE id_plano=%s;""",id)
        return jsonify('Plano excluido!')
    elif session.get('usuario') == None:
        return redirect('/entrar')
    else:
        flash('Acesso restrito aos administradores!')
        return redirect('/entrar')

@app.route('/empresas')
def empresas():
    usuario = session.get('usuario')
    senha = session.get('senha')
    if banco.adm(usuario, senha):
        if request.args.get('nome'):
            nome = request.args['nome']
            dados = banco.retornasbd("""select * from empresas where nome=%s;""",nome)
        elif request.args.get('id_empresa'):
            id_empresa = request.args['id_empresa']
            dados = banco.retornasbd("""select * from empresas where id_empresa=%s;""",id_empresa)
        elif request.args.get('senha'):
            senha = request.args['senha']
            dados = banco.retornasbd("""select * from empresas where senha=%s;""",senha)
        elif request.args.get('usuario'):
            usuario = request.args['usuario']
            dados = banco.retornasbd("""select * from empresas where usuario=%s;""",usuario)
        elif request.args.get('telefone'):
            telefone = request.args['telefone']
            dados = banco.retornasbd("""select * from empresas where telefone=%s;""",telefone)
        elif request.args.get('endereco'):
            endereco = request.args['endereco']
            dados = banco.retornasbd("""select * from empresas where endereco=%s;""",endereco)        
        elif request.args.get('ativa'):
            ativa = request.args['ativa']
            dados = banco.retornasbd("""select * from empresas where ativa=%s;""",ativa)        
        else:
            dados = banco.retornasbd("""select * from empresas;""",0)    
        empresas = []
        for i in dados:
            empresas.append( { "id_empresa" : i[0], "usuario" : i[1], "nome" : i[2], "senha": i[3] })
        return jsonify(empresas)
    elif session.get('usuario') == None:
        return redirect('/entrar')
    else:
        flash('Acesso restrito aos administradores!')
        return redirect('/entrar')

@app.route('/empresas', methods=['POST'])
def novoempresa(): 
    if banco.consultabd("""select * from empresas where usuario=%s;""", request.args.get('usuario')):
        return jsonify(('Usuario já existe!'))
    elif request.args.get('usuario') and request.args.get('nome') and request.args.get('senha'):
        usuario1 = request.args['usuario']
        nome1 = request.args['nome']
        senha1 = request.args['senha']
        banco.cadastrarEmpresa(usuario1, nome1, senha1)        
        if request.args.get('telefone'):
            telefone = request.args['telefone']
            banco.alterabd("""update empresas set telefone=%s where usuario=%s;""", (telefone,usuario1)) 
        if request.args.get('endereco'):
            endereco = request.args['endereco']
            banco.alterabd("""update empresas set endereco=%s where usuario=%s;""", (endereco,usuario1)) 
        if request.args.get('ativa'):
            ativa = request.args['ativa']
            banco.alterabd("""update empresas set aativa=%s where usuario=%s;""", (ativa,usuario1)) 
        return jsonify('Empresa adicionado!')
    else:
        return jsonify('Faltam argumentos!')

@app.route('/empresas/<int:id>', methods=['PUT'])
def alteraempresas(id):
    usuario = session.get('usuario')
    senha = session.get('senha')
    alterados = []
    if banco.adm(usuario, senha):
        if request.args.get('usuario'):
            usuario = request.args['usuario']
            banco.alterabd("""UPDATE empresas SET usuario=%s WHERE id_empresa=%s;""",(usuario,id))
            alterados.append('usuario')
        if request.args.get('nome'):
            nome = request.args['nome']
            banco.alterabd("""UPDATE empresas SET nome=%s WHERE id_empresa=%s;""",(nome,id))
            alterados.append('nome')
        if request.args.get('senha'):
            senha = request.args['senha']
            banco.alterabd("""UPDATE empresas SET senha=%s WHERE id_empresa=%s;""",(senha,id))
            alterados.append('senha')
        if request.args.get('telefone'):
            telefone = request.args['telefone']
            banco.alterabd("""UPDATE empresas SET telefone=%s WHERE id=%s;""",(telefone,id))
            alterados.append('Telefone')
        if request.args.get('endereco'):
            endereco = request.args['endereco']
            banco.alterabd("""UPDATE empresas SET endereco=%s WHERE id=%s;""",(endereco,id))
            alterados.append('Endereço')
        if request.args.get('ativa'):
            ativa = request.args['ativa']
            banco.alterabd("""UPDATE empresas SET ativa=%s WHERE id=%s;""",(ativa,id))
            alterados.append('Ativação')
        if alterados:
            if len(alterados) > 1:
                alterados[-1] += (' alterados') 
            else:
                alterados[-1] += (' alterado')           
            return jsonify(alterados)
        else:
            return jsonify('Nenhuma alteração realizada')
    elif session.get('usuario') == None:
        return redirect('/entrar')
    else:
        flash('Acesso restrito aos administradores!')
        return redirect('/entrar')

@app.route('/empresas/<int:id>', methods=['DELETE'])
def deleteempresas(id):
    usuario = session.get('usuario')
    senha = session.get('senha')
    if banco.adm(usuario, senha):
        banco.alterabd("""DELETE FROM empresas WHERE id_empresa=%s;""",id)
        return jsonify('Empresa excluida')
    elif session.get('usuario') == None:
        return redirect('/entrar')
    else:
        flash('Acesso restrito aos administradores!')
        return redirect('/entrar')

app.run(host='192.168.1.100', port=80, debug=True)