grammar EpiNetLang;

@header {
    # Classe pour les informations de localisation
}

program: (importDecl | networkDecl | modelDecl | analysisDecl | dataDecl)* EOF;

importDecl: 'import' STRING ';';
networkDecl: 'network' ID '(' parameterList? ')' block;
modelDecl: 'model' ID '(' parameterList? ')' block;
analysisDecl: 'analysis' ID '(' parameterList? ')' block;
dataDecl: 'data' ID '=' dataSource ';';

parameterList: parameter (',' parameter)*;
parameter: type ID ('=' expression)?;

type: 'int' | 'float' | 'bool' | 'string' | 'Network' | 'Model' | 'Data' | 'Matrix' | 'Graph';

block: '{' statement* '}';

statement: 
    varDecl
    | assignStmt
    | ifStmt
    | forStmt
    | whileStmt
    | exprStmt
    | returnStmt
    | analysisStmt;

varDecl: type ID ('=' expression)? ';';
assignStmt: ID '=' expression ';';
ifStmt: 'if' '(' expression ')' block ('else' block)?;
forStmt: 'for' '(' ID 'in' expression ')' block;
whileStmt: 'while' '(' expression ')' block;
exprStmt: expression ';';
returnStmt: 'return' expression ';';

analysisStmt: 
    'compute' 'R0' ';'
    | 'sensitivity' '(' expression ')' ';'
    | 'fit' 'to' expression ';'
    | 'forecast' expression ';';

dataSource: 
    'CSV' '(' STRING ',' parameterList? ')'
    | 'JSON' '(' STRING ',' parameterList? ')'
    | 'SQL' '(' STRING ',' parameterList? ')';

expression: 
    primary
    | expression '.' ID
    | expression '(' argumentList? ')'
    | expression '[' expression ']'
    | '-' expression
    | '!' expression
    | expression ('*' | '/' | '%') expression
    | expression ('+' | '-') expression
    | expression ('<' | '<=' | '>' | '>=' | '==' | '!=') expression
    | expression '&&' expression
    | expression '||' expression
    | expression '=' expression
    | <assoc=right> expression '?' expression ':' expression;

primary: 
    ID
    | INT
    | FLOAT
    | STRING
    | BOOL
    | '(' expression ')'
    | '[' expressionList? ']'
    | '{' pairList? '}';

argumentList: expression (',' expression)*;
expressionList: expression (',' expression)*;
pairList: pair (',' pair)*;
pair: expression ':' expression;

ID: [a-zA-Z_][a-zA-Z0-9_]*;
INT: [0-9]+;
FLOAT: [0-9]+ '.' [0-9]* | '.' [0-9]+;
STRING: '"' (~["\r\n] | '\\"')* '"';
BOOL: 'true' | 'false';

WS: [ \t\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;
MULTILINE_COMMENT: '/*' .*? '*/' -> skip;