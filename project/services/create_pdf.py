import json
import locale
import os
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    """
    Se falhar, busca o nome do locale sem o '.UTF-8'
    """
    locale.setlocale(locale.LC_ALL, 'pt_BR')


def create_relatorio(path_uf: Path, file_path: str, data: dict):
    """
    Gera um PDF com os dados da estação e a imagem fornecida

    Args:
        path_uf (Path): Caminho do arquivo UF.
        file_path (str): Caminho do arquivo PDF a ser gerado.
        data (dict): Um dicionário contendo os dados da estação.
    """
 
    with open(path_uf, 'r', encoding='utf-8') as file:
        sigla_para_nome = json.load(file)

    name_to_abbreviation = {v.strip(): k.strip() for k, v in sigla_para_nome.items()}
    
    # ------------------------------------------------
    # Formantando as variaves
    dmax = data['dmax']
    pref = data['pref']
    valor_ab = data['valor_ab']
    valor_bc = data['valor_bc']
    ptot = data['ptot']
    vpc = data['vpc']
    ipca = data['ipca']
    map_path = data['caminho_mapa_temp']
    
    dmax_normalized = locale.format_string("%.1f", float(dmax), grouping=True)
    pref_normalized = locale.format_string("%d", int(pref), grouping=True)
    valor_ab_normalized = locale.format_string("%.2f", float(valor_ab), grouping=True)
    valor_bc_normalized = locale.format_string("%.2f", float(valor_bc), grouping=True)
    ptot_normalized = locale.format_string("%d", int(ptot), grouping=True)
    vpc_normalized = locale.format_string("%.2f", float(vpc), grouping=True)
    ipca_normalized = locale.format_string("%.2f", float(ipca), grouping=True)
    # ------------------------------------------------

    doc = SimpleDocTemplate(file_path, pagesize=letter)
    story = []
    
    # ------------------------------------------------
    # Configurações de estilo
    styles = getSampleStyleSheet()

    styles['Title'].fontSize = 18
    styles['Title'].fontName = 'Helvetica-Bold'
    styles['Title'].alignment = 1

    styles['Heading1'].fontSize = 16
    styles['Heading1'].fontName = 'Helvetica-Bold'
    styles['Heading1'].leading = 22
    styles['Heading1'].alignment = 0
    styles['Heading1'].spaceBefore = 20
    styles['Heading1'].spaceAfter = 10

    styles['Normal'].alignment = 4
    styles['Normal'].fontSize = 10
    styles['Normal'].leading = 14
    styles['Normal'].firstLineIndent = 12

    styles.add(ParagraphStyle(
        name='Text_img',
        alignment=1,
        fontSize=8,
        leading=14
    ))

    styles.add(ParagraphStyle(
        name='Text_2',
        alignment=4,
        fontSize=10,
        leading=18
    ))

    styles.add(ParagraphStyle(
        name='SubTitle', 
        fontSize=12, 
        leading=14, 
        spaceBefore=0,
        spaceAfter=5
    ))
    
    styles.add(ParagraphStyle(
        name='Data',
        fontSize=12,
        leading=14,
        spaceBefore=0,
        spaceAfter=0
    ))

    # ------------------------------------------------
    
    # ------------------- Página 1 -------------------
    
    # Título do documento
    story.append(Paragraph("Cálculo do Valor de Promoção de Classe", styles['Title']))
    story.append(Paragraph("com Mudança de Grupo de Enquadramento", styles['Title']))
    story.append(Spacer(1, 0.5 * inch))
    
    # Tabel com dados do processo.
    data_process = [
        ["Processo:", data['numero_processo']],
        ["Serviço:", data['servico']],
        ["Entidade:", data['entidade']],
        ["Finalidade:", data['finalidade']],
        ["Consulta Pública:", data['consulta_publica']],
    ]

    # Estilo para formatação da tabela
    table_process = Table(data_process, colWidths=[None, None])
    table_process.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('LINEABOVE', (0,0), (-1,0), 1, colors.black),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.black),
    ]))

    story.append(table_process)
    story.append(Spacer(1, 0.2 * inch))

    # Seção 1
    story.append(Paragraph("<b>1 Dados sobre a alteração de canal</b>", styles['Heading1']))
    story.append(Spacer(1, 0.2 * inch))

    # Estrutura dos dados da tabela.
    modification_datas = [
        ["", "Situação Atual", "Situação Proposta"],
        ["Município", f"{data['municipio_atual']}/{data['uf_atual']}", f"{data['municipio_proposto']}/{data['uf_proposta']}"],
        ["Canal", f"{data['canal_atual']}", f"{data['canal_proposto']}"],
        ["Classe", f"{data['classe_atual']}", f"{data['classe_proposta']}"],
        ["Grupo", f"{data['grupo_atual']}", f"{data['grupo_proposto']}"],
        ["Latitude", f"{data['latitude_atual']}", f"{data['latitude_proposta']}"],
        ["Longitude", f"{data['longitude_atual']}", f"{data['longitude_proposta']}"]
    ]

    # Estilo para formatação da tabela
    modification_table = Table(modification_datas, colWidths=[None, None])
    modification_table.setStyle(TableStyle([
        ('GRID', (1,0), (-1,0), 1, colors.black),
        ('GRID', (0,1), (-1,-1), 1, colors.black),
        ('BACKGROUND', (1,0), (-1,0), colors.lightgrey),
        ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),

    ]))
    story.append(modification_table)
    story.append(Spacer(1, 0.2 * inch))
    
    # Seção 2
    story.append(Paragraph("<b>2 Municípios atingidos pelo contorno protegido</b>", styles['Heading1']))
    story.append(Paragraph(
    'Conforme o art. 34 da <a href="https://relatorios-secoe.mcom.gov.br/gm/">Portaria GM/MCom nº 1/2023</a>, nos casos em que o contorno protegido, resultante da alteração das características técnicas pretendidas, atinge a zona urbana onde estão localizadas as sedes de mais de um município, o valor a ser pago será calculado com base nos preços mínimos de outorga de todos os municípios atendidos.', styles['Normal']))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(
        "Na figura a seguir, os polígonos em laranja representam as áreas urbanas das sedes dos "
        "municípios. Esses polígonos ficam vermelhos quando são atingidos pelo contorno protegido "
        "do canal (circunferência em vermelho). Em seguida, são listados os municípios cujas áreas "
        "urbanas são atingidas pelo contorno protegido da classe proposta.", styles['Normal']))
    story.append(Spacer(1, 0.1 * inch))

    # ------------------- Página 2 -------------------
    # Adiciona imagem do mapa
    try:
        story.append(Image(map_path, width=6.5*inch, height=5*inch))
    except FileNotFoundError:
        story.append(Paragraph("<i>(Imagem do mapa não encontrada)</i>", styles['Normal']))

    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Figura 1: Municípios com áreas urbanas atingidas pelo contorno protegido da classe.", styles['Text_img']))
    story.append(Spacer(1, 0.3 * inch))
    
    # Tabela de municípios
    municipalities = [
        ["UF", "Município", "População"]
    ]

    # Processa cada string e adiciona à tabela
    for item in data['municipios_afetados']:
        parts = item.split('/')
        full_state_name = parts[0]
        municipality = parts[1]
        population = parts[2]
        
        populacao_formatado = locale.format_string("%d", int(population), grouping=True)
        
        # Converte o nome completo do estado para a sigla
        uf_sigla = name_to_abbreviation.get(full_state_name, full_state_name)
        
        # Adiciona a nova linha à sua tabela
        municipalities.append([uf_sigla, municipality, populacao_formatado])
    
    # Estilo para formatação da tabela
    table_municipalities = Table(municipalities, colWidths=[None, None])
    table_municipalities.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
    ]))
    story.append(table_municipalities)
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Tabela 1: Municípios", styles['Text_img']))
    story.append(PageBreak())

    # ------------------- Página 2 -------------------
    
    # Seção 3
    story.append(Paragraph("<b>3 Cálculo do valor da promoção de classe</b>", styles['Heading1']))
    # Dados para a tabela de cálculo
    data_calculation_table = [
        ["Item", "Descrição", "Valor"],
        ["1", "Tempo para atingir a classe proposta", Paragraph(f"T<sub>cp</sub> = {data['tcp']} anos", styles['Text_img'])],
        ["2", "Distância máxima ao contorno protegido", Paragraph(f"d<sub>max</sub> = {dmax_normalized} km", styles['Text_img'])],
        ["3", "Município de referência", f"{data['municipio_referencia']}"],
        ["4", "População do município de referência", Paragraph(f"P<sub>ref</sub> = {pref_normalized}", styles['Text_img'])],
        ["5", "Valor de referência de A para B", Paragraph(f"V<sub>AB</sub> = R$ {valor_ab_normalized}", styles['Text_img'])],
        ["6", "Valor de referência de B para C", Paragraph(f"V<sub>BC</sub> = R$ {valor_bc_normalized}", styles['Text_img'])],
        ["7", "População total dos municípios cobertos", Paragraph(f"P<sub>tot</sub> = {ptot_normalized}", styles['Text_img'])]
    ]

    # Estilo para formatação da tabela
    calculation_table = Table(data_calculation_table, colWidths=[None, None])
    calculation_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('LINEABOVE', (0,0), (-1,0), 1, colors.black),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
    ]))
    story.append(calculation_table)
    story.append(Spacer(1, 0.2 * inch))

    # Parágrafo 01
    story.append(Paragraph('O valor de referência a ser pago pelas concessionárias, permissionárias e autorizadas dos Serviços de Radiodifusão Sonora em FM, em decorrência da promoção de classe de canal, conforme o art. 33, § 1º, é o estabelecido na tabela do <a href="https://relatorios-secoe.mcom.gov.br/gm/#544530">Anexo XXX da Portaria GM/MCom n° 1/2023</a>. Se o aumento de potência ocorrer no município utilizado para o cálculo do valor de referência, o valor a ser pago será o constante dessa tabela.', styles['Normal']))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph('No entanto, conforme os artigos 33 e 34 da <a href="https://relatorios-secoe.mcom.gov.br/gm/">Portaria GM/MCom nº 1/2023</a>, se o aumento de potência ocorrer em um município diferente daquele utilizado para o cálculo do valor de referência, o valor a ser pago pela promoção de classe será proporcional à população total dos municípios cobertos pelo novo contorno protegido:', styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))
    # Fórmula matemática 01
    formula_text = "V<sub>pc</sub> = (P<sub>tot</sub> / P<sub>ref</sub>) (V<sub>AB</sub> + V<sub>BC</sub>)(1 + T<sub>cp</sub> / 10)"
    story.append(Paragraph(formula_text, styles['Text_img']))
    story.append(Spacer(1, 0.2 * inch))
    # Parágrafo 02
    story.append(Paragraph("onde V<sub>AB</sub> é o valor de referência da mudança do grupo de enquadramento A para o B, V<sub>BC</sub> é o valor de referência da mudança do grupo de enquadramento B para o C, P<sub>ref</sub> é a população residente do município de referência, P<sub>tot</sub> é a população residente total dos municípios cujas zonas urbanas das cidades são atingidas pelo contorno protegido da classe do canal, na situação proposta, e T<sub>cp</sub> é o tempo, em anos, que a entidade levaria para atingir a classe pretendida de maneira gradual.", styles['Text_2']))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Substituindo os valores, tem-se", styles['Normal']))
    story.append(Spacer(1, 0.1 * inch))
    # Fórmula matemática 02
    story.append(Paragraph(f"V<sub>pc</sub> = ({ptot_normalized} / {pref_normalized})({valor_ab_normalized} + {valor_bc_normalized})(1 + ({data['tcp']} / 10))", styles['Normal']))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(f"V<sub>pc</sub> = {vpc_normalized}", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))
    # Parágrafo 03
    story.append(Paragraph(f"Conforme o Ofício nº 35528/2023/MCom, de 01/12/2023, solicitou-se à Anatel que aplicasse a correção monetária pelo IPCA, desde 01/08/2013 até a data de emissão do boleto ({data['data_ipca']}), aos valores decorrentes da alteração de características técnicas que resultem em aumento de potência. Utilizando a calculadora de IPCA fornecida pelo Banco Central, o valor atualizado para a promoção de classe foi calculado em R$ {ipca_normalized}.", styles['Normal']))
    story.append(Paragraph(f"Portanto, o valor a ser cobrado pela promoção de classe é <b>R$ {ipca_normalized}</b>.", styles['Normal']))
    
    try:
        doc.build(story)
    finally:
        if os.path.exists(map_path):
            try:
                os.remove(map_path)
            except OSError as e:
                print(f"AVISO: Não foi possível excluir o arquivo temporário '{map_path}': {e}")
        else:
            print(f"AVISO: Mapa temporário '{map_path}' não encontrado para exclusão.")
