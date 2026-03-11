import streamlit as st
import pandas as pd
import re
import io
import plotly.express as px
from streamlit_mic_recorder import speech_to_text

# ==============================================================================
# CONFIGURAÇÃO VISUAL FUTURISTA
# ==============================================================================
st.set_page_config(layout="wide", page_title="Sistema de Monitoramento de Feminicídios", page_icon="📊")

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

        /* Estilo do Alerta de Políticas Públicas */
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
# LÓGICA DE MAPEAMENTO GEOPOLÍTICO (14 REGIÕES DO IPECE)
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

    return "Não Identificada"

# ==============================================================================
# LÓGICA DE EXTRAÇÃO
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
            (r'(ex-?companheiro|marido|ciúmes|separação|medida protetiva|doméstica|terminou)', 'Violência Doméstica'),
            (r'(tráfico|drogas|facção|território|execução|pistolagem|cativeiro|tribunal do crime)', 'Facção/Tráfico'),
            (r'(racismo|transfobia|homofobia|preconceito|ódio|orientação sexual|misoginia)', 'Preconceito/Ódio'),
            (r'(latrocínio|assalto|bala perdida|roubo)', 'Latrocínio/Urbana')
        ]

    def converter_extenso(self, texto_num):
        try:
            partes = texto_num.lower().split(' e ')
            soma = sum([self.mapa_numeros[p] for p in partes if p in self.mapa_numeros])
            return soma if soma > 0 else None
        except: return None

    def processar_texto(self, texto):
        texto_str = str(texto)

        data = "N/A"
        match_dt_num = re.search(self.regex_data_num, texto_str)
        if match_dt_num: data = match_dt_num.group(1).replace('.', '/')
        else:
            match_dt_ext = re.search(self.regex_data_ext, texto_str, re.IGNORECASE)
            if match_dt_ext:
                dia = match_dt_ext.group(1).zfill(2)
                mes = self.mapa_meses.get(match_dt_ext.group(2).lower(), '01')
                ano = match_dt_ext.group(3)
                data = f"{dia}/{mes}/{ano}"

        cidade = "Local Desconhecido"
        match_cid = re.search(self.regex_cidade, texto_str)
        if match_cid:
            cand = match_cid.group(1).strip()
            if cand.lower() not in ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro', 'polícia', 'pefoce', 'dhpp']:
                cidade = cand

        idade = None
        match_id_num = re.search(self.regex_idade_num, texto_str)
        if match_id_num: idade = int(match_id_num.group(1))
        else:
            match_id_ext = re.search(self.regex_idade_ext, texto_str)
            if match_id_ext: idade = self.converter_extenso(match_id_ext.group(1))

        match_cor = re.search(self.regex_cor, texto_str)
        cor = match_cor.group(1).lower() if match_cor else "Não informada"

        causa = "Outros/Indeterminado"
        texto_lower = texto_str.lower()
        for padrao, label in self.regras_causa:
            if re.search(padrao, texto_lower):
                causa = label
                break

        return {
            "DATA": data, "LOCALIDADE": cidade, "IDADE_ESTIMADA": idade,
            "COR_PELE": cor, "CLASSIFICACAO_CAUSA": causa, "NOTÍCIA_ORIGINAL": texto_str[:100] + "..."
        }

# ==============================================================================
# INTERFACE PRINCIPAL
# ==============================================================================
def main():
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.title("Sistema de Monitoramento de Feminicídios // CE")
        st.caption("Desenvolvido por: Yanna Queiroz | Orientadores: Me. Helyson Braz, Thyana Vicente e Roberta Jeane")

    st.sidebar.markdown("### Gerar Notícias por:")
    modo_input = st.sidebar.radio("Fonte de dados:", ("UPLOAD DE ARQUIVO (.CSV)", "INPUT MANUAL / VOZ"), label_visibility="collapsed")
    extractor = SmartExtractor()

    if modo_input == "UPLOAD DE ARQUIVO (.CSV)":
        uploaded_file = st.sidebar.file_uploader("Carregar Dataset Bruto", type="csv")
        if uploaded_file is not None:
            try:
                df_raw = pd.read_csv(uploaded_file)
                col_name = df_raw.columns[0]
                if 'conteudo_noticia' in df_raw.columns: col_name = 'conteudo_noticia'
                if st.sidebar.button("INICIAR PROCESSAMENTO EM LOTE"):
                    with st.spinner("ANALISANDO PADRÕES SEMÂNTICOS E GEOPOLÍTICOS..."):
                        dados_extraidos = df_raw[col_name].apply(lambda x: pd.Series(extractor.processar_texto(x)))
                        st.session_state['df_resultado'] = pd.concat([dados_extraidos, df_raw], axis=1)
            except Exception as e: st.error(f"FALHA: {e}")
    else:
        st.subheader("ANÁLISE UNITÁRIA E DE MULTI ENTRADA")
        st.info("Use ENTER para separar múltiplas notícias. O áudio adicionará novas linhas automaticamente.")

        if 'texto_manual' not in st.session_state: st.session_state['texto_manual'] = ""
        c_mic, c_void = st.columns([1, 4])
        with c_mic:
            st.markdown("**GRAVAR ÁUDIO:**")
            audio_text = speech_to_text(language='pt-BR', just_once=True, key='voice_recorder')

        if audio_text:
            if st.session_state['texto_manual']: st.session_state['texto_manual'] += "\n" + audio_text
            else: st.session_state['texto_manual'] = audio_text

        texto_input = st.text_area("Insira os relatórios (separados por ENTER):", height=200, key='texto_manual')

        if st.button("CLASSIFICAR DADOS"):
            if texto_input:
                lista_noticias = [t.strip() for t in texto_input.split('\n') if t.strip()]
                if lista_noticias:
                    resultados = [extractor.processar_texto(noticia) for noticia in lista_noticias]
                    st.session_state['df_resultado'] = pd.DataFrame(resultados)
                    st.success(f"{len(lista_noticias)} NOTÍCIAS IDENTIFICADAS!")

    if 'df_resultado' in st.session_state and not st.session_state['df_resultado'].empty:
        df_show = st.session_state['df_resultado'].copy()

        df_show['DATA_OBJ'] = pd.to_datetime(df_show['DATA'], dayfirst=True, errors='coerce')
        df_show['ANO_MES'] = df_show['DATA_OBJ'].dt.strftime('%Y-%m')
        df_show['MACROREGIAO'] = df_show['LOCALIDADE'].apply(mapear_macroregiao)

        # --- MÉTRICAS ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("CASOS ANALISADOS", len(df_show))
        c2.metric("MUNICÍPIOS AFETADOS", df_show['LOCALIDADE'].nunique())
        c3.metric("IDADE MÉDIA", f"{df_show['IDADE_ESTIMADA'].mean():.1f}")
        try: c4.metric("MODA CAUSA", df_show['CLASSIFICACAO_CAUSA'].mode()[0])
        except: pass

        st.markdown("---")

        # ==============================================================================
        # SISTEMA DE ALERTA COM TOP 5 (RANKING DE ICR)
        # ==============================================================================
        st.markdown("### SISTEMA DE ALERTA DE POLÍTICAS PÚBLICAS")

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
                # SEM INDENTAÇÃO AQUI!
                html_outras_regioes += f"""<div class='top5-item'>
<span class='top5-rank'>#{i+1}</span>
<strong>{r_nome}</strong> &mdash; ICR: <span style='color:#00ffcc;'>{r_icr:.1f}%</span>
<span style='font-size:0.85rem;'>({r_casos} casos)</span>
</div>"""

            st.markdown(f"""
<div class="alert-box">
<div class="alert-title">⚠️ ZONA DE ALTA CRITICIDADE DETECTADA: {regiao_critica.upper()}</div>
<div class="index-badge">ÍNDICE DE CONCENTRAÇÃO REGIONAL (ICR): {icr_1:.1f}%</div>
<div class="alert-text">
O monitoramento identificou que mais de {int(icr_1)}% de todos os casos analisados no Estado estão concentrados nesta Região de Planejamento (<span class="highlight">{total_critica} ocorrências</span>). O polo de maior vulnerabilidade é o município de <span class="highlight">{cidade_critica}</span>.<br><br>
<strong>DIRETRIZES DE INTERVENÇÃO (FOCO PRIMÁRIO):</strong><br>
• Instalação/ampliação da <i>Delegacia de Defesa da Mulher (DDM) ou Casa da Mulher</i> em {cidade_critica}.<br>
• Intensificação tática da <i>Patrulha Maria da Penha</i> em todo o {regiao_critica}.
</div>
<div class="top5-container">
<div style="color: #ff0055; font-weight: bold; margin-bottom: 8px;">MONITORAMENTO DE RISCO: TOP 5 REGIÕES</div>
{html_outras_regioes}
</div>
</div>
""", unsafe_allow_html=True)
        else:
            st.info("Dados regionais insuficientes para calcular os índices de criticidade.")

        st.markdown("---")
        st.markdown("### DASHBOARD ANALÍTICO")

        # --- LINHA 1: CAUSAS E CIDADES ---
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.caption("DISTRIBUIÇÃO POR CAUSA / MOTIVAÇÃO")
            fig_pie = px.pie(df_show, names='CLASSIFICACAO_CAUSA', hole=0.6, color_discrete_sequence=['#ff0055', '#00ffcc', '#ffffff', '#444444'], template="plotly_dark")
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_g2:
            st.caption("TOP 10 CIDADES COM MAIS OCORRÊNCIAS")
            top_cidades = df_show['LOCALIDADE'].value_counts().head(10).reset_index()
            top_cidades.columns = ['Cidade', 'Casos']
            fig_bar = px.bar(top_cidades, x='Cidade', y='Casos', color='Casos', color_continuous_scale=['#440022', '#ff0055'], template="plotly_dark")
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_bar, use_container_width=True)

        # --- LINHA 2: TEMPORAL E REGIÕES DE PLANEJAMENTO ---
        col_g3, col_g4 = st.columns(2)
        with col_g3:
            st.caption("EVOLUÇÃO TEMPORAL (MÊS/ANO)")
            timeline_df = df_show.groupby('ANO_MES').size().reset_index(name='QUANTIDADE').sort_values('ANO_MES')
            if not timeline_df.empty:
                fig_line = px.area(timeline_df, x='ANO_MES', y='QUANTIDADE', markers=True, color_discrete_sequence=['#00ffcc'], template="plotly_dark")
                fig_line.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title=None)
                st.plotly_chart(fig_line, use_container_width=True)

        with col_g4:
            st.caption("INCIDÊNCIA POR REGIÃO DE PLANEJAMENTO (IPECE)")
            regioes_count = df_show['MACROREGIAO'].value_counts().reset_index()
            regioes_count.columns = ['Região de Planejamento', 'Casos']
            fig_macro = px.bar(regioes_count, x='Casos', y='Região de Planejamento', orientation='h', color='Casos', color_continuous_scale=['#440022', '#ff0055'], template="plotly_dark")
            fig_macro.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_macro, use_container_width=True)

        # --- LINHA 3: DEMOGRAFIA ---
        st.markdown("### PERFIL DAS VÍTIMAS")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.caption("COR DA PELE IDENTIFICADA")
            df_cor = df_show['COR_PELE'].fillna('Não informada').value_counts().reset_index()
            df_cor.columns = ['Cor', 'Total']
            fig_skin = px.bar(df_cor, x='Total', y='Cor', orientation='h', color='Total', color_continuous_scale=['#333333', '#e0e0e0'], template="plotly_dark")
            fig_skin.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_skin, use_container_width=True)
        with col_d2:
            st.caption("DISTRIBUIÇÃO POR IDADE")
            df_idade = df_show.dropna(subset=['IDADE_ESTIMADA'])
            if not df_idade.empty:
                fig_hist = px.histogram(df_idade, x="IDADE_ESTIMADA", nbins=15, color_discrete_sequence=['#ff0055'], template="plotly_dark")
                fig_hist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", bargap=0.1)
                st.plotly_chart(fig_hist, use_container_width=True)

        # --- TABELA ---
        st.markdown("### DADOS BRUTOS")
        st.dataframe(df_show[['DATA', 'LOCALIDADE', 'MACROREGIAO', 'IDADE_ESTIMADA', 'COR_PELE', 'CLASSIFICACAO_CAUSA', 'NOTÍCIA_ORIGINAL']], use_container_width=True, height=300)

        # --- DOWNLOADS ---
        col_dl1, col_dl2 = st.columns(2)
        csv = df_show.to_csv(index=False).encode('utf-8-sig')
        col_dl1.download_button("[DOWNLOAD .CSV]", csv, 'femicide_data.csv', 'text/csv')
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer: df_show.to_excel(writer, index=False)
        col_dl2.download_button("[DOWNLOAD .XLSX]", buffer, 'femicide_data.xlsx', 'application/vnd.ms-excel')

    st.markdown("---")
    col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
    with col_p2:
        st.markdown("<h3 style='text-align: center; color: #444; font-size: 14px; margin-bottom: 10px;'>APOIO E PATROCINADORES</h3>", unsafe_allow_html=True)
        st.image("https://imgur.com/xLFPmmy.png", use_container_width=True)

if __name__ == "__main__":
    main()