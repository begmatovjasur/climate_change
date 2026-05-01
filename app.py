import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title=" Uzbekistan", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .main-header { font-size: 28px; font-weight: 700; color: #1e3a8a; margin-bottom: 5px; font-family: 'Arial', sans-serif;}
    .sub-header { font-size: 16px; color: #64748b; margin-bottom: 30px; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px;}
    .desc-box { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; font-size: 14px; color: #334155; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .desc-title { font-weight: 600; font-size: 16px; margin-bottom: 10px; color: #0f172a;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">Climate Change Knowledge Portal: Uzbekistan</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Historical Climate Data, ML Projections, and Aral Sea Disaster Analysis</div>', unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/regions_master.csv")
    aral_df = pd.read_csv("data/processed/aral_sea_master.csv")
    
    cols_to_drop = [col for col in df.columns if 'Unnamed' in col]
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)
        
    aral_df.columns = aral_df.columns.str.strip()
    aral_cols_drop = [col for col in aral_df.columns if 'Unnamed' in col]
    if aral_cols_drop:
        aral_df = aral_df.drop(columns=aral_cols_drop)
        
    df['Decade'] = (df['Year'] // 10) * 10
    df['Decade_Str'] = df['Decade'].astype(str) + "s"
    return df, aral_df

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

try:
    df, aral_df = load_data()
except Exception:
    st.error("Data files not found. Please check 'data/processed' directory.")
    st.stop()


st.sidebar.markdown("###  LOCATION")
location = st.sidebar.selectbox("Select Location", sorted(df['Viloyat'].dropna().unique()))

st.sidebar.markdown("### CLIMATE VARIABLE")
variables = [col for col in df.columns if col not in ['Year', 'Viloyat', 'Category', 'Decade', 'Decade_Str']]
parameter = st.sidebar.selectbox("Select Variable", variables)

df_filtered = df[df['Viloyat'] == location]

st.sidebar.markdown("---")
st.sidebar.markdown("### EXPLORE OUR DATA")
csv_data = convert_df_to_csv(df_filtered)
st.sidebar.download_button(
    label="Download Data (CSV)",
    data=csv_data,
    file_name=f"{location}_climate_data.csv",
    mime="text/csv"
)


tab_hist, tab_future, tab_aral = st.tabs([
    "Historical Time Series", 
    "Future Projections (2050)", 
    "Aral Sea Disaster"
])

with tab_hist:
    col1, col2 = st.columns([7, 3])
    with col1:
        fig1 = px.line(df_filtered, x='Year', y=parameter, markers=True, line_shape='spline')
        fig1.update_traces(line_color="#2563eb", marker=dict(size=5))
        fig1.add_hline(y=df_filtered[parameter].mean(), line_dash="dash", line_color="#ef4444", annotation_text="Mean")
        fig1.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=30, b=0), height=350)
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.markdown(f"""<div class="desc-box"><div class="desc-title">Historical Time Series</div><b>Analysis:</b> Shows the historical trajectory of <i>{parameter}</i> in <b>{location}</b> from 1950. The dashed line is the long-term average.</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col3, col4 = st.columns([7, 3])
    with col3:
        decadal_df = df_filtered.groupby('Decade_Str')[parameter].mean().reset_index()
        fig2 = px.bar(decadal_df, x='Decade_Str', y=parameter, text_auto='.2f')
        fig2.update_traces(marker_color="#0ea5e9")
        fig2.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=30, b=0), height=350,
                           xaxis_title="Decades", yaxis_title=f"Average {parameter}")
        st.plotly_chart(fig2, use_container_width=True)
    with col4:
        st.markdown(f"""<div class="desc-box"><div class="desc-title">Decadal Climatology</div><b>Understanding the Data:</b><br><br>This bar chart smoothes out annual variations to reveal broader climate trends over <b>decades</b>. A persistent upward or downward stair-step pattern strongly indicates systemic climate change rather than natural year-to-year variability.</div>""", unsafe_allow_html=True)

with tab_future:
    col_f1, col_f2 = st.columns([7, 3])
    x_hist, y_hist = df_filtered['Year'].values, df_filtered[parameter].values
    y_future = [] 
    
    with col_f1:
        try:
            future_df = pd.read_csv("data/processed/future_predictions.csv")
            future_filtered = future_df[(future_df['Viloyat'] == location) & (future_df['Parameter'] == parameter)]
            x_future, y_future = future_filtered['Year'].values, future_filtered['Predicted_Value'].values
            
            fig_proj = go.Figure()
            fig_proj.add_trace(go.Scatter(x=x_hist, y=y_hist, mode='lines', name='Historical Data', line=dict(color='#3b82f6', width=2)))
            if len(x_future) > 0:
                fig_proj.add_trace(go.Scatter(x=[x_hist[-1], x_future[0]], y=[y_hist[-1], y_future[0]], mode='lines', showlegend=False, line=dict(color='#ef4444', dash='dash', width=2)))
                fig_proj.add_trace(go.Scatter(x=x_future, y=y_future, mode='lines', name='ML Projection (2050)', line=dict(color='#ef4444', dash='dash', width=2)))
            fig_proj.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=30, b=0), height=400)
            st.plotly_chart(fig_proj, use_container_width=True)
        except Exception:
            st.warning("Future predictions file not found.")
            
    with col_f2:
        st.markdown(f"""<div class="desc-box"><div class="desc-title">Future ML Projections</div><b>Model:</b> Uses Machine Learning (Ridge, Lasso, Poly) to forecast the trend up to 2050 including natural variance.</div>""", unsafe_allow_html=True)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    if len(y_future) > 0:
        col_f3, col_f4 = st.columns([7, 3])
        with col_f3:
            hist_box = pd.DataFrame({'Value': y_hist, 'Period': 'Historical (1950-2024)'})
            fut_box = pd.DataFrame({'Value': y_future, 'Period': 'Projection (2025-2050)'})
            box_df = pd.concat([hist_box, fut_box])
            
            fig_box = px.box(box_df, x='Period', y='Value', color='Period', 
                             color_discrete_map={'Historical (1950-2024)': '#3b82f6', 'Projection (2025-2050)': '#ef4444'},
                             points="all")
            fig_box.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=30, b=0), height=400,
                                  xaxis_title="Comparison Period", yaxis_title=parameter,
                                  title="Climate Shift & Extreme Events Distribution")
            st.plotly_chart(fig_box, use_container_width=True)
            
        with col_f4:
            st.markdown(f"""<div class="desc-box"><div class="desc-title">Climate Shift Analysis (Boxplot)</div><b>Why is this important?</b><br><br>This distribution chart shows how the <b>extremes</b> (not just the average) are expected to shift. A shift up or down indicates a fundamental change in the region's climate baseline, while wider boxes indicate more chaotic weather.</div>""", unsafe_allow_html=True)

with tab_aral:
    st.markdown("### The Aral Sea Desiccation: Causes and Dynamics")
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        fig_cause = make_subplots(specs=[[{"secondary_y": True}]])
        total_river_volume = aral_df['Amudaryo volume'] + aral_df['Sirdaryo volume']
        salinity_col = [col for col in aral_df.columns if 'Salinity' in col or 'salinity' in col][-1] 
        fig_cause.add_trace(go.Scatter(x=aral_df['Year'], y=total_river_volume, name="Inflow (Amu+Sir)", line=dict(color='#3b82f6', width=2)), secondary_y=False)
        fig_cause.add_trace(go.Scatter(x=aral_df['Year'], y=aral_df[salinity_col], name="Salinity (g/l)", line=dict(color='#ef4444', width=2)), secondary_y=True)
        fig_cause.update_layout(template="plotly_white", title="Cause & Effect: River Inflow vs. Salinity", height=350, margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_cause, use_container_width=True)

    with col_a2:
        fig_effect = make_subplots(specs=[[{"secondary_y": True}]])
        area_col = [col for col in aral_df.columns if 'area' in col.lower()][0]
        level_col = [col for col in aral_df.columns if 'Level' in col or 'level' in col][0]
        fig_effect.add_trace(go.Bar(x=aral_df['Year'], y=aral_df[area_col], name="Surface Area", marker_color='#93c5fd', opacity=0.7), secondary_y=False)
        fig_effect.add_trace(go.Scatter(x=aral_df['Year'], y=aral_df[level_col], name="Water Level", line=dict(color='#1e3a8a', width=3)), secondary_y=True)
        fig_effect.update_layout(template="plotly_white", title="Disaster Dynamics: Water Level and Surface Area", height=350, margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_effect, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"### Micro-Climatic Impact & Climate Feedback Loop in {location}")
    
    aral_regions = ['qaraqal', 'qoraqal', 'karakal', 'xoraz', 'khore']
    is_aral_region = any(reg in location.lower() for reg in aral_regions)

    if is_aral_region:
        col_a3, col_a4 = st.columns(2)
        with col_a3:
            merged_area = pd.merge(df_filtered[['Year', parameter]], aral_df[['Year', area_col]], on='Year', how='inner')
            fig_corr = make_subplots(specs=[[{"secondary_y": True}]])
            fig_corr.add_trace(go.Scatter(x=merged_area['Year'], y=merged_area[area_col], name="Aral Area (km²)", fill='tozeroy', line=dict(color='#bfdbfe', width=1)), secondary_y=False)
            fig_corr.add_trace(go.Scatter(x=merged_area['Year'], y=merged_area[parameter], name=f"{parameter}", line=dict(color='#ef4444', width=2)), secondary_y=True)
            fig_corr.update_layout(template="plotly_white", title=f"Correlation: Sea Shrinkage vs. {parameter}", height=380, margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_corr, use_container_width=True)

        with col_a4:
            try:
                evap_col = [col for col in aral_df.columns if 'evapor' in col.lower()][0]
                temp_cols = [col for col in df_filtered.columns if 'temperature' in col.lower() and 'mean' in col.lower()]
                temp_col = temp_cols[0] if temp_cols else [col for col in df_filtered.columns if 'temperature' in col.lower()][0]
                merged_evap = pd.merge(df_filtered[['Year', temp_col]], aral_df[['Year', evap_col]], on='Year', how='inner')
                fig_evap = make_subplots(specs=[[{"secondary_y": True}]])
                fig_evap.add_trace(go.Bar(x=merged_evap['Year'], y=merged_evap[evap_col], name="Evaporation (km³)", marker_color='#fdba74', opacity=0.8), secondary_y=False)
                fig_evap.add_trace(go.Scatter(x=merged_evap['Year'], y=merged_evap[temp_col], name="Mean Temp (°C)", line=dict(color='#b91c1c', width=3)), secondary_y=True)
                fig_evap.update_layout(template="plotly_white", title="Feedback Loop: Regional Temperature vs. Evaporation", height=380, margin=dict(t=40, b=0, l=0, r=0))
                st.plotly_chart(fig_evap, use_container_width=True)
            except Exception as e:
                st.warning("Evaporation or Temperature data missing for this correlation.")

        st.markdown(f"""<div class="desc-box"><div class="desc-title">Scientific Conclusion: The Climate Feedback Loop</div><b>The Dual Crisis:</b> Because <b>{location}</b> is situated in the Aral Sea disaster zone, we observe a vicious cycle (Feedback Loop).<br><br>As regional temperatures inherently rise (red line on the right chart), it accelerates the <b>Evaporation</b> (orange bars) of the remaining water bodies. This massive evaporation accelerates the <b>Shrinkage</b> of the sea (blue area on the left chart). Consequently, the loss of this massive water body removes its cooling effect, causing the region's climate ({parameter}) to become even more extreme and arid.</div>""", unsafe_allow_html=True)
        
    else:
        st.info(f"""**Scientific Note on Regional Micro-Climate:** Currently selected region: **{location}**. The direct micro-climatic impact of the Aral Sea desiccation is geographically limited to the immediate Aral Sea region (**Karakalpakstan** and **Khorezm**). While macroeconomic and broader ecological impacts affect all of Uzbekistan, linking localized climate parameters of distant regions like {location} directly to the Aral Sea lacks strict statistical causality. *Tip: Select 'Qaraqalpogiston' or 'Xorazm' to view the direct climate feedback loop and evaporation correlations.*""")