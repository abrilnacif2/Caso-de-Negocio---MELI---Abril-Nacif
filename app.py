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
html,body,[class*="css"]{font-family:Inter,Arial,sans-serif;color:#202124!important}
.stApp{background:#FFFFFF;color:#202124}
.stMarkdown,.stMarkdown p,.stMarkdown span,label,[data-testid="stWidgetLabel"] p{color:#202124!important}
[data-testid="stCaptionContainer"] p{color:#5F6672!important}
[data-testid="stMetricLabel"] p,[data-testid="stMetricValue"]{color:#202124!important}
div[data-baseweb="select"] *{color:#FFFFFF!important}
div[data-baseweb="select"] > div{background:#292A30!important;border-color:#D9DCE2!important}
[data-baseweb="popover"] *{color:#202124!important}
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
  <div><div class="hero-title">Caso de negocio</div>
  <div class="hero-sub">Business Case — Abril Nacif · 50.000 paquetes voluminosos / mes</div></div>
  <div class="hero-pill">Punto de equilibrio&nbsp;&nbsp;{dec(be,2)}x</div>
</div>""",unsafe_allow_html=True)

# Filter in main canvas, not invisible sidebar
fa,fb,fc=st.columns([1.1,1.2,3.7])
with fa:
    focus=st.selectbox("Escenario",["Todos","5x","5,5x","6x"],index=0)
with fb:
    stage=st.selectbox("Etapa destacada",["Todas","Colecta","XD","Media milla","Service Center","Última milla"])
with fc:
    st.write("")

if focus=="Todos":
    cost=res=margin=monthly=None
else:
    cost,res,margin,monthly=met(focus)

# ---------------- TOP KPIs ----------------
k=st.columns(5)
if focus=="Todos":
    cards=[
    ("REVENUE / PAQ.",ars(REV),"voluminoso"),
    ("COSTO INCREMENTAL","$16.607 – $19.929","rango 5x–6x"),
    ("RESULTADO / PAQ.","+$2.393 → −$929","rango 5x–6x"),
    ("IMPACTO MENSUAL","+119,6 M → −46,4 M","50.000 paquetes"),
    ("BREAK-EVEN",f"{dec(be,2)}x","consumo de capacidad"),
    ]
else:
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
st.markdown('<div class="section-title">Escenarios</div>',unsafe_allow_html=True)
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


# ---------------- NORMAL VS BULKY ----------------
st.markdown('<div class="section-title">Normal vs. voluminoso</div>',unsafe_allow_html=True)

# Revenue is independent of the capacity scenario.
revcol, costcol = st.columns([0.82,1.7])
with revcol:
    st.markdown('<div class="section-sub">Revenue por paquete</div>',unsafe_allow_html=True)
    fig_rev=go.Figure()
    fig_rev.add_trace(go.Bar(
        x=["Normal","Voluminoso"],y=[3000,19000],
        marker_color=[BLUE,YELLOW],width=0.36,
        text=[ars(3000),ars(19000)],textposition="outside",cliponaxis=False
    ))
    fig_rev.update_layout(height=330,margin=dict(l=10,r=10,t=20,b=15),showlegend=False,
        xaxis=dict(title="",showgrid=False),yaxis=dict(title="$ / paquete",gridcolor="#EEF0F3",range=[0,22000]),
        plot_bgcolor="white",paper_bgcolor="white")
    st.plotly_chart(fig_rev,use_container_width=True,config={"displayModeBar":False})
    st.markdown('<div style="text-align:center;font-size:13px;color:#667085"><b style="color:#202124">6,33x</b> revenue · <b style="color:#202124">+$16.000</b> por paquete</div>',unsafe_allow_html=True)

with costcol:
    chosen_stages=list(NORMAL.keys()) if stage=="Todas" else [stage]
    st.markdown('<div class="section-sub">Costo por etapa</div>',unsafe_allow_html=True)
    xd_after=741000000/10050000; sc_after=741500000/10050000
    comp_rows=[]
    for e in chosen_stages:
        row={"Etapa":e,"Normal":NORMAL[e]}
        scenarios=list(FACT.keys()) if focus=="Todos" else [focus]
        for s in scenarios:
            if e in TRANS: row[s]=NORMAL[e]*FACT[s]
            elif e=="XD": row[s]=xd_after
            else: row[s]=sc_after
        comp_rows.append(row)
    comp=pd.DataFrame(comp_rows)
    fig_cmp=go.Figure()
    fig_cmp.add_trace(go.Bar(name="Normal",x=comp["Etapa"],y=comp["Normal"],marker_color=BLUE,width=0.13))
    for s in (list(FACT.keys()) if focus=="Todos" else [focus]):
        fig_cmp.add_trace(go.Bar(name=f"Voluminoso {s}",x=comp["Etapa"],y=comp[s],
                                 marker_color=SCOL[s],width=0.13))
    fig_cmp.update_layout(barmode="group",height=330,margin=dict(l=10,r=10,t=20,b=15),
        legend=dict(orientation="h",y=1.12,x=.5,xanchor="center"),
        xaxis=dict(title=""),yaxis=dict(title="$ / paquete",gridcolor="#EEF0F3"),
        plot_bgcolor="white",paper_bgcolor="white")
    st.plotly_chart(fig_cmp,use_container_width=True,config={"displayModeBar":False})

# ---------------- PROFITABILITY ----------------
st.markdown('<div class="section-title">Rentabilidad · sensibilidad</div>',unsafe_allow_html=True)
sc=list(FACT.keys())
sens=pd.DataFrame([{
    "Escenario":s,
    "Costo incremental":met(s)[0],
    "Resultado / paquete":met(s)[1],
    "Margen":met(s)[2],
    "Impacto mensual":met(s)[3]
} for s in sc])

left,right=st.columns([1.25,1])
with left:
    # Line is better than fat bars: ordered sensitivity from 5x to 6x
    fig=go.Figure()
    fig.add_trace(go.Scatter(
        x=[5,5.5,6],y=sens["Impacto mensual"],
        mode="lines+markers+text",
        line=dict(color=BLUE,width=4),
        marker=dict(size=14,color=[SCOL[s] for s in sc],line=dict(width=2,color="white")),
        text=[(f"{v:+.1f} M").replace(".",",") for v in sens["Impacto mensual"]],
        textposition=["top center","top center","bottom center"],
        textfont=dict(size=14,color=INK)
    ))
    fig.add_hline(y=0,line_width=1,line_color="#AEB4BD")
    fig.add_vline(x=be,line_dash="dash",line_color=INK,
                  annotation_text=f"Break-even {dec(be,2)}x",annotation_position="top")
    fig.update_layout(height=335,margin=dict(l=10,r=10,t=28,b=15),showlegend=False,
        xaxis=dict(title="Consumo de capacidad",tickvals=[5,5.5,6],ticktext=["5x","5,5x","6x"],
                   tickfont=dict(color=INK),showgrid=False),
        yaxis=dict(title="Resultado mensual ($M)",gridcolor="#EEF0F3",tickfont=dict(color=INK)),
        plot_bgcolor="white",paper_bgcolor="white")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with right:
    stab=sens.copy()
    stab["Costo incremental"]=stab["Costo incremental"].map(ars)
    stab["Resultado / paquete"]=stab["Resultado / paquete"].map(ars)
    stab["Margen"]=stab["Margen"].map(lambda x:dec(x)+"%")
    stab["Impacto mensual"]=stab["Impacto mensual"].map(lambda x:(f"{x:+.1f} M").replace(".",","))
    st.dataframe(stab,hide_index=True,use_container_width=True,height=205)

# ---------------- COSTS ----------------
st.markdown('<div class="section-title">Costos por etapa</div>',unsafe_allow_html=True)

xd_after=741000000/10050000
sc_after=741500000/10050000
selected_stages=list(NORMAL.keys()) if stage=="Todas" else [stage]
selected_scenarios=list(FACT.keys()) if focus=="Todos" else [focus]

cost_rows=[]
for e in selected_stages:
    row={"Etapa":e,"Normal":NORMAL[e]}
    for s in selected_scenarios:
        if e in TRANS:
            row[s]=NORMAL[e]*FACT[s]
        elif e=="XD":
            row[s]=xd_after
        else:
            row[s]=sc_after
    cost_rows.append(row)
if stage=="Todas":
    total={"Etapa":"TOTAL","Normal":sum(NORMAL.values())}
    for s in selected_scenarios:
        total[s]=sum(NORMAL[e]*FACT[s] for e in TRANS)+xd_after+sc_after
    cost_rows.append(total)
costdf=pd.DataFrame(cost_rows)

gc,tc=st.columns([1.25,1])
with gc:
    transport_stages=[e for e in selected_stages if e in TRANS]
    if transport_stages:
        fig=go.Figure()
        for s in selected_scenarios:
            vals=[NORMAL[e]*FACT[s] for e in transport_stages]
            fig.add_trace(go.Bar(name=s,y=transport_stages,x=vals,orientation="h",
                marker_color=SCOL[s],width=.16))
        fig.add_trace(go.Scatter(name="Normal",y=transport_stages,
            x=[NORMAL[e] for e in transport_stages],mode="markers",
            marker=dict(color=BLUE,size=13,symbol="diamond")))
        fig.update_layout(barmode="group",height=330,margin=dict(l=10,r=10,t=25,b=15),
            legend=dict(orientation="h",y=1.15,x=.5,xanchor="center",font=dict(color=INK)),
            xaxis=dict(title="$ / paquete",gridcolor="#EEF0F3",tickfont=dict(color=INK)),
            yaxis=dict(title="",tickfont=dict(color=INK,size=13)),
            plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    else:
        st.markdown('<div class="card"><div class="k-label">COSTO DE TRANSPORTE</div><div class="k-val">—</div><div class="k-sub">No aplica a centros fijos.</div></div>',unsafe_allow_html=True)
with tc:
    costtab=costdf.copy()
    for c in costtab.columns[1:]:
        costtab[c]=costtab[c].map(lambda x:"$"+f"{x:,.2f}".replace(",","X").replace(".",",").replace("X","."))
    st.dataframe(costtab,hide_index=True,use_container_width=True,height=min(245,45+35*len(costtab)))
    if stage=="Todas" or stage in ["XD","Service Center"]:
        centers=[e for e in selected_stages if e in ["XD","Service Center"]]
        if centers:
            incr=pd.DataFrame({"Etapa":centers,"Costo incremental proyecto":["$0"]*len(centers)})
            st.dataframe(incr,hide_index=True,use_container_width=True,height=45+35*len(incr))

# ---------------- CAPACITY ----------------
st.markdown('<div class="section-title">Capacidad equivalente por ruta</div>',unsafe_allow_html=True)
cap_stages=list(CAP) if stage=="Todas" else ([stage] if stage in CAP else [])
selected_scenarios=list(FACT.keys()) if focus=="Todos" else [focus]

if cap_stages:
    rows=[]
    for e in cap_stages:
        row={"Etapa":e,"Normal":CAP[e]}
        for s in selected_scenarios:
            row[s]=CAP[e]/FACT[s]
        rows.append(row)
    cdf=pd.DataFrame(rows)

    cg,ct=st.columns([1.0,1.15])
    with cg:
        # Relative capacity avoids misleading scale differences between route stages.
        labels=["Normal"]+selected_scenarios
        vals=[100]+[100/FACT[s] for s in selected_scenarios]
        cols=[BLUE]+[SCOL[s] for s in selected_scenarios]
        fig=go.Figure(go.Bar(
            y=labels,x=vals,orientation="h",marker_color=cols,width=.38,
            text=[num(v)+"%" for v in vals],textposition="inside",
            textfont=dict(color="white",size=13)
        ))
        fig.update_layout(height=245,margin=dict(l=10,r=15,t=20,b=15),showlegend=False,
            xaxis=dict(title="Capacidad relativa vs. normal",ticksuffix="%",range=[0,105],gridcolor="#EEF0F3"),
            yaxis=dict(title="",categoryorder="array",categoryarray=labels[::-1],tickfont=dict(color=INK,size=13)),
            plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    with ct:
        captab=cdf.copy()
        for c in captab.columns[1:]:
            captab[c]=captab[c].map(lambda x:num(x))
        st.dataframe(captab,hide_index=True,use_container_width=True,height=45+35*len(captab))
else:
    st.markdown('<div class="card"><div class="k-label">CAPACIDAD POR RUTA</div><div class="k-val">—</div><div class="k-sub">No aplica a centros fijos.</div></div>',unsafe_allow_html=True)

st.caption("* XD y Service Center: costo incremental $0 bajo el supuesto de capacidad ociosa. Sus costos promedio de red continúan existiendo.")
