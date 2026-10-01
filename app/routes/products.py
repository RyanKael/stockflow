from flask_login import login_required, current_user
from flask import (
    Blueprint,
    flash,
    redirect,
    request,
    render_template,
    url_for,
    Response
)

from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.extensions import db
from app.forms.product_form import ProductForm
from app.models.product import Product
from app.models.stock_movement import StockMovement, MovementType
from app.utils.auth import role_required
from app.models.user import UserRole
from app.models.category import Category
from app.services.audit_service import register_audit


products = Blueprint(
    "products",
    __name__,
    url_prefix="/products",
)


@products.route("/")
@login_required
def list_products():


    #parâmetros da url
    search = request.args.get(
        "search",
        "",
    ).strip()

    stock_filter = request.args.get(
        "stock",
        "",
    ).strip()

    category = request.args.get(
        "category",
        type=int,
    )

    sort_key = request.args.get(
        "sort",
        "name",
    ).strip()

    direction = request.args.get(
        "direction",
        "asc",
    ).strip()

    #Consulta inicial
    query = Product.query

    #--------------------
    #Busca
    #-------------------

    if search:

        search_filter = f"%{search}%"

        query = query.filter(
            db.or_(
                Product.name.ilike(search_filter),
                Product.code.ilike(search_filter),
                Product.location.ilike(search_filter),
            )
        )

    #---------------------
    #Filtros de por categoria
    #--------------------

    if category is not None:
        query = query.filter(
            Product.category_id == category
        )

    #---------------------------
    #FILTRO DE ESTOQUE
    #--------------------------

    if stock_filter == "normal":

        query = query.filter(
            Product.active == True,
            Product.quantity > Product.minimum_stock
        )

    elif stock_filter == "low":

        query = query.filter(
            Product.active == True,
            Product.quantity > 0,
            Product.quantity <= Product.minimum_stock,
        )

    elif stock_filter == "out":

        query = query.filter(
            Product.active == True,
            Product.quantity == 0,
        )



    #--------------------
    # Ordenação
    #--------------------

    if db.engine.dialect.name == "sqlite":
        name_sort_column = Product.name.collate("PTBR")
    else:
        name_sort_column = Product.name

    sort_columns = {
        "name": name_sort_column,
        "code": Product.code,
        "quantity": Product.quantity,
        "minimum_stock": Product.minimum_stock,
    }

    # Evita valores inválidos pela URL

    if sort_key not in sort_columns:
        sort_key = "name"

    if direction not in ["asc", "desc"]:
        direction = "asc"


    sort_column = sort_columns[sort_key]

    if direction == "desc":
        order_by = sort_column.desc()
    else:
        order_by = sort_column.asc()


    query = query.order_by(order_by)

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    pagination = query.paginate(
        page=page,
        per_page=20,
        error_out=False,
    )

    #-------------------
    #Produtos filtrados
    #-------------------

    products_list = pagination.items

    # ---------------------------------
    # Todos os produtos
    # ---------------------------------

    all_products = Product.query.all()

    # ---------------------------------
    # Contadores gerais
    # ---------------------------------

    total_products = len(all_products)

    normal_stock = sum(
        1
        for product in all_products
        if product.active
        and product.quantity > product.minimum_stock
    )

    low_stock = sum(
        1
        for product in all_products
        if product.active
        and 0 < product.quantity <= product.minimum_stock
    )

    out_of_stock = sum(
        1
        for product in all_products
        if product.active
        and product.quantity == 0
    )

    categories = (
        Category.query.filter_by(active=True)
        .order_by(Category.name)
        .all()
    )


    return render_template(
        "products/list.html",
        products=products_list,
        pagination=pagination,
        total_products=total_products,
        normal_stock=normal_stock,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        stock_filter=stock_filter,
        search=search,
        sort=sort_key,
        direction=direction,
        categories=categories,
        selected_category=category,
    )

@products.route("/new", methods=["GET", "POST"])
@role_required(
    UserRole.ADMIN,
    UserRole.MANAGER,
)
def new_product():

    form = ProductForm()

    form.category_id.choices = [
        (0, "Sem categoria")
    ] + [
        (category.id, category.name)
        for category in Category.query.filter_by(active=True)
        .order_by(Category.name)
        .all()
    ]


    if form.validate_on_submit():

        category_id = (
            form.category_id.data
            if form.category_id.data != 0
            else None
        )
        product = Product(
            code=form.code.data,
            name=form.name.data,
            description=form.description.data,
            quantity=0,
            minimum_stock=form.minimum_stock.data,
            location=form.location.data,
            active=form.active.data,
            category_id=category_id,
        )

        db.session.add(product)

        db.session.flush()

        initial_quantity = form.quantity.data

        if initial_quantity > 0:

            movement = StockMovement(
                product_id=product.id,
                user_id=current_user.id,
                movement_type=MovementType.ENTRY,
                quantity=initial_quantity,
                previous_quantity=0,
                reason="Estoque inicial",
            )

            product.quantity = initial_quantity

            db.session.add(movement)

        register_audit(
            user_id=current_user.id,
            action="CREATE",
            entity_type="Product",
            entity_id=product.id,
            description=f"Produto cadastrado: {product.name}",
        )

        db.session.commit()


        flash (
            "Produto cadastrado com sucesso!",
            "success",
        )

        return redirect(
            url_for("products.list_products")
        )

    return render_template(
        "products/form.html",
        form=form,
        title="Novo Produto",
        button_text="Salvar Produto",
        is_edit=False,
    )

@products.route("/<int:id>/edit", methods=["GET", "POST"])
@role_required(
    UserRole.ADMIN,
    UserRole.MANAGER,
)
def edit_product(id):

    product = db.get_or_404(Product, id)

    next_url = request.values.get("next")

    form = ProductForm(obj=product)

    form.category_id.choices = [
        (0, "Sem categoria")
    ] + [
        (category.id, category.name)
        for category in Category.query.filter_by(active=True)
        .order_by(Category.name)
        .all()
    ]

    if request.method == "GET":
        form.category_id.data = product.category_id or 0

    if form.validate_on_submit():

        old_data = {
            "code": product.code,
            "name": product.name,
            "description": product.description,
            "minimum_stock": product.minimum_stock,
            "location": product.location,
            "active": product.active,
            "category_id": product.category_id,
        }

        product.category_id = (
            form.category_id.data
            if form.category_id.data != 0
            else None
        )

        product.code = form.code.data
        product.name = form.name.data
        product.description = form.description.data
        product.minimum_stock = form.minimum_stock.data
        product.location = form.location.data
        product.active = form.active.data


        changes = []


        if old_data["code"] != product.code:

            changes.append(
                f"Código: "
                f"{old_data['code']} → {product.code}"
            )


        if old_data["name"] != product.name:

            changes.append(
                f"Nome: "
                f"{old_data['name']} → {product.name}"
            )


        if old_data["description"] != product.description:

            changes.append(
                f"Descrição: "
                f"{old_data['description'] or '-'} → "
                f"{product.description or '-'}"
            )


        if old_data["minimum_stock"] != product.minimum_stock:

            changes.append(
                f"Estoque mínimo: "
                f"{old_data['minimum_stock']} → "
                f"{product.minimum_stock}"
            )


        if old_data["location"] != product.location:

            changes.append(
                f"Localização: "
                f"{old_data['location'] or '-'} → "
                f"{product.location or '-'}"
            )


        if old_data["active"] != product.active:

            changes.append(
                f"Status: "
                f"{'Ativo' if old_data['active'] else 'Inativo'} → "
                f"{'Ativo' if product.active else 'Inativo'}"
            )


        if old_data["category_id"] != product.category_id:

            old_category = (
                db.session.get(
                    Category,
                    old_data["category_id"],
                )
                if old_data["category_id"]
                else None
            )

            new_category = (
                db.session.get(
                    Category,
                    product.category_id,
                )
                if product.category_id
                else None
            )

            changes.append(
                f"Categoria: "
                f"{old_category.name if old_category else 'Sem categoria'} → "
                f"{new_category.name if new_category else 'Sem categoria'}"
            )


        if changes:

            register_audit(
                user_id=current_user.id,
                action="UPDATE",
                entity_type="Product",
                entity_id=product.id,
                description=(
                    f"Produto atualizado: {product.name}. "
                    + " | ".join(changes)
                ),
            )


        db.session.commit()

        flash(
            "Produto atualizado com sucesso!",
            "success",
        )

        return redirect(
            next_url or url_for("products.list_products")
        )

    return render_template(
        "products/form.html",
        form=form,
        title="Editar Produto",
        button_text="Atualizar Produto",
        is_edit=True,
        next_url=next_url,
    )

@products.route("/<int:id>/delete", methods=["POST"])
@role_required(UserRole.ADMIN)
def delete_product(id):

    product = Product.query.get_or_404(id)

    #------------------------
    #Verifica histórico de movimentações
    #-------------------------

    if product.movements:

        flash(
            "Este produto possui movimentações registradas"
            " e não pode ser excluído.",
            "danger",
        )

        return redirect(
            url_for("products.list_products")
        )

    #---------------------------
    #Exclusão
    #---------------------------

    product_id = product.id
    product_name = product.name

    register_audit(
        user_id=current_user.id,
        action="DELETE",
        entity_type="Product",
        entity_id=product.id,
        description=f"Produto excluído: {product_name}"
    )

    db.session.delete(product)
    db.session.commit()

    flash(
        "Produto excluído com sucesso!",
        "success",
    )

    return redirect(
        url_for("products.list_products")
    )

@products.route("/<int:id>/deactivate", methods=["POST"])
@role_required(
    UserRole.ADMIN,
    UserRole.MANAGER,
)
def deactivate_product(id):

    product = Product.query.get_or_404(id)

    if not product.active:

        flash(
            "Este produto já está desativado."
            "warning",
        )

        return redirect(
            url_for("products.list_products")
        )

    product.active = False

    register_audit(
        user_id=current_user.id,
        action="DEACTIVATE",
        entity_type="Product",
        entity_id=product.id,
        description=f"Product desativado: {product.name}",
    )

    db.session.commit()

    flash(
        f"Produto '{product.name}' desativado com sucesso.",
        "success",
    )

    return redirect(
        url_for("products.list_products")
    )

@products.route("/<int:id>/activate", methods=["POST"])
@role_required(
    UserRole.ADMIN,
    UserRole.MANAGER,
)
def activate_product(id):

    product = Product.query.get_or_404(id)

    if product.active:

        flash(
            "Este produto já está ativo."
            "warning",
        )

        return redirect(
            url_for("products.list_products")
        )

    product.active = True

    register_audit(
        user_id=current_user.id,
        action="ACTIVATE",
        entity_type="Product",
        entity_id=product.id,
        description=f"Produto ativado: {product.name}",
    )

    db.session.commit()

    flash(
        f"Produto '{product.name}' reativado com sucesso."
        " success",
    )

    return redirect(
        url_for("products.list_products")
    )

@products.route("/<int:id>/history")
@login_required
def product_history(id):

    product = db.get_or_404(
        Product,
        id,
    )

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    pagination = (
        StockMovement.query.filter_by(product_id=product.id)
        .order_by(StockMovement.created_at.desc())
        .paginate(
            page=page,
            per_page=20,
            error_out=False,
        )
    )

    movements = pagination.items


    total_entries = sum(
        movement.quantity
        for movement in StockMovement.query.filter_by(
            product_id=product.id,
            movement_type=MovementType.ENTRY,
        ).all()
    )

    total_exits = sum(
        movement.quantity
        for movement in StockMovement.query.filter_by(
            product_id=product.id,
            movement_type=MovementType.EXIT,
        ).all()
    )

    total_adjustments = (
        StockMovement.query.filter_by(
            product_id=product.id,
            movement_type=MovementType.ADJUSTMENT,
        )
        .count()
    )

    return render_template(
        "products/history.html",
        product=product,
        movements=movements,
        pagination=pagination,
        total_entries=total_entries,
        total_exits=total_exits,
        total_adjustments=total_adjustments,
    )

@products.route("/<int:id>/inventory", methods=["GET", "POST"])
@role_required(
    UserRole.ADMIN,
    UserRole.MANAGER,
)
def product_inventory(id):

    product = db.get_or_404(
        Product,
        id,
    )

    if request.method == "POST":

        physical_quantity_raw = request.form.get(
            "physical_quantity",
            "",
        ).strip()

        reason = request.form.get(
            "reason",
            "",
        ).strip()


        #Validação da quantidade


        try:
            physical_quantity = int(
                physical_quantity_raw
            )

        except ValueError:

            flash(
                "Informe uma quantidade válida.",
                "danger",
            )

        if physical_quantity < 0:

            flash(
                "A quantidade física não pode ser negativa.",
                "danger",
            )

            return render_template(
                "products/inventory.html",
                product=product,
            )

        #Nenhuma diferença encontrada

        if physical_quantity == product.quantity:

            flash(
                "O estoque físico está igual ao estoque do sistema. Nenhum ajuste foi necessário.",
                "success",
            )

            return redirect(
                url_for("products.product_inventory", id=product.id)
            )

        #Motivo obrigatório quiando houver diferença


        if not reason:

            flash(
                "Informe o motivo da diferença encontrada.",
                "danger",
            )

            return render_template(
                "products/inventory.html",
                product=product,
            )

        previous_quantity = product.quantity


        movement = StockMovement(
            product_id=product.id,
            user_id=current_user.id,
            movement_type=MovementType.ADJUSTMENT,
            quantity=physical_quantity,
            previous_quantity=previous_quantity,
            reason=f"Inventário físico: {reason}",
        )

        product.quantity = physical_quantity

        db.session.add(movement)

        db.session.flush()

        register_audit(
            user_id=current_user.id,
            action="INVENTORY",
            entity_type="StockMovement",
            entity_id=movement.id,
            description=(
                f"Inventário físico realizado para {product.name}. "
                f"Estoque anterior: {previous_quantity}. "
                f"Estoque físico: {physical_quantity}. "
                f"Motivo: {reason}."
            ),
        )

        db.session.commit()


        flash(
            "Invetário conferido e estoque ajustado com sucesso.",
            "success",
        )

        return redirect(
            url_for(
                "products.product_history",
                id=product.id,
            )
        )

    return render_template(
        "products/inventory.html",
        product=product,
    )

@products.route("/export/pdf")
@login_required
def export_pdf():

    search = request.args.get(
        "search",
        "",
    ).strip()


    stock_filter = request.args.get(
        "stock",
        "",
    ).strip()

    category_id = request.args.get(
        "category",
        type=int,
    )

    query = Product.query

    #====================
    #FILTROS DE BUSCA
    #====================

    if search:

        search_term = f"%{search}%"

        query = query.filter(
            db.or_(
                Product.code.ilike(search_term),
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Product.location.ilike(search_term),
            )
        )

    #===================
    #FILTROS DE CATEGORIA
    #===================


    if category_id is not None:

        query = query.filter(
            Product.category_id == category_id
        )

    #====================
    #FILTROS DE ESTOQUE
    #====================

    if stock_filter == "normal":

        query = query.filter(
            Product.active.is_(True),
            Product.quantity > Product.minimum_stock,
        )

    elif stock_filter == "low":

        query = query.filter(
            Product.active.is_(True),
            Product.quantity > 0,
            Product.quantity <= Product.minimum_stock,
        )

    elif stock_filter == "out":

        query = query.filter(
            Product.active.is_(True),
            Product.quantity == 0,
        )

    elif stock_filter == "inactive":

        query = query.filter(
            Product.active.is_(False)
        )

    products_list = query.all()

    #=======================
    #INFORMAÇÕES DOS FILTROS
    #=======================

    category_name = "Todas"

    if category_id is not None:

        selected_category = db.session.get(
            Category,
            category_id,
        )

        if selected_category:
            category_name = selected_category.name


    stock_labels = {
        "normal": "Estoque normal",
        "low": "Estoque baixo",
        "out": "Sem estoque",
        "inactive": "Inativos",
    }

    stock_label = stock_labels.get(
        stock_filter,
        "Todos"
    )

    search_label = search or "Todos"


    #===================
    #INDICADORES
    #===================

    total_products = len(products_list)

    total_quantity = sum(
        product.quantity
        for product in products_list
    )

    low_stock = sum(
        1
        for product in products_list
        if (
            product.active
            and product.quantity > 0
            and product.quantity <= product.minimum_stock
        )
    )

    out_of_stock = sum(
        1
        for product in products_list
        if (
            product.active and product.quantity == 0
        )
    )

    #======================
    #CRIAÇÃO DO PDF
    #======================

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()


    title_style = ParagraphStyle(
        "StockReportTitle",
        parent=styles["title"],
        alignment=TA_CENTER,
        fontSize=18,
        spaceAfter=5,
    )

    subtitle_style = ParagraphStyle(
            "StockReportSubtitle",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=11,
            spaceAfter=15,
    )


    cell_style = ParagraphStyle(
        "StockTableCell",
        parent=styles["Normal"],
        fontSize=7,
        leading=8,
        alignment=TA_CENTER,
    )

    header_style = ParagraphStyle(
        "StockTableHeader",
        parent=styles["Normal"],
        fontSize=7,
        leading=8,
        alignment=TA_CENTER,
        textColor=colors.white,
    )


    elements = []


    #=====================
    #CABEÇALHO
    #=====================

    elements.append(
        Paragraph(
            "STOCKFLOW",
            title_style,
        )
    )

    elements.append(
        Paragraph(
            "Relatório de Estoque",
            subtitle_style,
        )
    )

    elements.append(
        Paragraph(
            f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
            subtitle_style,
        )
    )

    elements.append(
        Spacer(
            1,
            5 * mm,
        )
    )

    # =====================================================
    # FILTROS APLICADOS
    # =====================================================

    filter_data = [
        [
            "Busca:",
            search_label,
        ],
        [
            "Categoria:",
            category_name,
        ],
        [
            "Situação:",
            stock_label,
        ],
    ]


    filter_table = Table(
        filter_data,
        colWidths=[
            30 * mm,
            145 * mm,
        ],
    )


    filter_table.setStyle(
        TableStyle([
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold",
            ),
            (
                "FONTNAME",
                (1, 0),
                (1, -1),
                "Helvetica",
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
        ])
    )


    elements.append(filter_table)

    elements.append(
        Spacer(
            1,
            8 * mm,
        )
    )


    # =====================================================
    # RESUMO
    # =====================================================

    summary_data = [
        [
            "Produtos",
            "Estoque total",
            "Estoque baixo",
            "Sem estoque",
        ],
        [
            str(total_products),
            str(total_quantity),
            str(low_stock),
            str(out_of_stock),
        ],
    ]


    summary_table = Table(
        summary_data,
        colWidths=[
            43 * mm,
            43 * mm,
            43 * mm,
            43 * mm,
        ],
    )


    summary_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#343a40"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER",
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey,
            ),
        ])
    )


    elements.append(summary_table)

    elements.append(
        Spacer(
            1,
            10 * mm,
        )
    )


    # =====================================================
    # TABELA DE PRODUTOS
    # =====================================================

    product_data = [
        [
            Paragraph("Código", header_style),
            Paragraph("Produto", header_style),
            Paragraph("Categoria", header_style),
            Paragraph("Quantidade", header_style),
            Paragraph("Estoque mínimo", header_style),
            Paragraph("Localização", header_style),
            Paragraph("Status", header_style),
        ]
    ]


    if products_list:

        for product in products_list:

            if not product.active:
                status = "Inativo"

            elif product.quantity == 0:
                status = "Sem estoque"

            elif product.quantity <= product.minimum_stock:
                status = "Estoque baixo"

            else:
                status = "Normal"


            product_data.append([
                Paragraph(
                    product.code or "-",
                    cell_style,
                ),
                Paragraph(
                    product.name,
                    cell_style,
                ),
                Paragraph(
                    (
                        product.category.name
                        if product.category
                        else "Sem categoria"
                    ),
                    cell_style,
                ),
                Paragraph(
                    str(product.quantity),
                    cell_style,
                ),
                Paragraph(
                    str(product.minimum_stock),
                    cell_style,
                ),
                Paragraph(
                    product.location or "-",
                    cell_style,
                ),
                Paragraph(
                    status,
                    cell_style,
                ),
            ])

    else:

        product_data.append([
            Paragraph(
                "Nenhum produto encontrado para os filtros selecionados.",
                cell_style,
            ),
            "",
            "",
            "",
            "",
            "",
            "",
        ])


    product_table = Table(
        product_data,
        colWidths=[
            25 * mm,
            55 * mm,
            42 * mm,
            27 * mm,
            30 * mm,
            45 * mm,
            32 * mm,
        ],
        repeatRows=1,
    )


    product_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#343a40"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7,
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER",
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
        ])
    )


    if not products_list:

        product_table.setStyle(
            TableStyle([
                (
                    "SPAN",
                    (0, 1),
                    (-1, 1),
                ),
                (
                    "ALIGN",
                    (0, 1),
                    (-1, 1),
                    "CENTER",
                ),
            ])
        )


    elements.append(product_table)


    # =====================================================
    # RODAPÉ E PAGINAÇÃO
    # =====================================================

    def add_page_number(canvas, doc):

        canvas.saveState()

        canvas.setFont(
            "Helvetica",
            8,
        )

        canvas.setFillColor(
            colors.grey
        )

        canvas.drawString(
            15 * mm,
            8 * mm,
            "Gerado pelo StockFlow",
        )

        canvas.drawCentredString(
            landscape(A4)[0] / 2,
            8 * mm,
            datetime.now().strftime(
                "%d/%m/%Y às %H:%M"
            ),
        )

        canvas.drawRightString(
            landscape(A4)[0] - 15 * mm,
            8 * mm,
            f"Página {doc.page}",
        )

        canvas.restoreState()


    doc.build(
        elements,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )


    buffer.seek(0)


    response = Response(
        buffer.getvalue(),
        mimetype="application/pdf",
    )


    response.headers["Content-Disposition"] = (
        "attachment;"
        "filename=relatorio_estoque.pdf"
    )


    return response
