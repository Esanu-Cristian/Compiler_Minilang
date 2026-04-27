import re
import os
import subprocess
import sys

class Lexer:
    token_specification = [
        ('NUMBER',   r'\d+(\.\d+)?'),
        ('ASSIGN',   r'='),
        ('END',      r';'),
        ('ID',       r'[A-Za-z_]\w*'),
        ('OP',       r'\+|\-|\*|\/|%'),
        ('COMPARE',  r'==|!=|<=|>=|<|>'),
        ('LPAREN',   r'\('),
        ('RPAREN',   r'\)'),
        ('LBRACE',   r'\{'),
        ('RBRACE',   r'\}'),
        ('LOGIC',    r'&&|\|\||!'),
        ('SKIP',     r'[ \t]+'),
        ('NEWLINE',  r'\n'),
        ('MISMATCH', r'.'),
    ]

    keywords = {'if', 'while', 'print', 'true', 'false', 'int', 'float', 'bool'}

    def __init__(self, source_code):
        self.source_code = source_code

    def tokenize(self):
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.token_specification)
        get_token = re.compile(tok_regex).match
        line_num = 1
        line_start = 0
        pos = 0
        mo = get_token(self.source_code)
        tokens = []
        while mo is not None:
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'NUMBER':
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
                tokens.append(('NUMBER', value))
            elif kind == 'ID':
                if value in self.keywords:
                    tokens.append(('KEYWORD', value))
                else:
                    tokens.append(('ID', value))
            elif kind == 'ASSIGN':
                tokens.append(('ASSIGN', value))
            elif kind == 'END':
                tokens.append(('END', value))
            elif kind == 'OP':
                tokens.append(('OP', value))
            elif kind == 'COMPARE':
                tokens.append(('COMPARE', value))
            elif kind == 'LPAREN':
                tokens.append(('LPAREN', value))
            elif kind == 'RPAREN':
                tokens.append(('RPAREN', value))
            elif kind == 'LBRACE':
                tokens.append(('LBRACE', value))
            elif kind == 'RBRACE':
                tokens.append(('RBRACE', value))
            elif kind == 'LOGIC':
                tokens.append(('LOGIC', value))
            elif kind == 'NEWLINE':
                line_num += 1
                line_start = mo.end()
            elif kind == 'SKIP':
                pass
            elif kind == 'MISMATCH':
                raise RuntimeError(f'{value!r} unexpected on line {line_num}')
            pos = mo.end()
            mo = get_token(self.source_code, pos)
        return tokens


class ASTNode:
    def __init__(self, node_type, value=None, children=None):
        self.node_type = node_type
        self.value = value
        self.children = children or []

    def __repr__(self):
        return f"ASTNode({self.node_type}, {self.value}, {self.children})"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def eat(self, expected_type=None, expected_value=None):
        token = self.current()
        if token is None:
            raise Exception("Unexpected end of input")
        if expected_type and token[0] != expected_type:
            raise Exception(f"Expected token type {expected_type}, got {token[0]}")
        if expected_value and token[1] != expected_value:
            raise Exception(f"Expected token value {expected_value}, got {token[1]}")
        self.pos += 1
        return token

    def parse(self):
        statements = []
        while self.current() is not None:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return ASTNode("Program", children=statements)

    def parse_statement(self):
        token = self.current()
        if token is None:
            return None
        if token[0] == 'ID':
            var_token = self.eat('ID')
            self.eat('ASSIGN')
            expr = self.parse_expression()
            self.eat('END')
            return ASTNode("Assign", value=var_token[1], children=[expr])
        elif token[0] == 'KEYWORD' and token[1] == 'print':
            self.eat('KEYWORD', 'print')
            self.eat('LPAREN')
            expr = self.parse_expression()
            self.eat('RPAREN')
            self.eat('END')
            return ASTNode("Print", children=[expr])
        elif token[0] == 'KEYWORD' and token[1] == 'if':
            self.eat('KEYWORD', 'if')
            self.eat('LPAREN')
            cond = self.parse_expression()
            self.eat('RPAREN')
            self.eat('LBRACE')
            body = []
            while self.current() and self.current()[0] != 'RBRACE':
                body.append(self.parse_statement())
            self.eat('RBRACE')
            return ASTNode("If", children=[cond, ASTNode("Block", children=body)])
        elif token[0] == 'KEYWORD' and token[1] == 'while':
            self.eat('KEYWORD', 'while')
            self.eat('LPAREN')
            cond = self.parse_expression()
            self.eat('RPAREN')
            self.eat('LBRACE')
            body = []
            while self.current() and self.current()[0] != 'RBRACE':
                body.append(self.parse_statement())
            self.eat('RBRACE')
            return ASTNode("While", children=[cond, ASTNode("Block", children=body)])
        else:
            raise Exception(f"Unknown statement starting with {token}")

    def parse_expression(self):
        node = self.parse_term()
        while self.current() and self.current()[0] in ('OP', 'COMPARE', 'LOGIC'):
            op_token = self.eat()
            right = self.parse_term()
            node = ASTNode("BinOp", value=op_token[1], children=[node, right])
        return node

    def parse_term(self):
        token = self.current()
        if token[0] == 'NUMBER':
            return ASTNode("Number", value=self.eat('NUMBER')[1])
        elif token[0] == 'ID':
            return ASTNode("Var", value=self.eat('ID')[1])
        elif token[0] == 'KEYWORD' and token[1] in ('true', 'false'):
            return ASTNode("Bool", value=self.eat('KEYWORD')[1] == 'true')
        elif token[0] == 'LPAREN':
            self.eat('LPAREN')
            expr = self.parse_expression()
            self.eat('RPAREN')
            return expr
        else:
            raise Exception(f"Unexpected token in expression: {token}")


class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = {}

    def analyze(self):
        try:
            self.visit(self.ast)
            return True
        except Exception as e:
            print(f"Semantic error: {e}")
            return False

    def visit(self, node):
        method_name = f'visit_{node.node_type}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Program(self, node):
        for stmt in node.children:
            self.visit(stmt)

    def visit_Assign(self, node):
        var_name = node.value
        expr_type = self.visit(node.children[0])
        if var_name in self.symbol_table:
            if self.symbol_table[var_name] != expr_type:
                raise Exception(f"Type mismatch for variable '{var_name}'")
        else:
            self.symbol_table[var_name] = expr_type
        return expr_type

    def visit_Var(self, node):
        var_name = node.value
        if var_name not in self.symbol_table:
            raise Exception(f"Use of undeclared variable '{var_name}'")
        return self.symbol_table[var_name]

    def visit_Number(self, node):
        return 'float' if isinstance(node.value, float) else 'int'

    def visit_Bool(self, node):
        return 'bool'

    def visit_BinOp(self, node):
        left_type = self.visit(node.children[0])
        right_type = self.visit(node.children[1])
        op = node.value
        if op in ('+', '-', '*', '/', '%'):
            if left_type not in ('int', 'float') or right_type not in ('int', 'float'):
                raise Exception(f"Operator '{op}' requires numeric operands")
            if op == '/' and isinstance(node.children[1], ASTNode) and node.children[1].node_type == 'Number' and node.children[1].value == 0:
                raise Exception("Division by zero")
            return 'float' if 'float' in (left_type, right_type) else 'int'
        elif op in ('==', '!=', '<', '>', '<=', '>='):
            if left_type != right_type:
                raise Exception(f"Comparison '{op}' between different types")
            return 'bool'
        elif op in ('&&', '||'):
            if left_type != 'bool' or right_type != 'bool':
                raise Exception(f"Logical operator '{op}' requires boolean operands")
            return 'bool'
        else:
            raise Exception(f"Unknown binary operator '{op}'")

    def visit_Print(self, node):
        self.visit(node.children[0])

    def visit_If(self, node):
        cond_type = self.visit(node.children[0])
        if cond_type != 'bool':
            raise Exception("Condition in 'if' must be boolean")
        self.visit(node.children[1])

    def visit_While(self, node):
        cond_type = self.visit(node.children[0])
        if cond_type != 'bool':
            raise Exception("Condition in 'while' must be boolean")
        self.visit(node.children[1])

    def visit_Block(self, node):
        for stmt in node.children:
            self.visit(stmt)


class IRGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.instructions = []
        self.temp_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def generate(self):
        self.visit(self.ast)
        return self.instructions

    def visit(self, node):
        method_name = f'visit_{node.node_type}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Program(self, node):
        for stmt in node.children:
            self.visit(stmt)

    def visit_Assign(self, node):
        var_name = node.value
        expr_temp = self.visit(node.children[0])
        self.instructions.append(('ASSIGN', expr_temp, var_name))

    def visit_Number(self, node):
        temp = self.new_temp()
        self.instructions.append(('LOAD_CONST', node.value, temp))
        return temp

    def visit_Bool(self, node):
        temp = self.new_temp()
        self.instructions.append(('LOAD_CONST', node.value, temp))
        return temp

    def visit_Var(self, node):
        return node.value

    def visit_BinOp(self, node):
        left = self.visit(node.children[0])
        right = self.visit(node.children[1])
        temp = self.new_temp()
        if node.value in ('==', '!=', '<', '>', '<=', '>='):
            self.instructions.append(('CMP_OP', node.value, left, right, temp))
        else:
            self.instructions.append(('BINOP', node.value, left, right, temp))
        return temp

    def visit_Print(self, node):
        value_temp = self.visit(node.children[0])
        self.instructions.append(('PRINT', value_temp))

    def visit_If(self, node):
        cond_temp = self.visit(node.children[0])
        label_else = f"label_else_{self.temp_count}"
        label_end = f"label_end_{self.temp_count}"
        self.instructions.append(('JUMP_IF_FALSE', cond_temp, label_else))
        self.visit(node.children[1])
        self.instructions.append(('JUMP', label_end))
        self.instructions.append(('LABEL', label_else))
        self.instructions.append(('LABEL', label_end))

    def visit_While(self, node):
        label_start = f"label_start_{self.temp_count}"
        label_end = f"label_end_{self.temp_count}"
        self.instructions.append(('LABEL', label_start))
        cond_temp = self.visit(node.children[0])
        self.instructions.append(('JUMP_IF_FALSE', cond_temp, label_end))
        self.visit(node.children[1])
        self.instructions.append(('JUMP', label_start))
        self.instructions.append(('LABEL', label_end))

    def visit_Block(self, node):
        for stmt in node.children:
            self.visit(stmt)


class Optimizer:
    def __init__(self, ir):
        self.ir = ir

    def optimize(self):
        ir = self.constant_folding(self.ir)
        ir = self.dead_code_elimination(ir)
        return ir

    def constant_folding(self, ir):
        new_ir = []
        constants = {}
        for instr in ir:
            if instr[0] == 'BINOP':
                op, left, right, dest = instr[1], instr[2], instr[3], instr[4]
                left_val = constants.get(left, None)
                right_val = constants.get(right, None)
                if left_val is not None and right_val is not None:
                    try:
                        if op == '+':
                            result = left_val + right_val
                        elif op == '-':
                            result = left_val - right_val
                        elif op == '*':
                            result = left_val * right_val
                        elif op == '/':
                            result = left_val / right_val
                        elif op == '%':
                            result = left_val % right_val
                        else:
                            result = None
                        if result is not None:
                            new_ir.append(('LOAD_CONST', result, dest))
                            constants[dest] = result
                            continue
                    except Exception:
                        pass
                new_ir.append(instr)
            elif instr[0] == 'LOAD_CONST':
                constants[instr[2]] = instr[1]
                new_ir.append(instr)
            else:
                new_ir.append(instr)
        return new_ir

    def dead_code_elimination(self, ir):
        used = set()
        for instr in ir:
            if instr[0] == 'BINOP':
                used.add(instr[2])
                used.add(instr[3])
            elif instr[0] == 'ASSIGN':
                used.add(instr[1])
            elif instr[0] == 'PRINT':
                used.add(instr[1])
            elif instr[0] == 'JUMP_IF_FALSE':
                used.add(instr[1])
            elif instr[0] == 'CMP_OP':
                used.add(instr[2])
                used.add(instr[3])
        new_ir = []
        assigned = set()
        for instr in reversed(ir):
            if instr[0] == 'ASSIGN':
                dest = instr[2]
                if dest in used or dest in assigned:
                    new_ir.insert(0, instr)
                    assigned.add(dest)
            elif instr[0] == 'LOAD_CONST':
                dest = instr[2]
                if dest in used or dest in assigned:
                    new_ir.insert(0, instr)
                    assigned.add(dest)
            else:
                new_ir.insert(0, instr)
        return new_ir


class CodeGenerator:
    def __init__(self, ir):
        self.ir = ir
        self.asm = []
        self.variables = set()
        self.temp_vars = set()
        self.is_win = os.name == "nt"

    def generate(self):
        self.asm = []
        self.variables = set()
        self.temp_vars = set()

        for instr in self.ir:
            if instr[0] == 'ASSIGN':
                self.variables.add(instr[2])
            elif instr[0] == 'LOAD_CONST':
                self.temp_vars.add(instr[2])
            elif instr[0] == 'BINOP':
                self.temp_vars.add(instr[4])
            elif instr[0] == 'CMP_OP':
                self.temp_vars.add(instr[4])

        self.asm.append("section .data")
        fmt_str = '%I64d' if self.is_win else '%ld'
        self.asm.append(f'    fmt db "{fmt_str}", 10, 0')
        
        if self.is_win:
            self.asm.append('    pause_cmd db "pause", 0')
        else:
            self.asm.append('    pause_cmd db "read -p \'Press enter to continue...\' dummy", 0')

        self.asm.append("section .bss")
        for var in self.variables:
            self.asm.append(f"    {var} resq 1")
        for temp in self.temp_vars:
            self.asm.append(f"    {temp} resq 1")

        self.asm.append("section .text")
        self.asm.append("    global main")
        self.asm.append("    extern printf")
        self.asm.append("    extern system")
        self.asm.append("main:")
        
        self.asm.append("    sub rsp, 40")

        for instr in self.ir:
            op = instr[0]
            if op == 'LOAD_CONST':
                value, dest = instr[1], instr[2]
                self.asm.append(f"    mov qword [rel {dest}], {int(value)}")
            elif op == 'ASSIGN':
                src, dest = instr[1], instr[2]
                self.asm.append(f"    mov rax, qword [rel {src}]")
                self.asm.append(f"    mov qword [rel {dest}], rax")
            elif op == 'BINOP':
                op_type, left, right, dest = instr[1], instr[2], instr[3], instr[4]
                self.asm.append(f"    mov rax, qword [rel {left}]")
                self.asm.append(f"    mov rbx, qword [rel {right}]")
                if op_type == '+':
                    self.asm.append(f"    add rax, rbx")
                elif op_type == '-':
                    self.asm.append(f"    sub rax, rbx")
                elif op_type == '*':
                    self.asm.append(f"    imul rax, rbx")
                elif op_type == '/':
                    self.asm.append(f"    cqo")
                    self.asm.append(f"    idiv rbx")
                elif op_type == '%':
                    self.asm.append(f"    cqo")
                    self.asm.append(f"    idiv rbx")
                    self.asm.append(f"    mov rax, rdx")
                self.asm.append(f"    mov qword [rel {dest}], rax")
            elif op == 'CMP_OP':
                cmp_type, left, right, dest = instr[1], instr[2], instr[3], instr[4]
                self.asm.append(f"    mov rax, qword [rel {left}]")
                self.asm.append(f"    cmp rax, qword [rel {right}]")
                set_instr = {'==': 'sete', '!=': 'setne', '<': 'setl', '<=': 'setle', '>': 'setg', '>=': 'setge'}[cmp_type]
                self.asm.append(f"    {set_instr} al")
                self.asm.append(f"    movzx rax, al")
                self.asm.append(f"    mov qword [rel {dest}], rax")
            elif op == 'PRINT':
                src = instr[1]
                if self.is_win:
                    self.asm.append(f"    mov rdx, qword [rel {src}]")
                    self.asm.append(f"    lea rcx, [rel fmt]")
                else:
                    self.asm.append(f"    mov rsi, qword [rel {src}]")
                    self.asm.append(f"    lea rdi, [rel fmt]")
                self.asm.append(f"    mov rax, 0")
                self.asm.append(f"    call printf")
            elif op == 'LABEL':
                self.asm.append(f"{instr[1]}:")
            elif op == 'JUMP':
                self.asm.append(f"    jmp {instr[1]}")
            elif op == 'JUMP_IF_FALSE':
                cond, label = instr[1], instr[2]
                self.asm.append(f"    mov rax, qword [rel {cond}]")
                self.asm.append(f"    cmp rax, 0")
                self.asm.append(f"    je {label}")

        if self.is_win:
            self.asm.append("    lea rcx, [rel pause_cmd]")
        else:
            self.asm.append("    lea rdi, [rel pause_cmd]")
        
        self.asm.append("    call system")
        self.asm.append("    add rsp, 40")
        self.asm.append("    ret")
        return "\n".join(self.asm)



class Linker:
    def __init__(self, asm_code, output_name="output"):
        self.asm_code = asm_code
        self.output_name = output_name

    def link(self):
        asm_file = f"{self.output_name}.asm"
        obj_file = f"{self.output_name}.o"
        exe_file = f"{self.output_name}.exe" if os.name == "nt" else f"{self.output_name}"

        with open(asm_file, "w") as f:
            f.write(self.asm_code)

        format_nasm = "win64" if os.name == "nt" else "elf64"
        nasm_cmd = ["nasm", "-f", format_nasm, asm_file, "-o", obj_file]
        
        try:
            subprocess.check_call(nasm_cmd)
        except subprocess.CalledProcessError:
            print("Error: NASM assembly failed.")
            return None

        gcc_cmd = ["gcc", obj_file, "-o", exe_file]
        
        if os.name != "nt":
            gcc_cmd.append("-no-pie")

        try:
            subprocess.check_call(gcc_cmd)
        except subprocess.CalledProcessError:
            print("Error: Linking failed.")
            return None

        return exe_file


def main(source_code):
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    semantic_analyzer = SemanticAnalyzer(ast)
    if not semantic_analyzer.analyze():
        print("Semantic errors detected.")
        return

    ir_generator = IRGenerator(ast)
    ir = ir_generator.generate()

    optimizer = Optimizer(ir)
    optimized_ir = optimizer.optimize()

    code_generator = CodeGenerator(optimized_ir)
    asm_code = code_generator.generate()

    linker = Linker(asm_code)
    executable = linker.link()

    print(f"Compilation successful. Executable: {executable}")

if __name__ == "__main__":
    with open("input.minilang", "r") as f:
        source = f.read()
    main(source)
