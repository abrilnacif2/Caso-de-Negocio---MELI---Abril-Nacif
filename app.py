import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Voluminosos | Business Case", page_icon="📦", layout="wide")

NORMAL = {"Colecta":250000/280,"XD":741000000/10000000,"Media milla":900000/2100,
          "Service Center":741500000/10000000,"Última milla":150000/75}
FACTORS={"5x":5.0,"5,5x":5.5,"6x":6.0}
CAP={"Colecta":280,"Media milla":2100,"Última milla":75}
REV=19000
VOL=50000
TRANS=["Colecta","Media milla","Última milla"]
COLORS={"5x":"#00A650","5,5x":"#F5A623","6x":"#E55353","Normal":"#3483FA"}

def ars(v):
    sign="−" if v<0 else ""
    return sign+"$"+f"{abs(v):,.0f}".replace(",",".")
def dec(v):
    return f"{v:.1f}".replace(".",",")
def metrics(s):
    f=FACTORS[s]
    cost=sum(NORMAL[e]*f for e in TRANS)
    result=REV-cost
    return cost,result,result/REV*100,result*VOL/1e6

st.markdown("""
<style>
html,body,[class*="css"]{font-family:Arial,sans-serif}
.block-container{max-width:1480px;padding-top:1rem;padding-bottom:2rem}
[data-testid="stSidebar"]{background:#F7F8FA;border-right:1px solid #E4E7EC}
h1,h2,h3{color:#24272C}
.header{background:#FFE600;border-radius:18px;padding:20px 26px;margin-bottom:16px}
.header .title{font-size:31px;font-weight:800;color:#24272C}
.header .sub{font-size:14px;color:#5B606B;margin-top:3px}
.card{background:white;border:1px solid #E4E7EC;border-radius:16px;padding:15px 17px;
box-shadow:0 2px 10px rgba(0,0,0,.04);min-height:105px}
.lab{font-size:11px;font-weight:800;color:#737A86;letter-spacing:.5px}
.val{font-size:25px;font-weight:800;color:#24272C;margin-top:5px}
.subv{font-size:12px;color:#737A86;margin-top:1px}
.section{font-size:19px;font-weight:800;color:#24272C;margin:22px 0 8px}
.badge{display:inline-block;padding:5px 10px;border-radius:20px;font-size:12px;font-weight:800}
</style>
""",unsafe_allow_html=True)

st.markdown('<div class="header"><div class="title">Dashboard · Paquetes voluminosos</div><div class="sub">Business Case — Abril Nacif</div></div>',unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Vista")
    focus=st.radio("Escenario destacado",["5x","5,5x","6x"],index=1)
    st.markdown("### Mostrar")
    show_cost=st.checkbox("Costos",True)
    show_cap=st.checkbox("Capacidad",True)
    show_profit=st.checkbox("Rentabilidad",True)

cost,res,margin,monthly=metrics(focus)
be=REV/sum(NORMAL[e] for e in TRANS)

c1,c2,c3,c4,c5=st.columns(5)
kpis=[
    ("ESCENARIO",focus,"seleccionado"),
    ("REVENUE / PAQ.",ars(REV),"voluminoso"),
    ("COSTO INCREMENTAL",ars(cost),"transporte"),
    ("RESULTADO / PAQ.",ars(res),("positivo" if res>=0 else "negativo")),
    ("IMPACTO MENSUAL",(f"{monthly:+.1f} M").replace(".",","),f"margen {dec(margin)}%"),
]
for c,(lab,val,sub) in zip([c1,c2,c3,c4,c5],kpis):
    with c:
        st.markdown(f'<div class="card"><div class="lab">{lab}</div><div class="val">{val}</div><div class="subv">{sub}</div></div>',unsafe_allow_html=True)

if show_profit:
    st.markdown('<div class="section">Rentabilidad · comparación de todos los escenarios</div>',unsafe_allow_html=True)
    data=[]
    for s in FACTORS:
        co,re,ma,mo=metrics(s)
        data.append({"Escenario":s,"Resultado mensual":mo,"Resultado por paquete":re,"Margen":ma,"Costo incremental":co})
    df=pd.DataFrame(data)

    a,b=st.columns([1.35,1])
    with a:
        fig=go.Figure()
        fig.add_bar(
            x=df["Escenario"],y=df["Resultado mensual"],
            marker_color=[COLORS[s] for s in df["Escenario"]],
            text=[(f"{v:+.1f} M").replace(".",",") for v in df["Resultado mensual"]],
            textposition="outside",cliponaxis=False
        )
        fig.add_hline(y=0,line_width=1,line_color="#9AA0A8")
        fig.update_layout(height=360,margin=dict(l=15,r=15,t=25,b=10),showlegend=False,
                          xaxis_title="",yaxis_title="Resultado mensual ($M)",
                          plot_bgcolor="white",paper_bgcolor="white",
                          yaxis=dict(gridcolor="#EEF0F3",zeroline=False))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    with b:
        table=df[["Escenario","Costo incremental","Resultado por paquete","Margen"]].copy()
        table["Costo incremental"]=table["Costo incremental"].map(ars)
        table["Resultado por paquete"]=table["Resultado por paquete"].map(ars)
        table["Margen"]=table["Margen"].map(lambda x: dec(x)+"%")
        st.dataframe(table,hide_index=True,use_container_width=True,height=205)
        st.metric("Punto de equilibrio",f"{be:.2f}x".replace(".",","))

if show_cost:
    st.markdown('<div class="section">Costos por etapa · todos los escenarios</div>',unsafe_allow_html=True)

    # TRANSPORT COSTS ONLY: comparable scenario economics
    rows=[]
    for e in TRANS:
        row={"Etapa":e,"Normal":NORMAL[e]}
        for s,f in FACTORS.items(): row[s]=NORMAL[e]*f
        rows.append(row)
    tdf=pd.DataFrame(rows)

    fig=go.Figure()
    for s in ["Normal","5x","5,5x","6x"]:
        fig.add_bar(name=s,x=tdf["Etapa"],y=tdf[s],marker_color=COLORS[s],
                    text=[ars(v) for v in tdf[s]],textposition="outside",cliponaxis=False)
    fig.update_layout(barmode="group",height=390,margin=dict(l=15,r=15,t=30,b=10),
                      xaxis_title="",yaxis_title="$ por paquete",
                      legend=dict(orientation="h",y=1.12,x=.5,xanchor="center"),
                      plot_bgcolor="white",paper_bgcolor="white",
                      yaxis=dict(gridcolor="#EEF0F3"))
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    # Fixed centers: show average network cost separately, not zero
    xd_after=741000000/10050000
    sc_after=741500000/10050000
    fixed=pd.DataFrame({
        "Etapa":["XD","Service Center"],
        "Normal":[NORMAL["XD"],NORMAL["Service Center"]],
        "Con 50.000 voluminosos":[xd_after,sc_after],
        "Incremental proyecto":[0,0]
    })
    st.dataframe(
        fixed.style.format({
            "Normal":lambda x: "$"+f"{x:,.2f}".replace(",", "X").replace(".",",").replace("X","."),
            "Con 50.000 voluminosos":lambda x: "$"+f"{x:,.2f}".replace(",", "X").replace(".",",").replace("X","."),
            "Incremental proyecto":lambda x: ars(x)
        }),
        hide_index=True,use_container_width=True
    )

if show_cap:
    st.markdown('<div class="section">Capacidad equivalente por ruta · todos los escenarios</div>',unsafe_allow_html=True)
    rows=[]
    for e,n in CAP.items():
        row={"Etapa":e,"Normal":n}
        for s,f in FACTORS.items(): row[s]=n/f
        rows.append(row)
    capdf=pd.DataFrame(rows)

    fig=go.Figure()
    for s in ["Normal","5x","5,5x","6x"]:
        fig.add_bar(name=s,x=capdf["Etapa"],y=capdf[s],marker_color=COLORS[s],
                    text=[dec(v) for v in capdf[s]],textposition="outside",cliponaxis=False)
    fig.update_layout(barmode="group",height=390,margin=dict(l=15,r=15,t=30,b=10),
                      xaxis_title="",yaxis_title="Equivalentes por ruta",
                      legend=dict(orientation="h",y=1.12,x=.5,xanchor="center"),
                      plot_bgcolor="white",paper_bgcolor="white",
                      yaxis=dict(gridcolor="#EEF0F3"))
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
