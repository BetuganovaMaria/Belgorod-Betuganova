from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class CalculatorForm(FlaskForm):
    first = IntegerField('A', validators=[DataRequired()])
    sign = SelectField('Операция', choices=['A + B',
                                            'A - B',
                                            'A * B',
                                            'A / B',
                                            'A ^ B'],
                       validators=[DataRequired()])
    second = IntegerField('B', validators=[DataRequired()])
    submit = SubmitField('Выполнить')