import re
import math

import numpy as np
import matplotlib.pyplot as plt

import config

function_pattern = re.compile('(?:[0-9-+*/^()x]|abs|e\^x|ln|log|a?(?:sin|cos|tan)h?)+')
math_functions = {'e': np.e, 'log': math.log, 'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                  'asin': np.arcsin, 'acos': np.arccos, 'atan': np.arctan, 'sinh': np.sinh,
                  'cosh': np.cosh, 'tanh': np.tanh, 'ln': np.log}


def check_expression(expression):
    return function_pattern.fullmatch(expression)


def convert_expression(expression):
    name_end = expression.find('=')
    if name_end < 0:
        return None, None
    
    name = expression[:name_end]
    body = expression[name_end + 1:]
    
    if not check_expression(body) or name in math_functions:
        return None, None
    
    return name, 'def ' + name + '(x): return ' + adapt_expression(body)


def adapt_expression(expression):
    return expression.replace('^', '**')


def create_python_functions(expressions):
    functions = math_functions.copy()
    for expression in expressions:
        exec(expression, functions)
    return functions


def draw_plot(chat_id, plots, settings):
    expressions = [plot.body for plot in plots]
    functions = create_python_functions(expressions)
    
    for plot in plots:
        if plot.name[0] != '_':
            min_x = plot.min_x
            max_x = plot.max_x
            if min_x is None or max_x is None:
                min_x = settings.x_min
                max_x = settings.x_max
            grid = np.linspace(min_x, max_x, 1000)
            if plot.color is None:
                plt.plot(grid, functions.get(plot.name)(grid), label=plot.name)
            else:
                try:
                    plt.plot(grid, functions.get(plot.name)(grid), label=plot.name, color=plot.color)
                except (KeyError, ValueError):
                    plt.plot(grid, functions.get(plot.name)(grid), label=plot.name)
    
    if not (settings.x_min is None or settings.x_max is None):
        plt.xlim((settings.x_min, settings.x_max))
        
    if not (settings.y_min is None or settings.y_max is None):
        plt.ylim((settings.y_min, settings.y_max))
    
    if settings.x_label is not None:
        plt.xlabel(settings.x_label)
    
    if settings.y_label is not None:
        plt.ylabel(settings.y_label)
    
    plt.legend()
    plt.grid(settings.grid)
    
    plot_path = config.PATH_TO_PLOTS + str(chat_id) + '.png'
    plt.savefig(plot_path)
    plt.clf()
    return plot_path
