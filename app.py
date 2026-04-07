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
    page_title="Feminicide Monitoring System",
    page_icon="📊"
)

st.markdown("""
    <style>
        .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Courier New', Courier, monospace; }
        h1, h2, h3 { color: #ff0055; text-transform: uppercase; letter-spacing: 2px; text-shadow: 0 0 10px #ff0055; }
        .stDataFrame { border: 1px solid #333; }
        .stTextArea textarea { background-color: #0a0a0a; color: #00ffcc; border: 1px solid #333; }
        div.stButton > button { background-color: #000; color: #ff0055; border: 1px solid #ff0055; border-radius: 0px; padding: 10px 24px; text-transform: uppercase; font-weight: bold; width: 100%; }
        div.stButton > button:hover { background-color: #ff0055; color: #fff; box-shadow: 0 0 20px #ff0055; }
        section[data-testid="stSidebar"] { background-color: #080808; border-right: 1px solid #222; }
        div[data-testid="stMetricValue"] { color: #00ffcc; text-shadow: 0 0 5px #00ffcc; }

        /* Public policy alert styling */
        .alert-box {
            background-color: #1a0008;
            border: 1px solid #ff0055;
            border-left: 8px solid #ff0055;
            padding: 20px;
            margin-bottom: 25px;
            border-radius: 4px;
        }
        .alert-title { color: #ff0055; font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; display: flex; align-items: center;}
        .alert-text { color: #e0e0e0; font-size: 1rem; line-height: 1.5;}
        .highlight { color: #00ffcc; font-weight: bold; }
        .index-badge {
            background-color: #ff0055;
            color: #ffffff;
            padding: 8px 15px;
            border-radius: 3px;
            font-size: 1.2rem;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 15px;
            box-shadow: 0 0 10px #ff0055;
        }
        .top5-container {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px dashed rgba(255, 0, 85, 0.4);
        }
        .top5-item {
            font-size: 0.95rem;
            margin-bottom: 5px;
            color: #ccc;
        }
        .top5-rank { color: #00ffcc; font-weight: bold; width: 30px; display: inline-block; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# GEOPOLITICAL MAPPING LOGIC (14 IPECE REGIONS)
# ==============================================================================
def mapear_macroregiao(cidade):
    mapa_regioes = {
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

    for regiao, cidades in mapa_regioes.items():
        if cidade in cidades:
            return regiao

    return "Not Identified"

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

        self.regex_cidade = r'(?:em|no|na|município de|cidade de|região de|LOCAL:|Comarca de)\s+([A-ZÁ-Ü][a-zbxà-ü]+(?:\s(?:do|da|de|e)\s[A-ZÁ-Ü][a-zà-ü]+)*(?:\s[A-ZÁ-Ü][a-zà-ü]+)?)'
        self.regex_data_num = r'(\d{2}[/.]\d{2}[/.]\d{2,4})'
        self.regex_data_ext = r'(\d{1,2})\s+de\s+([a-zA-Zç]+)\s+de\s+(\d{4})'
        self.regex_idade_num = r'(?i)(\d{1,2})\s?anos'
        self.regex_idade_ext = r'(?i)\b([a-z]+(?:\s+e\s+[a-z]+)?)\s+anos\b'
        self.regex_cor = r'(?i)\b(branca|preta|parda|amarela)\b'
        self.regras_causa = [
            (r'(ex-?companheiro|marido|ciúmes|separação|medida protetiva|doméstica|terminou)', 'Domestic Violence'),
            (r'(tráfico|drogas|facção|território|execução|pistolagem|cativeiro|tribunal do crime)', 'Gang/Drug Trafficking'),
            (r'(racismo|transfobia|homofobia|preconceito|ódio|orientação sexual|misoginia)', 'Bias/Hate Crime'),
            (r'(latrocínio|assalto|bala perdida|roubo)', 'Robbery/Urban Violence')
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

        cidade = "Unknown Location"
        match_cid = re.search(self.regex_cidade, texto_str)
        if match_cid:
            cand = match_cid.group(1).strip()
            if cand.lower() not in [
                'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho',
                'agosto', 'setembro', 'outubro', 'novembro', 'dezembro',
                'polícia', 'pefoce', 'dhpp'
            ]:
                cidade = cand

        idade = None
        match_id_num = re.search(self.regex_idade_num, texto_str)
        if match_id_num:
            idade = int(match_id_num.group(1))
        else:
            match_id_ext = re.search(self.regex_idade_ext, texto_str)
            if match_id_ext:
                idade = self.converter_extenso(match_id_ext.group(1))

        match_cor = re.search(self.regex_cor, texto_str)
        cor = match_cor.group(1).lower() if match_cor else "Not informed"

        causa = "Other/Undetermined"
        texto_lower = texto_str.lower()
        for padrao, label in self.regras_causa:
            if re.search(padrao, texto_lower):
                causa = label
                break

        return {
            "DATE": data,
            "LOCATION": cidade,
            "ESTIMATED_AGE": idade,
            "SKIN_COLOR": cor,
            "CAUSE_CLASSIFICATION": causa,
            "ORIGINAL_NEWS": texto_str[:100] + "..."
        }

# ==============================================================================
# MAIN INTERFACE
# ==============================================================================
def main():
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.title("Feminicide Monitoring System // CE")
        st.caption("Developed by: Yanna Queiroz | Advisors: Prof. Helyson Braz, Profa. Thyana Vicente and Profa. Roberta Jeane")

    st.sidebar.markdown("### Generate News By:")
    modo_input = st.sidebar.radio(
        "Data source:",
        ("FILE UPLOAD (.CSV)", "MANUAL INPUT / VOICE"),
        label_visibility="collapsed"
    )
    extractor = SmartExtractor()

    if modo_input == "FILE UPLOAD (.CSV)":
        uploaded_file = st.sidebar.file_uploader("Upload Raw Dataset", type="csv")
        if uploaded_file is not None:
            try:
                df_raw = pd.read_csv(uploaded_file)
                col_name = df_raw.columns[0]
                if 'conteudo_noticia' in df_raw.columns:
                    col_name = 'conteudo_noticia'
                if st.sidebar.button("START BATCH PROCESSING"):
                    with st.spinner("ANALYZING SEMANTIC AND GEOPOLITICAL PATTERNS..."):
                        dados_extraidos = df_raw[col_name].apply(lambda x: pd.Series(extractor.processar_texto(x)))
                        st.session_state['df_resultado'] = pd.concat([dados_extraidos, df_raw], axis=1)
            except Exception as e:
                st.error(f"ERROR: {e}")
    else:
        st.subheader("UNITARY AND MULTI-ENTRY ANALYSIS")
        st.info("Use ENTER to separate multiple news items. Audio will add new lines automatically.")

        if 'texto_manual' not in st.session_state:
            st.session_state['texto_manual'] = ""

        c_mic, c_void = st.columns([1, 4])
        with c_mic:
            st.markdown("**RECORD AUDIO:**")
            audio_text = speech_to_text(language='pt-BR', just_once=True, key='voice_recorder')

        if audio_text:
            if st.session_state['texto_manual']:
                st.session_state['texto_manual'] += "\n" + audio_text
            else:
                st.session_state['texto_manual'] = audio_text

        texto_input = st.text_area("Insert reports (separated by ENTER):", height=200, key='texto_manual')

        if st.button("CLASSIFY DATA"):
            if texto_input:
                lista_noticias = [t.strip() for t in texto_input.split('\n') if t.strip()]
                if lista_noticias:
                    resultados = [extractor.processar_texto(noticia) for noticia in lista_noticias]
                    st.session_state['df_resultado'] = pd.DataFrame(resultados)
                    st.success(f"{len(lista_noticias)} NEWS ITEMS IDENTIFIED!")

    if 'df_resultado' in st.session_state and not st.session_state['df_resultado'].empty:
        df_show = st.session_state['df_resultado'].copy()

        # Keep the data itself in Portuguese / original context, but translate the interface.
        if 'DATA' not in df_show.columns and 'DATE' in df_show.columns:
            df_show['DATA'] = df_show['DATE']
        if 'LOCALIDADE' not in df_show.columns and 'LOCATION' in df_show.columns:
            df_show['LOCALIDADE'] = df_show['LOCATION']
        if 'IDADE_ESTIMADA' not in df_show.columns and 'ESTIMATED_AGE' in df_show.columns:
            df_show['IDADE_ESTIMADA'] = df_show['ESTIMATED_AGE']
        if 'COR_PELE' not in df_show.columns and 'SKIN_COLOR' in df_show.columns:
            df_show['COR_PELE'] = df_show['SKIN_COLOR']
        if 'CLASSIFICACAO_CAUSA' not in df_show.columns and 'CAUSE_CLASSIFICATION' in df_show.columns:
            df_show['CLASSIFICACAO_CAUSA'] = df_show['CAUSE_CLASSIFICATION']
        if 'NOTÍCIA_ORIGINAL' not in df_show.columns and 'ORIGINAL_NEWS' in df_show.columns:
            df_show['NOTÍCIA_ORIGINAL'] = df_show['ORIGINAL_NEWS']

        df_show['DATA_OBJ'] = pd.to_datetime(df_show['DATA'], dayfirst=True, errors='coerce')
        df_show['ANO_MES'] = df_show['DATA_OBJ'].dt.strftime('%Y-%m')
        df_show['MACROREGIAO'] = df_show['LOCALIDADE'].apply(mapear_macroregiao)

        # --- METRICS ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("CASES ANALYZED", len(df_show))
        c2.metric("AFFECTED MUNICIPALITIES", df_show['LOCALIDADE'].nunique())
        c3.metric("AVERAGE AGE", f"{df_show['IDADE_ESTIMADA'].mean():.1f}")
        try:
            c4.metric("MOST COMMON CAUSE", df_show['CLASSIFICACAO_CAUSA'].mode()[0])
        except:
            pass

        st.markdown("---")

        # ==============================================================================
        # ALERT SYSTEM WITH TOP 5 (ICR RANKING)
        # ==============================================================================
        st.markdown("### PUBLIC POLICY ALERT SYSTEM")

        regioes_afetadas = df_show[df_show['MACROREGIAO'] != "Not Identified"]
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
<strong>{r_nome}</strong> &mdash; ICR: <span style='color:#00ffcc;'>{r_icr:.1f}%</span>
<span style='font-size:0.85rem;'>({r_casos} cases)</span>
</div>"""

            st.markdown(f"""
<div class="alert-box">
<div class="alert-title">⚠️ HIGH-CRITICALITY ZONE DETECTED: {regiao_critica.upper()}</div>
<div class="index-badge">REGIONAL CONCENTRATION INDEX (ICR): {icr_1:.1f}%</div>
<div class="alert-text">
Monitoring identified that more than {int(icr_1)}% of all analyzed cases in the state are concentrated in this planning region (<span class="highlight">{total_critica} occurrences</span>). The main vulnerability hotspot is the municipality of <span class="highlight">{cidade_critica}</span>.<br><br>
<strong>INTERVENTION GUIDELINES (PRIMARY FOCUS):</strong><br>
• Installation/expansion of a <i>Women’s Police Station (DDM) or Women’s House</i> in {cidade_critica}.<br>
• Tactical strengthening of the <i>Maria da Penha Patrol</i> throughout {regiao_critica}.
</div>
<div class="top5-container">
<div style="color: #ff0055; font-weight: bold; margin-bottom: 8px;">RISK MONITORING: TOP 5 REGIONS</div>
{html_outras_regioes}
</div>
</div>
""", unsafe_allow_html=True)
        else:
            st.info("Insufficient regional data to calculate criticality indices.")

        st.markdown("---")
        st.markdown("### ANALYTICAL DASHBOARD")

        # --- ROW 1: CAUSES AND CITIES ---
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.caption("DISTRIBUTION BY CAUSE / MOTIVE")
            fig_pie = px.pie(
                df_show,
                names='CLASSIFICACAO_CAUSA',
                hole=0.6,
                color_discrete_sequence=['#ff0055', '#00ffcc', '#ffffff', '#444444'],
                template="plotly_dark"
            )
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_g2:
            st.caption("TOP 10 CITIES WITH THE MOST OCCURRENCES")
            top_cidades = df_show['LOCALIDADE'].value_counts().head(10).reset_index()
            top_cidades.columns = ['City', 'Cases']
            fig_bar = px.bar(
                top_cidades,
                x='City',
                y='Cases',
                color='Cases',
                color_continuous_scale=['#440022', '#ff0055'],
                template="plotly_dark"
            )
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_bar, use_container_width=True)

        # --- ROW 2: TEMPORAL AND PLANNING REGIONS ---
        col_g3, col_g4 = st.columns(2)
        with col_g3:
            st.caption("TIME EVOLUTION (MONTH/YEAR)")
            timeline_df = df_show.groupby('ANO_MES').size().reset_index(name='QUANTITY').sort_values('ANO_MES')
            if not timeline_df.empty:
                fig_line = px.area(
                    timeline_df,
                    x='ANO_MES',
                    y='QUANTITY',
                    markers=True,
                    color_discrete_sequence=['#00ffcc'],
                    template="plotly_dark"
                )
                fig_line.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis_title=None
                )
                st.plotly_chart(fig_line, use_container_width=True)

        with col_g4:
            st.caption("INCIDENCE BY PLANNING REGION (IPECE)")
            regioes_count = df_show['MACROREGIAO'].value_counts().reset_index()
            regioes_count.columns = ['Planning Region', 'Cases']
            fig_macro = px.bar(
                regioes_count,
                x='Cases',
                y='Planning Region',
                orientation='h',
                color='Cases',
                color_continuous_scale=['#440022', '#ff0055'],
                template="plotly_dark"
            )
            fig_macro.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_macro, use_container_width=True)

        # --- ROW 3: DEMOGRAPHICS ---
        st.markdown("### VICTIM PROFILE")
        col_d1, col_d2 = st.columns(2)

        with col_d1:
            st.caption("IDENTIFIED SKIN COLOR")
            df_cor = df_show['COR_PELE'].fillna('Not informed').value_counts().reset_index()
            df_cor.columns = ['Color', 'Total']
            fig_skin = px.bar(
                df_cor,
                x='Total',
                y='Color',
                orientation='h',
                color='Total',
                color_continuous_scale=['#333333', '#e0e0e0'],
                template="plotly_dark"
            )
            fig_skin.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_skin, use_container_width=True)

        with col_d2:
            st.caption("AGE DISTRIBUTION")
            df_idade = df_show.dropna(subset=['IDADE_ESTIMADA'])
            if not df_idade.empty:
                fig_hist = px.histogram(
                    df_idade,
                    x="IDADE_ESTIMADA",
                    nbins=15,
                    color_discrete_sequence=['#ff0055'],
                    template="plotly_dark"
                )
                fig_hist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", bargap=0.1)
                st.plotly_chart(fig_hist, use_container_width=True)

        # --- TABLE ---
        st.markdown("### RAW DATA")
        df_tabela = df_show[[
            'DATA', 'LOCALIDADE', 'MACROREGIAO', 'IDADE_ESTIMADA',
            'COR_PELE', 'CLASSIFICACAO_CAUSA', 'NOTÍCIA_ORIGINAL'
        ]].copy()

        df_tabela.columns = [
            'Date', 'Location', 'Planning Region', 'Estimated Age',
            'Skin Color', 'Cause Classification', 'Original News'
        ]

        st.dataframe(df_tabela, use_container_width=True, height=300)

        # --- DOWNLOADS ---
        col_dl1, col_dl2 = st.columns(2)

        csv = df_show.to_csv(index=False).encode('utf-8-sig')
        col_dl1.download_button("DOWNLOAD .CSV", csv, 'femicide_data.csv', 'text/csv')

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_show.to_excel(writer, index=False)
        buffer.seek(0)

        col_dl2.download_button(
            "DOWNLOAD .XLSX",
            buffer,
            'femicide_data.xlsx',
            'application/vnd.ms-excel'
        )

    st.markdown("---")
    col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
    with col_p2:
        st.markdown(
            "<h3 style='text-align: center; color: #444; font-size: 14px; margin-bottom: 10px;'>SUPPORT AND SPONSORS</h3>",
            unsafe_allow_html=True
        )
        st.image("https://imgur.com/xLFPmmy.png", use_container_width=True)

if __name__ == "__main__":
    main()
