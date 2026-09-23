import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Caso de negocio | Abril Nacif", page_icon="📦", layout="wide", initial_sidebar_state="collapsed")

# ==================== MODEL ====================
NORMAL={"Colecta":250000/280,"XD":741000000/10000000,"Media milla":900000/2100,
        "Service Center":741500000/10000000,"Última milla":150000/75}
CAP={"Colecta":280,"Media milla":2100,"Última milla":75}
TRANS=["Colecta","Media milla","Última milla"]
FACT={"5x":5.0,"5,5x":5.5,"6x":6.0}
REV_N,REV_V,VOL=3000,19000,50000
XD_AFTER=741000000/10050000
SC_AFTER=741500000/10050000

C={
"ink":"#202124","muted":"#69707D","line":"#E9EBEF","soft":"#F7F8FA",
"yellow":"#FFE600","blue":"#3483FA","green":"#00A650","amber":"#E8A329","red":"#D9534F",
"navy":"#26364A","cyan":"#57B7E8"
}
SCOL={"5x":C["green"],"5,5x":C["amber"],"6x":C["red"]}

def ars(v,d=0):
    sign="−" if v<0 else ""
    s=f"{abs(v):,.{d}f}".replace(",","X").replace(".",",").replace("X",".")
    return sign+"$"+s
def n(v,d=1): return f"{v:.{d}f}".replace(".",",")
def cap_floor(v):
    # Capacity is operational: if a fraction appears, use only complete equivalent packages.
    return str(int(v // 1))
def transport(s): return sum(NORMAL[e]*FACT[s] for e in TRANS)
def met(s):
    cost=transport(s); res=REV_V-cost
    return cost,res,res/REV_V*100,res*VOL/1e6
def stage_cost(e,s):
    if e in TRANS:return NORMAL[e]*FACT[s]
    return XD_AFTER if e=="XD" else SC_AFTER
def total_avg(s): return sum(stage_cost(e,s) for e in NORMAL)
BE=REV_V/sum(NORMAL[e] for e in TRANS)

PLOT_FONT=dict(family="Inter, Arial, sans-serif",color="#111318",size=12)


# ==================== CSS ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',Arial,sans-serif;color:#202124!important}
.stApp{background:#FBFBFC}
.block-container{max-width:1480px;padding:1.1rem 2.1rem 3rem}
header[data-testid="stHeader"]{background:rgba(251,251,252,.95)}
.stMarkdown p,.stMarkdown span,label,[data-testid="stWidgetLabel"] p{color:#202124!important}
[data-testid="stCaptionContainer"] p{color:#69707D!important}
div[data-baseweb="select"]>div{background:#fff!important;border:1px solid #DDE0E5!important;border-radius:10px!important}
div[data-baseweb="select"] *{color:#111318!important}
.hero{background:#FFE600;border-radius:22px;padding:24px 30px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 7px 22px rgba(32,33,36,.07)}
.hero h1{font-size:31px;line-height:1;margin:0;font-weight:800;letter-spacing:-.8px}
.hero p{margin:8px 0 0;font-size:13px;color:#4F545C!important;font-weight:500}
.pill{background:#202124;color:#fff!important;padding:9px 14px;border-radius:999px;font-size:12px;font-weight:700}
.eyebrow{font-size:10px;color:#7A818D!important;font-weight:800;letter-spacing:1.2px;text-transform:uppercase;margin-top:27px}
.title{font-size:23px;font-weight:800;letter-spacing:-.45px;margin:3px 0 2px}
.subtitle{font-size:12px;color:#69707D!important;margin-bottom:12px}
.kpi{background:#fff;border:1px solid #E7E9ED;border-radius:16px;padding:15px 17px;min-height:104px;box-shadow:0 2px 9px rgba(32,33,36,.025)}
.kpi .l{font-size:10px;color:#747B87!important;font-weight:800;letter-spacing:.7px}
.kpi .v{font-size:24px;font-weight:800;margin:5px 0 1px}
.kpi .s{font-size:11px;color:#747B87!important}
.panel{background:#fff;border:1px solid #E7E9ED;border-radius:18px;padding:15px 17px;box-shadow:0 3px 14px rgba(32,33,36,.035)}
.insight{background:#fff;border:1px solid #E7E9ED;border-radius:16px;padding:17px 18px;border-left:5px solid #FFE600;min-height:112px}
.insight .num{font-size:27px;font-weight:800;margin:5px 0 2px}
.insight .txt{font-size:11px;color:#69707D!important}
[data-testid="stDataFrame"]{border:1px solid #E7E9ED;border-radius:13px;overflow:hidden;background:white}
hr{border-color:#ECEEF1}
</style>

<style>
/* Maximum contrast on all light surfaces */
.stApp, .main, .block-container,
[data-testid="stAppViewContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"] { color:#111318 !important; }

h1,h2,h3,h4,h5,h6,p,span,label,div,
.stMarkdown, .stMarkdown p, .stMarkdown span,
[data-testid="stWidgetLabel"] p,
[data-testid="stCaptionContainer"] p {
    color:#111318 !important;
}

/* Keep only deliberately dark UI surfaces white */
.hero .pill, .hero .pill *,
div[data-baseweb="select"] > div,
div[data-baseweb="select"] > div * {
    color:#111318 !important;
}

/* Tables */
[data-testid="stDataFrame"] * {
    color:#111318 !important;
}

/* Cards */
.kpi .l,.kpi .v,.kpi .s,
.insight .lab,.insight .num,.insight .txt,
.eyebrow,.title,.subtitle {
    color:#111318 !important;
}
</style>

""",unsafe_allow_html=True)

# ==================== HEADER ====================
st.markdown(f"""
<div class="hero">
<div><h1>Caso de negocio</h1><p>Abril Nacif · Paquetes voluminosos · 50.000 unidades / mes</p></div>
<div class="pill">BREAK-EVEN&nbsp;&nbsp;{n(BE,2)}x</div>
</div>""",unsafe_allow_html=True)

a,b,_=st.columns([1.15,1.3,3.55])
with a: focus=st.selectbox("Escenario",["Todos","5x","5,5x","6x"],0)
with b: stage=st.selectbox("Etapa",["Todas","Colecta","XD","Media milla","Service Center","Última milla"],0)
scenarios=list(FACT) if focus=="Todos" else [focus]

# ==================== 01 CAPACITY ====================
st.markdown('<div class="eyebrow">01 · Operación</div><div class="title">Capacidad</div><div class="subtitle">Cuánto de la capacidad de una ruta normal consume un paquete voluminoso.</div>',unsafe_allow_html=True)

cap_stages=list(CAP) if stage=="Todas" else ([stage] if stage in CAP else [])
if cap_stages:
    left,right=st.columns([1.15,1])
    with left:
        # Executive dumbbell / benchmark chart: remaining route capacity relative to normal.
        labs=["Normal"]+scenarios
        vals=[100]+[100/FACT[s] for s in scenarios]
        cols=[C["blue"]]+[SCOL[s] for s in scenarios]
        fig=go.Figure()
        for i,(lab,val,col) in enumerate(zip(labs,vals,cols)):
            fig.add_trace(go.Scatter(x=[0,val],y=[lab,lab],mode="lines",
                line=dict(color="#E6E9ED",width=9),showlegend=False,hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=[val],y=[lab],mode="markers+text",
                marker=dict(size=18,color=col,line=dict(color="white",width=2)),
                text=[n(val)+"%"],textposition="middle right",
                textfont=dict(size=13,color=C["ink"]),showlegend=False,
                hovertemplate=f"<b>{lab}</b><br>{n(val)}% de capacidad relativa<extra></extra>"))
        fig.update_layout(font=PLOT_FONT,height=245,margin=dict(l=5,r=65,t=10,b=20),
            xaxis=dict(range=[0,108],ticksuffix="%",title="Capacidad relativa vs. normal",gridcolor="#F0F1F3",zeroline=False),
            yaxis=dict(title="",categoryorder="array",categoryarray=labs[::-1],tickfont=dict(size=13,color=C["ink"])),
            plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    with right:
        rows=[]
        for e in cap_stages:
            row={"Etapa":e,"Normal":CAP[e]}
            for s in scenarios: row[s]=CAP[e]/FACT[s]
            rows.append(row)
        d=pd.DataFrame(rows)
        for col in d.columns[1:]: d[col]=d[col].map(cap_floor)
        st.dataframe(d,hide_index=True,use_container_width=True,height=45+35*len(d))
else:
    st.info("La capacidad por ruta aplica a Colecta, Media milla y Última milla.")

# ==================== 02 COST ====================
st.markdown('<div class="eyebrow">02 · Economía</div><div class="title">Costos por etapa</div><div class="subtitle">Transporte + costos fijos de XD y Service Center. La tabla incluye el costo total.</div>',unsafe_allow_html=True)

selected_stages=list(NORMAL) if stage=="Todas" else [stage]
rows=[]
for e in selected_stages:
    row={"Etapa":e,"Normal":NORMAL[e]}
    for s in scenarios: row[s]=stage_cost(e,s)
    rows.append(row)
if stage=="Todas":
    total={"Etapa":"TOTAL","Normal":sum(NORMAL.values())}
    for s in scenarios: total[s]=total_avg(s)
    rows.append(total)
costdf=pd.DataFrame(rows)

# Visual first: waterfall-style cost composition for selected single scenario, or 3 total comparison cards when Todos
if focus=="Todos":
    c1,c2=st.columns([1.15,1])
    with c1:
        fig=go.Figure()
        totals=[sum(NORMAL.values())]+[total_avg(s) for s in FACT]
        labels=["Normal","5x","5,5x","6x"]
        colors=[C["blue"],C["green"],C["amber"],C["red"]]
        fig.add_trace(go.Bar(x=labels,y=totals,marker_color=colors,width=.42,
            text=[ars(v) for v in totals],textposition="outside",cliponaxis=False,
            hovertemplate="<b>%{x}</b><br>Costo total promedio: $%{y:,.0f}<extra></extra>"))
        fig.update_layout(font=PLOT_FONT,height=300,margin=dict(l=5,r=5,t=30,b=15),showlegend=False,
            xaxis=dict(title="",tickfont=dict(size=13,color=C["ink"])),
            yaxis=dict(title="$ / paquete",gridcolor="#F0F1F3",range=[0,max(totals)*1.18]),
            plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    with c2:
        # 100% cost mix: communicates concentration without scale clutter
        fig=go.Figure()
        for e,col in zip(TRANS,[C["cyan"],C["amber"],C["navy"]]):
            vals=[]
            for s in FACT:
                vals.append(NORMAL[e]*FACT[s]/transport(s)*100)
            fig.add_trace(go.Bar(name=e,x=list(FACT),y=vals,marker_color=col,
                                 hovertemplate=f"<b>{e}</b><br>%{{y:.1f}}% del transporte<extra></extra>"))
        fig.update_layout(barmode="stack",height=300,margin=dict(l=5,r=5,t=30,b=15),
            legend=dict(orientation="h",y=1.15,x=.5,xanchor="center"),
            xaxis=dict(title=""),yaxis=dict(title="Mix del costo de transporte",ticksuffix="%",range=[0,100],gridcolor="#F0F1F3"),
            plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
else:
    c1,c2=st.columns([1.2,1])
    with c1:
        s=focus
        # Waterfall shows how total is built
        labels=list(NORMAL.keys())+["TOTAL"]
        vals=[stage_cost(e,s) for e in NORMAL]
        fig=go.Figure(go.Waterfall(
            x=labels,y=vals+[0],measure=["relative"]*5+["total"],
            connector={"line":{"color":"#D8DCE2"}},
            increasing={"marker":{"color":C["blue"]}},
            totals={"marker":{"color":SCOL[s]}},
            text=[ars(v) for v in vals]+[ars(sum(vals))],textposition="outside"
        ))
        fig.update_layout(font=PLOT_FONT,height=310,margin=dict(l=5,r=5,t=25,b=15),showlegend=False,
            yaxis=dict(title="$ / paquete",gridcolor="#F0F1F3"),
            plot_bgcolor="white",paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    with c2:
        vals=[NORMAL[e]*FACT[s] for e in TRANS]
        total_t=sum(vals)
        fig=go.Figure(go.Pie(labels=TRANS,values=vals,hole=.66,
            marker=dict(colors=[C["cyan"],C["amber"],C["navy"]]),
            textinfo="percent",textfont=dict(size=13),
            hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>"))
        fig.add_annotation(text=f"<b>{ars(total_t)}</b><br><span style='font-size:11px'>transporte</span>",
                           x=.5,y=.5,showarrow=False,font=dict(size=17,color=C["ink"]))
        fig.update_layout(font=PLOT_FONT,height=310,margin=dict(l=5,r=5,t=20,b=15),
            legend=dict(orientation="h",y=1.08,x=.5,xanchor="center"),paper_bgcolor="white")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

disp=costdf.copy()
for col in disp.columns[1:]: disp[col]=disp[col].map(lambda x:ars(x,2))
st.dataframe(disp,hide_index=True,use_container_width=True,height=min(300,45+35*len(disp)))

if stage=="Todas" or stage in ["XD","Service Center"]:
    centers=["XD","Service Center"] if stage=="Todas" else [stage]
    fixed=pd.DataFrame({
        "Centro":centers,
        "Costo promedio normal":[ars(NORMAL[e],2) for e in centers],
        "Costo promedio con voluminosos":[ars(XD_AFTER,2) if e=="XD" else ars(SC_AFTER,2) for e in centers],
        "Costo incremental del proyecto":["$0"]*len(centers)
    })
    st.dataframe(fixed,hide_index=True,use_container_width=True,height=45+35*len(fixed))

# ==================== 03 REVENUE ====================
st.markdown('<div class="eyebrow">03 · Monetización</div><div class="title">Revenue</div><div class="subtitle">Ingreso por paquete cobrado al seller.</div>',unsafe_allow_html=True)
r1,r2=st.columns([1.2,1])
with r1:
    # Bullet comparison, cleaner than columns
    fig=go.Figure()
    fig.add_trace(go.Bar(y=["Revenue"],x=[REV_V],orientation="h",marker_color=C["yellow"],width=.34,
                         text=[ars(REV_V)],textposition="inside",textfont=dict(color=C["ink"],size=15),
                         name="Voluminoso"))
    fig.add_trace(go.Scatter(y=["Revenue"],x=[REV_N],mode="markers",
        marker=dict(symbol="line-ns-open",size=34,color=C["blue"],line=dict(width=5,color=C["blue"])),
        name="Normal",hovertemplate=f"Normal: {ars(REV_N)}<extra></extra>"))
    fig.update_layout(font=PLOT_FONT,height=190,margin=dict(l=5,r=20,t=30,b=20),
        xaxis=dict(title="$ / paquete",range=[0,21000],gridcolor="#F0F1F3"),
        yaxis=dict(title="",showticklabels=False),
        legend=dict(orientation="h",y=1.2,x=.5,xanchor="center"),plot_bgcolor="white",paper_bgcolor="white")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with r2:
    k1,k2=st.columns(2)
    with k1: st.markdown('<div class="kpi"><div class="l">DIFERENCIA / PAQ.</div><div class="v">+$16.000</div><div class="s">voluminoso vs. normal</div></div>',unsafe_allow_html=True)
    with k2: st.markdown('<div class="kpi"><div class="l">REVENUE RELATIVO</div><div class="v">6,33x</div><div class="s">+$533% vs. normal</div></div>',unsafe_allow_html=True)

# ==================== 04 SENSITIVITY ====================
st.markdown('<div class="eyebrow">04 · Decisión</div><div class="title">Sensibilidad y rentabilidad</div><div class="subtitle">Cómo cambia el resultado cuando aumenta el consumo de capacidad.</div>',unsafe_allow_html=True)
sens=pd.DataFrame([{"Escenario":s,"Costo incremental":met(s)[0],"Resultado / paquete":met(s)[1],
                    "Margen":met(s)[2],"Impacto mensual":met(s)[3]} for s in FACT])
s1,s2=st.columns([1.2,1])
with s1:
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=[5,5.5,6],y=sens["Impacto mensual"],mode="lines+markers",
        line=dict(color=C["ink"],width=3),marker=dict(size=15,color=[SCOL[s] for s in FACT],line=dict(color="white",width=2)),
        fill="tozeroy",fillcolor="rgba(52,131,250,.06)",
        hovertemplate="Resultado mensual: %{y:.1f} M<extra></extra>"))
    for x,y,s in zip([5,5.5,6],sens["Impacto mensual"],FACT):
        fig.add_annotation(x=x,y=y,text=(f"<b>{y:+.1f} M</b>").replace(".",","),showarrow=False,
                           yshift=18 if y>=0 else -20,font=dict(size=13,color=C["ink"]))
    fig.add_hline(y=0,line_color="#AEB4BD",line_width=1)
    fig.add_vline(x=BE,line_dash="dash",line_color=C["red"],
                  annotation_text=f"Break-even {n(BE,2)}x",annotation_position="top")
    fig.update_layout(font=PLOT_FONT,height=320,margin=dict(l=5,r=5,t=30,b=15),showlegend=False,
        xaxis=dict(title="Consumo de capacidad",tickvals=[5,5.5,6],ticktext=["5x","5,5x","6x"],showgrid=False),
        yaxis=dict(title="Resultado mensual ($M)",gridcolor="#F0F1F3"),
        plot_bgcolor="white",paper_bgcolor="white")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with s2:
    d=sens.copy()
    d["Costo incremental"]=d["Costo incremental"].map(ars)
    d["Resultado / paquete"]=d["Resultado / paquete"].map(ars)
    d["Margen"]=d["Margen"].map(lambda x:n(x)+"%")
    d["Impacto mensual"]=d["Impacto mensual"].map(lambda x:(f"{x:+.1f} M").replace(".",","))
    st.dataframe(d,hide_index=True,use_container_width=True,height=180)

# ==================== 05 CONTROL DRIVERS ====================
st.markdown('<div class="eyebrow">05 · Management view</div><div class="title">Drivers de control</div><div class="subtitle">Los indicadores que más condicionan la decisión de escalar.</div>',unsafe_allow_html=True)
m55=met("5,5x")
lm_share=NORMAL["Última milla"]*5.5/m55[0]*100
cards=st.columns(4)
drivers=[
("ÚLTIMA MILLA",n(lm_share)+"%","del costo incremental de transporte"),
("HEADROOM · 5,5x",ars(m55[1]),"resultado incremental por paquete"),
("BREAK-EVEN",n(BE,2)+"x","límite económico bajo supuestos base"),
("SENSIBILIDAD","16,4 p.p.","caída de margen entre 5x y 6x")
]
for col,(lab,val,txt) in zip(cards,drivers):
    with col:
        st.markdown(f'<div class="insight"><div class="lab">{lab}</div><div class="num">{val}</div><div class="txt">{txt}</div></div>',unsafe_allow_html=True)

st.caption("* XD y Service Center: costo incremental $0 bajo el supuesto de capacidad ociosa. Sus costos promedio de red continúan existiendo.")
