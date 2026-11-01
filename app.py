import streamlit as st
import pandas as pd
import re
import io
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# ==============================================================================
# VISUAL CONFIGURATION
# ==============================================================================
st.set_page_config(
    layout="wide",
    page_title="Monitoramento de feminicídios no Ceará"
)

st.markdown("""
    <style>
        .stApp {
            background: #f7f7f5;
            color: #28312f;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }
        .block-container { max-width: 1280px; padding: 2.5rem 2rem 3rem; }
        h1, h2, h3 { color: #28312f; letter-spacing: -0.025em; text-transform: none; }
        h1 { font-size: 2.15rem; font-weight: 650; }
        h2, h3 { font-weight: 600; }
        [data-testid="stCaptionContainer"] { color: #68716e; }
        section[data-testid="stSidebar"] {
            background: #f0f1ee;
            color: #28312f;
            border-right: 1px solid #e1e4df;
        }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
        section[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] label p,
        section[data-testid="stSidebar"] label span,
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] small {
            color: #28312f !important;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e6e8e4;
            border-radius: 10px;
            padding: 16px 18px;
        }
        div[data-testid="stMetricLabel"] { color: #68716e; }
        div[data-testid="stMetricValue"] { color: #28312f; }
        .stTextArea textarea, .stTextInput input {
            background: #ffffff;
            color: #28312f;
            border: 1px solid #d9ded9;
            border-radius: 8px;
        }
        .stTextArea textarea:focus, .stTextInput input:focus {
            border-color: #8a4b55;
            box-shadow: 0 0 0 1px #8a4b55;
        }
        
        /* Botões Primários (Ações principais) e Downloads */
        div.stButton > button[kind="primary"], div.stDownloadButton > button {
            background: #7d3f49;
            color: #ffffff;
            border: 1px solid #7d3f49;
            border-radius: 8px;
            padding: 0.55rem 1rem;
            font-weight: 600;
            transition: all 120ms ease;
        }
        div.stButton > button[kind="primary"]:hover, div.stDownloadButton > button:hover {
            background: #69343d;
            border-color: #69343d;
            color: #ffffff;
        }
        div.stButton > button[kind="primary"]:focus, div.stDownloadButton > button:focus {
            box-shadow: 0 0 0 2px #f7f7f5, 0 0 0 4px #7d3f49;
        }

        /* Botões Secundários (Ações discretas / de apoio) */
        div.stButton > button[kind="secondary"] {
            background: transparent;
            color: #68716e;
            border: 1px solid #d9ded9;
            border-radius: 8px;
            padding: 0.55rem 1rem;
            font-weight: 500;
            transition: all 120ms ease;
        }
        div.stButton > button[kind="secondary"]:hover {
            border-color: #8a4b55;
            color: #8a4b55;
            background: #fcfcfb;
        }

        .alert-box {
            background: #ffffff;
            border: 1px solid #e6e8e4;
            border-left: 4px solid #8a4b55;
            padding: 22px 24px;
            margin: 12px 0 24px;
            border-radius: 10px;
        }
        .alert-title { color: #713943; font-size: 1.1rem; font-weight: 650; margin-bottom: 12px; }
        .alert-text { color: #454e4b; font-size: 0.98rem; line-height: 1.65; }
        .highlight { color: #713943; font-weight: 650; }
        .index-badge {
            background: #f5ebec;
            color: #713943;
            padding: 7px 11px;
            border-radius: 6px;
            font-size: 0.95rem;
            font-weight: 600;
            display: inline-block;
            margin: 2px 0 15px;
        }
        .top5-container {
            margin-top: 18px;
            padding-top: 14px;
            border-top: 1px solid #e6e8e4;
        }
        .top5-item { font-size: 0.94rem; margin-bottom: 7px; color: #454e4b; }
        .top5-rank { color: #713943; font-weight: 650; width: 30px; display: inline-block; }
        .stDataFrame { border: 1px solid #e1e4df; border-radius: 8px; }
        div[data-testid="stImage"] { display: flex; justify-content: center; }
        hr { border-color: #e1e4df; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# GEOPOLITICAL MAPPING LOGIC (14 IPECE REGIONS)
# ==============================================================================
MAPA_REGIOES = {
    "Cariri": ["Abaiara", "Altaneira", "Antonina do Norte", "Araripe", "Assaré", "Aurora", "Barbalha", "Barro", "Brejo Santo", "Campos Sales", "Caririaçu", "Crato", "Farias Brito", "Granjeiro", "Jardim", "Jati", "Juazeiro do Norte", "Lavras da Mangabeira", "Mauriti", "Milagres", "Missão Velha", "Nova Olinda", "Penaforte", "Porteiras", "Potengi", "Salitre", "Santana do Cariri", "Tarrafas", "Várzea Alegre"],
    "Centro Sul": ["Acopiara", "Baixio", "Cariús", "Catarina", "Cedro", "Icó", "Iguatu", "Ipaumirim", "Jucás", "Orós", "Quixelô", "Saboeiro", "Umari"],
    "Grande Fortaleza": ["Aquiraz", "Cascavel", "Caucaia", "Chorozinho", "Eusébio", "Fortaleza", "Guaiúba", "Horizonte", "Itaitinga", "Maracanaú", "Maranguape", "Pacajus", "Pacatuba", "Paracuru", "Paraipaba", "Pindoretama", "São Gonçalo do Amarante", "São Luís do Curu", "Trairi"],
    "Litoral Leste": ["Aracati", "Beberibe", "Fortim", "Icapuí", "Itaiçaba", "Jaguaruana"],
    "Litoral Norte": ["Acaraú", "Barroquinha", "Bela Cruz", "Camocim", "Chaval", "Cruz", "Granja", "Itarema", "Jijoca de Jericoacoara", "Marco", "Martinópole", "Morrinhos", "Uruoca"],
    "Litoral Oeste / Vale do Curu": ["Amontada", "Apuiarés", "General Sampaio", "Irauçuba", "Itapagé", "Itapipoca", "Miraíma", "Pentecoste", "Tejuçuoca", "Tururu", "Umirim", "Uruburetama"],
    "Maciço de Baturité": ["Acarape", "Aracoiaba", "Aratuba", "Barreira", "Baturité", "Capistrano", "Guaramiranga", "Itapiúna", "Mulungu", "Ocara", "Pacoti", "Palmácia", "Redenção"],
    "Serra da Ibiapaba": ["Carnaubal", "Croatá", "Guaraciaba do Norte", "Ibiapina", "Ipu", "São Benedito", "Tianguá", "Ubajara", "Viçosa do Ceará"],
    "Sertão Central": ["Banabuiú", "Choró", "Deputado Irapuan Pinheiro", "Ibaretama", "Ibicuitinga", "Milhã", "Mombaça", "Pedra Branca", "Piquet Carneiro", "Quixadá", "Quixeramobim", "Senador Pompeu", "Solonópole"],
    "Sertão de Canindé": ["Boa Viagem", "Canindé", "Caridade", "Itatira", "Madalena", "Paramoti"],
    "Sertão de Sobral": ["Alcântaras", "Cariré", "Coreaú", "Forquilha", "Frecheirinha", "Graça", "Groaíras", "Massapê", "Meruoca", "Moraújo", "Mucambo", "Pacujá", "Pires Ferreira", "Reriutaba", "Santana do Acaraú", "Senador Sá", "Sobral", "Varjota"],
    "Sertão dos Crateús": ["Ararendá", "Catunda", "Crateús", "Hidrolândia", "Independência", "Ipaporanga", "Ipueiras", "Monsenhor Tabosa", "Nova Russas", "Novo Oriente", "Poranga", "Santa Quitéria", "Tamboril"],
    "Sertão dos Inhamuns": ["Aiuaba", "Arneiroz", "Parambu", "Quiterianópolis", "Tauá"],
    "Vale do Jaguaribe": ["Alto Santo", "Ereré", "Iracema", "Jaguaretama", "Jaguaribara", "Jaguaribe", "Limoeiro do Norte", "Morada Nova", "Palhano", "Pereiro", "Potiretama", "Quixeré", "Russas", "São João do Jaguaribe", "Tabuleiro do Norte"]
}

TODAS_CIDADES = []
for cidades in MAPA_REGIOES.values():
    TODAS_CIDADES.extend(cidades)
TODAS_CIDADES.sort(key=len, reverse=True)

def mapear_macroregiao(cidade):
    for regiao, cidades in MAPA_REGIOES.items():
        if cidade in cidades:
            return regiao
    return "Não Identificada"

# ==============================================================================
# EXTRACTION LOGIC
# ==============================================================================
class SmartExtractor:
    def __init__(self):
        self.mapa_numeros = {
            'um': 1, 'uma': 1, 'dois': 2, 'duas': 2, 'três': 3, 'quatro': 4, 'cinco': 5, 'seis': 6, 'sete': 7, 'oito': 8, 'nove': 9, 'dez': 10,
            'onze': 11, 'doze': 12, 'treze': 13, 'catorze': 14, 'quinze': 15, 'dezesseis': 16, 'dezessete': 17, 'dezoito': 18, 'dezenove': 19,
            'vinte': 20, 'trinta': 30, 'quarenta': 40, 'cinquenta': 50, 'sessenta': 60, 'setenta': 70, 'oitenta': 80, 'noventa': 90
        }
        self.mapa_meses = {
            'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04', 'maio': '05', 'junho': '06',
            'julho': '07', 'agosto': '08', 'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
        }

        self.regex_data_num = r'(\d{2}[/.]\d{2}[/.]\d{2,4})'
        self.regex_data_ext = r'(\d{1,2})\s+de\s+([a-zA-Zç]+)\s+de\s+(\d{4})'
        self.regex_idade_num = r'(?i)(\d{1,2})\s?anos'
        self.regex_idade_ext = r'(?i)\b([a-z]+(?:\s+e\s+[a-z]+)?)\s+anos\b'
        self.regex_cor = r'(?i)\b(branca|preta|parda|amarela)\b'
        
        self.regras_causa = [
            (r'(ex-?companheiro|marido|ciúmes|separação|medida protetiva|doméstica|terminou)', 'Violência Doméstica'),
            (r'(tráfico|drogas|facção|território|execução|pistolagem|cativeiro|tribunal do crime)', 'Tráfico/Facção'),
            (r'(racismo|transfobia|homofobia|preconceito|ódio|orientação sexual|misoginia)', 'Crime de Ódio/Preconceito'),
            (r'(latrocínio|assalto|bala perdida|roubo)', 'Latrocínio/Violência Urbana')
        ]

    def converter_extenso(self, texto_num):
        try:
            partes = texto_num.lower().split(' e ')
            soma = sum([self.mapa_numeros[p] for p in partes if p in self.mapa_numeros])
            return soma if soma > 0 else None
        except:
            return None

    def processar_texto(self, texto):
        texto_str = str(texto)

        data = "N/A"
        match_dt_num = re.search(self.regex_data_num, texto_str)
        if match_dt_num:
            data = match_dt_num.group(1).replace('.', '/')
        else:
            match_dt_ext = re.search(self.regex_data_ext, texto_str, re.IGNORECASE)
            if match_dt_ext:
                dia = match_dt_ext.group(1).zfill(2)
                mes = self.mapa_meses.get(match_dt_ext.group(2).lower(), '01')
                ano = match_dt_ext.group(3)
                data = f"{dia}/{mes}/{ano}"

        cidade = "Local Desconhecido"
        for cid in TODAS_CIDADES:
            padrao = r'(?<![a-zA-ZÀ-ÿ])' + re.escape(cid) + r'(?![a-zA-ZÀ-ÿ])'
            if re.search(padrao, texto_str, re.IGNORECASE):
                cidade = cid
                break

        idade = None
        match_id_num = re.search(self.regex_idade_num, texto_str)
        if match_id_num:
            idade = int(match_id_num.group(1))
        else:
            match_id_ext = re.search(self.regex_idade_ext, texto_str)
            if match_id_ext:
                idade = self.converter_extenso(match_id_ext.group(1))

        match_cor = re.search(self.regex_cor, texto_str)
        cor = match_cor.group(1).lower() if match_cor else "Não informada"

        causa = "Outros/Não Determinado"
        texto_lower = texto_str.lower()
        for padrao, label in self.regras_causa:
            if re.search(padrao, texto_lower):
                causa = label
                break

        return {
            "DATA": data,
            "LOCALIDADE": cidade,
            "IDADE_ESTIMADA": idade,
            "COR_PELE": cor,
            "CLASSIFICACAO_CAUSA": causa,
            "NOTÍCIA_ORIGINAL": texto_str[:100] + "..."
        }

# ==============================================================================
# MAIN INTERFACE
# ==============================================================================
def main():
    st.title("Monitoramento de feminicídios no Ceará")
    st.caption("Análise de dados extraídos de notícias e relatórios.")

    st.sidebar.markdown("### Fonte dos dados")
    if 'modo_input' not in st.session_state:
        st.session_state['modo_input'] = "ENTRADA MANUAL / VOZ"

    modo_input = st.sidebar.radio(
        "Como deseja inserir os dados?",
        ("ENTRADA MANUAL / VOZ", "UPLOAD DE ARQUIVO (.CSV)"),
        format_func=lambda value: {
            "ENTRADA MANUAL / VOZ": "Entrada manual ou por voz",
            "UPLOAD DE ARQUIVO (.CSV)": "Enviar arquivo CSV",
        }[value],
        key='modo_input',
        label_visibility="collapsed"
    )

    extractor = SmartExtractor()

    if modo_input == "ENTRADA MANUAL / VOZ":
        sample_text = (
            "Fortaleza, 12/03/2024 — 34 anos, parda, relato de ex-companheiro com ciúmes e medida protetiva negada após várias tentativas de polícia.\n"
            "Em 5 de abril de 2024, Sobral registrou ameaça contra uma mulher de 28 anos, branca, motivada por separação, e a família pediu ajuda urgente.\n"
            "Uma jovem de 23 anos, preta, foi morta em Juazeiro do Norte no dia 18 de junho de 2024, em caso que envolve violência doméstica pelo ex-marido.\n"
            "Crato, 30 de janeiro de 2024: mulher de 41 anos, amarela, denunciou transfobia e agressão cometida pelo companheiro que se recusava a aceitar sua orientação.\n"
            "22/02 em Limoeiro do Norte, 30 anos, parda, sofreu ataque após expor denúncias de tráfico e violência na família.\n"
            "Iguatu, 03/07/2024 — 27 anos, preta, relacionamento conturbado terminou com o autor descumprindo medida protetiva.\n"
            "No começo de maio de 2024, Maranguape viu ameaças de ex-companheiro armado contra uma jovem de 19 anos, branca, em episódio marcado por ciúmes obsessivos.\n"
            "27-08-2024 Canindé, 38 anos, parda, caso complexo com quadrilha de tráfico e intimidação explícita à vítima.\n"
            "Quixadá registrou em 15/09/2024 uma ocorrência de crime motivado por orientação sexual e ódio, com vítima de 26 anos, amarela, que relatou preconceito.\n"
            "Viçosa do Ceará, 09/10/2024: 32 anos, preta, desentendimento doméstico virou homicídio durante briga com o parceiro."
        )

        st.subheader("Adicionar notícias")
        st.info("Digite ou cole uma notícia por linha. A transcrição de áudio será adicionada ao texto.")

        if 'texto_manual' not in st.session_state:
            st.session_state['texto_manual'] = ""

        # Sem colunas, empilhando os itens verticalmente
        st.markdown("**Transcrever áudio**")
        audio_text = speech_to_text(language='pt-BR', just_once=True, key='voice_recorder')
        
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        
        if st.button("Carregar notícias de exemplo", key='btn_sample'):
            st.session_state['texto_manual'] = sample_text

        if audio_text:
            if st.session_state['texto_manual']:
                st.session_state['texto_manual'] += "\n" + audio_text
            else:
                st.session_state['texto_manual'] = audio_text

        texto_input = st.text_area("Notícias e relatos", height=200, key='texto_manual')

        if st.button("Analisar notícias", type="primary"):
            if texto_input:
                lista_noticias = [t.strip() for t in texto_input.split('\n') if t.strip()]
                if lista_noticias:
                    resultados = [extractor.processar_texto(noticia) for noticia in lista_noticias]
                    st.session_state['df_resultado'] = pd.DataFrame(resultados)
                    st.success(f"{len(lista_noticias)} notícias identificadas!")
    else:
        uploaded_file = st.sidebar.file_uploader("Selecione um arquivo", type="csv")
        if uploaded_file is not None:
            try:
                df_raw = pd.read_csv(uploaded_file)
                col_name = df_raw.columns[0]
                if 'conteudo_noticia' in df_raw.columns:
                    col_name = 'conteudo_noticia'
                if st.sidebar.button("Processar arquivo", type="primary"):
                    with st.spinner("Analisando os dados..."):
                        dados_extraidos = df_raw[col_name].apply(lambda x: pd.Series(extractor.processar_texto(x)))
                        st.session_state['df_resultado'] = pd.concat([dados_extraidos, df_raw], axis=1)
            except Exception as e:
                st.error(f"Não foi possível processar o arquivo: {e}")

    if 'df_resultado' in st.session_state and not st.session_state['df_resultado'].empty:
        df_show = st.session_state['df_resultado'].copy()

        df_show['DATA_OBJ'] = pd.to_datetime(df_show['DATA'], dayfirst=True, errors='coerce')
        df_show['ANO_MES'] = df_show['DATA_OBJ'].dt.strftime('%Y-%m')
        df_show['MACROREGIAO'] = df_show['LOCALIDADE'].apply(mapear_macroregiao)

        # --- METRICS ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Casos analisados", len(df_show))
        c2.metric("Municípios identificados", df_show['LOCALIDADE'].nunique())
        c3.metric("Idade média", f"{df_show['IDADE_ESTIMADA'].mean():.1f}")
        try:
            c4.metric("Causa mais comum", df_show['CLASSIFICACAO_CAUSA'].mode()[0])
        except:
            pass

        st.markdown("---")

        # ==============================================================================
        # ALERT SYSTEM WITH TOP 5 (ICR RANKING)
        # ==============================================================================
        st.markdown("### Concentração regional")

        regioes_afetadas = df_show[df_show['MACROREGIAO'] != "Não Identificada"]
        if not regioes_afetadas.empty:
            top5_regioes = regioes_afetadas['MACROREGIAO'].value_counts().head(5)
            total_estado = len(regioes_afetadas)

            regiao_critica = top5_regioes.index[0]
            total_critica = top5_regioes.values[0]
            icr_1 = (total_critica / total_estado) * 100
            cidade_critica = df_show[df_show['MACROREGIAO'] == regiao_critica]['LOCALIDADE'].value_counts().index[0]

            html_outras_regioes = ""
            for i in range(1, len(top5_regioes)):
                r_nome = top5_regioes.index[i]
                r_casos = top5_regioes.values[i]
                r_icr = (r_casos / total_estado) * 100
                html_outras_regioes += f"""<div class='top5-item'>
<span class='top5-rank'>#{i+1}</span>
<strong>{r_nome}</strong> &mdash; Índice: <span style='color:#713943;'>{r_icr:.1f}%</span>
<span style='font-size:0.85rem;'>({r_casos} casos)</span>
</div>"""

            st.markdown(f"""
<div class="alert-box">
<div class="alert-title">Região com maior concentração: {regiao_critica}</div>
<div class="index-badge">Índice de concentração regional: {icr_1:.1f}%</div>
<div class="alert-text">
Os dados mostram que <span class="highlight">{total_critica} casos ({icr_1:.1f}%)</span> estão nessa região. O município com mais registros é <span class="highlight">{cidade_critica}</span>.<br><br>
<strong>Possíveis frentes de atenção</strong><br>
- Avaliar a oferta de atendimento especializado em {cidade_critica}.<br>
- Acompanhar os registros e a rede de proteção em {regiao_critica}.
</div>
<div class="top5-container">
<div style="color: #713943; font-weight: 600; margin-bottom: 8px;">Outras regiões com mais registros</div>
{html_outras_regioes}
</div>
</div>
""", unsafe_allow_html=True)
        else:
            st.info("Dados regionais insuficientes para calcular índices de criticidade.")

        st.markdown("---")
        st.markdown("### Visão geral")

        # --- ROW 1: CAUSES AND CITIES ---
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.caption("Casos por causa identificada")
            fig_pie = px.pie(
                df_show,
                names='CLASSIFICACAO_CAUSA',
                hole=0.6,
                color_discrete_sequence=['#7d3f49', '#6f8b80', '#c5a36d', '#a8adaa'],
                template="plotly_white"
            )
            fig_pie.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", font_color="#454e4b")
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_g2:
            st.caption("Municípios com mais registros")
            top_cidades = df_show['LOCALIDADE'].value_counts().head(10).reset_index()
            top_cidades.columns = ['Cidade', 'Ocorrências']
            fig_bar = px.bar(
                top_cidades,
                x='Cidade',
                y='Ocorrências',
                color='Ocorrências',
                color_continuous_scale=['#eadbdd', '#7d3f49'],
                template="plotly_white"
            )
            fig_bar.update_layout(
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font_color="#454e4b",
                xaxis_title='Município',
                yaxis_title='Registros'
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # --- ROW 2: TEMPORAL AND PLANNING REGIONS ---
        col_g3, col_g4 = st.columns(2)
        with col_g3:
            st.caption("Registros ao longo do tempo")
            timeline_df = df_show.groupby('ANO_MES').size().reset_index(name='Quantidade').sort_values('ANO_MES')
            if not timeline_df.empty:
                fig_line = px.area(
                    timeline_df,
                    x='ANO_MES',
                    y='Quantidade',
                    markers=True,
                    color_discrete_sequence=['#6f8b80'],
                    template="plotly_white"
                )
                fig_line.update_layout(
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#ffffff",
                    font_color="#454e4b",
                    xaxis_title='Período',
                    yaxis_title='Quantidade'
                )
                st.plotly_chart(fig_line, use_container_width=True)

        with col_g4:
            st.caption("Registros por região de planejamento")
            regioes_count = df_show['MACROREGIAO'].value_counts().reset_index()
            regioes_count.columns = ['Região de Planejamento', 'Casos']
            fig_macro = px.bar(
                regioes_count,
                x='Casos',
                y='Região de Planejamento',
                orientation='h',
                color='Casos',
                color_continuous_scale=['#eadbdd', '#7d3f49'],
                template="plotly_white"
            )
            fig_macro.update_layout(
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font_color="#454e4b",
                xaxis_title='Casos',
                yaxis_title='Região de Planejamento',
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_macro, use_container_width=True)

        # --- ROW 3: DEMOGRAPHICS ---
        st.markdown("### Perfil das vítimas")
        col_d1, col_d2 = st.columns(2)

        with col_d1:
            st.caption("Cor da pele informada")
            df_cor = df_show['COR_PELE'].fillna('Não informada').value_counts().reset_index()
            df_cor.columns = ['Cor', 'Total']
            fig_skin = px.bar(
                df_cor,
                x='Total',
                y='Cor',
                orientation='h',
                color='Total',
                color_continuous_scale=['#e2e8e4', '#71847a'],
                template="plotly_white"
            )
            fig_skin.update_layout(
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font_color="#454e4b",
                xaxis_title='Total',
                yaxis_title='Cor de pele'
            )
            st.plotly_chart(fig_skin, use_container_width=True)

        with col_d2:
            st.caption("Faixa etária")
            df_idade = df_show.dropna(subset=['IDADE_ESTIMADA'])
            if not df_idade.empty:
                fig_hist = px.histogram(
                    df_idade,
                    x="IDADE_ESTIMADA",
                    nbins=15,
                    color_discrete_sequence=['#7d3f49'],
                    template="plotly_white"
                )
                fig_hist.update_layout(
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#ffffff",
                    font_color="#454e4b",
                    bargap=0.1,
                    xaxis_title='Idade Estimada',
                    yaxis_title='Contagem'
                )
                st.plotly_chart(fig_hist, use_container_width=True)

        # --- TABLE ---
        st.markdown("### Registros analisados")
        df_tabela = df_show[[
            'DATA', 'LOCALIDADE', 'MACROREGIAO', 'IDADE_ESTIMADA',
            'COR_PELE', 'CLASSIFICACAO_CAUSA', 'NOTÍCIA_ORIGINAL'
        ]].copy()

        df_tabela.columns = [
            'Data', 'Localidade', 'Região de Planejamento', 'Idade Estimada',
            'Cor da Pele', 'Classificação da Causa', 'Notícia Original'
        ]

        st.dataframe(df_tabela, use_container_width=True, height=300)

        # --- DOWNLOADS ---
        col_dl1, col_dl2 = st.columns(2)

        csv = df_show.to_csv(index=False).encode('utf-8-sig')
        col_dl1.download_button("Baixar arquivo CSV", csv, 'dados_feminicidio.csv', 'text/csv')

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_show.to_excel(writer, index=False)
        buffer.seek(0)

        col_dl2.download_button(
            "Baixar arquivo Excel",
            buffer,
            'dados_feminicidio.xlsx',
            'application/vnd.ms-excel'
        )

    st.markdown("---")
    _, apoio, _ = st.columns([1, 2, 1])
    with apoio:
        st.markdown(
            "<h3 style='text-align: center; color: #68716e; font-size: 14px; margin-bottom: 10px;'>Apoio</h3>",
            unsafe_allow_html=True
        )
        st.image("https://imgur.com/xLFPmmy.png", width=300)

if __name__ == "__main__":
    main()
