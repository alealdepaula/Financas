import streamlit as st
import pandas as pd
import datetime
import io

# Configuração da página no Chrome
st.set_page_config(page_title="Simulador de Investimentos", layout="wide")

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
        dados.append({'Ano': ano, 'Aporte Mensal': round(aporte_atual, 2), 
                      'Total Investido': round(investido_acumulado, 2), 
                      'Saldo Bruto': round(saldo, 2), 
                      'Poder de Compra Real': round(poder_compra, 2)})
        if ano > 0: aporte_atual *= (1 + infla_a/100)
    return pd.DataFrame(dados)

# --- INTERFACE NO NAVEGADOR ---
st.title("📈 Simulador de Investimentos Pro")
st.markdown("Preencha os dados na barra lateral para ver o resultado em tempo real.")

# Barra lateral para entrada de dados
with st.sidebar:
    st.header("Parâmetros")
    v_ini = st.number_input("Valor Inicial (R$)", value=10000.0)
    aporte_ini = st.number_input("Aporte Mensal Inicial (R$)", value=5000.0)
    infla = st.number_input("Inflação Anual (%)", value=4.5)
    anos = st.slider("Tempo (Anos)", 1, 50, 14)
    st.subheader("Cenários de Taxas")
    taxa_a = st.number_input("Taxa Anual Cenário A (%)", value=8.0)
    taxa_b = st.number_input("Taxa Anual Cenário B (%)", value=10.0)

# Cálculos
df_a = simular_evolucao(v_ini, aporte_ini, taxa_a, infla, anos)
df_b = simular_evolucao(v_ini, aporte_ini, taxa_b, infla, anos)

# --- EXIBIÇÃO DE RESULTADOS ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("Cenário A")
    st.metric("Saldo Bruto Final", f"R$ {df_a['Saldo Bruto'].iloc[-1]:,.2f}")
    st.metric("Poder de Compra Real", f"R$ {df_a['Poder de Compra Real'].iloc[-1]:,.2f}")

with col2:
    st.subheader("Cenário B")
    st.metric("Saldo Bruto Final", f"R$ {df_b['Saldo Bruto'].iloc[-1]:,.2f}")
    st.metric("Poder de Compra Real", f"R$ {df_b['Poder de Compra Real'].iloc[-1]:,.2f}")

# Gráfico Comparativo no Navegador
st.subheader("Evolução do Poder de Compra Real")
df_chart = pd.DataFrame({
    'Ano': df_a['Ano'],
    'Cenário A': df_a['Poder de Compra Real'],
    'Cenário B': df_b['Poder de Compra Real']
}).set_index('Ano')
st.line_chart(df_chart)

# Botão para baixar o Excel
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_a.to_excel(writer, sheet_name='Cenário A', index=False)
    df_b.to_excel(writer, sheet_name='Cenário B', index=False)
st.download_button(label="📥 Baixar Detalhamento em Excel", data=output.getvalue(), 
                   file_name="simulacao_investimentos.xlsx", mime="application/vnd.ms-excel")
