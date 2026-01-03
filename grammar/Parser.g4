parser grammar Parser;

options { tokenVocab=Lexer; }

program: (importDecl | networkDecl | modelDecl | analysisDecl | dataDecl)* EOF;

importDecl: IMPORT STRING SEMI;
networkDecl: NETWORK ID LPAREN parameterList? RPAREN block;
modelDecl: MODEL ID LPAREN parameterList? RPAREN block;
analysisDecl: ANALYSIS ID LPAREN parameterList? RPAREN block;
dataDecl: DATA ID ASSIGN dataSource SEMI;

parameterList: parameter (COMMA parameter)*;
parameter: type ID (ASSIGN expression)?;

type: INT_TYPE | FLOAT_TYPE | BOOL_TYPE | STRING_TYPE | NETWORK_TYPE | MODEL_TYPE | DATA_TYPE | MATRIX_TYPE | GRAPH_TYPE;

block: LBRACE statement* RBRACE;

statement: 
    varDecl
    | assignStmt
    | ifStmt
    | forStmt
    | whileStmt
    | exprStmt
    | returnStmt
    | analysisStmt;

varDecl: type ID (ASSIGN expression)? SEMI;
assignStmt: ID ASSIGN expression SEMI;
ifStmt: IF LPAREN expression RPAREN block (ELSE block)?;
forStmt: FOR LPAREN ID IN expression RPAREN block;
whileStmt: WHILE LPAREN expression RPAREN block;
exprStmt: expression SEMI;
returnStmt: RETURN expression SEMI;

analysisStmt: 
    COMPUTE R0 SEMI
    | SENSITIVITY LPAREN expression RPAREN SEMI
    | FIT TO expression SEMI
    | FORECAST expression SEMI;

dataSource: 
    CSV LPAREN STRING (COMMA parameterList)? RPAREN
    | JSON LPAREN STRING (COMMA parameterList)? RPAREN
    | SQL LPAREN STRING (COMMA parameterList)? RPAREN;

expression: 
    primary
    | expression DOT ID
    | expression LPAREN argumentList? RPAREN
    | expression LBRACK expression RBRACK
    | MINUS expression
    | NOT expression
    | expression (MULT | DIV | MOD) expression
    | expression (PLUS | MINUS) expression
    | expression (LT | LE | GT | GE | EQ | NEQ) expression
    | expression AND expression
    | expression OR expression
    | expression ASSIGN expression
    | expression QUESTION expression COLON expression;

primary: 
    ID
    | INT
    | FLOAT
    | STRING
    | BOOL
    | LPAREN expression RPAREN
    | LBRACK expressionList? RBRACK
    | LBRACE pairList? RBRACE;

argumentList: expression (COMMA expression)*;
expressionList: expression (COMMA expression)*;
pairList: pair (COMMA pair)*;
pair: expression COLON expression;