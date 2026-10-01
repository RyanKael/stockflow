from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user

from app.extensions import db
from app.forms.category_form import CategoryForm
from app.models.category import Category
from app.services.audit_service import register_audit


categories = Blueprint(
    "categories",
    __name__,
    url_prefix="/categories",
)

@categories.route("/")
def list_categories():

    categories_list = (
        Category.query.order_by(
            Category.name
        ).all()
    )

    return render_template(
        "categories/list.html",
        categories=categories_list,
    )


@categories.route("/new", methods=["GET", "POST"])
def new_category():

    form = CategoryForm()

    if form.validate_on_submit():

        name = form.name.data.strip()

        existing_category = Category.query.filter(
            db.func.lower(Category.name) == name.lower()
        ).first()

        if existing_category:

            flash(
                "Já existe uma categoria com esse nome.",
                "danger",
            )

            return render_template(
                "categories/form.html",
                form=form,
                title="Nova categoria",
            )

        category = Category(
            name=name,
            active=form.active.data,
        )

        db.session.add(category)

        db.session.flush()

        register_audit(
            user_id=current_user.id,
            action="CREATE",
            entity_type="Category",
            entity_id=category.id,
            description=f"Categoria cadastrada: {category.name}",
        )

        db.session.commit()

        flash(
            "Categoria cadastrada com sucesso.",
            "success",
        )

        return redirect(
            url_for("categories.list_categories")
        )

    return render_template(
        "categories/form.html",
        form=form,
        title="Nova categoria",
    )


@categories.route("/<int:id>/edit", methods=["GET", "POST"])
def edit_category(id):

    category = db.get_or_404(
        Category,
        id,
    )

    form = CategoryForm(
        obj=category,
    )

    if form.validate_on_submit():

        name = form.name.data.strip()

        existing_category = Category.query.filter(
            db.func.lower(Category.name) == name.lower(),
            Category.id != category.id,
        ).first()

        if existing_category:

            flash(
                "Já existe uma categoria com esse nome.",
                "danger",
            )

            return render_template(
                "categories/form.html",
                form=form,
                category=category,
                title="Editar categoria",
            )

        old_data = {
            "name": category.name,
            "active": category.active,
        }

        category.name = name
        category.active = form.active.data

        changes = []

        if old_data["name"] != category.name:

            changes.append(
                f"Nome: "
                f"{old_data['name']} → {category.name}"
            )

        if old_data["active"] != category.active:

            changes.append(
                f"Status: "
                f"{'Ativa' if old_data['active'] else 'Inativa'} → "
                f"{'Ativa' if category.active else 'Inativa'}"
            )

        if changes:

            register_audit(
                user_id=current_user.id,
                action="UPDATE",
                entity_type="Category",
                entity_id=category.id,
                description=(
                    f"Categoria atualizada: {category.name}. "
                    + " | ".join(changes)
                ),
            )

        if old_data["active"] != category.active:

            register_audit(
                user_id=current_user.id,
                action=(
                    "ACTIVATE"
                    if category.active
                    else "DEACTIVATE"
                ),
                entity_type="Category",
                entity_id=category.id,
                description=(
                    f"Categoria "
                    f"{'ativada' if category.active else 'desativada'}: "
                    f"{category.name}"
                ),
            )

        db.session.commit()

        flash(
            "Categoria atualizada com sucesso.",
            "success",
        )

        return redirect(
            url_for("categories.list_categories")
        )

    return render_template(
        "categories/form.html",
        form=form,
        category=category,
        title="Editar categoria",
    )