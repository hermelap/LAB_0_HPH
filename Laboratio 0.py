# -- ------------------------------------------------------------------------------------ -- #
# -- Proyecto: Repaso de python 3 y analisis de precios OHLC                              -- #
# -- Codigo: principal.py - script principal de proyecto                                  -- #
# -- Rep: https://github.com/hermelap/LAB_0_HPH
# -- #
# -- Autor: Hermela Peña                                                              -- #
# -- ------------------------------------------------------------------------------------ -- #

# -- ------------------------------------------------------------- Importar con funciones -- #

import Funciones as fn  # Para procesamiento de datos
import visualizacion as vs  # Para visualizacion de datos
import pandas as pd  # Procesamiento de datos
from datos import token as OA_Ak  # Importar token para API de OANDA
import plotly.graph_objects as go

# -- --------------------------------------------------------- Descargar precios de OANDA -- #

# token de OANDA
OA_In = "EUR_USD"  # Instrumento
OA_Gn = "D"  # Granularidad de velas
fini = pd.to_datetime("2019-07-06 00:00:00").tz_localize('GMT')  # Fecha inicial
ffin = pd.to_datetime("2019-12-06 00:00:00").tz_localize('GMT')  # Fecha final

# Descargar precios masivos
df_pe = fn.f_precios_masivos(p0_fini=fini, p1_ffin=ffin, p2_gran=OA_Gn,
                             p3_inst=OA_In, p4_oatk=OA_Ak, p5_ginc=4900)

# -- --------------------------------------------------------------- Graficar OHLC plotly -- #

vs_grafica1 = vs.g_velas(p0_de=df_pe.iloc[0:120, :])
vs_grafica1.show()

# -- ------------------------------------------------------------------- Conteno de velas -- #

# multiplicador de precios
pip_mult = 10000

# -- 0A.1: Hora
df_pe['hora'] = [df_pe['TimeStamp'][i].hour for i in range(0, len(df_pe['TimeStamp']))]

# -- 0A.2: Dia de la semana.
df_pe['dia'] = [df_pe['TimeStamp'][i].weekday() for i in range(0, len(df_pe['TimeStamp']))]

# -- 0B: Boxplot de amplitud de velas (close - open).
df_pe['co'] = (df_pe['Close'] - df_pe['Open']) * pip_mult

# -- ------------------------------------------------------------ Graficar Boxplot plotly -- #
vs_grafica2 = vs.g_boxplot_varios(p0_data=df_pe[['co']], p1_norm=False)
vs_grafica2.show()

# -- 01: Mes de la vela.
df_pe['mes'] = [df_pe['TimeStamp'][i].month for i in range(0, len(df_pe['TimeStamp']))]

# -- 02: Sesion de la vela.
condiciones = [(lambda i: i == 22 or i == 23 or i == 0 or i == 1 or i == 2 or i == 3 or i == 4 or i == 5 or i == 6
                          or i == 7, 'asia'),
               (lambda i: i == 8, 'asia_europa'),
               (lambda i: i == 9 or i == 10 or i == 11 or i == 12, 'europa'),
               (lambda i: i == 13 or i == 14 or i == 15 or i == 16, 'europa_america'),
               (lambda i: i == 17 or i == 18 or i == 19 or i == 20 or i == 21, 'america')]


def condiciones2(i):
    for cond, icion in condiciones:
        if cond(i):
            return icion
    return i


df_pe['sesion'] = list(map(condiciones2, df_pe['hora']))

# -- 03: Amplitud OC esperada de vela para cualquier dia de la semana (Dist de Freq).
df_pe['oc'] = (df_pe['Open'] - df_pe['Close']) * pip_mult

# -- 04: Amplitud HL esperada de vela para cualquier dia de la semana (Dist de Freq).
df_pe['hl'] = (df_pe['High'] - df_pe['Low']) * pip_mult

# -- 05: Evolucion de velas consecutivas (1: Alcistas, 0: Bajistas).
df_pe['sentido'] = ['alcista' if df_pe["Close"][i] >= df_pe['Open'][i] else 'bajista'
                    for i in range(0, len(df_pe['Open']))]

# -- 06: Maxima evolucion esperada de velas consecutivas (Dist Acum de Freq).
df_pe['sentido_c'] = 0
x = 0
for i in range(1, len(df_pe['sentido_c'])):
    if df_pe['sentido'][i] == df_pe['sentido'][i - 1]:
        x = x + 1
        df_pe.loc[i, 'sentido_c'] = x
    else:
        x = 0
        df_pe.loc[i, 'sentido_c'] = x

# -- 07: Ventanas moviles de volatilidad
x = df_pe.columns.get_loc('hl')
df_pe['volatilidad_5'] = df_pe.iloc[:, x].rolling(window=5).mean()
df_pe['volatilidad_25'] = df_pe.iloc[:, x].rolling(window=25).mean()
df_pe['volatilidad_50'] = df_pe.iloc[:, x].rolling(window=50).mean()

# -- Gráfica plotly
# --  Tiene que tener título de gráfica
# --  Tiene que tener título de eje x y etiquetas de eje x
# --  Tiene que tener título de eje y y etiquetas de eje y
# --  Se debe de poder visualizar una leyenda (en cualquier posición).

vs_grafica3 = go.Figure()
vs_grafica3.add_trace(go.Histogram(x=df_pe['sentido_c']))
vs_grafica3.update_layout(title={'text': "Distribución conteo velas consecutivas"}, xaxis_title='repeticiones',
                          yaxis_title='frecuencia')
vs_grafica3.show()
