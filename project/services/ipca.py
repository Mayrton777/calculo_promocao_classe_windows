import requests
import pandas as pd
import json  # <-- Adicionada a importação

def ipca_calculation(valor_original: float, static_ipca_path: str) -> tuple | None:
    """
    Recebe o valor monetario e aplica o calculo
    do IPCA, apartir de 01/08/2013 até a data mais recente.
    Como retorna temos a data utilizada e o valor corrigido.
    
    Tenta buscar dados da API do BCB. Se falhar, usa o arquivo
    JSON estático fornecido em 'static_ipca_path'.
    """
    
    # [CORREÇÃO] A linha abaixo foi removida, pois 'ipca_df' é o 
    # caminho para os dados estáticos de IPCA, e a função não 
    # é um método de classe (não usa 'self').
    # with open(ipca_df, 'r', encoding='utf-8') as file:
    #         self.uf_names = json.load(file)
   
    data_inicial_str = '01/08/2013'
    url_api = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json&dataInicial={data_inicial_str}'
    
    dados = None
    
    try:
        # 1. Tenta buscar os dados da API
        response = requests.get(url_api, timeout=5) # Adiciona um timeout
        response.raise_for_status() # Lança um erro para respostas 4xx ou 5xx
        dados = response.json()
        print("INFO: Usando dados atualizados da API do BCB.")
        
    except requests.exceptions.RequestException as e:
        # 2. Se a API falhar, usa os dados estáticos de fallback
        print(f"AVISO: Falha ao buscar dados da API ({e}). Usando dados estáticos de fallback.")
        try:
            with open(static_ipca_path, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            print(f"INFO: Dados estáticos carregados de '{static_ipca_path}'.")
        except FileNotFoundError:
            print(f"ERRO FATAL: A API falhou E o arquivo estático '{static_ipca_path}' não foi encontrado.")
            return None
        except json.JSONDecodeError:
            print(f"ERRO FATAL: A API falhou E o arquivo estático '{static_ipca_path}' está mal formatado (não é um JSON válido).")
            return None
        except Exception as file_e:
            print(f"ERRO FATAL: A API falhou E ocorreu um erro ao ler o arquivo estático: {file_e}")
            return None

    # Se 'dados' ainda for None (por alguma razão), retorna o erro.
    if dados is None:
        print("ERRO: Nenhum dado de IPCA pôde ser carregado.")
        return None

    try:
        # 3. Processa os dados (sejam da API ou do arquivo estático)
        df = pd.DataFrame(dados)
        
        # Converte e garante que os tipos de dados estão corretos
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
        df['valor'] = pd.to_numeric(df['valor'])
        
        # Garante que o cálculo começa na data correta (o arquivo estático pode ter dados antigos)
        data_inicial = pd.to_datetime(data_inicial_str, format='%d/%m/%Y')
        df = df[df['data'] >= data_inicial].copy()
        
        if df.empty:
            print(f"ERRO: Não há dados de IPCA disponíveis a partir de {data_inicial_str}.")
            return None
            
        data_final = df['data'].max()
        
        # Calculo do fator de correção acumulado
        df['fator_mensal'] = 1 + (df['valor'] / 100)
        fator_acumulado = df['fator_mensal'].prod()
        valor_corrigido = valor_original * fator_acumulado
        
        data_final_str = data_final.strftime('%d/%m/%Y')

        return valor_corrigido, data_final_str

    except KeyError as e:
        print(f"ERRO: Os dados de IPCA (da API ou do arquivo) estão mal formatados. Coluna esperada {e} não encontrada.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao processar os dados do IPCA: {e}")
        return None