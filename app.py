from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from marshmallow import ValidationError



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:your_password@127.0.0.1/e_commerc_db'
db = SQLAlchemy(app)
ma = Marshmallow (app)

class CustomerSchema(ma.Schema):
    name = fields.String(required=True)
    phone = fields.String(required=True)
    email = fields.String(required=True)

    class Meta:
        fields = ("name", "phone", "email", "id")


class ProductSchema(ma.Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0))

    class Meta:
        fields = ("name", "price", "id")


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)



class CustomerAccount(db.Model):
    __tablename__ = 'Customer_Accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.string(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customer.id'))
    customer = db.relationship('Customer', backref='customer_account', uselist=False)


class Customer(db.Model):
    __tablename__ = 'Customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(15))
    email = db.Column(db.String(320))
    orders = db.relationship('Orders', backref='customer')


class Orders(db.Model):
    __tablename__ = 'Orders'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customer.id'))


order_product = db.Table('Orders_Products',
        db.Column('order_id', db.Integer, db.ForeignKey('Orders.id'), primary_key=True),
        db.Column('product_id', db.Integer, db.ForeignKey('Products.id'), primary=False)
)


class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    orders = db.relationship('Orders', secondary = order_product, backref = db.backref('products'))




# CRUD for customers

@app.route('/customer', methods=['GET'])
def get_customer():
    customers = Customer.quer.all()
    return customers_schema.jsonify(customers)


@app.route('/customer', methods=['GET'])
def get_customer_by_email():
    email = request.args.get('email')
    customer = Customer.query.filter_by(email=email).first()
    if customer:
        return customer_schema.jsonify(customer)
    else:
        return jsonify({"message": "Customer not found"}), 404


@app.route('/customer', methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.message), 400
    
    new_customer = Customer(name = customer_data['name'], phone = customer_data['phone'], email = customer_data['email'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "New customer added successfully"})


@app.route('/customer/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        customer_data = customer_schema.load(request.json)
    except ValueError as err:
        return jsonify(err.messages), 400
    
    customer.name = customer_data['name']
    customer.phone = customer_data['phone']
    customer.email = customer_data['email']
    db.session.commit()
    return jsonify({"message": "Customer details updated successfully"})


@app.route('/customer/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer removed successfully"})



# CRUD for customer accounts

@app.route('/customer_accounts')


# CRUD for Products

@app.route('/products', methods=['POST'])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_product = Product(name=product_data['name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Products added successfullt"}), 201


@app.route('/products/<int:id>', methods=['PUT'])
def update_products(id):
    product = Product.query.get_or_404(id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    product.name = product_data['name']
    product.price = product_data['price']
    db.session.commit()
    return jsonify({"message": "Product updated successfully"}), 200


@app.route('/products', methods=['GET'])
def get_product(id):
    products = Product.query.all()
    return products_schema.jsonify(products)


@app.route('/products', methods=['GET'])
def get_product_by_name():
    name = request.args.get('name')
    product = Product.query.filter(Product.name == name).first()
    if product:
        return product_schema.jsonify(product)
    else:
        return jsonify({"message": "Product not found"}), 404


@app.route('/products', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200


with app.app_context():
    db.create_all()

if __name__=='___main__':
    app.run(debug=True)