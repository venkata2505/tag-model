from models import SessionLocal, Tag, Product, SaleOrder, SaleOrderDetail
from datetime import datetime

# TAG MODEL
def add_tag():
    print("\n Create New Tag ")
    value = input("Enter tag value: ")
    type_ = input("Enter tag type: ") 
    color = input("Enter tag color: ")
    description = input("Enter description: ")

    new_tag = Tag(value=value, type_=type_, color=color, description=description)

    with SessionLocal() as session:
        session.add(new_tag)
        session.commit()

    print("Tag added successfully \n")

def list_tags():
    try:
        page = int(input("Enter page number (default 1): ") or 1)
        page_size = int(input("Enter page size (default 20, -1 for all): ") or 20)
    except ValueError:
        print("Invalid input. Using defaults.")
        page, page_size = 1, 20

    with SessionLocal() as session:
        query = session.query(Tag)

        if page_size == -1:
            tags = query.all()
        else:
            offset = (page - 1) * page_size
            tags = query.offset(offset).limit(page_size).all()

        print("\n All Tags ")
        if not tags:
            print("No tags found \n")
            return

        for tag in tags:
            print(tag)
        print("")

def update_tag():
    session = SessionLocal()
    print("\n Update Tag ")
    tag_id = input("Enter tag ID to update: ")

    tag = session.query(Tag).filter_by(id=tag_id).first()
    if not tag:
        print("Tag not found \n")
        return

    print("Leave field empty to keep old value")

    new_value = input(f"New value ({tag.value}): ")
    new_type = input(f"New type ({tag.type_}): ")
    new_color = input(f"New color ({tag.color}): ")
    new_desc = input(f"New description ({tag.description}): ")

    if new_value: tag.value = new_value
    if new_type: tag.type_ = new_type
    if new_color: tag.color = new_color
    if new_desc: tag.description = new_desc

    session.commit()
    session.close()
    print("Tag updated successfully \n")

def delete_tag():
    tid = input("\nEnter Tag ID to delete: ")

    with SessionLocal() as session:
        tag = session.query(Tag).filter_by(id=tid).first()

        if not tag:
            print("Tag not found \n")
            return

        session.delete(tag)
        session.commit()
    print("Tag deleted successfully \n")

#PRODUCTS MODEL
def add_product():
    print("\n Create New Product")
    name = input("Enter the name: ")
    sku = input("Enter the sku: ")
    price = input("Enter the price: ")
    description = input("Enter the description: ")
    category = input("Enter the category: ")
    brand = input("Enter the brand: ")
    stock_qty = input("Enter the stock quantity: ")
    status = input("Enter the status: ")
    
    new_product = Product(name=name, sku=sku, price=price, 
                          description=description, category=category, 
                          brand=brand, stock_qty=stock_qty, status=status)
    with SessionLocal() as session:
        session.add(new_product)
        session.commit()
    print("Product added successfully \n")

def list_products():
    try:
        page = int(input("Enter page number (default 1): ") or 1)
        page_size = int(input("Enter page size (default 20, -1 for all): ") or 20)
    except ValueError:
        print("Invalid input. Using defaults.")
        page, page_size = 1, 20

    with SessionLocal() as session:
        query = session.query(Product)

        if page_size == -1:
            products = query.all()
        else:
            offset = (page - 1) * page_size
            products = query.offset(offset).limit(page_size).all()

        print("\n All Products ")
        if not products:
            print("No products found \n")
            return

        for product in products:
            tag_list = [tag.value for tag in product.tags] 
            print(f"ID: {product.id} | Name: {product.name} | SKU: {product.sku} | Price: {product.price} | Tags: {tag_list}")
            #print(product)
        print("")

def update_product():
    pid = input("\nEnter Product ID to update: ")
    with SessionLocal() as session:
        product = session.query(Product).filter_by(id=pid).first()
    if not product:
        print("Product not found \n")
        return

    print("Leave field empty to keep old value")
    name = input(f"New name ({product.name}): ")
    sku = input(f"New SKU ({product.sku}): ")
    price = input(f"New price ({product.price}): ")
    stock_qty = input(f"New stock ({product.stock_qty}): ")
    brand = input(f"New brand ({product.brand}): ")
    category = input(f"New category ({product.category}): ")

    if name: product.name = name
    if sku: product.sku = sku
    if price: product.price = float(price)
    if stock_qty: product.stock_qty = int(stock_qty)
    if brand: product.brand = brand
    if category: product.category = category

    session.commit()
    print("Product updated successfully \n")

def delete_product():
    pid = input("\nEnter Product ID to delete: ")

    with SessionLocal() as session:
        product = session.query(Product).filter_by(id=pid).first()

        if not product:
            print("Product not found \n")
            return

        session.delete(product)
        session.commit()
    print("Product deleted successfully \n")
# Assign and remove tags to product   
def assign_tag_to_product():
    with SessionLocal() as session:
        product_id = int(input("Enter Product ID: "))
        tag_id = int(input("Enter Tag ID: "))

        product = session.query(Product).filter_by(id=product_id).first()
        tag = session.query(Tag).filter_by(id=tag_id).first()

        if not product or not tag:
            print("Invalid Product ID or Tag ID\n")
            return

        if tag in product.tags:
            print("Tag already assigned \n")
            return

        product.tags.append(tag)
        session.commit()
        print("Tag assigned to product successfull \n")

def remove_tag_from_product():
    with SessionLocal() as session:
        product_id = int(input("Enter Product ID: "))
        tag_id = int(input("Enter Tag ID: "))

        product = session.query(Product).filter_by(id=product_id).first()
        tag = session.query(Tag).filter_by(id=tag_id).first()

        if not product or not tag:
            print("Invalid Product ID or Tag ID\n")
            return

        if tag not in product.tags:
            print("Tag not assigned to this product \n")
            return

        product.tags.remove(tag)
        session.commit()
        print("Tag removed from product successfully \n")

#SALE ORDERS MODEL
def create_sale_order():
    print("\nCreate New Sale Order")
    customer_name = input("Enter customer name: ")

    new_order = SaleOrder(
        customer_name=customer_name,
        total_amount=0,
        status="draft",
        created_at=datetime.utcnow()
    )

    with SessionLocal() as session:
        session.add(new_order)
        session.commit()
        order_id = new_order.id
        print(f"Sale Order created with ID {order_id}")

    add_items = input("Add items now? (y/n): ").lower()
    if add_items == "y":
        add_order_items(order_id)

def add_order_items(order_id):
    with SessionLocal() as session:
        order = session.query(SaleOrder).filter_by(id=order_id).first()
        if not order:
            print("Sale Order not found ")
            return

        while True:
            product_id = int(input("Enter Product ID: "))
            qty = int(input("Enter Quantity: ") or 1)

            product = session.query(Product).filter_by(id=product_id).first()
            if not product:
                print("Invalid Product ID ")
                continue

            if qty > product.stock_qty:
                print(f"Not enough stock. Available: {product.stock_qty}")
                continue

            subtotal = product.price * qty

            detail = SaleOrderDetail(
                sale_order_id=order.id,
                product_id=product.id,
                qty=qty,
                price=product.price,
                subtotal=subtotal
            )

            product.stock_qty -= qty
            session.add(detail)
            session.commit()
            print(f"Added {qty} x {product.name} to Sale Order {order.id}")

            more = input("Add another item? (y/n): ").lower()
            if more != "y":
                break
        total = session.query(SaleOrderDetail).filter_by(sale_order_id=order.id).all()
        order.total_amount = sum(d.subtotal for d in total)
        session.commit()
        print(f"Order total updated: {order.total_amount}\n")


def list_sale_orders():
    with SessionLocal() as session:
        orders = session.query(SaleOrder).all()
        if not orders:
            print("No sale orders found \n")
            return

        print("\nAll Sale Orders")
        for order in orders:
            tag_list = [tag.value for tag in order.tags]
            print(f"[ID {order.id}] Customer: {order.customer_name} | Status: {order.status} | Total: {order.total_amount} | Tags: {tag_list}")
        print("")

def order_details():
    order_id = int(input("\nEnter Sale Order ID: "))
    with SessionLocal() as session:
        order = session.query(SaleOrder).filter_by(id=order_id).first()
        if not order:
            print("Sale Order not found \n")
            return

        print(f"Order ID {order.id} | Customer: {order.customer_name} | Status: {order.status} | Total: {order.total_amount}")
        details = session.query(SaleOrderDetail).filter_by(sale_order_id=order.id).all()
        if not details:
            print("No items in this order.\n")
            return

        print("Order Items:")
        for d in details:
            product = session.query(Product).filter_by(id=d.product_id).first()
            print(f"- Product: {product.name if product else 'Deleted'} | Qty: {d.qty} | Unit Price: {d.price} | Subtotal: {d.subtotal}")
        print("")

def delete_sale_order():
    order_id = input("\nEnter Sale Order ID to delete: ")

    with SessionLocal() as session:
        order = session.query(SaleOrder).filter_by(id=order_id).first()

        if not order:
            print("Sale Order not found \n")
            return

        details = session.query(SaleOrderDetail).filter_by(sale_order_id=order.id).all()
        for d in details:
            session.delete(d)

        session.delete(order)
        session.commit()

    print(f"Sale Order ID {order_id} deleted successfully \n")
# Assign and remove tags to sale order
def assign_tag_to_sale_order():
    with SessionLocal() as session:
        order_id = int(input("Enter Sale Order ID: "))
        tag_id = int(input("Enter Tag ID: "))

        order = session.query(SaleOrder).filter_by(id=order_id).first()
        tag = session.query(Tag).filter_by(id=tag_id).first()

        if not order or not tag:
            print("Invalid Order ID or Tag ID\n")
            return

        if tag in order.tags:
            print("Tag already assigned \n")
            return

        order.tags.append(tag)
        session.commit()
        print("Tag assigned to sale order successfully \n")

def remove_tag_from_sale_order():
    with SessionLocal() as session:
        order_id = int(input("Enter Sale Order ID: "))
        tag_id = int(input("Enter Tag ID: "))

        order = session.query(SaleOrder).filter_by(id=order_id).first()
        tag = session.query(Tag).filter_by(id=tag_id).first()

        if not order or not tag:
            print("Invalid Order ID or Tag ID\n")
            return

        if tag not in order.tags:
            print("Tag not assigned to this order \n")
            return

        order.tags.remove(tag)
        session.commit()
        print("Tag removed from sale order successfully \n")

def tag_menu():
    while True:
        print("\nTag Menu: 1:add 2:list 3:update 4:delete 5:back")
        c = input("Choose: ").strip()
        if c == "1": add_tag()
        elif c == "2": list_tags()
        elif c == "3": update_tag()
        elif c == "4": delete_tag()
        elif c == "5": break
        else: print("Invalid")

def product_menu():
    while True:
        print("\nProduct Menu: 1:add 2:list 3:update 4:delete 5:back")
        c = input("Choose: ").strip()
        if c == "1": add_product()
        elif c == "2": list_products()
        elif c == "3": update_product()
        elif c == "4": delete_product()
        elif c == "5": break
        else: print("Invalid")

def order_menu():
    while True:
        print("\nSale Order Menu: 1:create 2:add items 3:list 4:details 5:delete 6:back")
        c = input("Choose: ").strip()
        if c == "1":
            create_sale_order()
        elif c == "2":
            order_id = int(input("Enter Sale Order ID to add items: "))
            add_order_items(order_id)
        elif c == "3":
            list_sale_orders()
        elif c == "4":
            order_details()
        elif c == "5":
            delete_sale_order()
        elif c == "6":
            break
        else:
            print("Invalid choice")

def tag_assign_menu():
    while True:
        print("\nTag Assign Menu: ")
        print("1: Assign tag to product")
        print("2: Remove tag from product")
        print("3: Assign tag to sale order")
        print("4: Remove tag from sale order")
        print("5: back")
        c = input("Choose: ").strip()
        if c == "1": assign_tag_to_product()
        elif c == "2": remove_tag_from_product()
        elif c == "3": assign_tag_to_sale_order()
        elif c == "4": remove_tag_from_sale_order()
        elif c == "5": break
        else: print("Invalid")

def main():
    while True:
        print("\nMain Menu: 1:Tags 2:Products 3:Orders 4:Tag Assign/Remove 5:Exit")
        c = input("Choose: ").strip()
        if c == "1": 
            tag_menu()
        elif c == "2": 
            product_menu()
        elif c == "3": 
            order_menu()
        elif c == "4":
            tag_assign_menu()
        elif c == "5": 
            print("exit ")
            break
        else: 
            print("Invalid")

if __name__ == "__main__":
    main()

