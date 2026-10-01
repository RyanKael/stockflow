from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, render_template
from flask_login import login_required

from app.extensions import db
from app.models.product import Product
from app.models.stock_movement import StockMovement, MovementType

main = Blueprint("main", __name__)


@main.route("/")
@login_required
def index():

    return render_template(
        "home/index.html"
    )

@main.route("/dashboard")
@login_required
def dashboard():

    #Produtos ativos
    active_products = Product.query.filter_by(
        active=True
    ).count()

    # Quantidade total em estoque
    total_stock = db.session.query(
        db.func.sum(Product.quantity)
    ).filter(
        Product.active == True
    ).scalar() or 0

    #Produtos com estoque baixo
    low_stock_products = Product.query.filter(
        Product.active == True,
        Product.quantity <= Product.minimum_stock,
        Product.quantity > 0,
    ).count()

    #Produtos sem estoque
    out_of_stock_products = Product.query.filter(
        Product.active == True,
        Product.quantity == 0,
    ).count()

    #Últimas movimentações
    recent_movements = StockMovement.query.order_by(
        StockMovement.created_at.desc()
    ).limit(5).all()

    #--------------------
    #Movimentações realizadas hoje
    #--------------------

    today = datetime.now(
        ZoneInfo("America/Sao_Paulo")
    ).date()

    today_movements = StockMovement.query.all()

    entries_today = db.session.query(
        db.func.sum(StockMovement.quantity)
    ).filter(
        StockMovement.movement_type == MovementType.ENTRY,
        db.func.date(StockMovement.created_at) == today,
    ).scalar() or 0

    exits_today = db.session.query(
        db.func.sum(StockMovement.quantity)
    ).filter(
        StockMovement.movement_type == MovementType.EXIT,
        db.func.date(StockMovement.created_at) == today,
    ).scalar() or 0

    today_balance = exits_today - exits_today


    return render_template(
        "home/dashboard.html",
        active_products=active_products,
        total_stock=total_stock,
        low_stock_products=low_stock_products,
        out_of_stock_products=out_of_stock_products,
        recent_movements=recent_movements,
        entries_today=entries_today,
        exits_today=exits_today,
        today_balance=today_balance,
    )