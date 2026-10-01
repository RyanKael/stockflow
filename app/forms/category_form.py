from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class CategoryForm(FlaskForm):

    name = StringField(
        "Nome",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    active = BooleanField(
        "Categoria ativa",
        default=True,
    )

    submit = SubmitField(
        "Salvar",
    )