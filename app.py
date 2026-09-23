import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Bulky | Control Tower", page_icon="📦", layout="wide", initial_sidebar_state="collapsed")

# ---------------- DATA ----------------
NORMAL={"Colecta":250000/280,"XD":741000000/10000000,"Media milla":900000/2100,
        "Service Center":741500000/10000000,"Última milla":150000/75}
TRANS=["Colecta","Media milla","Última milla"]
CAP={"Colecta":280,"Media milla":2100,"Última milla":75}
FACT={"5x":5.0,"5,5x":5.5,"6x":6.0}
REV=19000; VOL=50000
BLUE="#3483FA"; YELLOW="#FFE600"; GREEN="#00A650"; ORANGE="#F5A623"; RED="#E55353"; INK="#202124"; MUTED="#667085"
SCOL={"5x":GREEN,"5,5x":ORANGE,"6x":RED}

def ars(v):
    s=f"{abs(v):,.0f}".replace(",",".")
    return ("−" if v<0 else "")+"$"+s
def dec(v,n=1): return f"{v:.{n}f}".replace(".",",")
def met(s):
    f=FACT[s]; c=sum(NORMAL[e]*f for e in TRANS); r=REV-c
    return c,r,r/REV*100,r*VOL/1e6
be=REV/sum(NORMAL[e] for e in TRANS)

# ---------------- STYLE ----------------
st.markdown("""
<style>
:root{--ink:#202124;--muted:#667085;--line:#E8EAED;--soft:#F7F8FA}
html,body,[class*="css"]{font-family:Inter,Arial,sans-serif}
.stApp{background:#FFFFFF;color:#202124}
.block-container{max-width:1500px;padding:1.15rem 2rem 2.5rem}
header[data-testid="stHeader"]{background:rgba(255,255,255,.95)}
[data-testid="stSidebar"]{background:#FFFFFF}
h1,h2,h3,p{color:#202124}
.hero{display:flex;justify-content:space-between;align-items:center;background:#FFE600;border-radius:20px;padding:22px 28px;margin-bottom:16px}
.hero-title{font-size:30px;font-weight:850;letter-spacing:-.7px}
.hero-sub{font-size:13px;font-weight:600;color:#50545B;margin-top:4px}
.hero-pill{background:#202124;color:white;border-radius:999px;padding:9px 14px;font-size:12px;font-weight:750}
.section-title{font-size:19px;font-weight:850;margin:25px 0 3px;letter-spacing:-.25px}
.section-sub{font-size:12px;color:#667085;margin-bottom:10px}
.card{border:1px solid #E8EAED;border-radius:16px;padding:15px 17px;background:#FFF;min-height:102px}
.card.hot{border:2px solid #FFE600;box-shadow:0 5px 18px rgba(32,33,36,.07)}
.k-label{font-size:10px;font-weight:800;color:#7B8190;letter-spacing:.7px}
.k-val{font-size:25px;font-weight:850;margin-top:5px;color:#202124}
.k-sub{font-size:11px;color:#7B8190;margin-top:2px}
.scenario{border:1px solid #E8EAED;border-radius:17px;padding:17px 18px;background:#FFF}
.s-name{font-size:14px;font-weight:850}
.s-big{font-size:27px;font-weight:900;margin:6px 0 2px}
.s-row{display:flex;justify-content:space-between;border-top:1px solid #F0F1F3;padding:7px 0 0;margin-top:7px;font-size:12px}
.s-muted{color:#7B8190}
div[data-baseweb="select"] > div{background:white!important;color:#202124!important}
[data-testid="stDataFrame"]{border:1px solid #E8EAED;border-radius:14px;overflow:hidden}
</style>
""",unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown(f"""
<div class="hero">
  <div><div class="hero-title">Bulky · Control Tower</div>
  <div class="hero-sub">Business Case — Abril Nacif · 50.000 paquetes voluminosos / mes</div></div>
  <div class="hero-pill">Punto de equilibrio&nbsp;&nbsp;{dec(be,2)}x</div>
</div>""",unsafe_allow_html=True)

# Filter in main canvas, not invisible sidebar
fa,fb,fc=st.columns([1.1,1.2,3.7])
with fa:
    focus=st.selectbox("Escenario destacado",["5x","5,5x","6x"],index=1)
with fb:
    stage=st.selectbox("Etapa destacada",["Todas","Colecta","XD","Media milla","Service Center","Última milla"])
with fc:
    st.write("")

cost,res,margin,monthly=met(focus)

# ---------------- TOP KPIs ----------------
k=st.columns(5)
cards=[
("REVENUE / PAQ.",ars(REV),"tarifa seller"),
("COSTO INCREMENTAL",ars(cost),f"escenario {focus}"),
("RESULTADO / PAQ.",ars(res),f"margen {dec(margin)}%"),
("IMPACTO MENSUAL",(f"{monthly:+.1f} M").replace(".",","),"50.000 paquetes"),
("BREAK-EVEN",f"{dec(be,2)}x","consumo de capacidad"),
]
for col,(lab,val,sub) in zip(k,cards):
    with col:
        hot=' hot' if lab in ["RESULTADO / PAQ.","IMPACTO MENSUAL"] else ''
        st.markdown(f'<div class="card{hot}"><div class="k-label">{lab}</div><div class="k-val">{val}</div><div class="k-sub">{sub}</div></div>',unsafe_allow_html=True)

# ---------------- SCENARIO SCORECARDS ----------------
st.markdown('<div class="section-title">Escenarios · lectura ejecutiva</div><div class="section-sub">Los tres escenarios permanecen visibles; el selector solo destaca uno.</div>',unsafe_allow_html=True)
cols=st.columns(3)
for col,s in zip(cols,FACT):
    c,r,m,mo=met(s)
    border=SCOL[s]
    with col:
        st.markdown(f"""
        <div class="scenario" style="border-top:5px solid {border}">
          <div class="s-name">{s}</div>
          <div class="s-big" style="color:{border}">{ars(r)} <span style="font-size:13px;color:#7B8190">/ paq.</span></div>
          <div class="s-row"><span class="s-muted">Costo incremental</span><b>{ars(c)}</b></div>
          <div class="s-row"><span class="s-muted">Margen</span><b>{dec(m)}%</b></div>
          <div class="s-row"><span class="s-muted">Impacto mensual</span><b>{(f"{mo:+.1f} M").replace(".",",")}</b></div>
        </div>""",unsafe_allow_html=True)

# ---------------- PROFITABILITY ----------------
st.markdown('<div class="section-title">Rentabilidad · sensibilidad</div>',unsafe_allow_html=True)
sc=list(FACT.keys())
monthly_vals=[met(s)[3] for s in sc]
results=[met(s)[1] for s in sc]
margins=[met(s)[2] for s in sc]

left,right=st.columns([1.65,1])
with left:
    fig=go.Figure()
    fig.add_trace(go.Bar(x=sc,y=monthly_vals,
        marker_color=[SCOL[s] for s in sc],
        text=[(f"{v:+.1f} M").replace(".",",") for v in monthly_vals],
        textposition="outside",textfont=dict(size=15,color=INK),
        hovertemplate="<b>%{x}</b><br>Resultado mensual: %{y:.1f} M<extra></extra>"))
    fig.add_hline(y=0,line_width=1,line_color="#AEB4BD")
    fig.update_layout(height=340,margin=dict(l=10,r=10,t=30,b=15),showlegend=False,
        xaxis=dict(title="",tickfont=dict(size=13,color=INK),showgrid=False),
        yaxis=dict(title="Resultado mensual ($M)",gridcolor="#EEF0F3",zeroline=False,tickfont=dict(color=MUTED)),
        plot_bgcolor="white",paper_bgcolor="white",hoverlabel=dict(bgcolor="white",font_color=INK))
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with right:
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=[5,5.5,6],y=margins,mode="lines+markers+text",
        line=dict(color=BLUE,width=4),marker=dict(size=13,color=[SCOL[s] for s in sc]),
        text=[dec(v)+"%" for v in margins],textposition=["top center","top center","bottom center"],
        textfont=dict(size=14,color=INK),hovertemplate="Margen: %{y:.1f}%<extra></extra>"))
    fig.add_hline(y=0,line_width=1,line_color="#AEB4BD")
    fig.add_vline(x=be,line_dash="dash",line_color=INK,
                  annotation_text=f"Break-even {dec(be,2)}x",annotation_position="top")
    fig.update_layout(height=340,margin=dict(l=10,r=10,t=30,b=15),showlegend=False,
        xaxis=dict(title="Consumo de capacidad",tickvals=[5,5.5,6],ticktext=["5x","5,5x","6x"],showgrid=False),
        yaxis=dict(title="Margen incremental",ticksuffix="%",gridcolor="#EEF0F3",zeroline=False),
        plot_bgcolor="white",paper_bgcolor="white")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

# ---------------- COSTS ----------------
st.markdown('<div class="section-title">Costos · dónde se genera el impacto</div>',unsafe_allow_html=True)
transport_rows=[]
stages=TRANS if stage in ["Todas","XD","Service Center"] else [stage]
for e in stages:
    row={"Etapa":e,"Normal":NORMAL[e]}
    for s,f in FACT.items(): row[s]=NORMAL[e]*f
    transport_rows.append(row)
tdf=pd.DataFrame(transport_rows)

left,right=st.columns([1.7,1])
with left:
    fig=go.Figure()
    for s,color in [("Normal",BLUE),("5x",GREEN),("5,5x",ORANGE),("6x",RED)]:
        fig.add_trace(go.Bar(name=s,x=tdf["Etapa"],y=tdf[s],marker_color=color,
            hovertemplate=f"<b>{s}</b><br>%{{x}}: $%{{y:,.0f}}<extra></extra>"))
    fig.update_layout(barmode="group",height=360,margin=dict(l=10,r=10,t=30,b=15),
        legend=dict(orientation="h",y=1.14,x=.5,xanchor="center",font=dict(color=INK)),
        xaxis=dict(title="",tickfont=dict(color=INK)),yaxis=dict(title="$ / paquete",gridcolor="#EEF0F3"),
        plot_bgcolor="white",paper_bgcolor="white")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with right:
    xd_after=741000000/10050000; sc_after=741500000/10050000
    fixed=pd.DataFrame({
        "Centro":["XD","Service Center"],
        "Normal":[NORMAL["XD"],NORMAL["Service Center"]],
        "Con voluminosos":[xd_after,sc_after],
        "Incremental":[0,0]
    })
    fixed["Normal"]=fixed["Normal"].map(lambda x:"$"+dec(x,2))
    fixed["Con voluminosos"]=fixed["Con voluminosos"].map(lambda x:"$"+dec(x,2))
    fixed["Incremental"]=["$0","$0"]
    st.dataframe(fixed,hide_index=True,use_container_width=True,height=145)
    st.markdown("""
    <div style="display:flex;gap:8px;margin-top:8px">
      <span class="badge" style="background:#EEF5FF;color:#2366C7">Costo promedio ≠ $0</span>
      <span class="badge" style="background:#EAF8F0;color:#08783E">Incremental = $0*</span>
    </div>""",unsafe_allow_html=True)

# ---------------- CAPACITY ----------------
st.markdown('<div class="section-title">Capacidad · productividad por ruta</div>',unsafe_allow_html=True)
cap_stages=list(CAP) if stage not in CAP else [stage]
rows=[]
for e in cap_stages:
    row={"Etapa":e,"Normal":CAP[e]}
    for s,f in FACT.items(): row[s]=CAP[e]/f
    rows.append(row)
cdf=pd.DataFrame(rows)

fig=go.Figure()
for s,color in [("Normal",BLUE),("5x",GREEN),("5,5x",ORANGE),("6x",RED)]:
    fig.add_trace(go.Bar(name=s,x=cdf["Etapa"],y=cdf[s],marker_color=color,
        text=[dec(v) for v in cdf[s]],textposition="outside",cliponaxis=False,
        hovertemplate=f"<b>{s}</b><br>%{{x}}: %{{y:.1f}} equivalentes/ruta<extra></extra>"))
fig.update_layout(barmode="group",height=350,margin=dict(l=10,r=10,t=35,b=15),
    legend=dict(orientation="h",y=1.14,x=.5,xanchor="center",font=dict(color=INK)),
    xaxis=dict(title="",tickfont=dict(color=INK)),yaxis=dict(title="Equivalentes / ruta",gridcolor="#EEF0F3"),
    plot_bgcolor="white",paper_bgcolor="white")
st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

st.caption("* XD y Service Center: costo incremental $0 bajo el supuesto de capacidad ociosa. Sus costos promedio de red continúan existiendo.")
