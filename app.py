from functools import wraps
from flask import Flask, jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from models import SessionLocalExemplo, Usuario, Denuncia_anonima, Animal, Categoria, Ong, Login, \
    Login_ong
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager

from models import Usuario

app = Flask(__name__)

# Definir a SENHA, em produção colocar em lugar SEGURO
app.config['JWT_SECRET_KEY'] = 'Segund@_ch@nc&'
jwt = JWTManager(app)


def shutdown_session(exception=None):
    db = SessionLocalExemplo()
    db.remove()
    db.close()


def load_user(id_u1):
    db = SessionLocalExemplo()
    user = select(Usuario).where(Usuario.id_usuario == int(id_u1))
    resultado = db.execute(user).scalar_one_or_none()
    db.close()
    return resultado


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        print(f"User: {current_user}")
        db = SessionLocalExemplo()
        try:
            sql = select(Usuario).where(Usuario.email == current_user)
            sql_resultado = db.execute(sql).scalar()
            print('Usuario:', sql_resultado)
            if sql_resultado and sql_resultado.perfil == 'ADMIN':
                return fn(*args, **kwargs)
            dado = {
                "msg": "Acesso negado: Requer privilégio de administrador",
            }
            return jsonify(dado), 403
        except Exception as e:
            print(e)
        finally:
            db.close()

    return wrapper


@app.route("/post_usuario", methods=["POST"])
def cadastrar_usuario():
    """
    **API para cadastro de Usuario**

    ### Endpoint:
    POST/ post_usuario

    ### Parâmetros de Entrada (JSON)
    ```json
    {
    "nome": "String (obrigatorio) - Nome completo do usuario",
    "email": "String (obrigatorio) - Endereço de e-mail do usuario",
    "senha": "Text (obrigatorio) - Senha do usuario para acesso ao sistema",
    "criado_em": "DateTime -   Quando o cadastro foi realizado"
    }
    ```

    ### Respostas (JSON):
    * **200 Created:** usuario registrado com sucesso.
        ```json
        {
            "msg":"Usuario cadastrado"
        }
        ```
    * **400 Bad Request:** Ausencia de campos obrigatorios.
        ```json
        {
            "msg":"Valor não encontrado"
        }
        ```
     * **409 Conflict:** Usuario já cadastrado com e-mail fornecido.
        ```json
        {
            "msg":"Usuario já cadastrado"
        }
        ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
        ```json
        {
            "msg":"Erro ao registrar usuario: [Descricao do Erro]"
        }
        ```
    """
    dados = request.get_json()
    nome = dados.get("nome")
    email = dados.get("email")
    senha = dados.get("senha")

    db = SessionLocalExemplo()

    print(nome, email, senha)
    if not nome or not email or not senha:
        return jsonify({"msg": "valor não encontrado"}), 400

    user_v = select(Usuario).where(Usuario.email == email)
    result_usuario = db.execute(user_v).first()

    if result_usuario:
        return jsonify({"msg": "Usuario já cadastrado"}), 409
    try:
        user = Usuario(nome=nome, email=email)
        user.set_password(senha)
        db.add(user)
        db.commit()
        return jsonify({"msg": "Usuario cadastrado"}), 200
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        return jsonify({"msg:" f"Erro ao registrar o Usuario: {str(e)}"}), 500
    finally:
        db.close()

@app.route("/login_do_usuario", methods=["POST"])
def login_usuarios():
    """
        **API para Autenticação de Usuario**

        ### Endpoint:
        POST/ login

        ### Parãmetros de Entrada (JSON):
        ```json
        {
            "email": "VARCHAR (obrigatorio) - Endereco de e-mail do usuario",
            "senha": "VARCHAR (obrigatorio) - Senha De acesso do usuario"
        }
        ```

        ### Respostas (JSON):
        * **200 OK:** Usuario autenticado com sucesso.
            ```json
            {
                "msg": "Usuario logado com sucesso"
            }
            ```
        * **401 Unauthorized:** credenciais invalidas ou incorretas.
        ```json
        {
            "msg": "Credenciais"
        }
        ```
        * **404 Bad Request:** Falha operacional ao processar a solicitacao.
        ```json
        {
            "msg": "[Descricao do Erro]"
        }
        ```
    """
    dados = request.get_json()
    email = dados.get("email")
    senha = dados.get("senha")
    if not email or not senha:
        return jsonify({"msg": "valor não encontrado"}), 404
    db = SessionLocalExemplo()
    try:
        sql_user = select(Usuario).where(Usuario.email == email)
        usuario_existente = db.execute(sql_user).scalar_one_or_none()

        if usuario_existente and usuario_existente.check_password(senha):
            return jsonify({"msg": "Usuario logado com sucesso"}), 200

        dados = {
            "msg": "Credenciais"
        }
        return jsonify(dados), 401
    except Exception as e:
        return jsonify({"msg": str(e)}), 400
    finally:
        db.close()


@app.route("/post_ong", methods=["POST"])
def cadastrar_ong():
    """
    **API para cadastro de ONG**

    ### Endpoint:
    POST/ post_ong

    ### Parâmetros de Entrada (JSON)
    ```json
    {
    "nome": "String (obrigatorio) - Nome completo da ONG",
    "cnpj": "String (obrigatorio) - CNPJ da ONG",
    "estado": "String (obrigatorio) - Estado da ONG",
    "senha": "Text (obrigatorio) - Senha da ONG para acesso ao sistema",
    "criado_em": "DateTime -   Quando o cadastro foi realizado"
    }
    ```

    ### Respostas (JSON):
    * **200 Created:** ONG registrado com sucesso.
        ```json
        {
            "msg":"ONG cadastrado"
        }
        ```
    * **400 Bad Request:** Ausencia de campos obrigatorios.
        ```json
        {
            "msg":"Valor não encontrado"
        }
        ```
     * **409 Conflict:** ONG já cadastrado com cnpj fornecido.
        ```json
        {
            "msg":"ONG já cadastrado"
        }
        ```
    * **500 Internal Server Error:** Falha operacional no banco de dados.
        ```json
        {
            "msg":"Erro ao registrar ONG: [Descricao do Erro]"
        }
        ```
    """

    dados = request.get_json()
    nome = dados.get("nome")
    cnpj = dados.get("cnpj")
    estado = dados.get("estado")
    senha = dados.get("senha")

    db = SessionLocalExemplo()

    print(nome, cnpj, estado, senha)
    if not nome or not cnpj or not estado or not senha:
        return jsonify({"msg": "valor não encontrado"}), 400

    ong_v = select(Ong).where(Ong.cnpj == cnpj)
    result_ong = db.execute(ong_v).first()

    if result_ong:
        return jsonify({"msg": "ONG já cadastrada"}), 409
    try:
        ong = Ong(nome=nome, cnpj=cnpj, estado=estado)
        ong.set_password(senha)
        db.add(ong)
        db.commit()
        return jsonify({"msg": "ONG cadastrada"}), 200
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        return jsonify({"msg:" f"Erro ao registrar ONG: {str(e)}"}), 500
    finally:
        db.close()

@app.route("/login_da_ong", methods=["POST"])
def login_ong():
    """
        **API para Autenticação da ONG**

        ### Endpoint:
        POST/ login

        ### Parãmetros de Entrada (JSON):
        ```json
        {
            "cnpj": "VARCHAR (obrigatório) -  CNPJ da ONG",
            "senha": "VARCHAR (obrigatório) - Senha De acesso da ONG"
        }
        ```

        ### Respostas (JSON):
        * **200 OK:** ONG autenticado com sucesso.
            ```json
            {
                "msg": "ONG logado com sucesso"
            }
            ```
        * **401 Unauthorized:** credênciais inválidas ou incorretas.
        ```json
        {
            "msg": "Credênciais"
        }
        ```
        * **404 Bad Request:** Falha operacional ao processar a solicitação.
        ```json
        {
            "msg": "[Descricao do Erro]"
        }
        ```
    """
    dados = request.get_json()
    cnpj = dados.get("cnpj")
    senha = dados.get("senha")
    if not cnpj or not senha:
        return jsonify({"msg": "valor não encontrado"}), 404
    db = SessionLocalExemplo()
    try:
        sql_user = select(Ong).where(Ong.cnpj == cnpj)
        ong_existente = db.execute(sql_user).scalar_one_or_none()

        if ong_existente and ong_existente.check_password(senha):
            return jsonify({"msg": "ONG logada com sucesso"}), 200

        dados = {
            "msg": "Credênciais"
        }
        return jsonify(dados), 401
    except Exception as e:
        return jsonify({"msg": str(e)}), 400
    finally:
        db.close()



@app.route("/animal_post", methods=["POST"])
def cadastro_animal():
    """
           **API para adoção de animais**

           ### Endpoint:
           POST/ animal

           ### Parãmetros de Entrada (JSON):
           ```json
           {
               "cnpj": "VARCHAR (obrigatório) -  CNPJ da ONG",
               "senha": "VARCHAR (obrigatório) - Senha De acesso da ONG"
           }
           ```

           ### Respostas (JSON):
           * **200 OK:** ONG autenticado com sucesso.
               ```json
               {
                   "msg": "ONG logado com sucesso"
               }
               ```
           * **401 Unauthorized:** credênciais inválidas ou incorretas.
           ```json
           {
               "msg": "Credênciais"
           }
           ```
           * **404 Bad Request:** Falha operacional ao processar a solicitação.
           ```json
           {
               "msg": "[Descricao do Erro]"
           }
           ```
       """
    dados = request.get_json()
    nome = dados.get("nome")
    id_user = dados.get("id_user")
    id_categoria = dados.get("id_categoria")
    porte = dados.get("porte")
    sexo = dados.get("sexo")
    raca = dados.get("raca")
    adotado = dados.get("adotado")
    idade = dados.get("idade")
    print(nome, porte, sexo, raca, adotado, idade)

    banco = SessionLocalExemplo()

    if not nome or not id_user or not id_categoria or not porte or not sexo or not raca or not adotado or not idade:
        return jsonify({"msg": "valor não encontrado"}), 400

    try:
        novo_animal = Animal(nome=nome,fk_id_usuarios1=id_user,fk_id_categoria=id_categoria, porte=porte, sexo=sexo, raca=raca, adotado=adotado, idade=idade)
        banco.add(novo_animal)
        banco.commit()

        return jsonify({
            "msg": "Animal cadastrado com sucesso",
            "novo_animal": novo_animal.id
        }), 201
    except SQLAlchemyError as e:
        banco.rollback()
        return jsonify({"Erro": str(e)}), 500


@app.route("/animal_get", methods=["GET"])
def listar_animal():
    """
           **API para adoção de animais**

           ### Endpoint:
           GET/ animal

           ### Parãmetros de Entrada (JSON):
           ```json
           {
               "cnpj": "VARCHAR (obrigatório) -  CNPJ da ONG",
               "senha": "VARCHAR (obrigatório) - Senha De acesso da ONG"
           }
           ```

           ### Respostas (JSON):
           * **200 OK:** ONG autenticado com sucesso.
               ```json
               {
                   "msg": "ONG logado com sucesso"
               }
               ```
           * **401 Unauthorized:** credênciais inválidas ou incorretas.
           ```json
           {
               "msg": "Credênciais"
           }
           ```
           * **404 Bad Request:** Falha operacional ao processar a solicitação.
           ```json
           {
               "msg": "[Descricao do Erro]"
           }
           ```
       """
    db = SessionLocalExemplo()
    try:
        sql_animal = select(Animal)
        result_animal = db.execute(sql_animal).scalars().all()
        list_animal = []
        for animal in result_animal:
            list_animal.append(animal.serialize())
        return jsonify(list_animal), 200
    except Exception as e:
        db.rollback()
    finally:
        db.close()



@app.route("/denuncia_post", methods=["POST"])
def criar_denuncia_anonima():
    """
               **API para adoção de animais**

               ### Endpoint:
               POST/ denuncia_anonima

                ### Parâmetros de Entrada (JSON)
                    ```json
                    {
                    "urgencia": "String (obrigatorio) - Urgencia da denuncia",
                    "descricao":"String (obrigatorio) - Descricao da denuncia",
                    "criado_em": "DateTime -   Quando a denuncia foi realizado"
                    }
                    ```

               ### Respostas (JSON):
               * **200 OK:** Denuncia autenticado com sucesso.
                   ```json
                   {
                       "msg": "Denuncia enviada com sucesso"
                   }
                   ```
               * **401 Unauthorized:** credênciais inválidas ou incorretas.
               ```json
               {
                   "msg": "Credênciais"
               }
               ```
               * **404 Bad Request:** Falha operacional ao processar a solicitação.
               ```json
               {
                   "msg": "[Descricao do Erro]"
               }
               ```
           """
    dados = request.get_json()
    descricao = dados.get("descricao")
    urgencia = dados.get("urgencia")
    estado = dados.get("estado")

    banco = SessionLocalExemplo()

    print(descricao, urgencia, estado)
    if not descricao or not urgencia or not estado:
        return jsonify({"msg": "valor não encontrado"}), 400
    try:
        nova_denuncia = Denuncia_anonima(descricao=descricao, urgencia=urgencia, estado=estado)
        banco.add(nova_denuncia)
        banco.commit()

        return jsonify({
            "msg": "Denuncia enviada com sucesso",
            "nova_denuncia": nova_denuncia.id
        }), 201
    except SQLAlchemyError as e:
        banco.rollback()
        return jsonify({"Erro": str(e)}), 500

@app.route("/denuncia_get", methods=["GET"])
def listar_denuncia_anonima():
    """
               **API para adoção de animais**

               ### Endpoint:
               GET/ denuncia_anonima

                ### Parâmetros de Entrada (JSON)
                    ```json
                    {
                    "urgencia": "String (obrigatorio) - Urgencia da denuncia",
                    "descricao":"String (obrigatorio) - Descricao da denuncia",
                    "criado_em": "DateTime -   Quando a denuncia foi realizado"
                    }
                    ```

               ### Respostas (JSON):
               * **200 OK:** Denuncia autenticado com sucesso.
                   ```json
                   {
                       "msg": "Denuncia enviada com sucesso"
                   }
                   ```
               * **401 Unauthorized:** credênciais inválidas ou incorretas.
               ```json
               {
                   "msg": "Credênciais"
               }
               ```
               * **404 Bad Request:** Falha operacional ao processar a solicitação.
               ```json
               {
                   "msg": "[Descricao do Erro]"
               }
               ```
           """
    db = SessionLocalExemplo()
    try:
        sql_denuncia = select(Denuncia_anonima)
        result_denuncia = db.execute(sql_denuncia).scalars().all()
        list_denuncia = []
        for denuncia in result_denuncia:
            list_denuncia.append(denuncia.serialize())
        return jsonify(list_denuncia), 200
    except Exception as e:
        db.rollback()
    finally:
        db.close()




@app.route("/categoria_post", methods=["POST"])
def criar_categoria():
    """
           **API para adoção de animais**

           ### Endpoint:
           POST/ categoria

           ### Parãmetros de Entrada (JSON):
           ```json
           {
               "nome": "String (obrigatório) -  nome da categoria",

           ```

           ### Respostas (JSON):
           * **200 OK:** nome autenticado com sucesso.
               ```json
               {
                   "msg": "nome criado com sucesso"
               }
               ```
           * **401 Unauthorized:** credênciais inválidas ou incorretas.
           ```json
           {
               "msg": "Credênciais"
           }
           ```
           * **404 Bad Request:** Falha operacional ao processar a solicitação.
           ```json
           {
               "msg": "[Descricao do Erro]"
           }
           ```
       """
    dados = request.get_json()
    nome = dados.get("nome")

    print(nome)
    banco = SessionLocalExemplo()

    print(nome)
    if not nome:
        return jsonify({"msg": "valor não encontrado"}), 400
    try:
        nova_categoria = Categoria(nome=nome)
        banco.add(nova_categoria)
        banco.commit()

        return jsonify({
            "msg": "Categoria enviada com sucesso",
            "nova_categoria": nova_categoria.id
        }), 201
    except SQLAlchemyError as e:
        banco.rollback()
        return jsonify({"Erro": str(e)}), 500

@app.route("/categoria_get", methods=["GET"])
def listar_categoria():
    """
           **API para adoção de animais**

           ### Endpoint:
           GET/ categoria

           ### Parãmetros de Entrada (JSON):
           ```json
           {
               "nome": "String (obrigatório) -  nome da categoria",

           ```

           ### Respostas (JSON):
           * **200 OK:** nome autenticado com sucesso.
               ```json
               {
                   "msg": "nome criado com sucesso"
               }
               ```
           * **401 Unauthorized:** credênciais inválidas ou incorretas.
           ```json
           {
               "msg": "Credênciais"
           }
           ```
           * **404 Bad Request:** Falha operacional ao processar a solicitação.
           ```json
           {
               "msg": "[Descricao do Erro]"
           }
           ```
       """
    db = SessionLocalExemplo()
    try:
        sql_categoria = select(Categoria)
        result_categoria = db.execute(sql_categoria).scalars().all()
        list_categoria = []
        for categoria in result_categoria:
            list_categoria.append(categoria.serialize())
        return jsonify(list_categoria), 200
    except Exception as e:
        db.rollback()
    finally:
        db.close()