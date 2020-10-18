import re

from pyearl.exceptions import TemplateSyntaxError


class CodeBuilder:

    INDENT_STEP = 4         # 缩进的空格数

    def __init__(self, indent: int = 0):
        """

        :param indent:
        """
        self.code = []
        self.indent_level: int = indent

    def add_line(self, line: str):
        """
        添加一行代码
        :param line:
        :return:
        """
        self.code.extend([' ' * self.indent_level, line, '\n'])

    def indent(self):
        """
        增加一级缩进
        :return:
        """
        self.indent_level += self.INDENT_STEP

    def dedent(self):
        """
        减小一级缩进
        :return:
        """
        self.indent_level -= self.INDENT_STEP

    def add_section(self):
        """

        :return:
        """
        section = CodeBuilder(self.indent_level)
        self.code.append(section)
        return section

    def __str__(self):
        return ''.join(str(c) for c in self.code)

    def get_globals(self):
        """
        运行代码，并返回命名空间字典
        :return:
        """
        assert self.indent_level == 0           # 检查缩进
        python_source = str(self)
        global_namespace = {}
        exec(python_source, global_namespace)
        return global_namespace


def _do_dots(value, *dots):
    """

    :param value:
    :param dots:
    :return:
    """
    for dot in dots:
        try:
            value = getattr(value, dot)
        except AttributeError:
            value = value[dot]
        if callable(value):
            value = value()
    return value


class Template:

    def __init__(self, text, *contexts):
        """

        :param text:
        :param contexts:
        """
        self.context = {}
        for context in contexts:
            self.context.update(context)

        self.all_vars = set()           # 所有变量名
        self.loop_vars = set()          # 用于循环的变量名

        code = CodeBuilder()
        code.add_line('def render_function(context, do_dots):')
        code.indent()
        vars_code = code.add_section()          # 添加一个变量名section占位，从上下文提取变量之后实现
        code.add_line('result = []')
        code.add_line('append_result = result.append')
        code.add_line('extend_result = result.extend')
        code.add_line('to_str = str')

        buffered = []           # 代码缓存
        def flush_output():
            """
            清空代码缓存
            :return:
            """
            if len(buffered) == 1:
                code.add_line(f'append_result({buffered[0]})')
            elif len(buffered) > 1:
                code.add_line('extend_result([{}])'.format(', '.join(buffered)))
            del buffered[:]         # 清空缓存

        ops_stack = []          # 检查嵌套是否完整
        tokens = re.split(r"(?s)({{.*?}}|{%.*?%}|{#.*?#})", text)           # 将文本分割
        for token in tokens:
            if token.startswith('{#'):          # 注释
                continue
            elif token.startswith('{{'):            # 变量
                expr = self._expr_code(token[2:-2].strip())
                buffered.append(f'to_str({expr})')
            elif token.startswith('{%'):            # 控制语句
                flush_output()
                words = token[2:-2].strip().split()
                if words[0] == 'if':
                    if len(words) != 2:
                        self._syntax_error('Don\'t understand if', token)
                    ops_stack.append('if')
                    code.add_line(f'if {self._expr_code(words[1])}')
                    code.indent()
                elif words[0] == 'for':
                    if len(words) != 4 or words[2] != 'in':
                        self._syntax_error('Don\'t understand for', token)
                    ops_stack.append('for')
                    self._variable(words[1], self.loop_vars)
                    code.add_line(f'for c_{words[1]} in {self._expr_code(words[3])}:')
                    code.indent()
                elif words[0].startswith('end'):
                    if len(words) != 1:
                        self._syntax_error('Don\'t understand end tag', token)
                    if not ops_stack:
                        self._syntax_error('Too many ends', token)
                    end_tag = words[0][3:]
                    start_tag = ops_stack.pop()
                    if start_tag != end_tag:
                        self._syntax_error('Mismatched end tag', token)
                    code.dedent()
                else:
                    self._syntax_error('Don\'t understand tag', words[0])
            else:
                if token:
                    buffered.append(repr(token))

        if ops_stack:
            self._syntax_error('Unmatched action tag', ops_stack[-1])
        flush_output()

        for var_name in self.all_vars - self.loop_vars:
            vars_code.add_line(f'c_{var_name} = context[{repr(var_name)}]')

        code.add_line('return \'\'.join(result)')
        code.dedent()

        self._render_function = code.get_globals()['render_function']

    def _expr_code(self, expr):
        """

        :param expr:
        :return:
        """
        if '|' in expr:
            pipes = expr.split('|')
            code = self._expr_code(pipes[0])
            for func in pipes[1:]:
                self._variable(func, self.all_vars)
                code = f'c_{func}({code})'
        elif '.' in expr:
            dots = expr.split('.')
            code = dots[0]
            args = ', '.join(repr(d) for d in dots[1:])
            code = f'do_dots({code}, {args})'
        else:
            self._variable(expr, self.all_vars)
            code = f'c_{expr}'
        return code

    def _syntax_error(self, msg, thing):
        """

        :param msg:
        :param thing:
        :return:
        """
        raise TemplateSyntaxError(msg, thing)

    def _variable(self, name, vars_set):
        """

        :param name:
        :param vars_set:
        :return:
        """
        if not re.match(r"[_a-zA-Z][_a-zA-Z0-9]*$", name):
            self._syntax_error("Not a valid name", name)
        vars_set.add(name)

    @property
    def html(self):
        render_context = dict(self.context)
        return self._render_function(render_context, _do_dots)

    def render(self):
        render_context = dict(self.context)
        return self._render_function(render_context, _do_dots)


def render(t_path: str, context: dict):
    """

    :param text:
    :param context:
    :return:
    """
    with open(t_path, 'r') as f:
        template = Template(f.read(), context)
        return template.html