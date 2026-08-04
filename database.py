import json
from datetime import timedelta, datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base, sessionmaker



engine=create_engine('sqlite:///database.db')
Base = declarative_base()
class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String)
    protocol =Column(String)
    traff_used_gb =Column(Float, nullable=True)
    traffic_limit_gb =Column(Float, nullable=False)
    name = Column(String)
    is_banned=Column(Boolean)
    Expires = Column(DateTime)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
now=datetime.now()
# User1 = Player(id=1, email="User1@mail.ru", protocol="U", traff_used_gb=50.0, traffic_limit_gb=50.0, name="User1", is_banned=False, Expires=now+timedelta(days=30))
# User2 = Player(id=2, email="User2@mail.ru", protocol="U", traff_used_gb=0.0, traffic_limit_gb=50.0, name="User2", is_banned=True, Expires=now-timedelta(days=10))
# session.add_all([User1, User2])
# session.commit()
# print(add_user("User2.mail@ru"))
def add_user(email):
    client = session.query(Player).filter(Player.email==email).first()
    Data={
        "email":client.email,
        "protocol":client.protocol,
        "traff_used_gb":client.traff_used_gb,
        "traffic_limit_gb":client.traffic_limit_gb,
        "name":client.name,
        "is_banned":client.is_banned,
        "Expires":client.Expires.strftime("%Y-%m-%d %H:%M:%S"),
    }
    print(client)
    return json.dumps(Data)
def register(email: str, protocol:str, name:str):
    user_id=Player(email=email, protocol=protocol, traff_used_gb=0.0, traffic_limit_gb=50.0, name=name, is_banned=False, Expires=now+timedelta(days=30))
    session.add(user_id)
    session.commit()
    Data={
        "description":"База данных отредактирована успешно",
        "email":user_id.email,
        "protocol":user_id.protocol,
        "traff_used_gb":user_id.traff_used_gb,
        "traffic_limit_gb":user_id.traffic_limit_gb,
        "name":user_id.name,
        "is_banned":user_id.is_banned,
        "Expires":user_id.Expires.strftime("%Y-%m-%d %H:%M:%S"),
    }
    return json.dumps(Data)
# Описываем модель таблицы messages как класс Python
class Message(Base):
    __tablename__ = "messages"  # Имя таблицы в БД

    id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор строки (автоматически растет)
    user_id = Column(Integer, index=True)  # ID пользователя из Telegram (добавлен индекс для скорости)
    role = Column(String)  # Роль отправителя: 'system', 'user' или 'assistant'
    content = Column(Text)  # Текст самого сообщения

def init_db():
    """Создает таблицы в базе данных, если они еще не существуют."""
    # Метод create_all сам смотрит на классы, наследуемые от Base, и создает нужные таблицы
    Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clear_user_history(user_id):
    """Удаляет всю историю переписки для конкретного пользователя."""
    # Открываем сессию (контекстный менеджер сам закроет её после выхода из блока)
    with SessionLocal() as db:
        # Ищем все сообщения пользователя и удаляем их
        db.query(Message).filter(Message.user_id == user_id).delete(synchronize_session=False)
        # Сохраняем изменения (коммитим транзакцию)
        db.commit()

def get_user_history(user_id):
    """Выгружает историю переписки пользователя из БД и форматирует её для API."""
    history = []
    with SessionLocal() as db:
        # Запрашиваем все сообщения для конкретного юзера, сортируем по id (хронологический порядок)
        messages = db.query(Message).filter(Message.user_id == user_id).order_by(Message.id.asc()).all()
        # Проходимся циклом по каждому объекту Message
        for msg in messages:
            # Формируем словарь в нужном для OpenAI/Groq формате и добавляем в список
            history.append({"role": msg.role, "content": msg.content})
    # Возвращаем готовую историю сообщений (или пустой список)
    return history

def save_message(user_id, role, content):
    """Сохраняет одно сообщение в базу данных."""
    with SessionLocal() as db:
        # Создаем экземпляр модели Message (новая строка в таблице)
        new_msg = Message(user_id=user_id, role=role, content=content)
        # Добавляем объект в сессию
        db.add(new_msg)
        # Сохраняем изменения в базе
        db.commit()
# При импорте этого файла автоматически создаем таблицу, если её нет