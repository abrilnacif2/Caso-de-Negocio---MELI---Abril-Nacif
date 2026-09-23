import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Business Case | Voluminosos", page_icon="📦", layout="wide")

# -------------------- DATOS DEL CASO --------------------
NORMAL = {
    "Colecta": 250000/280,
    "XD": 741000000/10000000,
    "Media milla": 900000/2100,
    "Service Center": 741500000/10000000,
    "Última milla": 150000/75,
}
CAP = {"Colecta":280, "Media milla":2100, "Última milla":75}
FACTORS = {"Normal":1.0, "5x":5.0, "5,5x":5.5, "6x":6.0}
REV_NORMAL, REV_VOL, VOL_MES = 3000, 19000, 50000
TRANSPORT = ["Colecta","Media milla","Última milla"]
CENTERS = ["XD","Service Center"]

def transport_costs(s):
    f = FACTORS[s]
    return {e: NORMAL[e]*f for e in TRANSPORT}

def ars(x, dec=0):
    sign = "−" if x < 0 else ""
    s = f"{abs(x):,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{sign}${s}"

def pct(x):
    return f"{x:.1f}%".replace(".", ",")

def scenario_metrics(s):
    f=FACTORS[s]
    inc_transport=sum(NORMAL[e]*f for e in TRANSPORT)
    result=REV_VOL-inc_transport
    return inc_transport,result,result/REV_VOL*100,result*VOL_MES/1e6

# -------------------- ESTILO --------------------
st.markdown("""
<style>
.block-container{padding-top:1.5rem;padding-bottom:2rem;max-width:1450px}
[data-testid="stSidebar"]{background:#f7f8fa;border-right:1px solid #e6e8ec}
.hero{background:linear-gradient(100deg,#FFE600 0%,#FFF4A8 100%);padding:24px 28px;border-radius:20px;margin-bottom:18px}
.hero h1{margin:0;color:#24272c;font-size:2.05rem}
.hero p{margin:6px 0 0;color:#555b66;font-size:1rem}
.kpi{background:white;border:1px solid #e7e9ee;border-radius:16px;padding:16px 18px;box-shadow:0 3px 14px rgba(20,30,55,.06);min-height:112px}
.kpi-label{font-size:.78rem;color:#6b7280;font-weight:700;letter-spacing:.04em}
.kpi-value{font-size:1.65rem;color:#25272b;font-weight:800;margin-top:5px}
.kpi-sub{font-size:.82rem;color:#7b8190;margin-top:2px}
.note{background:#f7f8fa;border-left:4px solid #3483FA;border-radius:10px;padding:12px 14px;color:#4d5562}
.good{background:#f1fbf5;border-left:4px solid #00A650;border-radius:10px;padding:12px 14px}
.warn{background:#fff8e7;border-left:4px solid #F5A623;border-radius:10px;padding:12px 14px}
.bad{background:#fff1f1;border-left:4px solid #E55353;border-radius:10px;padding:12px 14px}
.small{font-size:.82rem;color:#747b88}
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="hero"><h1>📦 Dashboard | Paquetes voluminosos</h1>
<p>Business Case — Abril Nacif · Sensibilidad operativa y económica</p></div>""", unsafe_allow_html=True)

# -------------------- FILTROS --------------------
with st.sidebar:
    st.markdown("## Filtros")
    scenario = st.selectbox("Escenario a analizar", ["5x","5,5x","6x"], index=1)
    stage_filter = st.multiselect("Etapas a visualizar", list(NORMAL), default=list(NORMAL))
    st.markdown("---")
    st.markdown("### Qué representa el escenario")
    st.caption("5x–6x mide cuánto consume un voluminoso de la capacidad de transporte respecto de un paquete normal. 5,5x es un escenario intermedio de sensibilidad.")
    st.markdown("### Supuesto base")
    st.caption("XD y Service Center mantienen su costo fijo total si existe capacidad ociosa. Por eso su costo incremental del proyecto es $0; su costo promedio de red NO es $0.")

f=FACTORS[scenario]
inc_cost,result,margin,monthly=scenario_metrics(scenario)
be=REV_VOL/sum(NORMAL[e] for e in TRANSPORT)

# -------------------- KPIs --------------------
cols=st.columns(5)
cards=[
    ("ESCENARIO",scenario,"consumo de capacidad"),
    ("REVENUE",ars(REV_VOL),"por voluminoso"),
    ("COSTO INCREMENTAL",ars(inc_cost),"transporte / voluminoso"),
    ("RESULTADO",ars(result),"por voluminoso"),
    ("MARGEN",pct(margin),f"{monthly:+.1f} M / mes".replace(".",",")),
]
for col,(lab,val,sub) in zip(cols,cards):
    with col:
        st.markdown(f'<div class="kpi"><div class="kpi-label">{lab}</div><div class="kpi-value">{val}</div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

st.markdown("### 1. Costos por etapa")
st.caption("Se muestran dos conceptos distintos para evitar confundir costo promedio de red con costo incremental del proyecto.")

# Build comparison data
rows=[]
for e in NORMAL:
    normal=NORMAL[e]
    if e in TRANSPORT:
        selected=normal*f
        incremental=selected
        label="Costo de transporte estimado"
    else:
        # Average network allocation after adding 50k packages, assuming fixed total unchanged
        total_fixed = 741000000 if e=="XD" else 741500000
        selected=total_fixed/10050000
        incremental=0
        label="Costo promedio de red"
    rows.append([e,normal,selected,incremental,label])
cdf=pd.DataFrame(rows,columns=["Etapa","Normal ($/paq.)",f"{scenario} ($/paq.)","Incremental proyecto ($/paq.)","Concepto"])

left,right=st.columns([1.55,1])
with left:
    shown=cdf[cdf["Etapa"].isin(stage_filter)]
    fig=go.Figure()
    fig.add_bar(name="Normal — costo promedio",x=shown["Etapa"],y=shown["Normal ($/paq.)"],marker_color="#3483FA")
    fig.add_bar(name=f"{scenario} — costo estimado/promedio",x=shown["Etapa"],y=shown[f"{scenario} ($/paq.)"],marker_color="#F5A623")
    fig.update_layout(barmode="group",height=390,margin=dict(l=10,r=10,t=35,b=10),
                      yaxis_title="$ por paquete",xaxis_title="",legend_orientation="h",
                      legend_y=1.13,plot_bgcolor="white",paper_bgcolor="white")
    st.plotly_chart(fig,use_container_width=True)

with right:
    st.markdown("#### XD y Service Center")
    xd_avg=741000000/10050000
    sc_avg=741500000/10050000
    st.markdown(f"""
    <div class="note"><b>NO cuestan $0.</b><br>
    Su costo promedio de red pasa aproximadamente de <b>{ars(NORMAL["XD"],2)} a {ars(xd_avg,2)}</b> en XD
    y de <b>{ars(NORMAL["Service Center"],2)} a {ars(sc_avg,2)}</b> en Service Center, si el costo fijo total no cambia.</div>
    <br>
    <div class="good"><b>Lo que es $0 es el costo incremental.</b><br>
    Bajo el supuesto de capacidad ociosa, incorporar los 50.000 voluminosos no agrega estructura fija en XD/SC.</div>
    """,unsafe_allow_html=True)

display=cdf.copy()
for col in ["Normal ($/paq.)",f"{scenario} ($/paq.)","Incremental proyecto ($/paq.)"]:
    display[col]=display[col].map(lambda x: ars(x,2))
st.dataframe(display,use_container_width=True,hide_index=True)

st.markdown("### 2. Capacidad equivalente por ruta")
cap_rows=[]
for e,n in CAP.items():
    cap_rows.append([e,n,n/f])
capdf=pd.DataFrame(cap_rows,columns=["Etapa","Normal",f"{scenario} — equivalentes/ruta"])
l,r=st.columns([1.5,1])
with l:
    fig2=go.Figure()
    fig2.add_bar(name="Normal",x=capdf["Etapa"],y=capdf["Normal"],marker_color="#3483FA")
    fig2.add_bar(name=scenario,x=capdf["Etapa"],y=capdf[f"{scenario} — equivalentes/ruta"],marker_color="#F5A623")
    fig2.update_layout(barmode="group",height=350,margin=dict(l=10,r=10,t=30,b=10),
                       yaxis_title="Paquetes equivalentes / ruta",xaxis_title="",
                       legend_orientation="h",legend_y=1.12,plot_bgcolor="white",paper_bgcolor="white")
    st.plotly_chart(fig2,use_container_width=True)
with r:
    st.markdown(f"""<div class="warn"><b>Lectura del escenario {scenario}</b><br><br>
    Colecta: <b>{280/f:.1f}</b> equivalentes/ruta<br>
    Media milla: <b>{2100/f:.1f}</b> equivalentes/ruta<br>
    Última milla: <b>{75/f:.1f}</b> equivalentes/ruta<br><br>
    <span class="small">Son equivalentes teóricos para estimar costos, no una cantidad física exacta de productos.</span></div>""".replace(".",","),unsafe_allow_html=True)

st.markdown("### 3. Rentabilidad y sensibilidad")
sens=[]
for s in ["5x","5,5x","6x"]:
    ci,re,ma,mo=scenario_metrics(s)
    sens.append([s,ci,re,ma,mo])
sdf=pd.DataFrame(sens,columns=["Escenario","Costo incremental","Resultado / paquete","Margen %","Resultado mensual ($M)"])

l,r=st.columns([1.45,1])
with l:
    fig3=go.Figure()
    colors=["#00A650" if x>=0 else "#E55353" for x in sdf["Resultado mensual ($M)"]]
    fig3.add_bar(x=sdf["Escenario"],y=sdf["Resultado mensual ($M)"],marker_color=colors,
                 text=[f"{x:+.1f} M".replace(".",",") for x in sdf["Resultado mensual ($M)"]],textposition="outside")
    fig3.add_hline(y=0,line_color="#7a7f88")
    fig3.update_layout(height=355,margin=dict(l=10,r=10,t=25,b=10),
                       yaxis_title="Resultado mensual ($M)",xaxis_title="Consumo de capacidad",
                       plot_bgcolor="white",paper_bgcolor="white")
    st.plotly_chart(fig3,use_container_width=True)
with r:
    cls="good" if result>0 else "bad"
    status="POSITIVO" if result>0 else "NEGATIVO"
    st.markdown(f"""<div class="{cls}"><b>Escenario seleccionado: {scenario}</b><br>
    Resultado: <b>{ars(result)} / paquete</b><br>
    Margen: <b>{pct(margin)}</b><br>
    Impacto mensual: <b>{monthly:+.1f} M</b></div>""".replace(".",","),unsafe_allow_html=True)
    st.markdown(f"""<div class="note" style="margin-top:12px"><b>Punto de equilibrio: {be:.2f}x</b><br>
    Por debajo, el resultado incremental es positivo; por encima, la tarifa de $19.000 deja de cubrir el costo incremental estimado.</div>""".replace(".",","),unsafe_allow_html=True)

st.markdown("---")
st.markdown("#### Insight principal")
st.markdown("""<div class="warn"><b>La rentabilidad es sensible al consumo real de capacidad.</b>
El margen pasa de 12,6% en 5x a 3,9% en 5,5x y se vuelve negativo (−4,9%) en 6x.
Por eso, el dato clave a validar en una prueba piloto es la productividad real de las rutas, especialmente en Última milla.</div>""",unsafe_allow_html=True)

st.caption("Supuesto base: XD y Service Center no generan costo incremental mientras exista capacidad ociosa. Sus costos promedio de red se mantienen como costos de estructura y no deben interpretarse como $0.")
