from lexer import Lexer
from parser import Parser

text_input = """
	in_ra(4 + 4 - 2)
"""

lexer = Lexer().get_lexer()
tokens = lexer.lex(text_input)
tokens2 = lexer.lex(text_input)

for token in tokens2:
    print(token)
print(tokens)

pg = Parser()
pg.parse()
parser = pg.get_parser()
parser.parse(tokens).eval()