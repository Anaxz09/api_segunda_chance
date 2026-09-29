from sqlalchemy import create_engine, Column, DateTime, Integer, String, Float, func, Enum, Text, TIMESTAMP, ForeignKey, \
    Date, VARCHAR
from sqlalchemy.orm import sessionmaker, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()
engine = create_engine('mysql+pymysql://root:senaisp@localhost:3306/frada')
SessionLocalExemplo = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    senha = Column(Text, nullable=False)
    criado_em = Column(DateTime, default=func.now())

    def set_password(self, password):
        self.senha = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha, password)

    def serialize(self):
        dados =  {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "criado_em": self.criado_em
        }
        return dados

class Denuncia_anonima(Base):
    __tablename__ = 'denuncias_anonimas'
    id = Column(Integer, primary_key=True)
    fk_id_usuarios2 = Column(String(70), nullable=False)
    descricao = Column(String(120), nullable=False)
    urgencia = Column(String(70), nullable=False)
    estado = Column(String(50), nullable=False)
    criado_em = Column(DateTime, default=func.now())

    def serialize(self):
        dados = {
            "id": self.id,
            "fk_id_usuarios2": self.fk_id_usuarios2,
            "descricao": self.descricao,
            "urgencia": self.urgencia,
            "estado": self.estado,
        }
        return dados

class Animal(Base):
    __tablename__ = 'animal'
    id = Column(Integer, primary_key=True)
    fk_id_usuarios1 = Column(Integer, ForeignKey('usuarios.id'))
    fk_id_categoria = Column(Integer, ForeignKey('categoria.id'))
    nome = Column(String(70), nullable=False)
    porte = Column(String(70), nullable=False)
    sexo = Column(String(50), nullable=False)
    raca = Column(String(50), nullable=False)
    adotado = Column(String(50), nullable=False)
    idade = Column(String(50), nullable=False)
    criado_em = Column(DateTime, default=func.now())

    def serialize(self):
        dados = {
            "id": self.id,
            "fk_id_usuarios1": self.fk_id_usuarios1,
            "fk_categoria": self.fk_id_categoria,
            "nome": self.nome,
            "porte": self.porte,
            "sexo": self.sexo,
            "raca": self.raca,
            "adotado": self.adotado,
            "idade": self.idade,
            "criado_em": self.criado_em
        }
        return dados

class Categoria(Base):
    __tablename__ = 'categoria'
    id = Column(Integer, primary_key=True)
    nome = Column(String(70), nullable=False)
    Criado_em = Column(DateTime, default=func.now())

    def serialize(self):
        dados = {
            "id": self.id,
            "nome": self.nome
        }
        return dados

class Ong (Base):
    __tablename__ = 'ong'
    id = Column(Integer, primary_key=True)
    nome = Column(String(70), nullable=False)
    cnpj = Column(String(50), nullable=False)
    estado = Column(String(50), nullable=False)
    senha = Column(String(50), nullable=False, unique=True)
    criado_em = Column(DateTime, default=func.now())

    def set_password(self, password):
        self.senha = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha, password)

    def serialize(self):
        dados = {
            "id": self.id,
            "nome": self.nome,
            "cnpj": self.cnpj,
            "estado": self.estado,
            "senha": self.senha,
            "criado_em": self.criado_em
        }
        return dados

class Login (Base):
    __tablename__ = 'login'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), nullable=False)
    senha = Column(String(225), nullable=False, unique=True)
    criado_em = Column(DateTime, default=func.now())

    def serialize(self):
        dados = {
            "id": self.id,
            "email": self.email,
            "senha": self.senha,
            "criado_em": self.criado_em
        }
        return dados

class Login_ong (Base):
    __tablename__ = 'login_ong'
    id = Column(Integer, primary_key=True)
    cnpj = Column(String(120), nullable=False, unique=True)
    senha = Column(String(225), nullable=False, unique=True)
    criado_em = Column(DateTime, default=func.now())

    def serialize(self):
        dados = {
            "id": self.id,
            "cnpj": self.cnpj,
            "senha": self.senha,
            "criado_em": self.criado_em
        }

        return dados