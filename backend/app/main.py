from datetime import date
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .database import Base, engine, get_db
from . import models, schemas
from .security import hash_password, verify_password, create_token, read_token
from .finance_agent import categorize, build_insights

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Agentic AI Personal Finance API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
bearer = HTTPBearer(auto_error=False)

def current_user(creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    uid = read_token(creds.credentials) if creds else None
    user = db.get(models.User, uid) if uid else None
    if not user:
        raise HTTPException(401, "Please log in again")
    return user

@app.get("/")
def home():
    return {"message":"Agentic AI Personal Finance API is running"}

@app.post("/api/auth/register")
def register(data: schemas.RegisterIn, db: Session=Depends(get_db)):
    if db.query(models.User).filter_by(email=data.email).first():
        raise HTTPException(400,"Email already registered")
    user=models.User(name=data.name,email=data.email,password_hash=hash_password(data.password))
    db.add(user); db.commit(); db.refresh(user)
    return {"token":create_token(user.id),"user":{"id":user.id,"name":user.name,"email":user.email}}

@app.post("/api/auth/login")
def login(data: schemas.LoginIn, db: Session=Depends(get_db)):
    user=db.query(models.User).filter_by(email=data.email).first()
    if not user or not verify_password(data.password,user.password_hash):
        raise HTTPException(401,"Incorrect email or password")
    return {"token":create_token(user.id),"user":{"id":user.id,"name":user.name,"email":user.email}}

@app.get("/api/me")
def me(user=Depends(current_user)):
    return {"id":user.id,"name":user.name,"email":user.email}

@app.get("/api/transactions")
def list_transactions(user=Depends(current_user),db:Session=Depends(get_db)):
    return db.query(models.Transaction).filter_by(user_id=user.id).order_by(desc(models.Transaction.txn_date),desc(models.Transaction.id)).all()

@app.post("/api/transactions")
def add_transaction(data:schemas.TransactionIn,user=Depends(current_user),db:Session=Depends(get_db)):
    category=data.category or (categorize(data.description) if data.kind=="expense" else "Income")
    item=models.Transaction(user_id=user.id,kind=data.kind,amount=data.amount,category=category,description=data.description,txn_date=data.txn_date)
    db.add(item); db.commit(); db.refresh(item); return item

@app.delete("/api/transactions/{item_id}")
def delete_transaction(item_id:int,user=Depends(current_user),db:Session=Depends(get_db)):
    item=db.query(models.Transaction).filter_by(id=item_id,user_id=user.id).first()
    if not item: raise HTTPException(404,"Transaction not found")
    db.delete(item); db.commit(); return {"ok":True}

@app.get("/api/budgets")
def list_budgets(user=Depends(current_user),db:Session=Depends(get_db)):
    return db.query(models.Budget).filter_by(user_id=user.id).all()

@app.post("/api/budgets")
def add_budget(data:schemas.BudgetIn,user=Depends(current_user),db:Session=Depends(get_db)):
    item=models.Budget(user_id=user.id,**data.model_dump()); db.add(item); db.commit(); db.refresh(item); return item

@app.get("/api/goals")
def list_goals(user=Depends(current_user),db:Session=Depends(get_db)):
    return db.query(models.SavingsGoal).filter_by(user_id=user.id).all()

@app.post("/api/goals")
def add_goal(data:schemas.GoalIn,user=Depends(current_user),db:Session=Depends(get_db)):
    item=models.SavingsGoal(user_id=user.id,**data.model_dump()); db.add(item); db.commit(); db.refresh(item); return item

@app.patch("/api/goals/{item_id}/contribute")
def contribute(item_id:int,amount:float,user=Depends(current_user),db:Session=Depends(get_db)):
    if amount<=0: raise HTTPException(400,"Contribution must be positive")
    item=db.query(models.SavingsGoal).filter_by(id=item_id,user_id=user.id).first()
    if not item: raise HTTPException(404,"Goal not found")
    item.saved_amount+=amount; db.commit(); db.refresh(item); return item

@app.get("/api/dashboard")
def dashboard(user=Depends(current_user),db:Session=Depends(get_db)):
    tx=db.query(models.Transaction).filter_by(user_id=user.id).all()
    bs=db.query(models.Budget).filter_by(user_id=user.id).all()
    gs=db.query(models.SavingsGoal).filter_by(user_id=user.id).all()
    result=build_insights(tx,bs,gs); month=date.today().strftime("%Y-%m")
    result["recent_transactions"]=[{"id":t.id,"kind":t.kind,"amount":t.amount,"category":t.category,"description":t.description,"txn_date":t.txn_date.isoformat()} for t in sorted(tx,key=lambda x:(x.txn_date,x.id),reverse=True)[:8]]
    result["budgets"]=[{"id":b.id,"category":b.category,"limit_amount":b.limit_amount,"spent":sum(t.amount for t in tx if t.kind=="expense" and t.category==b.category and t.txn_date.strftime("%Y-%m")==month)} for b in bs if b.month==month]
    result["goals"]=[{"id":g.id,"title":g.title,"target_amount":g.target_amount,"saved_amount":g.saved_amount} for g in gs]
    return result

@app.post("/api/demo/seed")
def seed(user=Depends(current_user),db:Session=Depends(get_db)):
    if db.query(models.Transaction).filter_by(user_id=user.id).count():
        return {"message":"Transactions already exist; demo data was not added."}
    today=date.today()
    samples=[("income",45000,"Income","Monthly salary",today.replace(day=1)),
    ("expense",4500,"Food","Groceries and food",today.replace(day=2)),
    ("expense",1800,"Travel","Uber rides",today.replace(day=4)),
    ("expense",3200,"Shopping","Clothes shopping",today.replace(day=7)),
    ("expense",2200,"Bills","Internet and electricity bill",today.replace(day=10)),
    ("expense",1200,"Education","Course books",today.replace(day=12))]
    for kind,amt,cat,desc,dt in samples:
        db.add(models.Transaction(user_id=user.id,kind=kind,amount=amt,category=cat,description=desc,txn_date=dt))
    for cat,limit in [("Food",6000),("Travel",3000),("Shopping",4000),("Bills",3500)]:
        db.add(models.Budget(user_id=user.id,category=cat,limit_amount=limit,month=today.strftime("%Y-%m")))
    db.add(models.SavingsGoal(user_id=user.id,title="Emergency Fund",target_amount=50000,saved_amount=12000))
    db.commit()
    return {"message":"Demo transactions, budgets and savings goal added"}
