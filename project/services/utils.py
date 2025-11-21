import re

def dms_for_decimal(dms):
        "Transforma (dms) para decimal"
        dms = dms.upper().strip().replace(' ', '').replace("’", "'").replace('”', '"').replace("''", '"').replace(',', '.')
        direction = re.findall(r'[A-Z]', dms)
        dms = re.sub(r'[A-Z]', '', dms)
        degree = float(dms.split('°')[0])
        minute = float(dms.split('°')[1].split("'")[0])
        second = float(dms.split('°')[1].split("'")[1].split('"')[0])
        decimal = degree + minute/60 + second/3600

        if 'S' in direction or 'W' in direction:
            decimal = -decimal

        return decimal


def capitalizar_string(texto):
    """
    Função feita para o tratamento de textos específicos
    do formulário.
    """

    texto = str(texto)
    texto = texto.lower()

    palavras_min = ['de', 'em', 'do', 'da', 'dos', 'das', 'e', 'o', 'a']    
    palavras_max = ['fm', 'am', 'ltda', 'tv']
    
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