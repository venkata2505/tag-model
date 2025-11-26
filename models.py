from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, ForeignKey, Table

DATABASE_URL = "postgresql+psycopg2://postgres:Srimammu%401@localhost:5432/tag_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

product_tag = Table(
    "product_tag",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

saleorder_tag = Table(
    "saleorder_tag",
    Base.metadata,
    Column("sale_order_id", Integer, ForeignKey("sale_orders.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    value = Column(String(100), nullable=False)
    type_ = Column(String(50), nullable=False)
    color = Column(String(20), nullable=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", secondary=product_tag, back_populates="tags")
    sale_orders = relationship("SaleOrder", secondary=saleorder_tag, back_populates="tags")

    def __repr__(self):
        return (f"<Tag id={self.id} value='{self.value}' type='{self.type_}' "
                f"color='{self.color}' description='{self.description}' "
                f"created_at={self.created_at}>")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    sku = Column(String(100), unique=True, nullable=False)
    price = Column(Integer, nullable=False)  
    description = Column(String(255), nullable=True)
    category = Column(String(100), nullable=True)
    brand = Column(String(100), nullable=True)
    stock_qty = Column(Integer, default=0)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    #Relationship
    sale_order_details = relationship("SaleOrderDetail", back_populates="product")
    tags = relationship("Tag", secondary=product_tag, back_populates="products")

    def __repr__(self):
        tag_values = [tag.value for tag in self.tags]
        return (f"<Product id={self.id} name='{self.name}' "
                f"sku='{self.sku}' price='{self.price}' "
                f"description='{self.description}' category='{self.category}' brand='{self.brand}' "
                f"stock_qty='{self.stock_qty}' status='{self.status}' created_at={self.created_at}>")

class SaleOrder(Base):
    __tablename__ = "sale_orders"

    id = Column(Integer, primary_key=True)
    customer_name = Column(String(150), nullable=False)
    total_amount = Column(Integer, default=0)
    status = Column(String(20), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    tags = relationship("Tag", secondary=saleorder_tag, back_populates="sale_orders")
    details = relationship("SaleOrderDetail", back_populates="sale_order")

    def __repr__(self):
        tag_values = [tag.value for tag in self.tags]
        return (f"<SaleOrder customer='{self.customer_name}' "
                f"total_amount='{self.total_amount}' status='{self.status}' created_at={self.created_at}>")

class SaleOrderDetail(Base):
    __tablename__ = "sale_order_details"

    id = Column(Integer, primary_key=True)
    sale_order_id = Column(Integer, ForeignKey("sale_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    qty = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)  
    subtotal = Column(Integer, nullable=False)

    # Relationships
    sale_order = relationship("SaleOrder", back_populates="details")
    product = relationship("Product", back_populates="sale_order_details")

    def __repr__(self):
        return f"<SaleOrderDetail id={self.id} qty={self.qty}>"

