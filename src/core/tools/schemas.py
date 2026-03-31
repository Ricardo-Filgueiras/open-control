from pydantic import BaseModel, Field

class CalculatorArgs(BaseModel):
    """Argumentos para operações matemáticas."""
    expression: str = Field(description="A expressão matemática para calcular (ex: '2 + 2', 'sqrt(16)', '15% of 200')")

class InfoArgs(BaseModel):
    """Argumentos para busca de informações gerais."""
    topic: str = Field(description="O tópico ou assunto sobre o qual o senhor deseja obter informações detalhadas")

class WebSearchArgs(BaseModel):
    """Argumentos para pesquisa na web."""
    query: str = Field(description="A consulta de pesquisa para buscar informações em tempo real na internet")
