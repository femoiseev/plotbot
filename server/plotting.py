import numpy as np
import matplotlib.pyplot as plt
from sympy.parsing.sympy_parser import parse_expr
from sympy import lambdify
from sympy.abc import x


def check_expression(expression):
    try:
        expr = parse_expr(expression)
        function = lambdify(x, expr, ('math', 'mpmath', 'sympy'))
        try:
            float(function(1))
        except (ValueError, ZeroDivisionError):
            return True
        return True
    except (SyntaxError, NameError, TypeError):
        return False


def convert_expression(expression):
    name_end = expression.find('=')
    if name_end < 0:
        return None, None
    
    name = expression[:name_end]
    body = adapt_expression(expression[name_end + 1:])
    
    if not check_expression(body):
        return None, None
    
    return name, body


def adapt_expression(expression):
    return expression.replace('^', '**').replace('e', 'exp(1)')


def draw_plot(chat_id, plots, settings):
    plt.clf()
    for plot in plots:
        if plot.name[0] != '_':
            min_x = plot.min_x
            max_x = plot.max_x
            if min_x is None or max_x is None:
                min_x = settings.x_min
                max_x = settings.x_max
            grid = np.linspace(min_x, max_x, 1000)
            expr = parse_expr(plot.body)
            function = lambdify(x, expr, ('math', 'mpmath', 'sympy'))
            
            try:
                if plot.color is None:
                    plt.plot(grid, [function(arg) for arg in grid], label=plot.name)
                else:
                    plt.plot(grid, [function(arg) for arg in grid], label=plot.name, color=plot.color)
            except (ValueError, SystemError, OverflowError, KeyError):
                plt.clf()
                return None
    
    if not (settings.x_min is None or settings.x_max is None):
        plt.xlim((settings.x_min, settings.x_max))
    
    if not (settings.y_min is None or settings.y_max is None):
        plt.ylim((settings.y_min, settings.y_max))
    
    if settings.x_label is not None:
        plt.xlabel(settings.x_label)
    
    if settings.y_label is not None:
        plt.ylabel(settings.y_label)
    
    plt.legend(loc='best')
    plt.grid(b=settings.grid, ls=':')
    
    plot_path = str(chat_id) + '.png'
    try:
        plt.savefig(plot_path)
    except (ValueError, KeyError):
        plot_path = None
    plt.clf()
    return plot_path
