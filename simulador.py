import streamlit as st
import pandas as pd
import datetime
import io

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

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Parâmetros")
    v_ini = st.number_input("Valor Inicial (R$)", value=10000.0)
    aporte_ini = st.number_input("Aporte Mensal Inicial (R$)", value=2000.0)
    infla = st.number_input("Inflação Anual (%)", value=4.5)
    anos_sim = st.slider("Tempo de Simulação (Anos)", 1, 50, 20)
    taxa_a = st.number_input("Taxa Anual Cenário A (%)", value=10.0)
    taxa_b = st.number_input("Taxa Anual Cenário B (%)", value=12.0)

# --- INTERFACE ---
st.title("📈 Planejador de Independência Financeira")
tab1, tab2, tab3 = st.tabs(["📊 Simulação", "🚀 Caminho da Liberdade", "💡 Dicas"])

df_a = simular_evolucao(v_ini, aporte_ini, taxa_a, infla, anos_sim)
df_b = simular_evolucao(v_ini, aporte_ini, taxa_b, infla, anos_sim)

with tab1:
    st.subheader("Evolução do Poder de Compra Real")
    df_chart = pd.DataFrame({'Ano': df_a['Ano'], f'Cenário A ({taxa_a}%)': df_a['Poder de Compra Real'], f'Cenário B ({taxa_b}%)': df_b['Poder de Compra Real']}).set_index('Ano')
    st.line_chart(df_chart)
    
    col1, col2 = st.columns(2)
    col1.metric("Saldo Real Final (A)", f"R$ {df_a['Poder de Compra Real'].iloc[-1]:,.2f}")
    col2.metric("Saldo Real Final (B)", f"R$ {df_b['Poder de Compra Real'].iloc[-1]:,.2f}")

with tab2:
    st.header("Quanto tempo falta para sua independência?")
    renda_desejada = st.number_input("Qual renda mensal você quer ter (em valores de hoje)?", value=5000.0)
    
    taxa_real_anual = ((1 + taxa_a/100) / (1 + infla/100)) - 1
    taxa_real_mensal = (1 + taxa_real_anual)**(1/12) - 1
    
    if taxa_real_mensal <= 0:
        st.error("A taxa de rendimento deve ser maior que a inflação para gerar renda passiva.")
    else:
        patrimonio_necessario = renda_desejada / taxa_real_mensal
        st.info(f"Para receber R$ {renda_desejada:,.2f}/mês, você precisa de um patrimônio de **R$ {patrimonio_necessario:,.2f}** (em poder de compra de hoje).")
        
        # Cálculo de tempo necessário
        saldo_r, meses_r, aporte_r = v_ini, 0, aporte_ini
        while saldo_r < patrimonio_necessario and meses_r < 1200: # Limite 100 anos
            saldo_r = (saldo_r * (1 + taxa_real_mensal)) + aporte_ini # Usando valores reais
            meses_r += 1
        
        anos_r = meses_r // 12
        meses_restantes = meses_r % 12
        
        st.success(f"### Você atingirá sua meta em: **{anos_r} anos e {meses_restantes} meses**")
        st.write(f"Isso considerando o Cenário A ({taxa_a}% ao ano).")

with tab3:
    st.header("Dicas de Investimento")
    st.write("1. **Foco no longo prazo**: Os juros compostos precisam de tempo.")
    st.write("2. **Reinvista os dividendos**: Isso acelera o tempo para a meta na aba ao lado.")
