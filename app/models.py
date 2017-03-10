from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Plot(db.Model):
    __tablename__ = 'plots'
    
    chat_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), primary_key=True)
    body = db.Column(db.String(120), nullable=False)
    min_x = db.Column(db.REAL)
    max_x = db.Column(db.REAL)
    color = db.Column(db.String(120))
    
    def __init__(self, chat_id, name, body):
        self.chat_id = chat_id
        self.name = name
        self.body = body


class Settings(db.Model):
    __tablename__ = 'settings'
    
    chat_id = db.Column(db.Integer, primary_key=True)
    x_min = db.Column(db.REAL)
    x_max = db.Column(db.REAL)
    y_min = db.Column(db.REAL)
    y_max = db.Column(db.REAL)
    x_label = db.Column(db.String(120))
    y_label = db.Column(db.String(120))
    grid = db.Column(db.String(120))
    
    def __init__(self, chat_id):
        self.chat_id = chat_id
