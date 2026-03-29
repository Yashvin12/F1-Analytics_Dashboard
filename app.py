"""
F1 Intelligence Dashboard - Main Application

Production-grade Streamlit dashboard for F1 analytics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_loader import (
    load_all_datasets,
    prepare_pitstop_data,
    prepare_race_results_data,
    get_unique_drivers,
    get_years_range,
    filter_data_by_driver_year,
    get_driver_pitstop_stats,
    get_pitstop_time_trend
)

from src.analysis.pitstop import (
    get_top_pit_crews,
    get_pitstop_distribution,
    get_pitstop_by_lap,
    get_pitstop_per_stop_number,
    get_era_comparison,
    calculate_pitstop_consistency,
    get_pitstop_improvements,
    get_pitstop_risk_analysis
)

from src.visuals.pitstop_viz import (
    create_pitstop_histogram,
    create_pitstop_boxplot,
    create_pitstop_trend,
    create_pitstop_by_stop_number,
    create_top_crews_chart,
    create_era_comparison_chart,
    create_consistency_gauge
)

from src.analysis.telemetry import (
    create_lap_time_analysis,
    create_speed_distribution,
    create_position_changes_chart,
    create_comparative_lap_times,
    get_lap_statistics
)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="F1 Intelligence Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
        /* Dark theme customization */
        [data-testid="stMetricValue"] {
            font-size: 28px;
        }
        [data-testid="stMetricLabel"] {
            font-size: 14px;
        }
        .metric-card {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid rgba(76, 110, 245, 0.3);
        }
        h1 {
            color: #4c6ef5;
            font-weight: 700;
            letter-spacing: 1px;
        }
        h2 {
            color: #a0b4ff;
            font-weight: 600;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
        }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# LOAD DATA
# ============================================================================

@st.cache_resource
def init_app():
    """Initialize and load all data."""
    datasets = load_all_datasets()
    pitstop_data = prepare_pitstop_data(datasets)
    race_results = prepare_race_results_data(datasets)
    lap_times = datasets.get('lap_times', None) or pd.read_csv("data/lap_times.csv")
    
    return {
        'datasets': datasets,
        'pitstop_data': pitstop_data,
        'race_results': race_results,
        'lap_times': lap_times
    }


# Initialize
data = init_app()
pitstop_data = data['pitstop_data']
race_results = data['race_results']
lap_times_df = data['lap_times']


# ============================================================================
# HEADER
# ============================================================================

col1, col2 = st.columns([0.8, 0.2])

with col1:
    st.title("🏎️ F1 Intelligence Dashboard")
    st.markdown("**Advanced Analytics & Performance Insights** | 1950-2024 Season Analysis")

with col2:
    st.metric("Data Points", f"{len(pitstop_data):,}")


st.divider()


# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

with st.sidebar:
    st.header("⚙️ Controls")
    
    # Page selection
    page = st.radio(
        "Select Analysis",
        ["📊 Pit Stop Analytics", "🏁 Telemetry & Lap Analysis", "🎯 Driver Insights"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Get years range
    min_year, max_year = get_years_range(pitstop_data)
    
    # Global filters
    st.subheader("Global Filters")
    
    selected_year = st.slider(
        "Season Year",
        min_value=min_year,
        max_value=max_year,
        value=max_year,
        step=1,
        help="Filter data by F1 season"
    )
    
    available_drivers = get_unique_drivers(pitstop_data)
    selected_driver = st.selectbox(
        "Driver (Optional)",
        ["All Drivers"] + available_drivers,
        help="Filter by specific driver or view all"
    )
    
    st.divider()
    
    # Info section
    st.subheader("📈 Dataset Info")
    st.write(f"""
    - **Total Pit Stops**: {len(pitstop_data):,}
    - **Total Races**: {pitstop_data['raceId'].nunique():,}
    - **Unique Drivers**: {pitstop_data['driver_name'].nunique():,}
    - **Years Covered**: {min_year}-{max_year}
    """)


# ============================================================================
# PAGE 1: PIT STOP ANALYTICS
# ============================================================================

if page == "📊 Pit Stop Analytics":
    
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 Overview", "🎯 Driver Analysis", "⏱️ Crew Performance", "📊 Trends & Comparisons"]
    )
    
    # ---- TAB 1: OVERVIEW ----
    with tab1:
        st.subheader("Pit Stop Performance Overview")
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        filtered_data = filter_data_by_driver_year(pitstop_data, selected_driver, selected_year)
        
        with col1:
            avg_pit_time = filtered_data['milliseconds'].mean()
            st.metric(
                "Avg Pit Stop",
                f"{avg_pit_time:.0f}ms",
                f"{avg_pit_time/1000:.2f}s",
            )
        
        with col2:
            fastest = filtered_data['milliseconds'].min()
            st.metric(
                "Fastest Stop",
                f"{fastest:.0f}ms",
                f"{fastest/1000:.2f}s",
                help="Best pit stop time"
            )
        
        with col3:
            slowest = filtered_data['milliseconds'].max()
            st.metric(
                "Slowest Stop",
                f"{slowest:.0f}ms",
                f"{slowest/1000:.2f}s"
            )
        
        with col4:
            total_stops = len(filtered_data)
            st.metric(
                "Total Stops",
                f"{total_stops:,}",
                help="Pit stops in selection"
            )
        
        st.divider()
        
        # Main visualizations
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.plotly_chart(
                create_pitstop_histogram(pitstop_data, selected_year if selected_year else None),
                use_container_width=True
            )
        
        with col2:
            st.plotly_chart(
                create_pitstop_by_stop_number(get_pitstop_per_stop_number(pitstop_data, selected_year)),
                use_container_width=True
            )
        
        st.divider()
        
        # Distribution analysis
        st.subheader("Detailed Distribution Analysis")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.plotly_chart(
                create_pitstop_boxplot(pitstop_data, selected_year),
                use_container_width=True
            )
        
        with col2:
            era_stats = get_era_comparison(pitstop_data)
            st.plotly_chart(
                create_era_comparison_chart(era_stats),
                use_container_width=True
            )
    
    # ---- TAB 2: DRIVER ANALYSIS ----
    with tab2:
        st.subheader("Individual Driver Performance")
        
        if selected_driver != "All Drivers":
            driver_name = selected_driver
            consistency = calculate_pitstop_consistency(pitstop_data, driver_name)
            improvements = get_pitstop_improvements(pitstop_data, driver_name)
            
            # Consistency gauge
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                st.plotly_chart(
                    create_consistency_gauge(consistency['consistency_score'], driver_name),
                    use_container_width=True
                )
            
            with col2:
                st.metric("Mean Stop Time", f"{consistency['mean']:.0f}ms")
                st.metric("Std Deviation", f"{consistency['std']:.0f}ms")
            
            with col3:
                st.metric("Coefficient of Variation", f"{consistency['cv']:.2f}%")
                st.metric("Total Pit Stops", f"{consistency['sample_size']:,}")
            
            st.divider()
            
            # Improvements over time
            st.subheader(f"{driver_name} - Pit Stop Evolution")
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=improvements['year'],
                y=improvements['avg_stop_ms'],
                name='Average Pit Stop',
                marker=dict(color=improvements['avg_stop_ms'], colorscale='Viridis'),
                hovertemplate='<b>%{x}</b><br>Avg: %{y:.0f}ms<extra></extra>'
            ))
            
            fig.update_layout(
                title=f"{driver_name} - Average Pit Stop by Season",
                xaxis_title="Season",
                yaxis_title="Average Duration (ms)",
                template="plotly_dark",
                height=450,
                font=dict(family="Arial", size=11, color='rgba(255, 255, 255, 0.8)'),
                plot_bgcolor='rgba(10, 10, 20, 1)',
                paper_bgcolor='rgba(10, 10, 20, 1)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            # Driver stats table
            st.subheader("Career Statistics")
            driver_stats = get_driver_pitstop_stats(pitstop_data)
            driver_stats = driver_stats[driver_stats['driver_name'] == driver_name]
            st.dataframe(
                driver_stats,
                use_container_width=True,
                hide_index=True
            )
        
        else:
            st.info("👈 Select a specific driver in the sidebar to see detailed analysis")
            
            # Show top drivers comparison
            st.subheader("Top 10 Most Consistent Drivers")
            
            consistency_data = []
            for driver in get_unique_drivers(pitstop_data)[:50]:
                cons = calculate_pitstop_consistency(pitstop_data, driver)
                consistency_data.append({
                    'Driver': driver,
                    'Consistency Score': cons['consistency_score'],
                    'Mean Time (ms)': cons['mean'],
                    'Std Dev (ms)': cons['std'],
                    'Pit Stops': cons['sample_size']
                })
            
            consistency_df = pd.DataFrame(consistency_data).sort_values('Consistency Score', ascending=False).head(10)
            st.dataframe(consistency_df, use_container_width=True, hide_index=True)
    
    # ---- TAB 3: CREW PERFORMANCE ----
    with tab3:
        st.subheader("Top Pit Crews Ranking")
        
        col1, col2 = st.columns([0.6, 0.4])
        
        with col1:
            top_crews = get_top_pit_crews(pitstop_data, selected_year if selected_year else None)
            st.plotly_chart(
                create_top_crews_chart(top_crews),
                use_container_width=True
            )
        
        with col2:
            st.info("🏁 **Top Pit Crews** ranked by average pit stop duration across all races.")
            st.dataframe(top_crews)
        
        st.divider()
        
        # Risk analysis
        st.subheader("Pit Stop Consistency & Risk Analysis")
        
        risk_analysis = get_pitstop_risk_analysis(pitstop_data, selected_year if selected_year else None)
        
        col1, col2 = st.columns([0.6, 0.4])
        
        with col1:
            risk_chart = go.Figure()
            risk_chart.add_trace(go.Bar(
                x=risk_analysis.head(15)['driver'],
                y=risk_analysis.head(15)['risk_score'],
                marker=dict(
                    color=risk_analysis.head(15)['risk_score'],
                    colorscale='RdYlGn_r'
                ),
                text=risk_analysis.head(15)['consistency'],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Risk: %{y:.2f}%<br>%{text}<extra></extra>'
            ))
            
            risk_chart.update_layout(
                title="Pit Stop Reliability (Top 15 Drivers)",
                xaxis_title="Driver",
                yaxis_title="Risk Score (% Outliers)",
                template="plotly_dark",
                height=500,
                font=dict(size=10),
                plot_bgcolor='rgba(10, 10, 20, 1)',
                paper_bgcolor='rgba(10, 10, 20, 1)'
            )
            
            st.plotly_chart(risk_chart, use_container_width=True)
        
        with col2:
            st.info("Risk scores indicate pit stop variability and unpredictability.")
            st.dataframe(
                risk_analysis.head(10)[['driver', 'total_stops', 'outlier_count', 'risk_score', 'consistency']],
                use_container_width=True,
                hide_index=True
            )
    
    # ---- TAB 4: TRENDS & COMPARISONS ----
    with tab4:
        st.subheader("Historical Trends & Era Analysis")
        
        # Trend over time
        trend_data = get_pitstop_time_trend(pitstop_data, window=50)
        st.plotly_chart(
            create_pitstop_trend(trend_data),
            use_container_width=True
        )
        
        st.divider()
        
        st.subheader("Key Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_2009 = pitstop_data[pitstop_data['year'] == 2009]['milliseconds'].mean()
            avg_2024 = pitstop_data[pitstop_data['year'] == 2024]['milliseconds'].mean()
            improvement = ((avg_2009 - avg_2024) / avg_2009) * 100
            
            st.metric(
                "Pit Stop Speed Improvement",
                f"{improvement:.1f}%",
                f"2009: {avg_2009:.0f}ms → 2024: {avg_2024:.0f}ms"
            )
        
        with col2:
            modern_era = pitstop_data[pitstop_data['year'] >= 2020]['milliseconds'].std()
            st.metric(
                "Modern Era Consistency",
                f"{modern_era:.1f}ms",
                "Std Dev (2020-2024)"
            )
        
        with col3:
            fastest_stop = pitstop_data['milliseconds'].min()
            st.metric(
                "F1 Record Pit Stop",
                f"{fastest_stop:.1f}ms",
                f"{fastest_stop/1000:.2f} seconds"
            )


# ============================================================================
# PAGE 2: TELEMETRY & LAP ANALYSIS
# ============================================================================

elif page == "🏁 Telemetry & Lap Analysis":
    
    st.subheader("Race Telemetry & Lap-by-Lap Analysis")
    
    col1, col2 = st.columns([0.5, 0.5])
    
    with col1:
        race_list = pitstop_data[pitstop_data['year'] == selected_year]['name'].unique().tolist()
        if race_list:
            selected_race = st.selectbox(
                "Select Race",
                sorted(race_list),
                key="race_select"
            )
        else:
            st.warning("No races available for selected year")
            selected_race = None
    
    with col2:
        if selected_race:
            race_id = pitstop_data[pitstop_data['name'] == selected_race].iloc[0]['raceId']
            race_drivers = pitstop_data[pitstop_data['raceId'] == race_id]['driverId'].unique()
            if len(race_drivers) > 0:
                selected_race_driver = st.selectbox(
                    "Select Driver",
                    race_drivers,
                    key="race_driver_select"
                )
            else:
                selected_race_driver = None
    
    if selected_race and selected_race_driver:
        race_id = pitstop_data[pitstop_data['name'] == selected_race].iloc[0]['raceId']
        
        st.divider()
        
        # Lap statistics
        stats = get_lap_statistics(lap_times_df, race_id, selected_race_driver)
        
        if stats:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Laps", f"{stats.get('total_laps', 0):.0f}")
            with col2:
                st.metric("Fastest Lap", f"{stats.get('fastest_lap_s', 0):.2f}s")
            with col3:
                st.metric("Average Lap", f"{stats.get('average_lap_s', 0):.2f}s")
            with col4:
                st.metric("Slowest Lap", f"{stats.get('slowest_lap_s', 0):.2f}s")
            with col5:
                st.metric("Consistency", f"{100 - stats.get('consistency_coefficient', 0):.1f}%")
        
        st.divider()
        
        # Visualizations
        tab1, tab2, tab3 = st.tabs(["📈 Lap Times", "📊 Distribution", "🏁 Position"])
        
        with tab1:
            st.plotly_chart(
                create_lap_time_analysis(lap_times_df, race_id, selected_race_driver),
                use_container_width=True
            )
        
        with tab2:
            st.plotly_chart(
                create_speed_distribution(lap_times_df, race_id, selected_race_driver),
                use_container_width=True
            )
        
        with tab3:
            st.plotly_chart(
                create_position_changes_chart(lap_times_df, race_id),
                use_container_width=True
            )
    
    else:
        st.info("👈 Select a race and driver to view telemetry analysis")


# ============================================================================
# PAGE 3: DRIVER INSIGHTS
# ============================================================================

elif page == "🎯 Driver Insights":
    
    st.subheader("Driver Performance Insights & Comparisons")
    
    tab1, tab2, tab3 = st.tabs(["👥 Comparison", "🏆 Rankings", "📈 Career Trends"])
    
    with tab1:
        st.subheader("Driver Pit Stop Comparison")
        
        # Select multiple drivers
        comparison_drivers = st.multiselect(
            "Select Drivers to Compare",
            get_unique_drivers(pitstop_data),
            default=[get_unique_drivers(pitstop_data)[0], get_unique_drivers(pitstop_data)[1]] 
            if len(get_unique_drivers(pitstop_data)) > 1 else [get_unique_drivers(pitstop_data)[0]]
        )
        
        if comparison_drivers:
            comparison_data = pitstop_data[pitstop_data['driver_name'].isin(comparison_drivers)]
            comparison_data = comparison_data.dropna(subset=['milliseconds'])
            
            fig = go.Figure()
            
            for driver in comparison_drivers:
                driver_data = comparison_data[comparison_data['driver_name'] == driver]
                fig.add_trace(go.Box(
                    y=driver_data['milliseconds'],
                    name=driver,
                    boxmean='sd'
                ))
            
            fig.update_layout(
                title="Pit Stop Distribution Comparison",
                yaxis_title="Duration (ms)",
                template="plotly_dark",
                height=600,
                font=dict(size=11),
                plot_bgcolor='rgba(10, 10, 20, 1)',
                paper_bgcolor='rgba(10, 10, 20, 1)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Comparison table
            st.divider()
            st.subheader("Statistical Comparison")
            
            comparison_stats = []
            for driver in comparison_drivers:
                driver_stops = pitstop_data[pitstop_data['driver_name'] == driver]['milliseconds']
                comparison_stats.append({
                    'Driver': driver,
                    'Mean (ms)': driver_stops.mean(),
                    'Median (ms)': driver_stops.median(),
                    'Min (ms)': driver_stops.min(),
                    'Max (ms)': driver_stops.max(),
                    'Std Dev (ms)': driver_stops.std(),
                    'Total Stops': len(driver_stops)
                })
            
            comparison_df = pd.DataFrame(comparison_stats)
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("All-Time Driver Rankings")
        
        # Different ranking options
        rank_metric = st.radio(
            "Rank By:",
            ["Fastest Average", "Most Consistent", "Most Pit Stops", "Improvement Over Career"]
        )
        
        if rank_metric == "Fastest Average":
            stats = get_driver_pitstop_stats(pitstop_data)
            stats = stats.sort_values('avg_time_ms')
            st.dataframe(stats.head(20), use_container_width=True, hide_index=True)
        
        elif rank_metric == "Most Consistent":
            consistency_list = []
            for driver in get_unique_drivers(pitstop_data):
                cons = calculate_pitstop_consistency(pitstop_data, driver)
                consistency_list.append({
                    'Driver': driver,
                    'Consistency Score': cons['consistency_score'],
                    'Mean (ms)': cons['mean'],
                    'Std Dev (ms)': cons['std']
                })
            consistency_df = pd.DataFrame(consistency_list).sort_values('Consistency Score', ascending=False)
            st.dataframe(consistency_df.head(20), use_container_width=True, hide_index=True)
        
        elif rank_metric == "Most Pit Stops":
            stop_counts = pitstop_data.groupby('driver_name').size().sort_values(ascending=False)
            stop_df = pd.DataFrame({
                'Driver': stop_counts.index,
                'Total Pit Stops': stop_counts.values
            })
            st.dataframe(stop_df.head(20), use_container_width=True, hide_index=True)
        
        else:  # Improvement
            improvement_list = []
            for driver in get_unique_drivers(pitstop_data):
                improvements = get_pitstop_improvements(pitstop_data, driver)
                if len(improvements) > 1:
                    first_year_avg = improvements.iloc[0]['avg_stop_ms']
                    last_year_avg = improvements.iloc[-1]['avg_stop_ms']
                    improvement_pct = ((first_year_avg - last_year_avg) / first_year_avg) * 100
                    improvement_list.append({
                        'Driver': driver,
                        'Improvement %': improvement_pct,
                        'First Year Avg (ms)': first_year_avg,
                        'Last Year Avg (ms)': last_year_avg
                    })
            
            if improvement_list:
                improvement_df = pd.DataFrame(improvement_list).sort_values('Improvement %', ascending=False)
                st.dataframe(improvement_df.head(20), use_container_width=True, hide_index=True)
    
    with tab3:
        st.subheader("Career Pit Stop Evolution")
        
        if selected_driver != "All Drivers":
            driver_name = selected_driver
            improvements = get_pitstop_improvements(pitstop_data, driver_name)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=improvements['year'],
                y=improvements['avg_stop_ms'],
                mode='lines+markers',
                name='Average Pit Stop',
                line=dict(color='rgba(76, 110, 245, 0.8)', width=2),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor='rgba(76, 110, 245, 0.1)',
                hovertemplate='<b>%{x}</b><br>Avg: %{y:.0f}ms<extra></extra>'
            ))
            
            fig.update_layout(
                title=f"{driver_name} - Career Pit Stop Evolution",
                xaxis_title="Season",
                yaxis_title="Average Duration (ms)",
                template="plotly_dark",
                height=500,
                font=dict(size=11),
                plot_bgcolor='rgba(10, 10, 20, 1)',
                paper_bgcolor='rgba(10, 10, 20, 1)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("👈 Select a driver in the sidebar to view career trends")


# ============================================================================
# FOOTER
# ============================================================================

st.divider()

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.caption("📊 Data Source: F1 Historical Database (1950-2024)")

with col2:
    st.caption("🔧 Built with Streamlit & Plotly")

with col3:
    st.caption("✨ F1 Intelligence Dashboard v1.0")