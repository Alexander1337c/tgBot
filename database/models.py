from sqlalchemy import String, Float, DateTime, func, Numeric, ForeignKey, BigInteger, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=True)
    last_name: Mapped[str]  = mapped_column(String(150), nullable=True)

class Account(Base):
    __tablename__ = 'account'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    limit: Mapped[float] = mapped_column(Numeric(10,2), nullable=True, default=0)
    balance: Mapped[float] = mapped_column(Numeric(10,2), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)

    user: Mapped['User'] = relationship(backref='account')

class Category(Base):
    __tablename__='category'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    icon: Mapped[str] = mapped_column(String(150), nullable=True)


class Transaction(Base):
    __tablename__='transaction'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)    
    account_id: Mapped[int] = mapped_column(ForeignKey('account.id', ondelete='CASCADE'), nullable=False)   
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id', ondelete='CASCADE'), nullable=True)
    income: Mapped[bool] = mapped_column(unique=False, default=False)

    user: Mapped['User'] = relationship(backref='transaction')
    account: Mapped['Account'] = relationship(backref='transaction')
    category: Mapped['Category'] = relationship(backref='transaction')