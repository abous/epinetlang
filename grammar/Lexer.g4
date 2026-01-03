lexer grammar Lexer;

// Opérateurs
PLUS: '+';
MINUS: '-';
MULT: '*';
DIV: '/';
MOD: '%';
ASSIGN: '=';
EQ: '==';
NEQ: '!=';
LT: '<';
LE: '<=';
GT: '>';
GE: '>=';
AND: '&&';
OR: '||';
NOT: '!';

// Ponctuation
DOT: '.';
COMMA: ',';
COLON: ':';
SEMI: ';';
LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
LBRACK: '[';
RBRACK: ']';
QUESTION: '?';

// Mots-clés
IMPORT: 'import';
NETWORK: 'network';
MODEL: 'model';
ANALYSIS: 'analysis';
DATA: 'data';
INT_TYPE: 'int';
FLOAT_TYPE: 'float';
BOOL_TYPE: 'bool';
STRING_TYPE: 'string';
NETWORK_TYPE: 'Network';
MODEL_TYPE: 'Model';
DATA_TYPE: 'Data';
MATRIX_TYPE: 'Matrix';
GRAPH_TYPE: 'Graph';
IF: 'if';
ELSE: 'else';
FOR: 'for';
IN: 'in';
WHILE: 'while';
RETURN: 'return';
COMPUTE: 'compute';
SENSITIVITY: 'sensitivity';
FIT: 'fit';
TO: 'to';
FORECAST: 'forecast';
CSV: 'CSV';
JSON: 'JSON';
SQL: 'SQL';
R0: 'R0';

// Littéraux
ID: [a-zA-Z_][a-zA-Z0-9_]*;
INT: [0-9]+;
FLOAT: [0-9]+ '.' [0-9]* | '.' [0-9]+;
STRING: '"' (~["\r\n] | '\\"')* '"';
BOOL: 'true' | 'false';

// Espaces et commentaires
WS: [ \t\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;
MULTILINE_COMMENT: '/*' .*? '*/' -> skip;