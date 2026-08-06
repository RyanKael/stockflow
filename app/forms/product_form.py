from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    IntegerField,
    TextAreaField,
    BooleanField,
    SubmitField,
)

from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
)


class ProductForm(FlaskForm):

    code = StringField(
        "Código",
        validators=[
            DataRequired(),
            Length(max=30),
        ],
    )

    name = StringField(
        "Nome",
        validators=[
            DataRequired(),
            Length(max=120),
        ],
    )

    description = TextAreaField(
        "Descrição",
    )

    quantity = IntegerField(
        "Quantidade",
        default=0,
        validators=[
            NumberRange(min=0),
        ],
    )

    minimum_stock = IntegerField(
        "Estoque mínimo",
        default=0,
        validators=[
            NumberRange(min=0),
        ],
    )

    location = StringField(
        "Localização",
        validators=[
            Length(max=30),
        ],
    )

    active = BooleanField(
        "Produto ativo",
        default=True,
    )

    submit = SubmitField(
        "Salvar"
    )