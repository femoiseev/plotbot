import telebot
import config
import constants
import utils
from SQLighter import SQLighter

bot = telebot.TeleBot(config.API_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    db_worker = SQLighter(config.PATH_TO_DATABASE)
    try:
        db_worker.add_chat(message.chat.id)
        bot.send_message(message.chat.id, constants.hello_message)
    except Exception as e:
        bot.send_message(message.chat.id, constants.error_message + str(e))
    finally:
        db_worker.close()
        
        
@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, constants.help_message)
    

@bot.message_handler(commands=['plot'], content_types=['text'])
def add_plot(message):
    db_worker = SQLighter(config.PATH_TO_DATABASE)
    try:
        expression = ''.join(message.text.split(' ')[1:])
        name, body = utils.convert_expression(expression)
        if name is None:
            bot.send_message(message.chat.id, constants.invalid_function_message)
        else:
            db_worker.put_function(message.chat.id, name, body)
            bot.send_message(message.chat.id, constants.success_function_add_message)
    except Exception as e:
        bot.send_message(message.chat.id, constants.error_message + str(e))
    finally:
        db_worker.close()


@bot.message_handler(commands=['color'], content_types=['text'])
def set_color(message):
    db_worker = SQLighter(config.PATH_TO_DATABASE)
    try:
        args = message.text.split(' ')
        name = args[1]
        color = args[2]
        db_worker.set_color(message.chat.id, name, color)
    except Exception as e:
        bot.send_message(message.chat.id, constants.error_message + str(e))
    finally:
        db_worker.close()
        
        
@bot.message_handler(commands=['domain'], content_types=['text'])
def set_color(message):
    db_worker = SQLighter(config.PATH_TO_DATABASE)
    try:
        args = message.text.split(' ')
        name = args[1]
        min_x = float(args[2])
        max_x = float(args[3])
        db_worker.set_domain(message.chat.id, name, min_x, max_x)
    except Exception as e:
        bot.send_message(message.chat.id, constants.error_message + str(e))
    finally:
        db_worker.close()


@bot.message_handler(commands=['xlim', 'ylim'], content_types=['text'])
def set_limits(message):
    db_worker = SQLighter(config.PATH_TO_DATABASE)
    try:
        args = message.text.split(' ')
        axis = args[0][1]
        try:
            min_value = float(args[1])
            max_value = float(args[2])
            db_worker.set_limits(message.chat.id, axis, (min_value, max_value))
        except (ValueError, IndexError):
            bot.send_message(message.chat.id, constants.invalid_data_message)
    except Exception as e:
        bot.send_message(message.chat.id, constants.error_message + str(e))
    finally:
        db_worker.close()
      
        
@bot.message_handler(commands=['xlabel', 'ylabel'], content_types=['text'])
def set_label(message):
    db_worker = SQLighter(config.PATH_TO_DATABASE)
    try:
        args = message.text.split(' ')
        axis = args[0][1]
        label = message.text[len(args[0]) + 1:]
        db_worker.set_label(message.chat.id, axis, label)
    except Exception as e:
        bot.send_message(message.chat.id, constants.error_message + str(e))
    finally:
        db_worker.close()
        

@bot.message_handler(commands=['grid'], content_types=['text'])
def set_grid(message):
    db_worker = SQLighter(config.PATH_TO_DATABASE)
    try:
        args = message.text.split(' ')
        mode = args[1]
        db_worker.set_grid(message.chat.id, mode)
    except Exception as e:
        bot.send_message(message.chat.id, constants.error_message + str(e))
    finally:
        db_worker.close()


@bot.message_handler(commands=['show'])
def show(message):
    db_worker = SQLighter(config.PATH_TO_DATABASE)
    try:
        functions, min_xs, max_xs, colors = db_worker.get_functions(message.chat.id)
        left, right, down, up, xlabel, ylabel, grid_mode = db_worker.get_settings(message.chat.id)
        if left is None or right is None:
            left = 0
            right = 10
        if grid_mode is None:
            grid_mode = 'on'
            
        plot_path = utils.draw_plot(message.chat.id, functions, min_xs, max_xs, colors, (left, right), (down, up), xlabel, ylabel, grid_mode)
        bot.send_photo(message.chat.id, photo=open(plot_path, 'rb'))
    except Exception as e:
        bot.send_message(message.chat.id, constants.error_message + str(e))
    finally:
        db_worker.close()
    

@bot.message_handler(commands=['new'])
def new_plot(message):
    db_worker = SQLighter(config.PATH_TO_DATABASE)
    try:
        db_worker.clear_functions(message.chat.id)
    except Exception as e:
        bot.send_message(message.chat.id, constants.error_message + str(e))
    finally:
        db_worker.close()
        
        
@bot.message_handler(commands=['default'])
def clear_settings(message):
    db_worker = SQLighter(config.PATH_TO_DATABASE)
    try:
        db_worker.clear_settings(message.chat.id)
    except Exception as e:
        bot.send_message(message.chat.id, constants.error_message + str(e))
    finally:
        db_worker.close()
        
        
@bot.message_handler(commands=['clear'])
def clear(message):
    db_worker = SQLighter(config.PATH_TO_DATABASE)
    try:
        db_worker.clear_all(message.chat.id)
    except Exception as e:
        bot.send_message(message.chat.id, constants.error_message + str(e))
    finally:
        db_worker.close()
    

if __name__ == '__main__':
    bot.polling(none_stop=True)