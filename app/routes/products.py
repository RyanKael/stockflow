from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
)

from app.extensions import db
from app.forms.product_form import ProductForm
from app.models.product import Product


products = Blueprint(
    "products",
    __name__,
    url_prefix="/products",
)


@products.route("/")
def list_products():

    products_list = Product.query.order_by(Product.name).all()

    return render_template(
        "products/list.html",
        products = products_list,
    ) 

@products.route("/new", methods=["GET", "POST"])
def new_product():

    form = ProductForm()

    if form.validate_on_submit():

        product = Product(
            code=form.code.data,
            name=form.name.data,
            description=form.description.data,
            quantity=form.quantity.data,
            minimum_stock=form.minimum_stock.data,
            location=form.location.data,
            active=form.active.data,
        )

        db.session.add(product)
        db.session.commit()


        flash (
            "Produto cadastrado com sucesso!",
            "Success",
        )

        return redirect(
            url_for("products.list_products")
        )

    return render_template(
        "products/form.html",
        form=form,
        title="Novo Produto",
        button_text="Salvar Produto",
    )

@products.route("/<int:id>/edit", methods=["GET", "POST"])
def edit_product(id):

    product = db.get_or_404(Product, id)

    form = ProductForm(obj=product)

    if form.validate_on_submit():

        product.code = form.code.data
        product.name = form.name.data
        product.description = form.description.data
        product.quantity = form.quantity.data
        product.minimum_stock = form.minimum_stock.data
        product.location = form.location.data
        product.active = form.active.data

        db.session.commit()

        flash(
            "Produto atualizado com sucesso!",
            "sucess",
        )

        return redirect(
            url_for("products.list_products")
        )

    return render_template(
        "products/form.html",
        form=form,
        title="Editar Produto",
        button_text="Atualizar Produto",
    )