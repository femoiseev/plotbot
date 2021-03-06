import logging
import os

import telebot
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_heroku import Heroku

from server import plotting, messages
from server.models import Plot, Settings


logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot = telebot.TeleBot(os.environ.get('API_TOKEN'))

server = Flask(__name__)
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
heroku = Heroku(server)
db = SQLAlchemy(server)


@bot.message_handler(commands=['start'])
def start(message):
    db.session.query(Settings).filter(Settings.chat_id == message.chat.id).delete()
    db.session.query(Plot).filter(Plot.chat_id == message.chat.id).delete()
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
        bot.send_message(message.chat.id, messages.color_changed)
    else:
        bot.send_message(message.chat.id, messages.too_few_arguments)


@bot.message_handler(commands=['domain'], content_types=['text'])
def set_domain(message):
    args = message.text.split(' ')
    if len(args) >= 4:
        name = args[1]
        try:
            min_x = float(args[2])
            max_x = float(args[3])
            plot = db.session.query(Plot).filter(Plot.chat_id == message.chat.id, Plot.name == name).first()
            if plot is None:
                bot.send_message(message.chat.id, messages.no_such_function)
            else:
                plot.min_x = min_x
                plot.max_x = max_x
            db.session.commit()
            bot.send_message(message.chat.id, messages.domain_changed)
        except ValueError:
            bot.send_message(message.chat.id, messages.invalid_data)
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
                start(message)
                settings = db.session.query(Settings).filter(Settings.chat_id == message.chat.id).first()
            if axis == 'x':
                settings.x_min = min_value
                settings.x_max = max_value
            else:
                settings.y_min = min_value
                settings.y_max = max_value
            db.session.commit()
            bot.send_message(message.chat.id, messages.limits_changed)
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
            settings = Settings(message.chat.id)
            db.session.add(settings)
            settings = db.session.query(Settings).filter(Settings.chat_id == message.chat.id).first()
        if axis == 'x':
            settings.x_label = label
            settings.x_label = label
        else:
            settings.y_label = label
        db.session.commit()
        bot.send_message(message.chat.id, messages.label_changed)
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
                settings = Settings(message.chat.id)
                db.session.add(settings)
                settings = db.session.query(Settings).filter(Settings.chat_id == message.chat.id).first()
            settings.grid = mode
            db.session.commit()
            bot.send_message(message.chat.id, messages.grid_changed)
        else:
            bot.send_message(message.chat.id, messages.invalid_data)
    else:
        bot.send_message(message.chat.id, messages.too_few_arguments)


@bot.message_handler(commands=['show'])
def show(message):
    plots = db.session.query(Plot).filter(Plot.chat_id == message.chat.id).all()
    settings = db.session.query(Settings).filter(Settings.chat_id == message.chat.id).first()
    if settings is None:
        settings = Settings(message.chat.id)
        db.session.add(settings)
    db.session.commit()
    
    if settings.x_min is None or settings.x_max is None:
        settings.x_min = 0
        settings.x_max = 10
    if settings.grid is None:
        settings.grid = 'on'
        
    plot_path = plotting.draw_plot(message.chat.id, plots, settings)
    if plot_path is not None:
        bot.send_photo(message.chat.id, photo=open(plot_path, 'rb'))
    else:
        bot.send_message(message.chat.id, messages.invalid_function_or_limits)


@bot.message_handler(commands=['new'])
def new_plot(message):
    db.session.query(Plot).filter(Plot.chat_id == message.chat.id).delete()
    db.session.commit()
    bot.send_message(message.chat.id, messages.plots_deleted)


@bot.message_handler(commands=['default'])
def clear_settings(message):
    db.session.query(Settings).filter(Settings.chat_id == message.chat.id).delete()
    settings = Settings(message.chat.id)
    db.session.add(settings)
    db.session.commit()
    bot.send_message(message.chat.id, messages.settings_cleared)


@bot.message_handler(commands=['clear'])
def clear(message):
    db.session.query(Plot).filter(Plot.chat_id == message.chat.id).delete()
    bot.send_message(message.chat.id, messages.plots_deleted)
    db.session.query(Settings).filter(Settings.chat_id == message.chat.id).delete()
    bot.send_message(message.chat.id, messages.settings_cleared)
    db.session.commit()


@server.route("/bot", methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://plotbot.herokuapp.com/bot")
    return "!", 200
