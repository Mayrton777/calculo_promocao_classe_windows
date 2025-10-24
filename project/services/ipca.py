import requests
import pandas as pd

def ipca_calculation(valor_original: float):
    """
    Recebe o valor monetario e aplica o calculo
    do IPCA, apartir de 01/08/2013 até a data mais recente.
    Como retorna temos a data utilizada e o valor corrigido
    """
   
    data_inicial_str = '01/08/2013'
    url_api = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json&dataInicial={data_inicial_str}'
    
    try:
        response = requests.get(url_api)
        response.raise_for_status()
        dados = response.json()
        
        df = pd.DataFrame(dados)
        
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
        df['valor'] = pd.to_numeric(df['valor'])
        
        data_final = df['data'].max()
        
        # Calculo do fator de correção acumulado
        df['fator_mensal'] = 1 + (df['valor'] / 100)
        fator_acumulado = df['fator_mensal'].prod()
        valor_corrigido = valor_original * fator_acumulado
        
        # Exibe os resultados
        # print(f"Dados do IPCA de {data_inicial_str} a {data_final.strftime('%d/%m/%Y')}")
        # print("-" * 50)
        # print(f"Valor original: R$ {valor_original:,.2f}")
        # print(f"Fator de correção acumulado: {fator_acumulado:.4f}")
        # print(f"Valor corrigido: R$ {valor_corrigido:,.2f}")
        
        data_final_str = data_final.strftime('%d/%m/%Y')

        return valor_corrigido, data_final_str

    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados da API: {e}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return None