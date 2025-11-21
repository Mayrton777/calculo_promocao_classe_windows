import requests
import pandas as pd
import json  # <-- Adicionada a importação

def ipca_calculation(valor_original: float, static_ipca_path: str) -> tuple | None:
    """
    Recebe o valor monetario e aplica o calculo
    do IPCA, apartir de 01/08/2013 até a data mais recente.
    Como retorna temos a data utilizada e o valor corrigido.
    """

    data_inicial_str = '01/08/2013'
    url_api = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json&dataInicial={data_inicial_str}'
    
    dados = None
    
    try:
        """
        Tenta buscar dados da API do BCB. Se falhar, usa o arquivo
        JSON estático fornecido em 'static_ipca_path'.
        """
        response = requests.get(url_api, timeout=5)
        response.raise_for_status()
        dados = response.json()
    except requests.exceptions.RequestException as e:
        try:
            with open(static_ipca_path, 'r', encoding='utf-8') as f:
                dados = json.load(f)
        except FileNotFoundError:
            raise ValueError(f"ERRO FATAL: A API falhou E o arquivo estático '{static_ipca_path}' não foi encontrado.")
        except json.JSONDecodeError:
            raise ValueError(f"ERRO FATAL: A API falhou E o arquivo estático '{static_ipca_path}' está mal formatado (não é um JSON válido).")
        except Exception as file_e:
            raise ValueError(f"ERRO FATAL: A API falhou E ocorreu um erro ao ler o arquivo estático: {file_e}")

    if dados is None:
        raise ValueError("ERRO: Nenhum dado de IPCA pôde ser carregado.")

    try:
        df = pd.DataFrame(dados)
        
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
        df['valor'] = pd.to_numeric(df['valor'])
        
        data_inicial = pd.to_datetime(data_inicial_str, format='%d/%m/%Y')
        df = df[df['data'] >= data_inicial].copy()
        
        if df.empty:
            raise ValueError(f"ERRO: Não há dados de IPCA disponíveis a partir de {data_inicial_str}.")
            
        data_final = df['data'].max()
        
        # Calculo do fator de correção acumulado
        df['fator_mensal'] = 1 + (df['valor'] / 100)
        fator_acumulado = df['fator_mensal'].prod()
        valor_corrigido = valor_original * fator_acumulado
        
        data_final_str = data_final.strftime('%d/%m/%Y')

        return valor_corrigido, data_final_str

    except KeyError as e:
        raise ValueError(f"ERRO: Os dados de IPCA (da API ou do arquivo) estão mal formatados. Coluna esperada {e} não encontrada.")
    except Exception as e:
        raise ValueError(f"Ocorreu um erro inesperado ao processar os dados do IPCA: {e}")