from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import SessionLocal, Tag, Product, SaleOrder, SaleOrderDetail
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AddItemRequest(BaseModel):
    product_id: int
    qty: int

class OrderResponse(BaseModel):
    id: int
    customer_name: str
    total_amount: float
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

@app.post("/tags")
def create_tag(data: dict):
    with SessionLocal() as session:
        tag = Tag(
            value=data["value"],
            type_=data["type_"],
            color=data["color"],
            description=data["description"]
        )
        session.add(tag)
        session.commit()
        session.refresh(tag)
    return tag

@app.get("/tags")
def list_tags(page: int = 1, page_size: int = 20):
    with SessionLocal() as session:
        query = session.query(Tag)

        if page_size == -1:
            tags = query.all()
        else:
            offset = (page - 1) * page_size
            tags = query.offset(offset).limit(page_size).all()

    return tags

@app.put("/tags/{tag_id}")
def update_tag(tag_id: int, data: dict):
    with SessionLocal() as session:
        tag = session.query(Tag).filter_by(id=tag_id).first()
        if not tag:
            raise HTTPException(404, "Tag not found")

        for key, value in data.items():
            if value:
                setattr(tag, key, value)

        session.commit()
        session.refresh(tag)
    return tag

@app.delete("/tags/{tag_id}")
def delete_tag(tag_id: int):
    with SessionLocal() as session:
        tag = session.query(Tag).filter_by(id=tag_id).first()
        if not tag:
            raise HTTPException(404, "Tag not found")

        session.delete(tag)
        session.commit()
    return {"message": "Tag deleted"}

@app.post("/products")
def create_product(data: dict):
    with SessionLocal() as session:
        new_product = Product(
            name=data["name"],
            sku=data["sku"],
            price=data["price"],
            description=data["description"],
            category=data["category"],
            brand=data["brand"],
            stock_qty=data["stock_qty"],
            status=data["status"]
        )
        session.add(new_product)
        session.commit()
        session.refresh(new_product)
    return new_product

@app.get("/products")
def list_products(page: int = 1, page_size: int = 20):
    with SessionLocal() as session:
        query = session.query(Product)

        if page_size == -1:
            products = query.all()
        else:
            offset = (page - 1) * page_size
            products = query.offset(offset).limit(page_size).all()

    return products

@app.put("/products/{pid}")
def update_product(pid: int, data: dict):
    with SessionLocal() as session:
        product = session.query(Product).filter_by(id=pid).first()
        if not product:
            raise HTTPException(404, "Product not found")

        for key, value in data.items():
            if value != "":
                setattr(product, key, value)

        session.commit()
        session.refresh(product)
    return product

@app.delete("/products/{pid}")
def delete_product(pid: int):
    with SessionLocal() as session:
        product = session.query(Product).filter_by(id=pid).first()
        if not product:
            raise HTTPException(404, "Product not found")

        session.delete(product)
        session.commit()
    return {"message": "Product deleted"}

@app.post("/products/{product_id}/tags/{tag_id}")
def assign_tag_to_product(product_id: int, tag_id: int):
    with SessionLocal() as session:
        product = session.query(Product).filter_by(id=product_id).first()
        tag = session.query(Tag).filter_by(id=tag_id).first()

        if not product or not tag:
            raise HTTPException(404, "Product or Tag not found")

        if tag in product.tags:
            raise HTTPException(400, "Tag already assigned")

        product.tags.append(tag)
        session.commit()

    return {"message": "Tag assigned to product"}

@app.delete("/products/{product_id}/tags/{tag_id}")
def remove_tag_from_product(product_id: int, tag_id: int):
    with SessionLocal() as session:
        product = session.query(Product).filter_by(id=product_id).first()
        tag = session.query(Tag).filter_by(id=tag_id).first()

        if not product or not tag:
            raise HTTPException(404, "Product or Tag not found")

        if tag not in product.tags:
            raise HTTPException(400, "Tag not assigned")

        product.tags.remove(tag)
        session.commit()

    return {"message": "Tag removed from product"}

@app.post("/orders")
def create_sale_order(data: dict):
    with SessionLocal() as session:
        order = SaleOrder(
            customer_name=data["customer_name"],
            total_amount=0,
            status="draft",
            created_at=datetime.utcnow()
        )
        session.add(order)
        session.commit()
        session.refresh(order)
    return order

@app.get("/orders")
def list_orders():
    with SessionLocal() as session:
        return session.query(SaleOrder).all()

@app.get("/orders/{order_id}")
def order_details(order_id: int):
    with SessionLocal() as session:
        order = session.query(SaleOrder).filter_by(id=order_id).first()
        if not order:
            raise HTTPException(404, "Order not found")

        details = session.query(SaleOrderDetail).filter_by(sale_order_id=order_id).all()

        return {
            "order": order,
            "items": details
        }

@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    with SessionLocal() as session:
        order = session.query(SaleOrder).filter_by(id=order_id).first()
        if not order:
            raise HTTPException(404, "Order not found")

        details = session.query(SaleOrderDetail).filter_by(sale_order_id=order_id).all()
        for d in details:
            session.delete(d)

        session.delete(order)
        session.commit()

    return {"message": "Order deleted"}

@app.post("/orders/{order_id}/items", response_model=OrderResponse)
def add_item(order_id: int, data: AddItemRequest):
    with SessionLocal() as session:
        # Fetch order and product
        order = session.query(SaleOrder).filter_by(id=order_id).first()
        product = session.query(Product).filter_by(id=data.product_id).first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        if data.qty > product.stock_qty:
            raise HTTPException(status_code=400, detail="Not enough stock")

        subtotal = product.price * data.qty

        try:
            # Deduct stock
            product.stock_qty -= data.qty

            # Add order detail
            detail = SaleOrderDetail(
                sale_order_id=order.id,
                product_id=product.id,
                qty=data.qty,
                price=product.price,
                subtotal=subtotal
            )
            session.add(detail)
            session.commit()

            # Update total_amount
            total_details = session.query(SaleOrderDetail).filter_by(sale_order_id=order.id).all()
            order.total_amount = sum(d.subtotal for d in total_details)
            session.commit()

        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

        # Return the order directly; Pydantic converts it to JSON
        return order

@app.post("/orders/{order_id}/tags/{tag_id}")
def assign_tag_to_order(order_id: int, tag_id: int):
    with SessionLocal() as session:
        order = session.query(SaleOrder).filter_by(id=order_id).first()
        tag = session.query(Tag).filter_by(id=tag_id).first()

        if not order or not tag:
            raise HTTPException(404, "Order or Tag not found")

        if tag in order.tags:
            raise HTTPException(400, "Tag already assigned")

        order.tags.append(tag)
        session.commit()

    return {"message": "Tag assigned to order"}

@app.delete("/orders/{order_id}/tags/{tag_id}")
def remove_tag_from_order(order_id: int, tag_id: int):
    with SessionLocal() as session:
        order = session.query(SaleOrder).filter_by(id=order_id).first()
        tag = session.query(Tag).filter_by(id=tag_id).first()

        if not order or not tag:
            raise HTTPException(404, "Order or Tag not found")

        if tag not in order.tags:
            raise HTTPException(400, "Tag not assigned")

        order.tags.remove(tag)
        session.commit()

    return {"message": "Tag removed from order"}

