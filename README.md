
   ```
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Global Stock Tracker", layout="wide")

st.title("📊 Monitor de Bolsa Mundial")
ticker = st.text_input("Digite o código da ação (Ex: AAPL, PETR4.SA, TSLA):", "AAPL")

# Busca os dados
data = yf.Ticker(ticker)
hist = data.history(period="1mo")

if not hist.empty:
    # Cabeçalho com preço atual
    current_price = hist['Close'].iloc[-1]
    change = current_price - hist['Close'].iloc[-2]
    
    st.metric(label=f"Preço Atual ({ticker})", value=f"${current_price:.2f}", delta=f"{change:.2f}")

    # Gráfico Interativo
    fig = go.Figure(data=[go.Candlestick(x=hist.index,
                open=hist['Open'], high=hist['High'],
                low=hist['Low'], close=hist['Close'])])
    
    fig.update_layout(title=f"Histórico de 30 dias - {ticker}", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
    # Informações da Empresa
    st.subheader("Sobre a Empresa")
    st.write(data.info.get('longBusinessSummary', 'Informação não disponível.'))
else:
    st.error("Ticker não encontrado. Tente 'AAPL' para Apple ou 'PETR4.SA' para Petrobras.")
