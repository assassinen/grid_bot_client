from flask_wtf import Form
# from wtforms import TextField
# from wtforms import TextField, BooleanField
from wtforms.validators import DataRequired, Length


class MessageForm(Form):
    pass
    # title = TextField('Title', validators=[DataRequired()])
    # description = TextField(
    #     'Description', validators=[DataRequired(), Length(max=140)])
