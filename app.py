from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///properties.db'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(os.getcwd(), 'static/uploads')

db = SQLAlchemy(app)
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Casa o Departamento
    rooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    square_meters = db.Column(db.Float, nullable=False)
    main_image = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)  # Nombre del agente o propietario
    additional_images = db.relationship('Image', backref='property', lazy=True)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(100), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)

# Crear las tablas si no existen
with app.app_context():
    db.create_all()

@app.route('/delete_property/<int:id>', methods=['POST'])
def delete_property(id):
    property_to_delete = Property.query.get_or_404(id)
    db.session.delete(property_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/')
def index():
    properties = Property.query.all()
    return render_template('index.html', properties=properties)

@app.route('/property/add', methods=['GET', 'POST'])
def add_property():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        typee = request.form['type']
        rooms = request.form['rooms']
        br = request.form['bathrooms']
        agent = request.form['owner_name']
        sm = request.form['square_meters']
        main_image = photos.save(request.files['main_image'])
        new_property = Property(title=title, description=description,rooms=rooms,bathrooms=br,owner_name=agent,square_meters=sm, price=price, type=typee, main_image=main_image)
        
        db.session.add(new_property)
        db.session.commit()
        
        if 'additional_images' in request.files:
            for image in request.files.getlist('additional_images'):
                if image.filename != '':
                    additional_image = photos.save(image)
                    property_image = Image(property_id=new_property.id, image_url=additional_image)
                    db.session.add(property_image)
        
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_property.html')

@app.route('/property/edit/<int:id>', methods=['GET', 'POST'])
def edit_property(id):
    property = Property.query.get_or_404(id)
    if request.method == 'POST':
        property.title = request.form['title']
        property.description = request.form['description']
        property.price = request.form['price']
        property.type = request.form['type']
        property.rooms = request.form['rooms']
        property.bathrooms = request.form['bathrooms']
        property.owner_name = request.form['owner_name']
        property.square_meters = request.form['square_meters']
        if 'main_image' in request.files and request.files['main_image'].filename != '':
            main_image = photos.save(request.files['main_image'])
            property.main_image = main_image
        
        if 'additional_images' in request.files:
            for image in request.files.getlist('additional_images'):
                if image.filename != '':
                    additional_image = photos.save(image)
                    property_image = Image(property_id=property.id, image_url=additional_image)
                    db.session.add(property_image)
        
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_property.html', property=property)

@app.route('/property/<int:id>')
def property_detail(id):
    property = Property.query.get_or_404(id)
    return render_template('property_detail.html', property=property)

if __name__ == '__main__':
    app.run(debug=True)
