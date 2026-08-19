import yfinance as yf
import pandas as pd

def obtener_sma200(ticker):
    # Pedimos 1 año y medio de datos para garantizar >200 ruedas hábiles
    df = yf.download(ticker, period="1y1m", progress=False)
    
    if df.empty or len(df) < 200:
        print(f"No hay suficientes datos para {ticker}")
        return None
    
    # Se calcula la media móvil simple de 200 ruedas sobre el precio de cierre
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    
    # Tomamos el último valor registrado
    precio_actual = float(df['Close'].iloc[-1])
    sma_200 = float(df['SMA_200'].iloc[-1])
    
    return {
        "Ticker": ticker,
        "Precio Actual": round(precio_actual, 2),
        "SMA 200 Ruedas": round(sma_200, 2),
        "Tendencia": "Alcista (por encima)" if precio_actual > sma_200 else "Bajista (por debajo)"
    }

def calcular_variacion_mensual(tickers):
    """
    Dada una lista de tickers, descarga los precios de cierre del último mes
    y calcula la variación porcentual de cada uno.
    """
    print("Obteniendo cotizaciones del último mes...")
    
    # 'period="1mo"' descarga el historial del último mes calendario
    data = yf.download(tickers, period="1mo", progress=False)['Close']
    
    # Manejamos el caso de que solo se pase un solo ticker en la lista
    if isinstance(data, pd.Series):
        data = data.to_frame()

    resultados = []

    for ticker in tickers:
        if ticker in data.columns:
            # Filtramos días sin cotización (fines de semana / feriados)
            precios = data[ticker].dropna()
            
            if len(precios) >= 2:
                precio_inicial = precios.iloc[0]
                precio_actual = precios.iloc[-1]
                variacion_pct = ((precio_actual - precio_inicial) / precio_inicial) * 100
                sma200 = obtener_sma200(ticker)  # Llamada a la función para obtener SMA200 y tendencia
                resultados.append({
                    "Ticker": ticker,
                    "Precio Hace 1 Mes": round(precio_inicial, 2),
                    "Precio Actual": round(precio_actual, 2),
                    "Variación (%)": round(variacion_pct, 2),
                    "SMA200": sma200.get("SMA 200 Ruedas") if sma200 else None,
                    "Tendencia": sma200.get("Tendencia") if sma200 else None
                })
            else:
                resultados.append({"Ticker": ticker, "Error": "Datos insuficientes"})
        else:
            resultados.append({"Ticker": ticker, "Error": "Ticker no encontrado"})

    # Convertimos a DataFrame y ordenamos de mayor a menor variación
    df = pd.DataFrame(resultados)
    if "Variación (%)" in df.columns:
        df = df.sort_values(by="Variación (%)", ascending=False, ignore_index=True)
        
    return df

# --- EJEMPLO DE USO ---
if __name__ == "__main__":
    # Tickers mixtos: EE.UU. (AAPL, NVDA, MELI) + Argentina (GGAL.BA, YPFD.BA, AL30.BA)
    lista_tickers =[
    "AAPL",
    "AXP",
    "CL",
    "EEM",
    "EWJ",
    "EWZ",
    "GLD",
    "GOOGL",
    "GS",
    "IBM",
    "IEUR",
    "MELI",
    "META",
    "MSFT",
    "MU",
    "NU",
    "NVDA",
    "RACE",
    "SLV",
    "SPY",
    "UL",
    "V",
    "VALE",
    "VEA",
    "VIST",
    "WMT",
    "XLI",
    "XLV",
]
    
    df_resultado = calcular_variacion_mensual(lista_tickers)
    
    print("\n" + "="*50)
    print("  VARIACIÓN MENSUAL DE COTIZACIONES")
    print("="*50)
    print(df_resultado.to_string(index=False))


