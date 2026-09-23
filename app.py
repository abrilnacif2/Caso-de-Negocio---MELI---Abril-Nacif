import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Caso de negocio | Abril Nacif", page_icon="📦", layout="wide", initial_sidebar_state="collapsed")

# ---------------- DATOS ----------------
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

BLUE = "#3483FA"
YELLOW = "#FFE600"
GREEN = "#00A650"
ORANGE = "#F2A93B"
RED = "#D95B57"
INK = "#24272C"
MUTED = "#59616E"
LINE = "#E7E9ED"
SCOL = {"5x": GREEN, "5,5x": ORANGE, "6x": RED}

XD_AFTER = 741000000/10050000
SC_AFTER = 741500000/10050000

def ars(x, d=0):
    sign = "−" if x < 0 else ""
    s = f"{abs(x):,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return sign + "$" + s

def dec(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")

def transport_cost(s):
    return sum(NORMAL[e] * FACT[s] for e in TRANS)

def metrics(s):
    c = transport_cost(s)
    r = REV_V - c
    return c, r, r/REV_V*100, r*VOL/1e6

def avg_stage_cost(e, s):
    if e in TRANS:
        return NORMAL[e] * FACT[s]
    return XD_AFTER if e == "XD" else SC_AFTER

def avg_total_cost(s):
    return sum(avg_stage_cost(e, s) for e in NORMAL)

BE = REV_V / sum(NORMAL[e] for e in TRANS)

# ---------------- ESTILO ----------------
st.markdown("""
<style>
html, body, [class*="css"] {font-family: Inter, Arial, sans-serif; color:#24272C !important;}
.stApp {background:#FFFFFF;}
.block-container {max-width:1480px; padding:1.1rem 2rem 3rem;}
header[data-testid="stHeader"] {background:#FFFFFF;}
.stMarkdown p, .stMarkdown span, label, [data-testid="stWidgetLabel"] p {color:#24272C !important;}
[data-testid="stCaptionContainer"] p {color:#59616E !important;}
div[data-baseweb="select"] > div {background:#292A30 !important; border-color:#292A30 !important;}
div[data-baseweb="select"] * {color:white !important;}
[data-baseweb="popover"] * {color:#24272C !important;}
.hero {display:flex; justify-content:space-between; align-items:center; background:#FFE600; border-radius:20px; padding:22px 28px; margin-bottom:18px;}
.hero-title {font-size:31px; font-weight:900; letter-spacing:-.7px;}
.hero-sub {font-size:13px; font-weight:650; color:#50545B !important; margin-top:4px;}
.hero-pill {background:#24272C; color:white !important; border-radius:999px; padding:9px 15px; font-size:12px; font-weight:800;}
.section {font-size:21px; font-weight:900; margin:30px 0 3px; letter-spacing:-.3px;}
.sub {font-size:12px; color:#59616E !important; margin-bottom:11px;}
.card {background:white; border:1px solid #E7E9ED; border-radius:16px; padding:15px 17px; min-height:100px;}
.lab {font-size:10px; font-weight:850; color:#68707D !important; letter-spacing:.65px;}
.val {font-size:24px; font-weight:900; color:#24272C !important; margin-top:5px;}
.mini {font-size:11px; color:#68707D !important; margin-top:2px;}
.driver {border:1px solid #E7E9ED; border-top:5px solid #FFE600; border-radius:16px; padding:17px; min-height:120px;}
.driver-val {font-size:27px; font-weight:900; margin:6px 0;}
[data-testid="stDataFrame"] {border:1px solid #E7E9ED; border-radius:13px; overflow:hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- CABECERA / FILTROS ----------------
st.markdown(f"""
<div class="hero">
  <div>
    <div class="hero-title">Caso de negocio</div>
    <div class="hero-sub">Abril Nacif · Paquetes voluminosos · 50.000 unidades / mes</div>
  </div>
  <div class="hero-pill">Punto de equilibrio&nbsp;&nbsp;{dec(BE,2)}x</div>
</div>
""", unsafe_allow_html=True)

f1, f2, _ = st.columns([1.15, 1.25, 3.6])
with f1:
    focus = st.selectbox("Escenario", ["Todos", "5x", "5,5x", "6x"], index=0)
with f2:
    stage = st.selectbox("Etapa", ["Todas", "Colecta", "XD", "Media milla", "Service Center", "Última milla"], index=0)

scenarios = list(FACT) if focus == "Todos" else [focus]

# =========================================================
# 1 CAPACIDAD
# =========================================================
st.markdown('<div class="section">1 · Capacidad</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Capacidad equivalente por ruta según consumo de capacidad.</div>', unsafe_allow_html=True)

cap_stages = list(CAP) if stage == "Todas" else ([stage] if stage in CAP else [])
if cap_stages:
    rows = []
    for e in cap_stages:
        row = {"Etapa": e, "Normal": CAP[e]}
        for s in scenarios:
            row[s] = CAP[e] / FACT[s]
        rows.append(row)
    capdf = pd.DataFrame(rows)

    left, right = st.columns([1.0, 1.35])
    with left:
        labels = ["Normal"] + scenarios
        values = [100] + [100/FACT[s] for s in scenarios]
        colors = [BLUE] + [SCOL[s] for s in scenarios]
        fig = go.Figure(go.Bar(
            y=labels, x=values, orientation="h", marker_color=colors, width=.34,
            text=[dec(v)+"%" for v in values], textposition="inside",
            textfont=dict(color="white", size=13)
        ))
        fig.update_layout(
            height=255, margin=dict(l=10,r=15,t=15,b=15), showlegend=False,
            xaxis=dict(title="Capacidad relativa vs. normal", ticksuffix="%", range=[0,105], gridcolor="#EEF0F3"),
            yaxis=dict(title="", categoryorder="array", categoryarray=labels[::-1], tickfont=dict(color=INK,size=13)),
            plot_bgcolor="white", paper_bgcolor="white"
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with right:
        d = capdf.copy()
        for c in d.columns[1:]:
            d[c] = d[c].map(lambda x: dec(x))
        st.dataframe(d, hide_index=True, use_container_width=True, height=45+35*len(d))
else:
    st.markdown('<div class="card"><div class="lab">CAPACIDAD POR RUTA</div><div class="val">No aplica</div><div class="mini">XD y Service Center son centros fijos.</div></div>', unsafe_allow_html=True)

# =========================================================
# 2 COSTOS
# =========================================================
st.markdown('<div class="section">2 · Costos por etapa</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Transporte + costos fijos de XD y Service Center.</div>', unsafe_allow_html=True)

selected_stages = list(NORMAL) if stage == "Todas" else [stage]
cost_rows = []
for e in selected_stages:
    row = {"Etapa": e, "Normal": NORMAL[e]}
    for s in scenarios:
        row[s] = avg_stage_cost(e, s)
    cost_rows.append(row)

if stage == "Todas":
    total = {"Etapa":"TOTAL", "Normal":sum(NORMAL.values())}
    for s in scenarios:
        total[s] = avg_total_cost(s)
    cost_rows.append(total)

costdf = pd.DataFrame(cost_rows)
disp = costdf.copy()
for c in disp.columns[1:]:
    disp[c] = disp[c].map(lambda x: ars(x,2))
st.dataframe(disp, hide_index=True, use_container_width=True, height=min(310,45+35*len(disp)))

transport_stages = [e for e in selected_stages if e in TRANS]
if transport_stages:
    left, right = st.columns([1.35, .9])
    with left:
        # Stacked composition answers "where is the cost?"
        fig = go.Figure()
        for e, color in zip(TRANS, [GREEN, ORANGE, RED]):
            if e in transport_stages:
                vals = [NORMAL[e]] + [NORMAL[e]*FACT[s] for s in scenarios]
                fig.add_trace(go.Bar(
                    name=e, x=["Normal"]+scenarios, y=vals,
                    marker_color=color,
                    hovertemplate=f"<b>{e}</b><br>$%{{y:,.0f}} / paq.<extra></extra>"
                ))
        fig.update_layout(
            barmode="stack", height=320, margin=dict(l=10,r=10,t=25,b=15),
            legend=dict(orientation="h", y=1.14, x=.5, xanchor="center", font=dict(color=INK)),
            xaxis=dict(title="", tickfont=dict(color=INK)),
            yaxis=dict(title="$ / paquete", gridcolor="#EEF0F3"),
            plot_bgcolor="white", paper_bgcolor="white"
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with right:
        mix = []
        for s in scenarios:
            total_t = transport_cost(s)
            mix.append({
                "Escenario":s,
                "Colecta":NORMAL["Colecta"]*FACT[s]/total_t*100,
                "Media milla":NORMAL["Media milla"]*FACT[s]/total_t*100,
                "Última milla":NORMAL["Última milla"]*FACT[s]/total_t*100
            })
        mixdf = pd.DataFrame(mix)
        for c in mixdf.columns[1:]:
            mixdf[c] = mixdf[c].map(lambda x:dec(x)+"%")
        st.dataframe(mixdf, hide_index=True, use_container_width=True, height=45+35*len(mixdf))

if stage == "Todas" or stage in ["XD","Service Center"]:
    centers = ["XD","Service Center"] if stage == "Todas" else [stage]
    fixed = pd.DataFrame({
        "Centro": centers,
        "Costo normal":[ars(NORMAL[e],2) for e in centers],
        "Costo promedio con voluminosos":[ars(XD_AFTER,2) if e=="XD" else ars(SC_AFTER,2) for e in centers],
        "Costo incremental":[ "$0" for _ in centers]
    })
    st.dataframe(fixed, hide_index=True, use_container_width=True, height=45+35*len(fixed))

# =========================================================
# 3 REVENUE
# =========================================================
st.markdown('<div class="section">3 · Revenue</div>', unsafe_allow_html=True)
left, right = st.columns([1.1,1.4])
with left:
    fig = go.Figure(go.Bar(
        y=["Normal","Voluminoso"], x=[REV_N,REV_V], orientation="h",
        marker_color=[BLUE,YELLOW], width=.34,
        text=[ars(REV_N),ars(REV_V)], textposition="outside", cliponaxis=False
    ))
    fig.update_layout(
        height=235, margin=dict(l=10,r=70,t=10,b=10), showlegend=False,
        xaxis=dict(title="$ / paquete", range=[0,22000], gridcolor="#EEF0F3"),
        yaxis=dict(title="", tickfont=dict(color=INK,size=13)),
        plot_bgcolor="white", paper_bgcolor="white"
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
with right:
    revdf = pd.DataFrame({
        "Tipo":["Normal","Voluminoso","Diferencia"],
        "Revenue / paquete":[ars(REV_N),ars(REV_V),"+$16.000"],
        "Relación":["1,00x","6,33x","+533%"]
    })
    st.dataframe(revdf, hide_index=True, use_container_width=True, height=145)

# =========================================================
# 4 SENSIBILIDAD
# =========================================================
st.markdown('<div class="section">4 · Sensibilidad y rentabilidad</div>', unsafe_allow_html=True)

sens = pd.DataFrame([{
    "Escenario":s,
    "Costo incremental":metrics(s)[0],
    "Resultado / paquete":metrics(s)[1],
    "Margen":metrics(s)[2],
    "Impacto mensual":metrics(s)[3]
} for s in FACT])

left, right = st.columns([1.15,1])
with left:
    fig = go.Figure(go.Scatter(
        x=[5,5.5,6], y=sens["Impacto mensual"], mode="lines+markers+text",
        line=dict(color=BLUE,width=4),
        marker=dict(size=14,color=[SCOL[s] for s in FACT],line=dict(width=2,color="white")),
        text=[(f"{v:+.1f} M").replace(".",",") for v in sens["Impacto mensual"]],
        textposition=["top center","top center","bottom center"],
        textfont=dict(size=14,color=INK)
    ))
    fig.add_hline(y=0,line_color="#AEB4BD",line_width=1)
    fig.add_vline(x=BE,line_dash="dash",line_color=INK,annotation_text="5,72x",annotation_position="top")
    fig.update_layout(
        height=320, margin=dict(l=10,r=10,t=25,b=15), showlegend=False,
        xaxis=dict(title="Consumo de capacidad",tickvals=[5,5.5,6],ticktext=["5x","5,5x","6x"],showgrid=False),
        yaxis=dict(title="Resultado mensual ($M)",gridcolor="#EEF0F3"),
        plot_bgcolor="white",paper_bgcolor="white"
    )
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with right:
    d=sens.copy()
    d["Costo incremental"]=d["Costo incremental"].map(ars)
    d["Resultado / paquete"]=d["Resultado / paquete"].map(ars)
    d["Margen"]=d["Margen"].map(lambda x:dec(x)+"%")
    d["Impacto mensual"]=d["Impacto mensual"].map(lambda x:(f"{x:+.1f} M").replace(".",","))
    st.dataframe(d,hide_index=True,use_container_width=True,height=180)

# =========================================================
# 5 DRIVERS
# =========================================================
st.markdown('<div class="section">5 · Drivers de control</div>', unsafe_allow_html=True)

base55 = metrics("5,5x")
lm_share = (NORMAL["Última milla"]*5.5)/base55[0]*100
cards = st.columns(3)
driver_data = [
    ("ÚLTIMA MILLA",dec(lm_share)+"%","del costo incremental de transporte en 5,5x"),
    ("HEADROOM · 5,5x",ars(base55[1]),"resultado incremental disponible por paquete"),
    ("PUNTO DE EQUILIBRIO",dec(BE,2)+"x","máximo consumo de capacidad bajo los supuestos base"),
]
for col,(lab,val,sub) in zip(cards,driver_data):
    with col:
        st.markdown(f'<div class="driver"><div class="lab">{lab}</div><div class="driver-val">{val}</div><div class="mini">{sub}</div></div>',unsafe_allow_html=True)

st.caption("* XD y Service Center: costo incremental $0 bajo el supuesto de capacidad ociosa. Sus costos promedio de red continúan existiendo.")
