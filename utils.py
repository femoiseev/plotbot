import numpy as np
import matplotlib.pyplot as plt
import re
import math
import config

function_pattern = re.compile('(?:[0-9-+*/^()x]|abs|e\^x|ln|log|a?(?:sin|cos|tan)h?)+')
math_functions = {'e': np.e, 'log': math.log, 'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                  'asin': np.arcsin, 'acos': np.arccos, 'atan': np.arctan, 'sinh': np.sinh,
                  'cosh': np.cosh, 'tanh': np.tanh, 'ln': math.log}


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


def draw_plot(chat_id, expressions, min_xs, max_xs, colors, xlim, ylim, xlabel, ylabel, grid_mode):
    functions = create_python_functions(expressions)
    
    for name, function in functions.items():
        if name[0] != '_' and name not in math_functions.keys():
            min_x = min_xs[name]
            max_x = max_xs[name]
            color = colors[name]
            if min_xs is None or max_x is None:
                min_x = xlim[0]
                max_x = xlim[1]
            grid = np.linspace(min_x, max_x, 1000)
            if color is None:
                plt.plot(grid, function(grid), label=name)
            else:
                plt.plot(grid, function(grid), label=name, color=color)
                
    if not (xlim is None or xlim[0] is None or xlim[1] is None):
        plt.xlim(xlim)
    
    if not (ylim is None or ylim[0] is None or ylim[1] is None):
        plt.ylim(ylim)
    
    if xlabel is not None:
        plt.xlabel(xlabel)
        
    if ylabel is not None:
        plt.ylabel(ylabel)
    
    plt.legend()
    plt.grid(grid_mode)
    
    plot_path = config.PATH_TO_PLOTS + str(chat_id) + '.png'
    plt.savefig(plot_path)
    plt.clf()
    return plot_path
