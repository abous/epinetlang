"""
Lexer ANTLR pour EpiNetLang
"""

class Lexer:
    """Stub de lexer ANTLR"""
    
    def __init__(self, input_stream=None):
        self.input_stream = input_stream
        self.tokens = []
    
    def getAllTokens(self):
        return self.tokens
    
    def getTokenNames(self):
        return []
    
    def getRuleNames(self):
        return []
    
    def getGrammarFileName(self):
        return "Lexer.g4"

class LexerVisitor:
    """Stub de visiteur pour le lexer"""
    pass
