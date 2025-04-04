# -*- coding: utf-8 -*-
"""newapp.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1D_SVhXGpyUoqqhRs_SFWQQpD5Qd5CDrK
"""
import streamlit as st
import pandas as pd
from datetime import datetime 
import os
import requests 
from PIL import Image  # For resizing images
from io import BytesIO, StringIO  # For handling file-like objects

# Import pipeline functions (ensure they are implemented in `pipeline.py`)
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

# Main app
def main():
    st.title("🇬🇦 Gabon Election Threat Intelligence Dashboard")
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

                st.session_state.processed = True
                st.session_state.clustered_df = clustered_df
                st.session_state.momentum_states = momentum_states
                st.session_state.emerging_trends = emerging_trends
                st.rerun()

            # Display Results for Real-Time Analysis
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
                        st.markdown("### Cluster Overview")
                        st.dataframe(clustered_df)

                        # Bar Chart for Total Posts and Peak Activity
                        st.markdown("### Total Posts and Peak Activity by Cluster")
                        bar_data = clustered_df.groupby('Cluster ID')[['Total Posts', 'Peak Activity']].sum().reset_index()
                        st.bar_chart(bar_data.set_index('Cluster ID'))

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

    elif analysis_option == "📈 View Preprocessed Data Results":
        # File upload for preprocessed report
        uploaded_file = st.file_uploader(
            "Upload Preprocessed Report (CSV)",
            type=["csv"],
            help="Requires columns: 'Cluster ID', 'First Detected', 'Last Updated', 'Momentum Score', 'Total Posts', 'Peak Activity', 'Unique Sources', 'Report Summary', 'All URLs', 'Thread Categorization'"
        )

        # If no file is uploaded, fetch the preprocessed report from GitHub
        if not uploaded_file:
            github_csv_url = "https://raw.githubusercontent.com/hanna-tes/RadarSystem/refs/heads/main/Gabon_intelligence_reportMarch.csv"
            st.write("Fetching preprocessed report from GitHub...")
            raw_data = fetch_data_from_github(github_csv_url)
            if raw_data:
                df = load_csv_data(raw_data)
                st.success("✅ Preprocessed report loaded successfully!")
            else:
                st.error("❌ Failed to fetch preprocessed report from GitHub.")
                return
        else:
            # Load uploaded file
            df = load_csv_data(uploaded_file)

        # Validate input data
        expected_columns = {
            'Cluster ID',
            'First Detected',
            'Last Updated',
            'Momentum Score',
            'Total Posts',
            'Peak Activity',
            'Unique Sources',
            'Report Summary',
            'All URLs',
            'Thread Categorization'
        }
        if not expected_columns.issubset(df.columns):
            missing_columns = expected_columns - set(df.columns)
            st.error(f"❌ The uploaded file is missing required columns. Missing: {missing_columns}. Found: {list(df.columns)}")
            return

        # Display Results
        st.session_state.processed = True
        st.session_state.preprocessed_data = df

        # Create tabs
        tab1, tab2, tab3 = st.tabs([
            "📊 Cluster Analytics",
            "📜 Threat Reports",
            "🚨 Threat Categorization"
        ])

        with tab1:
            st.markdown("### Cluster Overview")
            st.dataframe(df)

            # Heatmap Visualization
            heatmap_url = "https://raw.githubusercontent.com/hanna-tes/RadarSystem/main/trend_visualization_March_AP.png"
            try:
                response = requests.get(heatmap_url)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    resized_img = img.resize((800, 600))  # Adjust size as needed
                    st.image(resized_img, caption="Narrative Growth vs Momentum Intensity", use_container_width=True)
                else:
                    st.error(f"❌ Failed to fetch heatmap image. Status code: {response.status_code}")
            except Exception as e:
                st.error(f"❌ An error occurred while fetching the heatmap image: {e}")

            # Bar Chart for Total Posts and Peak Activity
            st.markdown("### Total Posts and Peak Activity by Cluster")
            bar_data = df.groupby('Cluster ID')[['Total Posts', 'Peak Activity']].sum().reset_index()
            st.bar_chart(bar_data.set_index('Cluster ID'))

        with tab2:
            cluster_selector = st.selectbox(
                "Select Cluster for Detailed Analysis",
                options=df['Cluster ID'].unique(),
                format_func=lambda x: f"Cluster {x}"
            )
            cluster_data = df[df['Cluster ID'] == cluster_selector]

            # Display report summary
            st.markdown(f"#### Report Summary for Cluster {cluster_selector}")
            st.info(cluster_data['Report Summary'].values[0])

            # Display associated URLs
            st.markdown("### Associated URLs")
            urls = cluster_data['All URLs'].values[0].split("\n")  # Assuming URLs are newline-separated
            for url in urls:
                st.markdown(f"- [{url.strip()}]({url.strip()})")

        with tab3:
            st.markdown("### Threat Tier Classification")
            categorization_df = df[['Cluster ID', 'Thread Categorization']]
            st.dataframe(categorization_df)

            # Add download button
            st.download_button(
                label="📥 Download Full Report",
                data=convert_df(df),
                file_name=f"threat_report_{datetime.now().date()}.csv",
                mime="text/csv"
            )

# Function to fetch data from GitHub
@st.cache_data
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

# Function to load CSV data with error handling
def load_csv_data(raw_data):
    try:
        df = pd.read_csv(StringIO(raw_data), on_bad_lines='skip')  # Skip problematic rows
        return df
    except Exception as e:
        st.error(f"❌ Failed to parse CSV data: {e}")
        return None

# Function to convert DataFrame to CSV for download
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Call the main function
if __name__ == "__main__":
    main()
