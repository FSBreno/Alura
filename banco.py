import pymysql

conexao = pymysql.connect(host='localhost', user= 'breno', password='Bren0ferr@z', database='alura')
cursor = conexao.cursor()    
if (conexao):
    cursor.close()
    conexao.close()
    print("Teste de conexão realizado com sucesso!")

def consultabd(comando, condicao):
    try:      
        conexao = pymysql.connect(host='localhost', user= 'breno', password='Bren0ferr@z', database='alura')
        cursor = conexao.cursor()         
        print('A consulta foi realizada')
        return cursor.execute(comando, condicao)
    except (Exception, pymysql.Error) as error :
        if(conexao):
            print("Falha ao se conectar ao Banco de Dados", error)
    finally:
            # closing database connection.
            if (conexao):
                cursor.close()
                conexao.close()
                print("A conexão com o MySQL foi fechada.")


def alterabd(comando, condicao):
    try:
        conexao = pymysql.connect(host='localhost', user= 'breno', password='Bren0ferr@z', database='alura')
        cursor = conexao.cursor()
        cursor.execute(comando, condicao)
        conexao.commit()
        print("A alteração foi realizada")
    except (Exception, pymysql.Error) as error :
        if(conexao):
            print("Falha ao se conectar ao Banco de Dados", error)
    finally:
            # closing database connection.
            if (conexao):
                cursor.close()
                conexao.close()
                print("A conexão com o MySQL foi fechada.")

def retornabd(comando, condicao):
    try:
        conexao = pymysql.connect(host='localhost', user= 'breno', password='Bren0ferr@z', database='alura')
        cursor = conexao.cursor()
        conexao = pymysql.connect(host='localhost', user= 'breno', password='Bren0ferr@z', database='alura')
        cursor = conexao.cursor()  
        cursor.execute(comando, condicao)
        print('A consulta foi realizada')
        return cursor.fetchone()
    except (Exception, pymysql.Error) as error :
        if(conexao):
            print("Falha ao se conectar ao Banco de Dados", error)
    finally:
            # closing database connection.
            if (conexao):
                cursor.close()
                conexao.close()
                print("A conexão com o MySQL foi fechada.")

def retornasbd(comando,condicao):
    try:
        if (condicao):
            conexao = pymysql.connect(host='localhost', user= 'breno', password='Bren0ferr@z', database='alura')
            cursor = conexao.cursor()
            conexao = pymysql.connect(host='localhost', user= 'breno', password='Bren0ferr@z', database='alura')
            cursor = conexao.cursor()  
            cursor.execute(comando,condicao)
            print('A consulta foi realizada')             
            return cursor.fetchall()
        else:
            conexao = pymysql.connect(host='localhost', user= 'breno', password='Bren0ferr@z', database='alura')
            cursor = conexao.cursor()
            conexao = pymysql.connect(host='localhost', user= 'breno', password='Bren0ferr@z', database='alura')
            cursor = conexao.cursor()  
            cursor.execute(comando)
            print('A consulta foi realizada')             
            return cursor.fetchall()
    except (Exception, pymysql.Error) as error :
        if(conexao):
            print("Falha ao se conectar ao Banco de Dados", error)
    finally:
            # closing database connection.
            if (conexao):
                cursor.close()
                conexao.close()
                print("A conexão com o MySQL foi fechada.")

#--------------------------------------
def autenticaUsuario(usuario, senha):
    try:
        comando = """select * from alunos where usuario = %s and senha = %s;"""
        condicao = [usuario, senha]
        return consultabd(comando, condicao)   
    except (Exception, pymysql.Error) as error:
        print(error)

def cadastrarUsuario(usuario, nome, senha):
    try:
        condicao = [usuario, nome, senha]
        comando = """insert into alunos (usuario,nome,senha) values (%s,%s,%s);"""
        alterabd(comando, condicao)
        return autenticaUsuario(usuario, senha)     
    except (Exception, pymysql.Error) as error:
        print(error)

def autenticaEmpresa(usuario, senha):
    try:
        comando = """select * from empresas where usuario = %s and senha = %s;"""
        condicao = [usuario, senha]
        return consultabd(comando, condicao)   
    except (Exception, pymysql.Error) as error:
        print(error)

def cadastrarEmpresa(usuario, nome, senha):
    try:
        ativa=False
        condicao = [usuario, nome, senha,ativa]
        comando = """insert into empresas (usuario,nome,senha,ativa) values (%s,%s,%s,%s);"""
        alterabd(comando, condicao)
        return autenticaUsuario(usuario, senha)     
    except (Exception, pymysql.Error) as error:
        print(error)


def adm(usuario, senha):
    try:
        comando = """select * from administrador where usuario = %s and senha = %s;"""
        condicao = [usuario, senha]
        return consultabd(comando, condicao)    
    except (Exception, pymysql.Error) as error:
        print(error)

def contrataplano(plano, usuario):
    try:
        condicao = [plano, str(usuario)]
        comando = """update alunos set id_plano=%s where usuario=%s;"""
        alterabd(comando, condicao)
        return consultabd("""select id_plano from alunos where usuario=%s""", condicao[1])     
    except (Exception, pymysql.Error) as error:
        print(error)

def adicionacurso(id_curso, usuario):
    id_aluno = retornabd("""select id from alunos where usuario=%s;""", usuario)
    status = "inativo"
    condicao = [id_aluno, id_curso, status]
    if not consultabd("""select * from matriculas where id_aluno=%s and id_curso=%s""", (condicao[0],condicao[1])):
        try:
            comando = """insert into matriculas (id_aluno, id_curso, status) values (%s,%s,%s);"""
            alterabd(comando, condicao)
            return consultabd("""select * from matriculas where id_aluno=%s and id_curso=%s""", (condicao[0],condicao[1]))     
        except (Exception, pymysql.Error) as error:
            print(error)
    else:
        return 0


#--------------------------------------
          