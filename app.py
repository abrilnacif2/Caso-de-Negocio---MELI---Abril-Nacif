import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Business Case | Voluminosos", page_icon="📦", layout="wide")

NORMAL = {"Colecta":250000/280,"XD":741000000/10000000,"Media milla":900000/2100,
          "Service Center":741500000/10000000,"Última milla":150000/75}
CAP = {"Colecta":280,"Media milla":2100,"Última milla":75}
FACTORS={"Normal":1.0,"5x":5.0,"5,5x":5.5,"6x":6.0}
REV_NORMAL, REV_VOL, VOL_MES = 3000, 19000, 50000

def costs(s):
    if s=="Normal": return NORMAL.copy()
    f=FACTORS[s]
    return {"Colecta":NORMAL["Colecta"]*f,"XD":0.0,"Media milla":NORMAL["Media milla"]*f,
            "Service Center":0.0,"Última milla":NORMAL["Última milla"]*f}

def ars(x): return ("−" if x<0 else "")+"$"+f"{abs(x):,.0f}".replace(",",".")
def pct(x): return f"{x:+.1f}%".replace(".",",")

st.title("📦 Dashboard — Paquetes voluminosos")
st.caption("Business Case | Normal vs. escenarios teóricos de consumo de capacidad 5x, 5,5x y 6x")

with st.sidebar:
    st.header("Filtros")
    sel=st.multiselect("Escenarios",list(FACTORS),default=list(FACTORS))
    stages=st.multiselect("Etapas",list(NORMAL),default=list(NORMAL))
    view=st.radio("Vista",["Costos por etapa","Capacidad por ruta","Rentabilidad"])
    st.caption("Base: XD y SC = $0 incremental mientras exista capacidad ociosa.")

if not sel: st.warning("Seleccioná al menos un escenario."); st.stop()

transport_normal=NORMAL["Colecta"]+NORMAL["Media milla"]+NORMAL["Última milla"]
be=REV_VOL/transport_normal
a,b,c,d=st.columns(4)
a.metric("Costo normal total",ars(sum(NORMAL.values())))
b.metric("Revenue voluminoso",ars(REV_VOL))
c.metric("Punto de equilibrio",f"{be:.2f}x".replace(".",","))
d.metric("Voluminosos / mes","50.000")
st.divider()

if view=="Costos por etapa":
    if not stages: st.warning("Seleccioná al menos una etapa."); st.stop()
    rows=[]
    for s in sel:
        cc=costs(s)
        for e in stages: rows.append({"Escenario":s,"Etapa":e,"Costo ($/paq.)":cc[e]})
    df=pd.DataFrame(rows)
    st.subheader("Costo por paquete y etapa")
    fig=px.bar(df,x="Etapa",y="Costo ($/paq.)",color="Escenario",barmode="group",text_auto=".0f",
               category_orders={"Escenario":["Normal","5x","5,5x","6x"]})
    fig.update_layout(height=480,xaxis_title="",yaxis_title="$ por paquete")
    st.plotly_chart(fig,use_container_width=True)
    st.dataframe(df.pivot(index="Etapa",columns="Escenario",values="Costo ($/paq.)").round(2),
                 use_container_width=True)
    st.info("En transporte, el mismo costo de ruta se reparte entre menos paquetes equivalentes. XD y SC no generan costo incremental en el escenario base.")

elif view=="Capacidad por ruta":
    rows=[]
    for e,n in CAP.items():
        for s in sel:
            rows.append({"Etapa":e,"Escenario":s,"Equivalentes por ruta":n/FACTORS[s]})
    df=pd.DataFrame(rows)
    st.subheader("Capacidad teórica por escenario")
    fig=px.bar(df,x="Etapa",y="Equivalentes por ruta",color="Escenario",barmode="group",text_auto=".1f",
               category_orders={"Escenario":["Normal","5x","5,5x","6x"]})
    fig.update_layout(height=480,xaxis_title="")
    st.plotly_chart(fig,use_container_width=True)
    st.dataframe(df.pivot(index="Etapa",columns="Escenario",values="Equivalentes por ruta").round(1),
                 use_container_width=True)
    st.info("Son equivalentes teóricos para modelar costos, no cantidades físicas exactas: el mix real puede variar en peso y tamaño.")

else:
    rows=[]
    for s in sel:
        if s=="Normal": continue
        ci=sum(costs(s).values()); res=REV_VOL-ci
        rows.append({"Escenario":s,"Revenue / paquete":REV_VOL,"Costo incremental / paquete":ci,
                     "Resultado / paquete":res,"Margen (%)":res/REV_VOL*100,
                     "Resultado mensual ($M)":res*VOL_MES/1e6})
    df=pd.DataFrame(rows)
    if df.empty: st.warning("Seleccioná 5x, 5,5x o 6x."); st.stop()
    l,r=st.columns(2)
    with l:
        st.subheader("Resultado incremental por paquete")
        f1=px.bar(df,x="Escenario",y="Resultado / paquete",text_auto=".0f")
        f1.add_hline(y=0); f1.update_layout(height=430,yaxis_title="$ / paquete",xaxis_title="")
        st.plotly_chart(f1,use_container_width=True)
    with r:
        st.subheader("Impacto mensual")
        f2=px.bar(df,x="Escenario",y="Resultado mensual ($M)",text_auto=".1f")
        f2.add_hline(y=0); f2.update_layout(height=430,yaxis_title="Millones de $ / mes",xaxis_title="")
        st.plotly_chart(f2,use_container_width=True)
    st.dataframe(df.round(1),use_container_width=True,hide_index=True)
    st.success("Sensibilidad: un cambio relativamente pequeño en el consumo de capacidad cambia fuertemente la rentabilidad. Punto de equilibrio ≈ 5,72x.")

st.divider()
st.caption("Escenarios 5x–6x: sensibilidad teórica basada en la relación de volumen y peso del caso.")
