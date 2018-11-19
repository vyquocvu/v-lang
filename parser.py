from rply import ParserGenerator
from ast import Number, Sum, Sub, Print, Mul, Div


class Parser():
	def __init__(self, module, builder, printf):
		self.pg = ParserGenerator(
			# A list of all token names accepted by the parser.
			['SO_NGUYEN',
				'IN_RA',
				'MO_NGOAC_TRON',
				'DONG_NGOAC_TRON',
				'HET_DONG',
				'CONG',
				'TRU',
				'NHAN',
				'CHIA'
			]
		)
		self.module = module
		self.builder = builder
		self.printf = printf


	def parse(self):
		@self.pg.production('program : IN_RA MO_NGOAC_TRON expression DONG_NGOAC_TRON HET_DONG')

		def program(p):
			return Print(self.builder, self.module, self.printf, p[2])

		@self.pg.production('expression : expression NHAN expression')
		@self.pg.production('expression : expression CHIA expression')
		@self.pg.production('expression : expression CONG expression')
		@self.pg.production('expression : expression TRU expression')

		def expression(p):
			left = p[0]
			right = p[2]
			operator = p[1]
			if operator.gettokentype() == 'NHAN':
				return Mul(self.builder, self.module, left, right)
			elif operator.gettokentype() == 'CHIA':
				return Div(self.builder, self.module, left, right)
			elif operator.gettokentype() == 'CONG':
				return Sum(self.builder, self.module, left, right)
			elif operator.gettokentype() == 'TRU':
				return Sub(self.builder, self.module, left, right)

		@self.pg.production('expression : SO_NGUYEN')

		def number(p):
			return Number(self.builder, self.module, p[0].value)

		@self.pg.error

		def error_handle(token):
			raise ValueError(token)

	def get_parser(self):
		return self.pg.build()
