from rply import LexerGenerator


class Lexer():
	def __init__(self):
		self.lexer = LexerGenerator()

	def _add_tokens(self):
		# Print
		self.lexer.add('IN_RA', r'in_ra')
		# Parenthesis
		self.lexer.add('MO_NGOAC_TRON', r'\(')
		self.lexer.add('DONG_NGOAC_TRON', r'\)')
		# Semi Colon
		# self.lexer.add('HET_DONG', r'\;')
		self.lexer.add('HET_DONG', r'(\n)|(\r\n)')
		# Operators
		self.lexer.add('CONG', r'\+')
		self.lexer.add('TRU', r'\-')
		self.lexer.add('NHAN', r'\*')
		self.lexer.add('CHIA', r'\/')
		# Number
		self.lexer.add('SO_NGUYEN', r'\d+')
		# Ignore spaces
		self.lexer.ignore(r'(^\s+)|( )+|\t+')


	def get_lexer(self):
		self._add_tokens()
		return self.lexer.build()

