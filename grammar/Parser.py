"""
Parser ANTLR pour EpiNetLang
"""

class Parser:
    """Stub de parser ANTLR"""
    
    def __init__(self, token_stream=None):
        self.token_stream = token_stream
        self._syntax_errors = 0
        self._errors = []
    
    def getNumberOfSyntaxErrors(self):
        return self._syntax_errors
    
    def getErrors(self):
        return self._errors
    
    def program(self):
        """Méthode stub pour la règle 'program'"""
        return None
    
    def getRuleNames(self):
        return [
            'program', 'importDecl', 'networkDecl', 'modelDecl', 
            'analysisDecl', 'dataDecl', 'parameterList', 'parameter',
            'type', 'block', 'statement', 'varDecl', 'assignStmt',
            'ifStmt', 'forStmt', 'whileStmt', 'exprStmt', 'returnStmt',
            'analysisStmt', 'dataSource', 'expression', 'primary',
            'argumentList', 'expressionList', 'pairList', 'pair'
        ]
    
    def getGrammarFileName(self):
        return "Parser.g4"

class ParserVisitor:
    """Visiteur pour le parser ANTLR"""
    
    def visitProgram(self, ctx):
        """Visiter un programme"""
        pass
    
    def visitImportDecl(self, ctx):
        """Visiter une déclaration d'import"""
        pass
    
    def visitNetworkDecl(self, ctx):
        """Visiter une déclaration de réseau"""
        pass
    
    def visitModelDecl(self, ctx):
        """Visiter une déclaration de modèle"""
        pass
    
    def visitAnalysisDecl(self, ctx):
        """Visiter une déclaration d'analyse"""
        pass
    
    def visitDataDecl(self, ctx):
        """Visiter une déclaration de données"""
        pass
    
    def visitParameterList(self, ctx):
        """Visiter une liste de paramètres"""
        pass
    
    def visitParameter(self, ctx):
        """Visiter un paramètre"""
        pass
    
    def visitType(self, ctx):
        """Visiter un type"""
        pass
    
    def visitBlock(self, ctx):
        """Visiter un bloc"""
        pass
    
    def visitStatement(self, ctx):
        """Visiter une instruction"""
        pass
    
    def visitVarDecl(self, ctx):
        """Visiter une déclaration de variable"""
        pass
    
    def visitAssignStmt(self, ctx):
        """Visiter une affectation"""
        pass
    
    def visitIfStmt(self, ctx):
        """Visiter une condition if"""
        pass
    
    def visitForStmt(self, ctx):
        """Visiter une boucle for"""
        pass
    
    def visitWhileStmt(self, ctx):
        """Visiter une boucle while"""
        pass
    
    def visitExprStmt(self, ctx):
        """Visiter une instruction expression"""
        pass
    
    def visitReturnStmt(self, ctx):
        """Visiter une instruction return"""
        pass
    
    def visitAnalysisStmt(self, ctx):
        """Visiter une instruction d'analyse"""
        pass
    
    def visitDataSource(self, ctx):
        """Visiter une source de données"""
        pass
    
    def visitExpression(self, ctx):
        """Visiter une expression"""
        pass
    
    def visitPrimary(self, ctx):
        """Visiter une expression primaire"""
        pass
    
    def visitArgumentList(self, ctx):
        """Visiter une liste d'arguments"""
        pass
    
    def visitExpressionList(self, ctx):
        """Visiter une liste d'expressions"""
        pass
    
    def visitPairList(self, ctx):
        """Visiter une liste de paires"""
        pass
    
    def visitPair(self, ctx):
        """Visiter une paire"""
        pass
