import streamlit as st
import pandas as pd
import datetime
import io

# Configuração da página para o navegador
st.set_page_config(page_title="Simulador de Investimentos Pro", layout="wide")

# --- FUNÇÃO DE CÁLCULO ---
def simular_evolucao(v_ini, aporte_ini, taxa_a, infla_a, anos):
    taxa_m = (1 + taxa_a/100)**(1/12) - 1
    infla_m = (1 + infla_a/100)**(1/12) - 1
    saldo = v_ini
    investido_acumulado = v_ini
    aporte_atual = aporte_ini
    dados = []
    
    for ano in range(0, anos + 1):
        if ano > 0:
            for _ in range(12):
                saldo = (saldo * (1 + taxa_m)) + aporte_atual
                investido_acumulado += aporte_atual
        
        poder_compra = saldo / ((1 + infla_m) ** (ano * 12))
        dados.append({
            'Ano': ano, 
            'Aporte Mensal (R$)': round(aporte_atual, 2),
            'Total Investido (R$)': round(investido_acumulado, 2),
            'Saldo Bruto (R$)': round(saldo, 2),
            'Poder de Compra Real (R$)': round(poder_compra, 2)
        })
        if ano > 0:
            aporte_atual *= (1 + infla_a/100)
    return pd.DataFrame(dados)

# --- BARRA LATERAL (ENTRADA DE DADOS) ---
with st.sidebar:
    st.header("⚙️ Parâmetros")
    v_ini = st.number_input("Valor Inicial (R$)", value=10000.0, step=1000.0)
    aporte_ini = st.number_input("Aporte Mensal Inicial (R$)", value=5000.0, step=100.0)
    infla = st.number_input("Inflação Anual Esperada (%)", value=4.5, step=0.1)
    anos = st.slider("Tempo de Investimento (Anos)", 1, 50, 14)
    
    st.subheader("Cenários de Rendimento")
    taxa_a = st.number_input("Taxa Anual Cenário A (%)", value=8.0, step=0.5)
    taxa_b = st.number_input("Taxa Anual Cenário B (%)", value=10.0, step=0.5)
    
    st.info("Os aportes são corrigidos anualmente pela inflação informada.")

# --- CÁLCULOS ---
df_a = simular_evolucao(v_ini, aporte_ini, taxa_a, infla, anos)
df_b = simular_evolucao(v_ini, aporte_ini, taxa_b, infla, anos)

# Cálculo de Renda Passiva para o Resumo
taxa_real_a = ((1 + taxa_a/100) / (1 + infla/100)) - 1
taxa_real_b = ((1 + taxa_b/100) / (1 + infla/100)) - 1
renda_a = (df_a['Poder de Compra Real (R$)'].iloc[-1] * taxa_real_a) / 12
renda_b = (df_b['Poder de Compra Real (R$)'].iloc[-1] * taxa_real_b) / 12

# --- INTERFACE PRINCIPAL COM ABAS ---
st.title("📈 Simulador de Investimentos Estratégico")

tab1, tab2 = st.tabs(["📊 Simulação Interativa", "💡 Dicas de Investimento"])

with tab1:
    # Métricas de destaque
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"### Cenário A ({taxa_a}%)")
        st.metric("Poder de Compra Final", f"R$ {df_a['Poder de Compra Real (R$)'].iloc[-1]:,.2f}")
        st.metric("Renda Passiva Mensal", f"R$ {renda_a:,.2f}")
    with c2:
        st.markdown(f"### Cenário B ({taxa_b}%)")
        st.metric("Poder de Compra Final", f"R$ {df_b['Poder de Compra Real (R$)'].iloc[-1]:,.2f}")
        st.metric("Renda Passiva Mensal", f"R$ {renda_b:,.2f}")

    # Gráfico de Evolução
    st.subheader("Evolução do Patrimônio (Poder de Compra Real)")
    df_chart = pd.DataFrame({
        'Ano': df_a['Ano'],
        'Cenário A': df_a['Poder de Compra Real (R$)'],
        'Cenário B': df_b['Poder de Compra Real (R$)']
    }).set_index('Ano')
    st.line_chart(df_chart)

    # Preparação do arquivo Excel para download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_a.to_excel(writer, sheet_name='Cenário A', index=False)
        df_b.to_excel(writer, sheet_name='Cenário B', index=False)
        
        # Auto-ajuste de colunas no Excel
        for sheet in ['Cenário A', 'Cenário B']:
            writer.sheets[sheet].set_column('A:E', 20)

    st.download_button(
        label="📥 Baixar Detalhamento Completo em Excel",
        data=output.getvalue(),
        file_name=f"simulacao_investimento_{datetime.datetime.now().strftime('%d%m%Y')}.xlsx",
        mime="application/vnd.ms-excel"
    )

with tab2:
    st.header("Dicas para turbinar seus investimentos")
    
    st.success("### 1. Foco no Ganho Real\nO que importa não é quanto seu dinheiro cresce, mas quanto ele compra. Sempre subtraia a inflação da sua rentabilidade para saber o ganho real.")
    
    st.info("### 2. A Constância vence a Sorte\nManter aportes mensais constantes e corrigi-los pela inflação (como fazemos neste simulador) é o segredo para construir patrimônio sólido.")
    
    st.warning("### 3. Reserva de Emergência\nAntes de buscar taxas agressivas no Cenário B, garanta que você tem de 6 a 12 meses de custo de vida em um investimento de alta liquidez.")
    
    st.write("### 4. O Efeito do Tempo")
    st.write("Note no gráfico acima como as linhas se distanciam mais nos anos finais. Isso é o efeito exponencial dos juros compostos. **Não pare no meio do caminho!**")
