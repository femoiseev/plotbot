import telebot
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_heroku import Heroku

from app import plotting, messages
from app.models import Plot, Settings
import config

bot = telebot.TeleBot(config.API_TOKEN)

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
heroku = Heroku(app)
db = SQLAlchemy(app)


@bot.message_handler(commands=['start'])
def start(message):
    settings = db.session.query(Settings).filter(Settings.chat_id == message.chat.id).first()
    if settings is None:
        settings = Settings(message.chat.id)
        db.session.add(settings)
    db.session.commit()
    bot.send_message(message.chat.id, messages.hello)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, messages.help_message)


@bot.message_handler(commands=['plot'], content_types=['text'])
def add_plot(message):
    args = message.text.split(' ')
    if len(args) >= 2:
        expression = ''.join(args[1:])
        name, body = plotting.convert_expression(expression)
        if name is None:
            bot.send_message(message.chat.id, messages.invalid_function)
        else:
            plot = db.session.query(Plot).filter(Plot.chat_id == message.chat.id, Plot.name == name).first()
            if plot is None:
                plot = Plot(message.chat.id, name, body)
                db.session.add(plot)
            else:
                plot.body = body
            db.session.commit()
            bot.send_message(message.chat.id, messages.success_add_plot)
    else:
        bot.send_message(message.chat.id, messages.too_few_arguments)


@bot.message_handler(commands=['color'], content_types=['text'])
def set_color(message):
    args = message.text.split(' ')
    if len(args) >= 3:
        name = args[1]
        color = args[2]
        plot = db.session.query(Plot).filter(Plot.chat_id == message.chat.id, Plot.name == name).first()
        if plot is None:
            bot.send_message(message.chat.id, messages.no_such_function)
        else:
            plot.color = color
        db.session.commit()
    else:
        bot.send_message(message.chat.id, messages.too_few_arguments)


@bot.message_handler(commands=['domain'], content_types=['text'])
def set_domain(message):
    args = message.text.split(' ')
    if len(args) >= 4:
        name = args[1]
        min_x = float(args[2])
        max_x = float(args[3])
        plot = db.session.query(Plot).filter(Plot.chat_id == message.chat.id, Plot.name == name).first()
        if plot is None:
            bot.send_message(message.chat.id, messages.no_such_function)
        else:
            plot.min_x = min_x
            plot.max_x = max_x
        db.session.commit()
    else:
        bot.send_message(message.chat.id, messages.too_few_arguments)


@bot.message_handler(commands=['xlim', 'ylim'], content_types=['text'])
def set_limits(message):
    args = message.text.split(' ')
    if len(args) >= 3:
        axis = args[0][1]
        try:
            min_value = float(args[1])
            max_value = float(args[2])
            settings = db.session.query(Settings).filter(Settings.chat_id == message.chat.id).first()
            if settings is None:
                db.session.commit()
                start()
                settings = db.session.query(Settings).filter(Settings.chat_id == message.chat.id).first()
            if axis == 'x':
                settings.x_min = min_value
                settings.x_max = max_value
            else:
                settings.y_min = min_value
                settings.y_max = max_value
            db.session.commit()
        except (ValueError, IndexError):
            bot.send_message(message.chat.id, messages.invalid_data)
    else:
        bot.send_message(message.chat.id, messages.too_few_arguments)


@bot.message_handler(commands=['xlabel', 'ylabel'], content_types=['text'])
def set_label(message):
    args = message.text.split(' ')
    if len(args) >= 2:
        axis = args[0][1]
        label = message.text[len(args[0]) + 1:]
        settings = db.session.query(Settings).filter(Settings.chat_id == message.chat.id).first()
        if settings is None:
            db.session.commit()
            start()
            settings = db.session.query(Settings).filter(Settings.chat_id == message.chat.id).first()
        if axis == 'x':
            settings.x_label = label
        else:
            settings.y_label = label
        db.session.commit()
    else:
        bot.send_message(message.chat.id, messages.too_few_arguments)


@bot.message_handler(commands=['grid'], content_types=['text'])
def set_grid(message):
    args = message.text.split(' ')
    if len(args) >= 2:
        mode = args[1]
        if mode == 'on' or mode == 'off':
            settings = db.session.query(Settings).filter(Settings.chat_id == message.chat.id).first()
            if settings is None:
                db.session.commit()
                start()
                settings = db.session.query(Settings).filter(Settings.chat_id == message.chat.id).first()
            settings.grid = mode
            db.session.commit()
    else:
        bot.send_message(message.chat.id, messages.too_few_arguments)


@bot.message_handler(commands=['show'])
def show(message):
    plots = db.session.query(Plot).filter(Plot.chat_id == message.chat.id).all()
    settings = db.session.query(Settings).filter(Settings.chat_id == message.chat.id).first()
    
    if settings is None:
        settings = Settings(message.chat.id)
    if settings.x_min is None or settings.x_max is None:
        settings.x_min = 0
        settings.x_max = 10
    if settings.grid is None:
        settings.grid = 'on'
        
    plot_path = plotting.draw_plot(message.chat.id, plots, settings)
    bot.send_photo(message.chat.id, photo=open(plot_path, 'rb'))
    db.session.commit()


@bot.message_handler(commands=['new'])
def new_plot(message):
    db.session.query(Plot).filter(Plot.chat_id == message.chat.id).delete()
    db.session.commit()


@bot.message_handler(commands=['default'])
def clear_settings(message):
    db.session.query(Settings).filter(Settings.chat_id == message.chat.id).delete()
    db.session.commit()


@bot.message_handler(commands=['clear'])
def clear(message):
    db.session.query(Plot).filter(Plot.chat_id == message.chat.id).delete()
    db.session.query(Settings).filter(Settings.chat_id == message.chat.id).delete()
    db.session.commit()


@app.route('/')
def index():
    return ''
