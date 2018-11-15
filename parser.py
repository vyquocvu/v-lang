from rply import ParserGenerator
from ast import Number, Sum, Sub, Print, Mul, Div


class Parser():
	def __init__(self):
		self.pg = ParserGenerator(
			# A list of all token names accepted by the parser.
			['SO_NGUYEN',
				'IN_RA',
				'MO_NGOAC_TRON',
				'DONG_NGOAC_TRON',
				'HET_DONG',
				'CONG',
				'TRU',
			]
		)

	def parse(self):
		@self.pg.production('program : IN_RA MO_NGOAC_TRON expression DONG_NGOAC_TRON HET_DONG')
		def program(p):
			return Print(p[2])

		@self.pg.production('expression : expression CONG expression')
		@self.pg.production('expression : expression TRU expression')
		
		def expression(p):
			left = p[0]
			right = p[2]
			operator = p[1]
			if operator.gettokentype() == 'CONG':
				return Sum(left, right)
			elif operator.gettokentype() == 'TRU':
				return Sub(left, right)
			elif operator.gettokentype() == 'NHAN':
				return Mul(left, right)
			elif operator.gettokentype() == 'CHIA':
				return Div(left, right)

		@self.pg.production('expression : SO_NGUYEN')
		def number(p):
			return Number(p[0].value)

		@self.pg.error
		def error_handle(token):
			raise ValueError(token)

	def get_parser(self):
		return self.pg.build()

# from rply import ParserGenerator
# from ast import Number, Sum, Sub, Print


# class Parser():
# 	def __init__(self):
# 		self.pg = ParserGenerator(
# 			# A list of all token names accepted by the parser.
# 			['NUMBER', 'PRINT', 'OPEN_PAREN', 'CLOSE_PAREN',
# 			 'SEMI_COLON', 'SUM', 'SUB']
# 		)

# 	def parse(self):
# 		@self.pg.production('program : PRINT OPEN_PAREN expression CLOSE_PAREN SEMI_COLON')
# 		def program(p):
# 			return Print(p[2])

# 		@self.pg.production('expression : expression SUM expression')
# 		@self.pg.production('expression : expression SUB expression')
# 		def expression(p):
# 			left = p[0]
# 			right = p[2]
# 			operator = p[1]
# 			if operator.gettokentype() == 'SUM':
# 				return Sum(left, right)
# 			elif operator.gettokentype() == 'SUB':
# 				return Sub(left, right)

# 		@self.pg.production('expression : NUMBER')
# 		def number(p):
# 			return Number(p[0].value)

# 		@self.pg.error
# 		def error_handle(token):
# 			raise ValueError(token)

# 	def get_parser(self):
# 		return self.pg.build()