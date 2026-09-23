import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

st.set_page_config(page_title="Caso de negocio | Abril Nacif", page_icon="📦", layout="wide", initial_sidebar_state="collapsed")

# =========================
# DATA MODEL
# =========================
NORMAL = {
    "Colecta": 250000/280,
    "XD": 741000000/10000000,
    "Media milla": 900000/2100,
    "Service Center": 741500000/10000000,
    "Última milla": 150000/75,
}
TRANS = ["Colecta", "Media milla", "Última milla"]
CAP = {"Colecta": 280, "Media milla": 2100, "Última milla": 75}
FACT = {"5x": 5.0, "5,5x": 5.5, "6x": 6.0}
REV_N, REV_V, VOL = 3000, 19000, 50000
XD_AFTER = 741000000/10050000
SC_AFTER = 741500000/10050000

INK="#111111"; SECONDARY="#3A3A3C"; GRID="#E5E5EA"; PANEL="#FFFFFF"; BG="#F5F5F7"
BLUE="#3483FA"; YELLOW="#FFE600"; GREEN="#00A650"; AMBER="#E8A329"; RED="#D9534F"; NAVY="#24364B"
SCOL={"5x":GREEN,"5,5x":AMBER,"6x":RED}

def ars(v,d=0):
    sign="−" if v < 0 else ""
    s=f"{abs(v):,.{d}f}".replace(",","X").replace(".",",").replace("X",".")
    return sign+"$"+s

def dec(v,d=1):
    return f"{v:.{d}f}".replace(".",",")

def cap_floor(v):
    return str(math.floor(v))

def transport_cost(s):
    return sum(NORMAL[e]*FACT[s] for e in TRANS)

def metrics(s):
    c=transport_cost(s)
    r=REV_V-c
    return c,r,r/REV_V*100,r*VOL/1e6

def stage_cost(e,s):
    if e in TRANS:
        return NORMAL[e]*FACT[s]
    return XD_AFTER if e=="XD" else SC_AFTER

def avg_total(s):
    return sum(stage_cost(e,s) for e in NORMAL)

BE = REV_V / sum(NORMAL[e] for e in TRANS)

# One single chart theme: NO light text on light backgrounds.
def executive_layout(fig, height=300, showlegend=True, margin=None):
    if margin is None:
        margin=dict(l=20,r=20,t=30,b=20)
    fig.update_layout(
        height=height,
        margin=margin,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, Arial, sans-serif", size=13, color="#111111"),
        title_font=dict(color="#111111"),
        legend=dict(
            orientation="h", y=1.10, x=0, xanchor="left",
            font=dict(size=12,color="#111111"),
            bgcolor="rgba(255,255,255,0)"
        ),
        showlegend=showlegend,
        hoverlabel=dict(bgcolor="#111111",font_color="#FFFFFF",font_size=12),
    )
    fig.update_xaxes(
        color="#111111",
        tickfont=dict(color="#111111",size=12),
        title_font=dict(color="#111111",size=12),
        gridcolor="#E5E5EA",
        zerolinecolor="#C7C7CC",
        linecolor="#C7C7CC"
    )
    fig.update_yaxes(
        color="#111111",
        tickfont=dict(color="#111111",size=12),
        title_font=dict(color="#111111",size=12),
        gridcolor="#E5E5EA",
        zerolinecolor="#C7C7CC",
        linecolor="#C7C7CC"
    )
    return fig

# =========================
# UI
# =========================
st.markdown("""
<style>
html,body,[class*="css"]{font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;color:#111!important}
.stApp{background:#F5F5F7}
.block-container{max-width:1440px;padding:1.2rem 2rem 3.5rem}
header[data-testid="stHeader"]{background:#F5F5F7}
#MainMenu,footer{visibility:hidden}

/* Every text element on a light surface is dark */
.stMarkdown,.stMarkdown p,.stMarkdown span,.stMarkdown div,
label,[data-testid="stWidgetLabel"] p,[data-testid="stCaptionContainer"] p,
[data-testid="stDataFrame"] * {color:#111!important}

.hero{
 background:#FFE600;border-radius:24px;padding:28px 32px;
 display:flex;align-items:center;justify-content:space-between;
 box-shadow:0 8px 30px rgba(0,0,0,.06);margin-bottom:18px
}
.hero-title{font-size:34px;font-weight:800;letter-spacing:-1.2px;color:#111!important;line-height:1}
.hero-sub{font-size:13px;font-weight:600;color:#111!important;margin-top:9px}
.hero-chip{background:#111;color:#fff!important;border-radius:999px;padding:10px 16px;font-size:12px;font-weight:750}
.hero-chip *{color:#fff!important}

div[data-baseweb="select"]>div{
 background:#fff!important;border:1px solid #D1D1D6!important;border-radius:12px!important;
 min-height:44px!important;box-shadow:none!important
}
div[data-baseweb="select"] *{color:#111!important}
[data-baseweb="popover"] *{color:#111!important}

.section-head{margin-top:38px;margin-bottom:14px}
.kicker{font-size:10px;font-weight:800;letter-spacing:1.35px;text-transform:uppercase;color:#111!important}
.h2{font-size:25px;font-weight:800;letter-spacing:-.6px;color:#111!important;margin-top:4px}
.deck{font-size:13px;color:#111!important;margin-top:4px}

.metric-card{
 background:#fff;border:1px solid #E5E5EA;border-radius:18px;padding:18px 20px;
 box-shadow:0 2px 10px rgba(0,0,0,.025);min-height:112px
}
.metric-label{font-size:10px;font-weight:800;letter-spacing:.8px;color:#111!important;text-transform:uppercase}
.metric-value{font-size:27px;font-weight:800;letter-spacing:-.5px;color:#111!important;margin-top:7px}
.metric-note{font-size:11px;color:#111!important;margin-top:3px}

.callout{
 background:#fff;border:1px solid #E5E5EA;border-radius:16px;padding:14px 16px;
 font-size:12px;color:#111!important
}
.callout b{color:#111!important}

[data-testid="stDataFrame"]{
 border:1px solid #E5E5EA;border-radius:14px;overflow:hidden;background:#fff;
 box-shadow:0 2px 10px rgba(0,0,0,.02)
}
</style>
""",unsafe_allow_html=True)

st.markdown(f"""
<div class="hero">
 <div>
   <div class="hero-title">Caso de negocio</div>
   <div class="hero-sub">Paquetes voluminosos · 50.000 unidades / mes · Abril Nacif</div>
 </div>
 <div class="hero-chip">PUNTO DE EQUILIBRIO&nbsp;&nbsp;{dec(BE,2)}x</div>
</div>
""",unsafe_allow_html=True)

f1,f2,_=st.columns([1.15,1.25,3.6])
with f1:
    focus=st.selectbox("Escenario",["Todos","5x","5,5x","6x"],0)
with f2:
    stage=st.selectbox("Etapa",["Todas","Colecta","XD","Media milla","Service Center","Última milla"],0)

scenarios=list(FACT) if focus=="Todos" else [focus]

# =========================
# 01 CAPACITY
# =========================
st.markdown("""
<div class="section-head">
 <div class="kicker">01 · Operación</div>
 <div class="h2">Capacidad</div>
 <div class="deck">Capacidad disponible por ruta al incorporar paquetes voluminosos.</div>
</div>
""",unsafe_allow_html=True)

cap_stages=list(CAP) if stage=="Todas" else ([stage] if stage in CAP else [])
if cap_stages:
    left,right=st.columns([1.05,1.25],gap="large")
    with left:
        labels=["Normal"]+scenarios
        values=[100]+[100/FACT[s] for s in scenarios]
        colors=[BLUE]+[SCOL[s] for s in scenarios]
        fig=go.Figure()
        for lab,val,col in zip(labels,values,colors):
            fig.add_trace(go.Bar(
                y=[lab],x=[val],orientation="h",width=.34,
                marker=dict(color=col,line=dict(width=0)),
                text=[dec(val)+"%"],textposition="outside",
                textfont=dict(color=INK,size=13),
                hovertemplate=f"<b>{lab}</b><br>{dec(val)}% de capacidad relativa<extra></extra>",
                showlegend=False
            ))
        executive_layout(fig,255,False,dict(l=10,r=60,t=10,b=28))
        fig.update_xaxes(title="Capacidad relativa vs. normal",range=[0,108],ticksuffix="%",dtick=20)
        fig.update_yaxes(title="",categoryorder="array",categoryarray=labels[::-1],showgrid=False)
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    with right:
        rows=[]
        for e in cap_stages:
            row={"Etapa":e,"Normal":str(CAP[e])}
            for s in scenarios:
                row[s]=cap_floor(CAP[e]/FACT[s])
            rows.append(row)
        st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True,height=45+35*len(rows))
else:
    st.markdown('<div class="callout"><b>No aplica:</b> la capacidad por ruta corresponde a Colecta, Media milla y Última milla.</div>',unsafe_allow_html=True)

# =========================
# 02 COSTS
# =========================
st.markdown("""
<div class="section-head">
 <div class="kicker">02 · Economía</div>
 <div class="h2">Costos por etapa</div>
 <div class="deck">Costo promedio por paquete y variación respecto de un paquete normal.</div>
</div>
""",unsafe_allow_html=True)

selected_stages=list(NORMAL) if stage=="Todas" else [stage]
rows=[]
for e in selected_stages:
    row={"Etapa":e,"Normal":NORMAL[e]}
    for s in scenarios:
        row[s]=stage_cost(e,s)
        # Variation vs normal: transport +450/+500%; fixed centers slightly dilute.
        row[f"Var. {s}"]=(stage_cost(e,s)/NORMAL[e]-1)*100
    rows.append(row)

if stage=="Todas":
    total={"Etapa":"TOTAL","Normal":sum(NORMAL.values())}
    for s in scenarios:
        total[s]=avg_total(s)
        total[f"Var. {s}"]=(avg_total(s)/sum(NORMAL.values())-1)*100
    rows.append(total)

costdf=pd.DataFrame(rows)

# Executive total-cost comparison: slim bars + explicit delta vs normal
left,right=st.columns([1.0,1.35],gap="large")
with left:
    labels=["Normal"]+scenarios
    totals=[sum(NORMAL.values())]+[avg_total(s) for s in scenarios]
    colors=[BLUE]+[SCOL[s] for s in scenarios]
    texts=[ars(totals[0])]
    for s,v in zip(scenarios,totals[1:]):
        var=(v/totals[0]-1)*100
        texts.append(f"{ars(v)}<br><b>+{dec(var,1)}%</b>")
    fig=go.Figure(go.Bar(
        x=labels,y=totals,width=.26,marker_color=colors,
        text=texts,textposition="outside",
        textfont=dict(color=INK,size=12),cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Costo total: $%{y:,.0f}/paq.<extra></extra>"
    ))
    executive_layout(fig,315,False,dict(l=10,r=10,t=42,b=20))
    fig.update_yaxes(title="$ / paquete",rangemode="tozero")
    fig.update_xaxes(title="",showgrid=False)
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

with right:
    # Display interleaved scenario and variation columns
    d=costdf.copy()
    for c in d.columns:
        if c=="Etapa": continue
        if c.startswith("Var."):
            d[c]=d[c].map(lambda x:("+" if x>=0 else "")+dec(x,1)+"%")
        else:
            d[c]=d[c].map(lambda x:ars(x,2))
    st.dataframe(d,hide_index=True,use_container_width=True,height=min(315,45+35*len(d)))

# Cost composition: donuts are better here because the question is "what makes up the total?"
if stage=="Todas":
    st.markdown('<div style="font-size:15px;font-weight:800;color:#111;margin:18px 0 6px;">Composición del costo por escenario</div>',unsafe_allow_html=True)
    donut_scenarios=["Normal"]+scenarios
    cols=st.columns(len(donut_scenarios))
    stage_colors=["#5AC8FA","#D7D9DE","#FF9F0A","#BFC3CA","#24364B"]
    for col,sc in zip(cols,donut_scenarios):
        with col:
            if sc=="Normal":
                vals=[NORMAL[e] for e in NORMAL]
                total_val=sum(vals)
            else:
                vals=[stage_cost(e,sc) for e in NORMAL]
                total_val=sum(vals)
            fig=go.Figure(go.Pie(
                labels=list(NORMAL.keys()), values=vals, hole=.70,
                marker=dict(colors=stage_colors,line=dict(color="#FFFFFF",width=2)),
                sort=False,
                textinfo="none",
                hovertemplate="<b>%{label}</b><br>$%{value:,.0f}/paq.<br>%{percent}<extra></extra>"
            ))
            fig.add_annotation(
                x=.5,y=.53,text=f"<b>{sc}</b><br>{ars(total_val)}",
                showarrow=False,font=dict(size=14,color=INK),align="center"
            )
            executive_layout(fig,235,False,dict(l=5,r=5,t=5,b=5))
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    # Compact legend shared by all donuts
    st.markdown(
        '<div style="display:flex;justify-content:center;gap:22px;flex-wrap:wrap;font-size:11px;color:#111;margin-top:-8px;">'
        '<span>● <b>Colecta</b></span><span>● XD</span><span>● <b>Media milla</b></span>'
        '<span>● Service Center</span><span>● <b>Última milla</b></span></div>',
        unsafe_allow_html=True
    )

if stage=="Todas" or stage in ["XD","Service Center"]:
    centers=["XD","Service Center"] if stage=="Todas" else [stage]
    fixed=pd.DataFrame({
        "Centro":centers,
        "Costo promedio normal":[ars(NORMAL[e],2) for e in centers],
        "Promedio con voluminosos":[ars(XD_AFTER,2) if e=="XD" else ars(SC_AFTER,2) for e in centers],
        "Variación":[
            dec(((XD_AFTER/NORMAL["XD"])-1)*100,1)+"%" if e=="XD"
            else dec(((SC_AFTER/NORMAL["Service Center"])-1)*100,1)+"%"
            for e in centers
        ],
        "Costo incremental proyecto":["$0"]*len(centers)
    })
    st.dataframe(fixed,hide_index=True,use_container_width=True,height=45+35*len(fixed))

# =========================
# 03 REVENUE
# =========================
st.markdown("""
<div class="section-head">
 <div class="kicker">03 · Monetización</div>
 <div class="h2">Revenue</div>
 <div class="deck">Ingreso por paquete: normal vs. voluminoso.</div>
</div>
""",unsafe_allow_html=True)

left,right=st.columns([1.2,1],gap="large")
with left:
    fig=go.Figure(go.Bar(
        y=["Normal","Voluminoso"],x=[REV_N,REV_V],orientation="h",width=.38,
        marker_color=[BLUE,YELLOW],
        text=[ars(REV_N),ars(REV_V)],textposition="outside",
        textfont=dict(color=INK,size=14),cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}/paq.<extra></extra>"
    ))
    executive_layout(fig,225,False,dict(l=10,r=65,t=10,b=25))
    fig.update_xaxes(title="$ / paquete",range=[0,22000])
    fig.update_yaxes(title="",showgrid=False)
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with right:
    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div class="metric-card"><div class="metric-label">Diferencia / paquete</div><div class="metric-value">+$16.000</div><div class="metric-note">voluminoso vs. normal</div></div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><div class="metric-label">Revenue relativo</div><div class="metric-value">6,33x</div><div class="metric-note">variación +533% vs. normal</div></div>',unsafe_allow_html=True)

# =========================
# 04 SENSITIVITY
# =========================
st.markdown("""
<div class="section-head">
 <div class="kicker">04 · Decisión</div>
 <div class="h2">Sensibilidad y rentabilidad</div>
 <div class="deck">Impacto económico ante distintos niveles de consumo de capacidad.</div>
</div>
""",unsafe_allow_html=True)

sens=pd.DataFrame([{
    "Escenario":s,
    "Costo incremental":metrics(s)[0],
    "Resultado / paquete":metrics(s)[1],
    "Margen":metrics(s)[2],
    "Impacto mensual":metrics(s)[3]
} for s in FACT])

left,right=st.columns([1.2,1],gap="large")
with left:
    fig=go.Figure(go.Scatter(
        x=[5,5.5,6],y=sens["Impacto mensual"],
        mode="lines+markers",
        line=dict(color=INK,width=3),
        marker=dict(size=14,color=[SCOL[s] for s in FACT],line=dict(color="#FFFFFF",width=2)),
        hovertemplate="Resultado mensual: %{y:.1f} M<extra></extra>"
    ))
    for x,y in zip([5,5.5,6],sens["Impacto mensual"]):
        fig.add_annotation(
            x=x,y=y,text=(f"<b>{y:+.1f} M</b>").replace(".",","),
            showarrow=False,yshift=18 if y>=0 else -18,
            font=dict(size=13,color=INK)
        )
    fig.add_hline(y=0,line_color="#8E8E93",line_width=1)
    fig.add_vline(
        x=BE,line_dash="dash",line_color=RED,line_width=2,
        annotation_text=f"Break-even {dec(BE,2)}x",
        annotation_position="top",
        annotation_font=dict(color=INK,size=12)
    )
    executive_layout(fig,320,False,dict(l=10,r=10,t=35,b=20))
    fig.update_xaxes(title="Consumo de capacidad",tickvals=[5,5.5,6],ticktext=["5x","5,5x","6x"],showgrid=False)
    fig.update_yaxes(title="Resultado mensual ($M)")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with right:
    d=sens.copy()
    d["Costo incremental"]=d["Costo incremental"].map(ars)
    d["Resultado / paquete"]=d["Resultado / paquete"].map(ars)
    d["Margen"]=d["Margen"].map(lambda x:dec(x)+"%")
    d["Impacto mensual"]=d["Impacto mensual"].map(lambda x:(f"{x:+.1f} M").replace(".",","))
    st.dataframe(d,hide_index=True,use_container_width=True,height=180)
