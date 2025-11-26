# Guia de Download de Dados Geoespaciais (Setores Censitários)

## Fonte Oficial dos Dados

A principal e mais confiável fonte para obter os arquivos de mapas (Shapefiles) dos setores censitários do Brasil é o **Instituto Brasileiro de Geografia e Estatística (IBGE)**.

O IBGE disponibiliza a **Malha Digital dos Setores Censitários** e a **Base Territorial** referente aos seus censos (Censo Demográfico e Contagem Populacional).

---

## Localização dos Arquivos

Os dados geoespaciais são geralmente encontrados na área de **Geociências** ou **Base Territorial** do site do IBGE.

### Passo a Passo para Download:

1.  **Acesse o site do IBGE.**
2.  **Busque por Malhas e Bases Geográficas.**
3.  **Selecione o ano de referência desejado.** Os dados mais recentes geralmente são os do último Censo Demográfico.
    * **Referência Recomendada:** Os mais recentes disponíveis.
4.  **Localize a seção "Malha de Setores Censitários".**
5.  **Baixe o arquivo compactado (.ZIP ou .7Z)** que contém os Shapefiles (`.shp`, `.shx`, `.dbf`, `.prj`, etc.) para o Brasil.

### Endereços Típicos de Acesso Rápido

Embora os URLs exatos mudem com o tempo e novas publicações, os dados costumam estar nos seguintes caminhos dentro do site do IBGE:

* **IBGE > Geociências > Organização do Território > Malhas e Estruturas Territoriais**
* **Malhas Digitais e Bases Cartográficas**

---

## Dica para o Projeto

Para o projeto de cálculo de promoção de classe, que utiliza o arquivo `BR_setores_CD2022.shp`, certifique-se de baixar a malha que inclua as informações necessárias, como o **código do município (`CD_MUN`)** e os dados populacionais (`v0001` ou coluna equivalente) para realizar o geoprocessamento e o cálculo de $\mathbf{V_{pc}}$ conforme a lógica do arquivo `calculation_service.py`.

* **Formato do Arquivo:** Você precisará do conjunto de arquivos **Shapefile (.shp)**, que deve ser descompactado na sua pasta `project/data/mapa/`.

**Atenção:** Como o arquivo é muito grande (dados de todo o Brasil), ele costuma exceder o limite de 100 MB para uploads diretos no GitHub e deve ser gerenciado com ferramentas externas.