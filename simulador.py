import streamlit as st
import pandas as pd
import datetime
import io
from fpdf import FPDF

st.set_page_config(page_title="Simulador de Investimentos Pro", layout="wide")

# --- FUNÇÃO DE CÁLCULO ---
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
        dados.append({
            'Ano': ano, 
            'Aporte Mensal': round(aporte_atual, 2), 
            'Total Investido': round(investido_acumulado, 2), 
            'Saldo Bruto': round(saldo, 2), 
            'Poder de Compra Real': round(poder_compra, 2)
        })
        if ano > 0: aporte_atual *= (1 + infla_a/100)
    return pd.DataFrame(dados)

# --- FUNÇÃO GERAR PDF ---
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
    pdf.cell(0, 10, f"Gerado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Parâmetros")
    v_ini = st.number_input("Valor Inicial (R$)", value=10000.0)
    aporte_ini = st.number_input("Aporte Mensal Inicial (R$)", value=2000.0)
    infla = st.number_input("Inflação Anual (%)", value=4.5)
    anos_sim = st.slider("Tempo de Simulação (Anos)", 1, 50, 20)
    taxa_a = st.number_input("Taxa Anual Cenário A (%)", value=10.0)
    taxa_b = st.number_input("Taxa Anual Cenário B (%)", value=12.0)

# --- CÁLCULOS ---
df_a = simular_evolucao(v_ini, aporte_ini, taxa_a, infla, anos_sim)
df_b = simular_evolucao(v_ini, aporte_ini, taxa_b, infla, anos_sim)
taxa_real_anual = ((1 + taxa_a/100) / (1 + infla/100)) - 1
taxa_real_mensal = (1 + taxa_real_anual)**(1/12) - 1

# --- INTERFACE COM 3 ABAS ---
st.title("📈 Planejador Estratégico Completo")
tab1, tab2, tab3 = st.tabs(["📊 Simulação", "🚀 Caminho da Liberdade", "💡 Dicas de Investimento"])

with tab1:
    st.subheader("Evolução do Poder de Compra Real")
    df_chart = pd.DataFrame({
        'Ano': df_a['Ano'], 
        'Cenário A': df_a['Poder de Compra Real'], 
        'Cenário B': df_b['Poder de Compra Real']
    }).set_index('Ano')
    st.line_chart(df_chart)
    
    c1, c2 = st.columns(2)
    c1.metric("Saldo Real Final (A)", f"R$ {df_a['Poder de Compra Real'].iloc[-1]:,.2f}")
    c2.metric("Saldo Real Final (B)", f"R$ {df_b['Poder de Compra Real'].iloc[-1]:,.2f}")

with tab2:
    st.header("Sua Meta de Independência")
    renda_desejada = st.number_input("Renda mensal desejada (Hoje):", value=5000.0)
    
    if taxa_real_mensal > 0:
        patrimonio_alvo = renda_desejada / taxa_real_mensal
        saldo_r, meses_r = v_ini, 0
        while saldo_r < patrimonio_alvo and meses_r < 1200:
            saldo_r = (saldo_r * (1 + taxa_real_mensal)) + aporte_ini
            meses_r += 1
        
        anos_r, meses_r_rest = meses_r // 12, meses_r % 12
        st.success(f"### Meta atingida em: {anos_r} anos e {meses_r_rest} meses")
        st.info(f"Patrimônio necessário: R$ {patrimonio_alvo:,.2f}")

        resumo_pdf = {
            "Valor Inicial": f"R$ {v_ini:,.2f}",
            "Aporte Mensal": f"R$ {aporte_ini:,.2f}",
            "Renda Desejada": f"R$ {renda_desejada:,.2f}",
            "Patrimônio Alvo": f"R$ {patrimonio_alvo:,.2f}",
            "Tempo Estimado": f"{anos_r} anos e {meses_r_rest} meses"
        }
        
        pdf_data = gerar_pdf(resumo_pdf)
        st.download_button("📄 Imprimir Plano (PDF)", pdf_data, "plano.pdf", "application/pdf")

with tab3:
    st.header("Dicas de Investimento")
    st.success("### 1. Reinvista sempre\nO segredo dos juros compostos é não retirar o rendimento antes da meta.")
    st.warning("### 2. Atenção à Inflação\nSempre ajuste seus aportes para manter seu poder de investimento ao longo dos anos.")
    st.info("### 3. Diversificação\nConsidere ativos que protejam seu capital contra crises econômicas.")
