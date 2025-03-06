from sqlmodel import SQLModel

class User(SQLModel, table=True):
    __table_args__ = {'schema': 'auth'} 