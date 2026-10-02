from flask_login import login_required, current_user
from app.utils.auth import role_required
from app.models.user import UserRole

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app


from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.product import Product
from app.models.stock_movement import StockMovement, MovementType
from app.services.audit_service import register_audit




movements = Blueprint(
    "movements",
     __name__,
     url_prefix="/movements",
     )



@movements.route("/")
@login_required
def list_movements():


    sort_key = request.args.get(
        "sort",
        "date",
    ).strip()

    direction = request.args.get(
        "direction",
        "desc",
    ).strip()

    sort_columns = {
        "date": StockMovement.created_at,
        "quantity": StockMovement.quantity,
        "type": StockMovement.movement_type,
    }

    if sort_key not in sort_columns:
        sort_key = "date"

    if direction not in ["asc", "desc"]:
        direction = "desc"


    sort_column = sort_columns[sort_key]

    if direction == "desc":
        order_by = sort_column.desc()
    else:
        order_by = sort_column.asc()


    page = request.args.get(
        "page",
        1,
        type=int,
    )

    pagination = StockMovement.query.order_by(
        order_by
    ).paginate(
        page=page,
        per_page=20,
        error_out=False,
    )

    movements_list = pagination.items

    return render_template(
        "movements/list.html",
        movements=movements_list,
        pagination=pagination,
        sort=sort_key,
        direction=direction,
    )

@movements.route("/<int:id>")
@login_required
def movement_detail(id):

    movement = db.get_or_404(
        StockMovement,
        id,
    )

    next_url = request.args.get("next")

    return render_template(
        "movements/detail.html",
        movement=movement,
        next_url=next_url,
    )

@movements.route("/new", methods=["GET", "POST"])
@login_required
def new_movement():

    products = Product.query.filter_by(active=True).order_by(
        Product.name
    ).all()

    next_url = request.values.get("next")

    if request.method == "POST":

        product_id = request.form.get("product_id", "")
        movement_type_value = request.form.get("movement_type", "")
        quantity_value = request.form.get("quantity", "")
        reason_value = request.form.get("reason", "")



        #--------------------
        #Validação do produto
        #--------------------

        try:
            product_id = int(request.form.get("product_id", ""))
        except (TypeError, ValueError):

            flash(
                "Selecione um produto válido.",
                "danger",
            )

            return render_template(
                "movements/new.html",
                products=products,
                selected_product_id=product_id,
                selected_movement_type=movement_type_value,
                quantity_value=quantity_value,
                reason_value=reason_value,
                next_url=next_url,
            )


        product = Product.query.filter_by(
            id=product_id,
            active=True,
        ).first()

        if product is None:

            flash(
                "O produto selecionado não foi encontrado ou está inativo.",
                "danger"
            )

            return render_template(
                "movements/new.html",
                products=products,
                selected_product_id=product_id,
                selected_movement_type=movement_type_value,
                quantity_value=quantity_value,
                reason_value=reason_value,
                next_url=next_url,
            )

        #---------------------------------
        #Validação do tipo de movimentação
        #---------------------------------

        movement_type_value = request.form.get(
            "movement_type",
            ""
        ).strip()

        try:

            movement_type = MovementType(
                movement_type_value
            )

        except ValueError:

            flash(
                "Selecione um tipo de movimentação válido.",
                "danger",
            )

            return render_template(
                "movements/new.html",
                products=products,
                selected_product_id=product_id,
                selected_movement_type=movement_type_value,
                quantity_value=quantity_value,
                reason_value=reason_value,
                next_url=next_url,
            )

        # 🔐Permissão de ajuste

        if (
            movement_type == MovementType.ADJUSTMENT
            and current_user.role == UserRole.USER
        ):
            flash(
                "Você não possui permissões para realizar ajustes de estoque.",
                " danger",
            )

            return render_template(
                "movements/new.html",
                products=products,
                selected_product_id=product_id,
                selected_movement_type=movement_type_value,
                quantity_value=quantity_value,
                reason_value=reason_value,
                next_url=next_url,
            )

        #-------------------------
        #Validação de quantidade
        #-------------------------

        quantity_value = request.form.get(
            "quantity",
            "",
        ).strip()

        if not quantity_value:

            flash(
                "Informe a quantidade da movimentação.",
                "danger",
            )

            return render_template(
                "movements/new.html",
                products=products,
                selected_product_id=product_id,
                selected_movement_type=movement_type_value,
                quantity_value=quantity_value,
                reason_value=reason_value,
                next_url=next_url,
            )

        try:

            quantity = int(quantity_value)

        except (TypeError, ValueError):

            flash(
                "A quantidade deve ser um número inteiro válido.",
                "danger",
            )

            return render_template(
                "movements/new.html",
                products=products,
                selected_product_id=product_id,
                selected_movement_type=movement_type_value,
                quantity_value=quantity_value,
                reason_value=reason_value,
                next_url=next_url,
            )

        # Nenhuma movimentação pode ter valor negativo

        if quantity < 0:

            flash(
                "A quantidade não pode ser negativa.",
                "danger",
            )

            return render_template(
                "movements/new.html",
                products=products,
                selected_product_id=product_id,
                selected_movement_type=movement_type_value,
                quantity_value=quantity_value,
                reason_value=reason_value,
                next_url=next_url,
            )

        # Entrada e saída precisam ser maiores que zero

        if movement_type in(
            MovementType.ENTRY,
            MovementType.EXIT,
        ) and quantity == 0:

            flash(
                "Para entrada ou saída, a quantidade deve ser maior do que zero.",
                "danger",
            )

            return render_template(
                "movements/new.html",
                products=products,
                selected_product_id=product_id,
                selected_movement_type=movement_type_value,
                quantity_value=quantity_value,
                reason_value=reason_value,
                next_url=next_url,
            )

        #------------------------
        #Validação de saída
        #------------------------

        if movement_type == MovementType.EXIT:

            if quantity > int(product.quantity):

                return render_template(
                    "movements/new.html",
                    products=products,
                    error=True,
                    available_quantity=product.quantity,
                    selected_product_id=product_id,
                    selected_movement_type=movement_type_value,
                    quantity_value=quantity_value,
                    reason_value=reason_value,
                    next_url=next_url,
                )

        #------------------------
        #Motivo
        #-----------------------

        reason = request.form.get(
            "reason",
            "",
        ).strip()

        if len (reason) > 250:

            flash(
                "O motivo não pode ultrapassar o limite de 250 caracteres.",
                "danger",
            )

            return render_template(
                "movements/new.html",
                products=products,
                selected_product_id=product_id,
                selected_movement_type=movement_type_value,
                quantity_value=quantity_value,
                reason_value=reason_value,
                next_url=next_url,
            )


        #------------------------------
        # Atualização de estoque
        #------------------------------

        previous_quantity = int(product.quantity)

        if movement_type == MovementType.ENTRY:

            product.quantity = (
                int(product.quantity) + quantity
            )

        elif movement_type == MovementType.EXIT:

            product.quantity = (
                int(product.quantity) - quantity
            )

        elif movement_type == MovementType.ADJUSTMENT:

            product.quantity = quantity

        #--------------------------
        # Criação de movimentação
        #--------------------------

        movement = StockMovement(
            product_id=product_id,
            movement_type=movement_type,
            quantity=quantity,
            previous_quantity=previous_quantity,
            reason=reason or None,
            user_id=current_user.id,
        )
        #---------------------------
        # Transação
        #---------------------------

        try:

            db.session.add(movement)

            db.session.flush()

            register_audit(
                user_id=current_user.id,
                action="CREATE",
                entity_type="StockMovement",
                entity_id=movement.id,
                description=(
                    f"{movement.movement_type.value} registrada para "
                    f"{product.name}. "
                    f"Quantidade: {movement.quantity}. "
                    f"Estoque anterior: {previous_quantity}. "
                    f"Estoque atual: {product.quantity}."
                ),
            )

            db.session.commit()

        except SQLAlchemyError:

            db.session.rollback()

            current_app.logger.exception(
                "Erro ao registrar movimentação."
            )

            flash(
                "Não foi possível registrar a movimentação.\n"
                "Nenhuma alteração foi realizada.",
                "danger",
            )

            return render_template(
                "movements/new.html",
                products=products,
                selected_product_id=product_id,
                selected_movement_type=movement_type_value,
                quantity_value=quantity_value,
                reason_value=reason_value,
                next_url=next_url,
            )

        #-------------------------
        # Mensagem de sucesso
        #-------------------------

        if movement_type == MovementType.ENTRY:

            flash(
                f"Entrada realizada com sucesso!\n"
                f"Produto: {product.name}\n"
                f"Quantidade adicionada: {quantity} unidades.",
                "movement-entry",
            )


        elif movement_type == MovementType.EXIT:

            flash(
                f"Saída realizada com sucesso!\n"
                f"Produto: {product.name}.\n"
                f"Quantidade retirada: {quantity} unidades.",
                "movement-exit",
            )

        elif movement_type == MovementType.ADJUSTMENT:

            flash(
                f"Ajuste realizado com sucesso!\n"
                f"Produto: {product.name}.\n"
                f"Estoque anterior: {previous_quantity} unidades.\n"
                f"Novo estoque: {quantity} unidades.",
                "movement-adjustment",
            )

        return redirect(
            next_url or url_for("movements.list_movements")
        )

    selected_product_id = request.args.get(
        "product_id",
        "",
    ).strip()

    selected_movement_type = request.args.get(
        "movement_type",
        "",
    ).strip()

    quantity_value = request.args.get(
        "quantity",
        "",
    )

    return render_template(
        "movements/new.html",
        products=products,
        selected_product_id=selected_product_id,
        selected_movement_type=selected_movement_type,
        quantity_value=quantity_value,
        reason_value="",
        next_url=next_url,
    )


@movements.route("/<int:id>/reverse", methods=["POST"])
@role_required(
    UserRole.ADMIN,
    UserRole.MANAGER,
)
def reverse_movement(id):

    #---------------------
    #Busca a movimentação original
    #----------------------

    movement = db.get_or_404(
        StockMovement,
        id,
    )

    #----------------------------
    #Impede estornar um estorno
    #----------------------------

    if movement.reversed_movement_id is not None:

        flash(
            "Está movimentação é um estorno e não pode ser estornada novamente.",
            "danger",
        )

        return redirect(
            url_for("movements.list_movements"),
        )

    #-------------------------
    #Verifica se já foi estornada
    #-------------------------

    existing_reverse = StockMovement.query.filter_by(
        reversed_movement_id=movement.id,
    ).first()

    if existing_reverse:

        flash(
            "Esta movimentação já foi estornada.",
            "danger",
        )

        return redirect(
            url_for("movements.list_movements"),
        )

    product = movement.product

    previous_quantity = int(product.quantity)

    #-----------------------------------
    #Define o tipo de estorno
    #----------------------------------

    if movement.movement_type == MovementType.ENTRY:

        reverse_type = MovementType.EXIT

        #Não pode gerar estoque negativo
        if movement.quantity > product.quantity:

            flash(
                "Não é possível estornar essa entrada porque"
                "a quantidade atual do estoque é insuficiente.",
                "danger",
            )

            return redirect(
                url_for("movements.list_movements")
            )

        product.quantity -= movement.quantity

    elif movement.movement_type == MovementType.EXIT:

        reverse_type = MovementType.ENTRY

        product.quantity += movement.quantity

    elif movement.movement_type == MovementType.ADJUSTMENT:

        reverse_type = MovementType.ADJUSTMENT

        if movement.previous_quantity is None:

            flash(
                "Não é possível estornar este ajuste porque"
                " o estoque anterior não foi registrado.",
                "danger",
            )

            return redirect(
                url_for("movements.list_movements")
            )

        # Restaura o estoque anterior ao ajuste

        product.quantity = int(movement.previous_quantity)


    else:

        flash(
            "O tipo de movimentação é inválido para estorno.",
            "danger",
        )

        return redirect(
            url_for("movements.list_movements")
        )

    #-----------------------------------
    #Cria a movimentação de estorno
    #-----------------------------------

    if movement.movement_type == MovementType.ADJUSTMENT:

        reverse_movement = StockMovement(
            product_id=product.id,
            movement_type=MovementType.ADJUSTMENT,
            quantity=movement.previous_quantity,
            previous_quantity=previous_quantity,
            reversed_movement_id=movement.id,
            reason=f"Estorno do ajuste de movimentação #{movement.id}",
            user_id=current_user.id,
        )

    else:

        reverse_movement = StockMovement(
            product_id=product.id,
            movement_type=reverse_type,
            quantity=movement.quantity,
            previous_quantity=previous_quantity,
            reversed_movement_id=movement.id,
            reason=f"Estorno da movimentação #{movement.id}",
            user_id=current_user.id,
        )

    #--------------------------------
    #Transação
    #--------------------------------

    try:

        db.session.add(reverse_movement)

        db.session.flush()

        register_audit(
            user_id=current_user.id,
            action="REVERSE",
            entity_type="StockMovement",
            entity_id=reverse_movement.id,
            description=(
                f"Movimentação #{movement.id} estornada. "
                f"Produto: {product.name}. "
                f"Tipo original: {movement.movement_type.value}. "
                f"Estoque anterior ao estorno: {previous_quantity}. "
                f"Estoque atual: {product.quantity}."
            )
        )

        db.session.commit()

    except SQLAlchemyError:

        db.session.rollback()

        flash(
            "Não foi possível realizar o estorno."
            "Nenhuma alteração foi realizada.",
            "danger",
        )

        return redirect(
            url_for("movements.list_movements")
        )

    flash(
        f"Movimentação #{movement.id} estornada com sucesso.",
        "success",
    )

    return redirect(
        url_for("movements.list_movements")
    )