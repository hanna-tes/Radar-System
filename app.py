# -*- coding: utf-8 -*-
"""newapp.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1D_SVhXGpyUoqqhRs_SFWQQpD5Qd5CDrK
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Import your existing functions (make sure to remove notebook-specific code)
from pipeline import (
        bertrend_analysis,
        calculate_trend_momentum,
        visualize_trends,
        generate_investigative_report,
        categorize_momentum
    )

# Configure page
st.set_page_config(
    page_title="Election Threat Monitor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'reports' not in st.session_state:
    st.session_state.reports = {}
#checking the existance
if os.path.exists("pipeline.py"):
    print("✅ pipeline.py found!")
else:
    print("❌ pipeline.py is missing!")

print("Current Directory:", os.getcwd())
print("Files and Folders:", os.listdir("."))

#removes running loop error
import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# Main app
def main():
    st.title("🇬🇦 Gabon Election Threat Intelligence Dashboard")
    st.markdown("### Real-time Narrative Monitoring & FIMI Detection")

    # File upload
    uploaded_file = st.file_uploader(
        "Upload Social Media Data (CSV/Excel)",
        type=["csv", "xlsx"],
        help="Requires columns: 'text', 'Timestamp', 'URL', 'Source'"
    )

    if uploaded_file:
        # Load and preprocess data
        @st.cache_data
        def load_data(file):
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            return df

        df = load_data(uploaded_file)

        # Analysis trigger
        if st.button("🚀 Analyze Data", help="Run full BERTrend analysis"):
            with st.status("Processing data...", expanded=True) as status:
                try:
                    st.write("🔍 Running temporal-semantic clustering...")
                    clustered_df = bertrend_analysis(df)
                    status.update(label="Temporal-semantic clustering complete!", state="running")

                    st.write("📈 Calculating narrative momentum...")
                    emerging_trends, momentum_states = calculate_trend_momentum(clustered_df)
                    status.update(label="Narrative momentum calculation complete!", state="running")

                    st.write("🎨 Generating visualizations...")
                    viz_path = visualize_trends(clustered_df, momentum_states)
                    status.update(label="Visualizations generated!", state="complete")
                except Exception as e:
                    st.error(f"❌ An error occurred during analysis: {e}")
                    return

            st.session_state.processed = True
            st.session_state.clustered_df = clustered_df
            st.session_state.momentum_states = momentum_states
            st.session_state.emerging_trends = emerging_trends
            st.rerun()

        # Display Results
        if st.session_state.processed:
            clustered_df = st.session_state.clustered_df
            momentum_states = st.session_state.momentum_states
            emerging_trends = st.session_state.emerging_trends
        
            # Validate input data
            if clustered_df is None or clustered_df.empty:
                st.error("❌ The uploaded file does not contain valid data. Please ensure the file includes 'text', 'Timestamp', 'URL', and 'Source' columns.")
            elif not momentum_states:
                st.error("❌ Momentum states could not be calculated. Please check the input data and try again.")
            else:
                # Generate visualization once and store in session state
                if 'viz_path' not in st.session_state:
                    with st.spinner("Generating visualizations..."):
                        st.session_state.viz_path = visualize_trends(clustered_df, momentum_states)
                    st.success("Visualizations generated successfully!")
        
                # Create tabs
                tab1, tab2, tab3 = st.tabs([
                    "📊 Cluster Analytics",
                    "📜 Threat Reports",
                    "🚨 Threat Categorization"
                ])
        
                with tab1:
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        if st.session_state.viz_path:
                            st.image(st.session_state.viz_path, caption="Cluster Activity Heatmap", use_column_width=True)
        
                    with col2:
                        st.markdown("### Top Clusters by Momentum")
                        momentum_df = pd.DataFrame([
                            {
                                "Cluster": cluster,
                                "Momentum": score,
                                "Sources": len(momentum_states[cluster]['sources']),
                                "Last Active": momentum_states[cluster]['last_update'].strftime('%Y-%m-%d %H:%M')
                            }
                            for cluster, score in emerging_trends
                        ])
                        st.dataframe(
                            momentum_df.sort_values('Momentum', ascending=False),
                            column_config={
                                "Momentum": st.column_config.ProgressColumn(
                                    format="%.0f",
                                    min_value=0,
                                    max_value=momentum_df['Momentum'].max()
                                )
                            },
                            height=400
                        )
        
                with tab2:
                    cluster_selector = st.selectbox(
                        "Select Cluster for Detailed Analysis",
                        [cluster for cluster, _ in emerging_trends],
                        format_func=lambda x: f"Cluster {x}"
                    )
        
                    cluster_score = next((score for cluster, score in emerging_trends if cluster == cluster_selector), 0)
        
                    category = categorize_momentum(cluster_score)
                    color_map = {
                        'Tier 1: Ambient Noise (Normal baseline activity)': '🟢',
                        'Tier 2: Emerging Narrative (Potential story development)': '🟡',
                        'Tier 3: Coordinated Activity (Organized group behavior)': '🟠',
                        'Tier 4: Viral Emergency (Requires immediate response)': '🔴'
                    }
                    color = color_map.get(category, '⚪')
                    st.markdown(f"**Threat Classification:** {color} `{category}`")
        
                    if cluster_selector not in st.session_state.reports:
                        with st.spinner("Generating intelligence report..."):
                            cluster_data = clustered_df[clustered_df['Cluster'] == cluster_selector]
                            cluster_data['momentum_score'] = cluster_score
                            report = generate_investigative_report(
                                cluster_data,
                                momentum_states,
                                cluster_selector
                            )
                            st.session_state.reports[cluster_selector] = report
                        st.success("Intelligence report generated successfully!")
        
                    report = st.session_state.reports[cluster_selector]
        
                    with st.expander("📄 Full Intelligence Report", expanded=True):
                        st.markdown(f"#### Cluster {cluster_selector} Analysis")
                        st.markdown(report['report'])
        
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### Example Content")
                        for i, text in enumerate(report['sample_texts'][:5]):
                            st.markdown(f"**Document {i+1}**")
                            st.info(text[:500] + "..." if len(text) > 500 else text)
        
                    with col2:
                        st.markdown("### Associated URLs")
                        for url in report['sample_urls']:
                            st.markdown(f"- [{url[:50]}...]({url})")
        
                with tab3:
                    st.markdown("### Threat Tier Classification")
        
                    if not emerging_trends:
                        st.error("❌ No emerging trends available for classification.")
                    else:
                        intel_df = pd.DataFrame([{
                            "Cluster": cluster,
                            "Momentum": score
                        } for cluster, score in emerging_trends])
        
                        st.bar_chart(
                            intel_df.set_index('Cluster')['Momentum'],
                            color="#FF4B4B",
                            height=400
                        )
        
                        st.dataframe(
                            intel_df,
                            hide_index=True
                        )
        
                        # Add download button here
                        st.download_button(
                            label="📥 Download Full Report",
                            data=convert_df(intel_df),
                            file_name=f"threat_report_{datetime.now().date()}.csv",
                            mime="text/csv"
                        )
        
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')
        
        if __name__ == "__main__":
            main()
