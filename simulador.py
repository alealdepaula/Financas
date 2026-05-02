import streamlit as st
import pandas as pd
import datetime
import io
from fpdf import FPDF

st.set_page_config(page_title="Simulador de Investimentos Pro", layout="wide")

def simular_evolucao(v_ini, aporte_ini, taxa_a, infla_a, anos):
    taxa_m = (1 + taxa_a/100)**(1/12) - 1
    infla_m = (1 + infla_a/100)**(1/12) - 1
    saldo, investido_acumulado, aporte_atual = v_ini, v_ini, aporte_ini
    dados = []
    for ano in range(0, anos + 1):
        if ano > 0:
            for _ in range(12):
                saldo = (saldo * (1 + taxa_m)) + aporte_atual
                investido_acumulado += aporte_atual
        poder_compra = saldo / ((1 + infla_m) ** (ano * 12))
        dados.append({'Ano': ano, 'Aporte Mensal': round(aporte_atual, 2), 'Total Investido': round(investido_acumulado, 2), 'Saldo Bruto': round(saldo, 2), 'Poder de Compra Real': round(poder_compra, 2)})
        if ano > 0: aporte_atual *= (1 + infla_a/100)
    return pd.DataFrame(dados)

def gerar_pdf(resumo_dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Plano de Liberdade Financeira", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    for chave, valor in resumo_dados.items():
        pdf.cell(0, 10, f"{chave}: {valor}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, f"Relatório gerado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Parâmetros")
    v_ini = st.number_input("Valor Inicial (R$)", value=10000.0)
    aporte_ini = st.number_input("Aporte Mensal Inicial (R$)", value=2000.0)
    infla = st.number_input("Inflação Anual (%)", value=4.5)
    anos_sim = st.slider("Tempo de Simulação (Anos)", 1, 50, 20)
    taxa_a = st.number_input("Taxa Anual (%)", value=10.0)

# --- CÁLCULOS ---
df_a = simular_evolucao(v_ini, aporte_ini, taxa_a, infla, anos_sim)
taxa_real_anual = ((1 + taxa_a/100) / (1 + infla/100)) - 1
taxa_real_mensal = (1 + taxa_real_anual)**(1/12) - 1

# --- INTERFACE ---
st.title("📈 Planejador Estratégico")
tab1, tab2 = st.tabs(["📊 Simulação", "🚀 Caminho da Liberdade"])

with tab1:
    st.line_chart(df_a.set_index('Ano')['Poder de Compra Real'])
    st.metric("Saldo Real Final", f"R$ {df_a['Poder de Compra Real'].iloc[-1]:,.2f}")

with tab2:
    renda_desejada = st.number_input("Renda mensal desejada (Hoje):", value=5000.0)
    if taxa_real_mensal > 0:
        patrimonio_necessario = renda_desejada / taxa_real_mensal
        saldo_r, meses_r = v_ini, 0
        while saldo_r < patrimonio_necessario and meses_r < 1200:
            saldo_r = (saldo_r * (1 + taxa_real_mensal)) + aporte_ini
            meses_r += 1
        
        anos_r, meses_restantes = meses_r // 12, meses_r % 12
        
        resumo_pdf = {
            "Valor Inicial": f"R$ {v_ini:,.2f}",
            "Aporte Mensal": f"R$ {aporte_ini:,.2f}",
            "Renda Desejada": f"R$ {renda_desejada:,.2f}",
            "Patrimônio Alvo": f"R$ {patrimonio_necessario:,.2f}",
            "Tempo Estimado": f"{anos_r} anos e {meses_restantes} meses",
            "Taxa Real Utilizada": f"{taxa_real_anual*100:.2f}% ao ano"
        }
        
        st.success(f"### Meta em: {anos_r} anos e {meses_restantes} meses")
        
        # Botão de Impressão (PDF)
        pdf_data = gerar_pdf(resumo_pdf)
        st.download_button(label="📄 Imprimir Plano (PDF)", data=pdf_data, 
                           file_name="plano_liberdade.pdf", mime="application/pdf")
