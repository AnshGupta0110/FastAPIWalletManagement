from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import uvicorn

# MySQL Database setup
MYSQL_DATABASE_URL = "mysql+pymysql://root:124578@localhost/WalletDB"
engine = create_engine(MYSQL_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database 
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    wallet_balance = Column(Float, default=0.0)
    
    transactions = relationship("Transaction", back_populates="user")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="transactions")

# Creating tables
Base.metadata.create_all(bind=engine)

# Models
class UserResponse(BaseModel):
    name: str
    email: str
    phone: str
    wallet_balance: float
    
    class Config:
        from_attributes = True

class WalletUpdateRequest(BaseModel):
    user_id: int
    amount: float

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    transaction_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

app = FastAPI(
    title="Wallet Management System",
    description="Backend Development Assignment - AMRR TechSols",
    version="1.0.0"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create some sample users for testing
@app.on_event("startup")
def create_sample_data():
    db = SessionLocal()
    try:
        if db.query(User).first() is None:
            users = [
                User(name="Ansh Gupta", email="ansh@example.com", phone="1234567890", wallet_balance=1000.0),
                User(name="Mahesh", email="mahesh@example.com", phone="9003922210", wallet_balance=500.0),
                User(name="Parth", email="parth@example.com", phone="5799005435", wallet_balance=250.0)
            ]
            for user in users:
                db.add(user)
            db.commit()
    finally:
        db.close()

# 1) List Users API – Fetch all users details (name, email, phone) along with their wallet balance
@app.get("/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# 2) Update Wallet API – Add or update an amount in any particular user's wallet
@app.put("/wallet/update")
def update_wallet(request: WalletUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update wallet balance
    user.wallet_balance += request.amount
    
    # Create transaction record
    transaction_type = "credit" if request.amount > 0 else "debit"
    transaction = Transaction(
        user_id=request.user_id,
        amount=abs(request.amount),
        transaction_type=transaction_type
    )
    
    db.add(transaction)
    db.commit()
    
    return {
        "message": "Wallet updated successfully",
        "user_id": request.user_id,
        "new_balance": user.wallet_balance
    }

# 3) Fetch Transactions API – Fetch all wallet transactions for a specific user by passing their user_id
@app.get("/transactions/{user_id}", response_model=List[TransactionResponse])
def fetch_transactions(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    return transactions

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
