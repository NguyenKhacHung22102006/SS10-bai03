from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel

DATABASE_URL = "mysql+pymysql://root:123456789@localhost:3306/connect_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

app = FastAPI()

# DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# MODEL (map tới bảng có sẵn)
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)

# SCHEMA
class ProductSchema(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        orm_mode = True

class ProductCreate(BaseModel):
    name: str
    price: float

class ProductUpdate(BaseModel):
    name: str
    price: float

# API
@app.get("/products", response_model=list[ProductSchema])
def get_all_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.post("/products", response_model=ProductSchema)
def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(name=product.name, price=product.price)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.put("/products/{product_id}", response_model=ProductSchema)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    prd = db.query(Product).filter(Product.id == product_id).first()

    if prd is None:
        raise HTTPException(404, "Sản phẩm không tồn tại")

    prd.name = product.name
    prd.price = product.price
    db.commit()
    db.refresh(prd)

    return prd

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    prd = db.query(Product).filter(Product.id == product_id).first()

    if prd is None:
        raise HTTPException(404, "Sản phẩm không tồn tại")

    db.delete(prd)
    db.commit()

    return {"message": "Xóa thành công"}