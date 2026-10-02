from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo
from io import StringIO, BytesIO
import csv

from flask import Blueprint, render_template, request, Response
from flask_login import login_required

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import(
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.models.product import Product
from app.models.stock_movement import StockMovement, MovementType


reports = Blueprint(
    "reports",
    __name__,
    url_prefix="/reports",
)

@reports.route("/")
@login_required
def index():

    movement_type_filter = request.args.get(
        "movement_type",
        ""
    ).strip()

    product_id_filter = request.args.get(
        "product_id",
        ""
    ).strip()

    start_date_filter = request.args.get(
        "start_date",
        ""
    ).strip()

    end_date_filter = request.args.get(
        "end_date",
        ""
    ).strip()

    query = StockMovement.query

    if movement_type_filter:
        try:
            movement_type = MovementType(
                movement_type_filter
            )

            query = query.filter(
                StockMovement.movement_type == movement_type
            )

        except ValueError:
            movement_type_filter = ""


    if product_id_filter:
        try:
            product_id = int(product_id_filter)

            query = query.filter(
                StockMovement.product_id == product_id
            )

        except ValueError:
            product_id_filter = ""



    local_tz = ZoneInfo("America/Sao_Paulo")


    # Filtro por data inicial

    if start_date_filter:
        try:
            start_date = datetime.strptime(
                start_date_filter,
                "%Y-%m-%d"
            ).date()

            start_local = datetime.combine(
                start_date,
                time.min,
                tzinfo=local_tz,
            )

            start_utc = start_local.astimezone(
                timezone.utc
            ).replace(tzinfo=None)

            query = query.filter(
                StockMovement.created_at >= start_utc
            )

        except ValueError:
            start_date_filter = ""


    # Filtro por data final

    if end_date_filter:
        try:
            end_date = datetime.strptime(
                end_date_filter,
                "%Y-%m-%d"
            ).date()

            end_local = datetime.combine(
                end_date,
                time.max,
                tzinfo=local_tz,
            )

            end_utc = end_local.astimezone(
                timezone.utc
            ).replace(tzinfo=None)

            query = query.filter(
                StockMovement.created_at <= end_utc
            )

        except ValueError:
            end_date_filter = ""

    #------------------
    # Ordenação
    #------------------

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
        "product": Product.name,
    }


    if sort_key not in sort_columns:
        sort_key = "date"

    if direction not in ["asc", "desc"]:
        direction = "desc"


    #-------------------------
    # Produto pertence a outra tabela
    #-------------------------

    if sort_key == "product":
        query = query.join(
            Product,
            StockMovement.product_id == Product.id
        )


    sort_column = sort_columns[sort_key]


    if direction == "desc":
        order_by = sort_column.desc()
    else:
        order_by = sort_column.asc()

    #----------------------------
    #Resumo dos registros filtrados
    #----------------------------

    filtered_movements = query.order_by(
        order_by
    ).all()

    total_movements = len(filtered_movements)

    total_entries = sum(
        movement.quantity
        for movement in filtered_movements
        if movement.movement_type == MovementType.ENTRY
    )

    total_exits = sum(
        movement.quantity
        for movement in filtered_movements
        if movement.movement_type == MovementType.EXIT
    )

    total_adjustments = sum(
        1
        for movement in filtered_movements
        if movement.movement_type == MovementType.ADJUSTMENT
    )

    #--------------------------------
    # Paginação da tabela
    #-------------------------------

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    pagination = query.order_by(
        order_by
    ).paginate(
        page=page,
        per_page=20,
        error_out=False,
    )

    movements = pagination.items


    products = Product.query.filter_by(
        active=True
    ).order_by(
        Product.name
    ).all()

    return render_template(
        "reports/index.html",
        movements=movements,
        pagination=pagination,
        total_movements=total_movements,
        total_entries=total_entries,
        total_exits=total_exits,
        total_adjustments=total_adjustments,
        movement_type_filter=movement_type_filter,
        products=products,
        product_id_filter=product_id_filter,
        start_date_filter=start_date_filter,
        end_date_filter=end_date_filter,
        sort=sort_key,
        direction=direction,
    )

@reports.route("/export/csv")
@login_required
def export_csv():

        movement_type_filter = request.args.get(
            "movement_type",
            ""
        ).strip()


        product_id_filter = request.args.get(
            "product_id",
            ""
        ).strip()


        start_date_filter = request.args.get(
            "start_date",
            ""
        ).strip()


        end_date_filter = request.args.get(
            "end_date",
            ""
        ).strip()


        query = StockMovement.query

    #Filtro por tipo

        if movement_type_filter:
            try:
                movement_type = MovementType(movement_type_filter)

                query = query.filter(
                    StockMovement.movement_type == movement_type
                )

            except ValueError:
                pass

        #Filtro por produto

        if product_id_filter:
            try:
                product_id = int(product_id_filter)

                query = query.filter(
                    StockMovement.product_id == product_id
                )

            except ValueError:
                pass

        #Filtro por data inicial

        if start_date_filter:
            try:
                start_date = datetime.strptime(
                    start_date_filter,
                    "%Y-%m-%d"
                ).date()

                query = query.filter(
                    StockMovement.created_at >= datetime.combine(
                        start_date,
                        time.min
                    )
                )

            except ValueError:
                pass


        #Filtro por data final

        if end_date_filter:
            try:
                end_date = datetime.strptime(
                    end_date_filter,
                    "%Y-%m-%d"
                ).date()

                query = query.filter(
                    StockMovement.created_at <= datetime.combine(
                        end_date,
                        time.max
                    )
                )

            except ValueError:
                pass


        movements = query.order_by(
            StockMovement.created_at.desc()
        ).all()

        #Criar CSV

        output = StringIO()

        writer = csv.writer(output)

        writer.writerow([
            "ID",
            "Produto",
            "Tipo",
            "Quantidade",
            "Usuário",
            "Data",
        ])

        for movement in movements:

            writer.writerow([
                movement.id,
                movement.product.name,
                movement.movement_type.value,
                movement.quantity,
                movement.user.username
                if movement.user
                else "-",
                movement.created_at.strftime(
                    "%d/%m/%Y %H:%M"
                ),
            ])

        response = Response(
            output.getvalue(),
            mimetype="text/csv; charset=utf-8",
        )

        response.headers["Content-Disposition"] = (
            "attachment; filename=relatorio_movimentacoes.csv"
        )

        return response

@reports.route("/export/pdf")
@login_required
def export_pdf():

        movement_type_filter = request.args.get(
            "movement_type",
            ""
        ).strip()


        product_id_filter = request.args.get(
            "product_id",
            ""
        ).strip()


        start_date_filter = request.args.get(
            "start_date",
            ""
        ).strip()


        end_date_filter = request.args.get(
            "end_date",
            ""
        ).strip()


        query = StockMovement.query

    #Filtro por tipo

        if movement_type_filter:
            try:
                movement_type = MovementType(movement_type_filter)

                query = query.filter(
                    StockMovement.movement_type == movement_type
                )

            except ValueError:
                pass

        #Filtro por produto

        if product_id_filter:
            try:
                product_id = int(product_id_filter)

                query = query.filter(
                    StockMovement.product_id == product_id
                )

            except ValueError:
                pass

        local_tz = ZoneInfo("America/Sao_Paulo")
        #Filtro por data inicial

        if start_date_filter:
            try:
                start_date = datetime.strptime(
                    start_date_filter,
                    "%Y-%m-%d"
                ).date()

                start_local = datetime.combine(
                    start_date,
                    time.min,
                    tzinfo=local_tz,
                )

                start_utc = start_local.astimezone(
                    timezone.utc
                ).replace(tzinfo=None)

                query = query.filter(
                    StockMovement.created_at >= start_utc
                )

            except ValueError:
                pass


        # Filtro por data final

        if end_date_filter:
            try:
                end_date = datetime.strptime(
                    end_date_filter,
                    "%Y-%m-%d"
                ).date()

                end_local = datetime.combine(
                    end_date,
                    time.max,
                    tzinfo=local_tz,
                )

                end_utc = end_local.astimezone(
                    timezone.utc
                ).replace(tzinfo=None)

                query = query.filter(
                    StockMovement.created_at <= end_utc
                )

            except ValueError:
                pass


        movements = query.order_by(
            StockMovement.created_at.desc()
        ).all()

      #---------------------
      #INDICADORES
      #---------------------

        total_movements = len(movements)

        total_entries = sum(
            movement.quantity
            for movement in movements
            if movement.movement_type == MovementType.ENTRY
        )

        total_exits = sum(
            movement.quantity
            for movement in movements
            if movement.movement_type == MovementType.EXIT
        )

        total_adjustment = sum(
            1
            for movement in movements
            if movement.movement_type == MovementType.ADJUSTMENT
        )

        #------------------------
        #Criação do PDF
        #------------------------

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
            "ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=18,
            spaceAfter=5,
        )

        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=11,
            spaceAfter=15,
        )

        elements = []

        elements.append(
            Paragraph(
                "STOCKFLOW",
                title_style,
            )
        )

        elements.append(
            Paragraph(
                "Relatório de Movimentações",
                subtitle_style,
            )
        )

        elements.append(
            Paragraph(
                f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
                subtitle_style,
            )
        )

        elements.append(Spacer(1, 5 * mm))

        periodo = "Todos os períodos"

        if start_date_filter and end_date_filter:
            periodo = (
                f"{start_date_filter} até {end_date_filter}"
            )

        elif start_date_filter:
            periodo = f"A partir de {start_date_filter}"

        elif end_date_filter:
            periodo = f"Até {end_date_filter}"

        tipo = movement_type_filter or "Todos"

        produto = "Todos"

        if product_id_filter:
            try:
                selected_product = Product.query.get(
                    int(product_id_filter)
                )

                if selected_product:
                    produto = selected_product.name

            except ValueError:
                pass


        filter_data = [
            ["Período:", periodo],
            ["Produto:", produto],
            ["Tipo", tipo],
        ]

        filter_table = Table(
            filter_data,
            colWidths=[30 * mm, 145 * mm],
        )

        filter_table.setStyle(
            TableStyle([
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ])
        )

        elements.append(filter_table)

        elements.append(Spacer(1, 8 * mm))


        summary_data = [
            ["Movimentações", "Entradas", "Saídas", "Ajustes"],
            [
                str(total_movements),
                str(total_entries),
                str(total_exits),
                str(total_adjustment),
            ]
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
                    colors.HexColor("#343a40",)
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

        elements.append(Spacer(1, 10 * mm))

        movement_data = [
            [
                "ID",
                "Data",
                "Produto",
                "Tipo",
                "Alteração",
                "Estoque",
                "Responsável",
                "Status",
            ]
        ]

        #Estilo para as cédulas da tabela
        cell_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontSize=7,
            leading=8,
            alignment=TA_CENTER,
        )

        header_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontSize=7,
            leading=8,
            alignment=TA_CENTER,
            textColor=colors.white,
        )

        #Cabeçalho usando Paragraph

        movement_data[0] = [
            Paragraph("ID", header_style),
            Paragraph("Data", header_style),
            Paragraph("Produto", header_style),
            Paragraph("Tipo", header_style),
            Paragraph("Alteração", header_style),
            Paragraph("Estoque", header_style),
            Paragraph("Responsável", header_style),
            Paragraph("Status", header_style),
        ]

        if movements:
            for movement in movements:


                if movement.previous_quantity is not None:

                    if movement.movement_type == MovementType.ENTRY:
                        alteration = f"+ {movement.quantity}"
                        stock = (
                        f"{movement.previous_quantity} → "
                        f"{movement.previous_quantity + movement.quantity}"
                    )

                    elif movement.movement_type == MovementType.EXIT:
                        alteration = f"-{movement.quantity}"
                        stock = (
                        f"{movement.previous_quantity} → "
                        f"{movement.previous_quantity - movement.quantity}"
                    )

                    else:
                        alteration = (
                        f"{movement.previous_quantity} → "
                        f"{movement.quantity}"
                    )
                        stock = str(movement.quantity)

                else:
                    alteration = str(movement.quantity)
                    stock = "-"

                if movement.reversed_movement_id is not None:
                    status = "Estorno"

                elif movement.reverse:
                    status = "Estornada"

                else:
                    status = "Normal"

                movement_data.append([
                    Paragraph(
                    str(movement.id),
                    cell_style,
                ),
                    Paragraph(
                    movement.created_at.strftime(
                      "%d/%m/%Y %H:%M"
                    ),
                    cell_style,
                ),
                    Paragraph(
                    movement.product.name,
                    cell_style,
                ),
                    Paragraph(
                    movement.movement_type.value,
                    cell_style,
                ),
                    Paragraph(
                    alteration,
                    cell_style,
                ),
                    Paragraph(
                    stock,
                    cell_style,
                ),
                    Paragraph(
                    movement.user.username
                    if movement.user
                    else "-",
                    cell_style,
                ),
                    Paragraph(
                    status,
                    cell_style,
                ),
            ])
        else:
                movement_data.append([
                    Paragraph(
                        "Nenhuma movimentação encontrada para os filtros selecionados.",
                        cell_style
                    ),
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                ])


        movement_table = Table(
            movement_data,
            colWidths=[
                12 * mm,
                27 * mm,
                48 * mm,
                23 * mm,
                27 * mm,
                35 * mm,
                30 * mm,
                30 * mm,
            ],
            repeatRows=1,
        )

        movement_table.setStyle(
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
            ]),
        )

        if not movements:
            movement_table.setStyle(
            TableStyle([
                ("SPAN", (0, 1), (-1, 1)),
                ("ALIGN", (0, 1), (-1, 1), "CENTER"),
                ("VALIGN", (0, 1), (-1, 1), "MIDDLE"),

            ])
        )

        elements.append(movement_table)

        #----------------
        #Cabeçalho e rodapé
        #-----------------

        def add_page_number(canvas, doc):
            canvas.saveState()

            #rodapé
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(colors.grey)

            canvas.drawString(
                15 * mm,
                8 * mm,
                "Gerado pelo StockFlow"
            )

            canvas.drawRightString(
                landscape(A4)[0] - 15 * mm,
                8 * mm,
                f"Página {doc.page}"
            )

            # Data de geração
            canvas.drawCentredString(
                landscape(A4)[0] / 2,
                8 * mm,
                datetime.now().strftime(
                    " %d/%m/%Y às %H:%M"
                )
            )

            canvas.restoreState()

        doc.build(
            elements,
            onFirstPage=add_page_number,
            onLaterPages=add_page_number
        )

        buffer.seek(0)

        response = Response(
            buffer.getvalue(),
            mimetype="application/pdf",
        )

        response.headers["Content-Disposition"] = (
            "attachment;"
            "filename=relatorio_movimentacoes.pdf"
        )

        return response