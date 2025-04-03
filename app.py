# -*- coding: utf-8 -*-
"""newapp.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1D_SVhXGpyUoqqhRs_SFWQQpD5Qd5CDrK
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from io import StringIO

# Configure page
st.set_page_config(
    page_title="Burkina Faso Election Threat Intelligence Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'real_time_analysis' not in st.session_state:
    st.session_state.real_time_analysis = False
if 'processed_data_loaded' not in st.session_state:
    st.session_state.processed_data_loaded = False

# Function to fetch processed data from GitHub
def fetch_data_from_github(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text  # Return raw content of the file
        else:
            st.error(f"❌ Failed to fetch data from GitHub. Status code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"❌ An error occurred while fetching data: {e}")
        return None

# Function to load CSV data
def load_csv_data(raw_data):
    try:
        df = pd.read_csv(StringIO(raw_data))
        return df
    except Exception as e:
        st.error(f"❌ Failed to parse CSV data: {e}")
        return None

# Main app
def main():
    st.title("🇧🇫 Burkina Faso Election Threat Intelligence Dashboard")
    st.markdown("### Real-time Narrative Monitoring & FIMI Detection")

    # User choice: Real-time analysis or preprocessed data
    analysis_option = st.radio(
        "Choose an option:",
        ["📊 Analyze Raw Data (Real-Time)", "📈 View Preprocessed Data Results"],
        help="Select whether you want to analyze raw data or view results from preprocessed data."
    )

    if analysis_option == "📊 Analyze Raw Data (Real-Time)":
        # File upload for raw data
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

                st.session_state.real_time_analysis = True
                st.session_state.clustered_df = clustered_df
                st.session_state.momentum_states = momentum_states
                st.session_state.emerging_trends = emerging_trends
                st.rerun()

            # Display Results for Real-Time Analysis
            if st.session_state.real_time_analysis:
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
                        st.markdown("### Narrative Growth vs Momentum Intensity")
                        heatmap_url = "https://raw.githubusercontent.com/yourusername/your-repo-name/main/visual_trends.png"
                        st.image(heatmap_url, caption="Narrative Growth vs Momentum Intensity", use_column_width=True)

                        col1, col2 = st.columns([2, 1])
                        with col1:
                            if st.session_state.viz_path:
                                st.image(st_session_state.viz_path, caption="Cluster Activity Heatmap", use_column_width=True)
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
                        st.markdown("### Detailed Threat Reports")
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

    elif analysis_option == "📈 View Preprocessed Data Results":
        # Fetch processed data from GitHub
        if not st.session_state.processed_data_loaded:
            github_csv_url = "https://github.com/hanna-tes/RadarSystem/blob/main/Burkina_Faso_intelligence_reportMarch31.csv"
            st.write("Fetching Burkina Faso intelligence report...")
            raw_data = fetch_data_from_github(github_csv_url)
            if raw_data:
                preprocessed_data = load_csv_data(raw_data)
                if preprocessed_data is not None:
                    st.session_state.preprocessed_data = preprocessed_data
                    st.session_state.processed_data_loaded = True
                    st.success("✅ Burkina Faso intelligence report loaded.")

        # Display results for preprocessed data
        if st.session_state.processed_data_loaded:
            preprocessed_data = st.session_state.preprocessed_data

            # Create tabs
            tab1, tab2, tab3 = st.tabs([
                "📊 Cluster Analytics",
                "📜 Threat Reports",
                "🚨 Threat Categorization"
            ])

            with tab1:
                st.markdown("### Narrative Growth vs Momentum Intensity")
                heatmap_url = "https://github.com/hanna-tes/RadarSystem/blob/main/trend_visualization.png"
                st.image(heatmap_url, caption="Narrative Growth vs Momentum Intensity", use_column_width=True)

                st.markdown("### Cluster Overview")
                st.dataframe(preprocessed_data)

            with tab2:
                st.markdown("### Burkina Faso Intelligence Report")
                st.dataframe(preprocessed_data)

                # Add download button
                st.download_button(
                    label="📥 Download Full Report",
                    data=convert_df(preprocessed_data),
                    file_name=f"threat_report_{datetime.now().date()}.csv",
                    mime="text/csv"
                )

            with tab3:
                st.markdown("### Threat Tier Classification")
                # Add content for Threat Categorization here (e.g., categorization metrics or visualizations)

# Function to convert DataFrame to CSV for download
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Call the main function
if __name__ == "__main__":
    main()
