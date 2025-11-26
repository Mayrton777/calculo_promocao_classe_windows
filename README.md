# Cálculo de Promoção de Classe de Estações

Este projeto é uma aplicação desktop desenvolvida em Python que automatiza o cálculo do Valor de Promoção de Classe ($\mathbf{V_{pc}}$) para estações de radiodifusão FM. Ele integra **geoprocessamento** (usando dados de setores censitários do IBGE) e lógica regulatória para determinar o valor de outorga, aplicando a correção monetária pelo **IPCA**.

A aplicação segue o padrão Model-View-Controller (MVC) com interface gráfica construída usando `ttkbootstrap` (Tkinter).

## Guia de Instalação e Execução Rápida

Siga os passos abaixo para clonar o repositório e executar a aplicação em seu ambiente local.

### 1. Clonar o Repositório

Use o Git para baixar o projeto para sua máquina local.

```bash
git clone [https://github.com/Mayrton777/calculo_promocao_classe_windows.git](https://github.com/Mayrton777/calculo_promocao_classe_windows.git)
cd calculo_promocao_classe_windows/project
```

### 2. Configurar e Ativar o Ambiente Virtual

É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto.

```bash
# Cria o ambiente virtual
python -m venv env

# Ativa o ambiente virtual (Escolha o comando correto para o seu SO)
# No Windows:
.\env\Scripts\activate

# No Linux/macOS:
source env/bin/activate
```

### 3\. Instalar as Dependências

Instale todas as bibliotecas necessárias listadas no arquivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 4\. Executar a Aplicação

Inicie a aplicação principal, que abrirá a interface gráfica do usuário (GUI).

```bash
python main.py
```

-----

## Estrutura do Projeto

A lógica do projeto está organizada em três pacotes principais (`app/`, `data/`, `services/`), seguindo o padrão MVC.

```text
project/
├── app/                  # Interface Gráfica e Lógica de Controle (MVC)
|   ├── app_controller.py  # Controller: Lógica de validação e orquestração do fluxo.
|   └── app_view.py        # View: Definição da interface gráfica (GUI) com ttkbootstrap.
├── data/                 # Arquivos de Dados Estáticos e Geoespaciais
|   ├── mapa/             # Contém o Shapefile BR_setores_CD2022.shp (setores censitários).
|   ├── ipca.json         # Dados de fallback do IPCA.
|   └── uf_code.json      # Mapeamento de siglas/nomes de UF.
├── services/             # Lógica de Negócios e Geração de Documentos
|   ├── calculation_service.py # Core: Geoprocessamento e cálculo da fórmula Vpc.
|   ├── ipca.py           # Busca e calcula a correção monetária pelo IPCA.
|   ├── create_pdf.py     # Gera o relatório final em PDF (ReportLab).
|   └── creat_pdf_oficio.py # Gera o ofício de cobrança em Word (.docx).
├── config.py             # Constantes, caminhos de arquivo e configurações globais.
├── main.py               # Ponto de entrada da aplicação.
├── main.spec             # Arquivo de especificação para o PyInstaller.
└── runtime_hook.py       # Hook para o PyInstaller (configura PATH para dependências geoespaciais).
```

-----

## Tecnologias Chave

  * **Geoprocessamento**: `geopandas`, `shapely` e `pyogrio` (para manipulação do Shapefile de setores censitários).
  * **Interface**: `ttkbootstrap` (interface moderna baseada em Tkinter).
  * **Relatórios**: `reportlab` (para PDF) e `python-docx` (para Ofício Word).
  * **Cálculos**: `pandas` e `requests` (para busca de índices do Banco Central).
  * **Empacotamento**: `PyInstaller` (para gerar o executável Windows).

## Desenvolvedores

### Mayrton Eduardo
* **contato**: mayrtontrabaho@gmail.com
### Victor Lima