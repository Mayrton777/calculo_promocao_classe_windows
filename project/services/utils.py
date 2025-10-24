import sys
import os
from pathlib import Path

def capitalizar_string(texto):
    """
    Função feita para o tratamento de textos específicos
    do formulário.
    """

    texto = str(texto)
    texto = texto.lower()

    palavras_min = ['de', 'em', 'do', 'da', 'dos', 'das', 'e', 'o', 'a']    
    palavras_max = ['fm', 'am']
    
    palavras = texto.split()
    
    resultado = []
    for palavra in palavras:
        if palavra in palavras_min:
            resultado.append(palavra)
        elif palavra in palavras_max:
            resultado.append(palavra.upper())
        else:
            resultado.append(palavra.capitalize())
            
    return ' '.join(resultado)

