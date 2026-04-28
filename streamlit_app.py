import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# --- CONFIGURAÇÃO ---
tickers_alvo = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA", "MGLU3.SA"]
resultados = []

def analisar_ticker(simbolo):
    dados = yf.Ticker(simbolo).history(period="1y")
    if dados.empty: return None
    
    # Cálculos
    ma20 = dados['Close'].rolling(window=20).mean().iloc[-1]
    
    delta = dados['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    ifr = (100 - (100 / (1 + rs))).iloc[-1]
    
    preco = dados['Close'].iloc[-1]
    
    # Lógica de Pontuação
    if preco > ma20 and ifr < 50:
        status, score = "COMPRA", 2
    elif preco < ma20 or ifr > 70:
        status, score = "VENDA/ALERTA", -2
    else:
        status, score = "NEUTRO", 0
        
    return {"Ticker": simbolo, "Preço": preco, "IFR": ifr, "Status": status, "Score": score, "Dados": dados}

# Processando lista
for t in tickers_alvo:
    analise = analisar_ticker(t)
    if analise: resultados.append(analise)

# Criando Ranking e pegando Top 3 (Melhores ou mais relevantes)
df_ranking = pd.DataFrame(resultados).sort_values(by="Score", ascending=False)
top_3 = df_ranking.head(3)

print("=== TOP 3 RECOMENDAÇÕES B3 ===")
print(top_3[['Ticker', 'Preço', 'Status', 'IFR']].to_string(index=False))

# --- GERANDO GRÁFICOS PARA O TOP 3 ---
for index, row in top_3.iterrows():
    ticker = row['Ticker']
    dados_plot = row['Dados']
    dados_plot['MA20'] = dados_plot['Close'].rolling(window=20).mean()
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                        subplot_titles=(f'Gráfico: {ticker} (Status: {row["Status"]})', 'IFR (14)'))

    fig.add_trace(go.Candlestick(x=dados_plot.index, open=dados_plot['Open'], high=dados_plot['High'],
                                 low=dados_plot['Low'], close=dados_plot['Close'], name='Preço'), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=dados_plot.index, y=dados_plot['MA20'], name='MA20', line=dict(color='orange')), row=1, col=1)
    
    # IFR dinâmico para o gráfico
    d = dados_plot['Close'].diff()
    g = (d.where(d > 0, 0)).rolling(14).mean()
    l = (-d.where(d < 0, 0)).rolling(14).mean()
    ifr_plot = 100 - (100 / (1 + (g/l)))
    
    fig.add_trace(go.Scatter(x=dados_plot.index, y=ifr_plot, name='IFR', line=dict(color='purple')), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    fig.update_layout(height=500, template='plotly_dark', xaxis_rangeslider_visible=False, showlegend=False)
    fig.show()