"""
F1 Intelligence Dashboard - Pit Stop Visualization Module

Creates interactive, professional Plotly visualizations for pit stop analysis.
All charts use dark theme for modern dashboard aesthetics.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats
from typing import Tuple


def create_pitstop_histogram(pitstop_data: pd.DataFrame,
                             year_filter: int = None) -> go.Figure:
    """
    Create histogram of pit stop duration distribution.
    
    Args:
        pitstop_data: Pit stop DataFrame
        year_filter: Optional year filter
        
    Returns:
        Plotly Figure
    """
    data = pitstop_data.copy()
    
    if year_filter:
        data = data[data['year'] == year_filter]
    
    data = data.dropna(subset=['milliseconds'])
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=data['milliseconds'],
        nbinsx=50,
        name='Pit Stop Duration',
        marker=dict(
            color='rgba(76, 110, 245, 0.7)',
            line=dict(color='rgba(76, 110, 245, 1)', width=1)
        ),
        hovertemplate='<b>Duration Range</b><br>%{x:.0f}ms<br><b>Count</b>: %{y}<extra></extra>'
    ))
    
    # Add mean line
    mean_val = data['milliseconds'].mean()
    fig.add_vline(
        x=mean_val,
        line_dash="dash",
        line_color="rgba(76, 230, 100, 0.8)",
        annotation_text=f"Mean: {mean_val:.0f}ms",
        annotation_position="top right",
        annotation=dict(
            textangle=-90,
            font=dict(color='rgba(76, 230, 100, 1)', size=12)
        )
    )
    
    title_suffix = f" - {year_filter}" if year_filter else ""
    
    fig.update_layout(
        title=f"Pit Stop Duration Distribution{title_suffix}",
        xaxis_title="Duration (milliseconds)",
        yaxis_title="Frequency",
        template="plotly_dark",
        hovermode='x unified',
        height=500,
        showlegend=True,
        font=dict(family="Arial, sans-serif", size=12, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def create_pitstop_boxplot(pitstop_data: pd.DataFrame,
                           year_filter: int = None,
                           top_n: int = 12) -> go.Figure:
    """
    Create box plot of pit stop times by driver.
    
    Args:
        pitstop_data: Pit stop DataFrame
        year_filter: Optional year filter
        top_n: Show top N drivers by pit stops
        
    Returns:
        Plotly Figure
    """
    data = pitstop_data.copy()
    
    if year_filter:
        data = data[data['year'] == year_filter]
    
    # Get top drivers by number of pit stops
    top_drivers = data['driver_code'].value_counts().head(top_n).index.tolist()
    data = data[data['driver_code'].isin(top_drivers)]
    data = data.dropna(subset=['milliseconds', 'driver_code'])
    
    # Sort by median for better visualization
    driver_order = data.groupby('driver_code')['milliseconds'].median().sort_values().index.tolist()
    
    fig = go.Figure()
    
    for driver in driver_order:
        driver_data = data[data['driver_code'] == driver]['milliseconds']
        fig.add_trace(go.Box(
            y=driver_data,
            name=driver,
            boxmean='sd',  # Show mean and std dev
            hovertemplate='<b>%{fullData.name}</b><br>%{y:.0f}ms<extra></extra>'
        ))
    
    title_suffix = f" - {year_filter}" if year_filter else ""
    
    fig.update_layout(
        title=f"Pit Stop Distribution by Driver (Top {top_n}){title_suffix}",
        yaxis_title="Duration (milliseconds)",
        xaxis_title="Driver",
        template="plotly_dark",
        hovermode='y unified',
        height=600,
        showlegend=False,
        font=dict(family="Arial, sans-serif", size=11, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def create_pitstop_trend(trend_data: pd.DataFrame) -> go.Figure:
    """
    Create line chart showing pit stop time evolution over years.
    
    Args:
        trend_data: DataFrame with year and pit stop metrics
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    # Actual average
    fig.add_trace(go.Scatter(
        x=trend_data['year'],
        y=trend_data['milliseconds'],
        mode='markers+lines',
        name='Actual Average',
        line=dict(color='rgba(76, 110, 245, 0.8)', width=2),
        marker=dict(size=6, color='rgba(76, 110, 245, 1)'),
        hovertemplate='<b>%{x}</b><br>Avg: %{y:.0f}ms<extra></extra>'
    ))
    
    # Rolling average
    fig.add_trace(go.Scatter(
        x=trend_data['year'],
        y=trend_data['rolling_avg'],
        mode='lines',
        name='50-Race Rolling Average',
        line=dict(color='rgba(255, 100, 50, 0.8)', width=2, dash='dash'),
        hovertemplate='<b>%{x}</b><br>Rolling: %{y:.0f}ms<extra></extra>'
    ))
    
    fig.update_layout(
        title="Pit Stop Performance Trend (1950-2024)",
        xaxis_title="Year",
        yaxis_title="Average Duration (milliseconds)",
        template="plotly_dark",
        hovermode='x unified',
        height=500,
        font=dict(family="Arial, sans-serif", size=12, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def create_pitstop_by_stop_number(stop_stats: pd.DataFrame) -> go.Figure:
    """
    Create bar chart showing pit stop duration by stop number.
    
    Args:
        stop_stats: DataFrame with stop statistics
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=stop_stats['stop'],
        y=stop_stats['avg_time_ms'],
        name='Average Duration',
        marker=dict(color=stop_stats['avg_time_ms'], colorscale='Viridis'),
        error_y=dict(
            type='data',
            array=stop_stats['std_dev_ms'],
            visible=True
        ),
        hovertemplate='<b>Stop #%{x}</b><br>Avg: %{y:.0f}ms<br>σ: %{error_y.array:.0f}ms<extra></extra>'
    ))
    
    fig.update_layout(
        title="Pit Stop Duration by Stop Sequence",
        xaxis_title="Stop Number",
        yaxis_title="Average Duration (milliseconds)",
        template="plotly_dark",
        hovermode='x unified',
        height=450,
        showlegend=False,
        font=dict(family="Arial, sans-serif", size=12, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def create_top_crews_chart(top_crews: pd.DataFrame) -> go.Figure:
    """
    Create horizontal bar chart of fastest pit crews.
    
    Args:
        top_crews: DataFrame with crew statistics
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    # We will dynamically grab whatever the first two columns are named!
    # Assuming Column 0 is the Driver/Team Name, and Column 1 is the Time.
    name_col = top_crews.columns[0]
    time_col = top_crews.columns[1]
    
    # Sort ascending for better horizontal bar appearance
    top_crews = top_crews.sort_values(time_col)
    
    fig.add_trace(go.Bar(
        y=top_crews[name_col],
        x=top_crews[time_col],
        orientation='h',
        name='Average Stop Time',
        marker=dict(
            color=top_crews[time_col],
            colorscale='RdYlGn_r',  # Red (slow) to Green (fast)
            showscale=False
        ),
        text=top_crews[time_col].round(0),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Avg: %{x:.0f}ms<extra></extra>'
    ))
    
    fig.update_layout(
        title="Top 10 Fastest Pit Crews (All Time)",
        xaxis_title="Average Duration (milliseconds)",
        yaxis_title="Driver / Crew",
        template="plotly_dark",
        hovermode='y unified',
        height=500,
        showlegend=False,
        font=dict(family="Arial, sans-serif", size=12, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=100, r=50, t=80, b=50)
    )
    
    return fig

def create_era_comparison_chart(era_stats: pd.DataFrame) -> go.Figure:
    """
    Create comparison chart of pit stop times across F1 eras.
    
    Args:
        era_stats: DataFrame with era statistics
        
    Returns:
        Plotly Figure
    """
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Average Duration by Era", "Median Duration by Era"),
        horizontal_spacing=0.12
    )
    
    fig.add_trace(
        go.Bar(
            x=era_stats['era'],
            y=era_stats['mean_time'],
            name='Mean',
            marker=dict(color='rgba(76, 110, 245, 0.8)'),
            hovertemplate='<b>%{x}</b><br>Mean: %{y:.0f}ms<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=era_stats['era'],
            y=era_stats['median_time'],
            name='Median',
            marker=dict(color='rgba(255, 100, 50, 0.8)'),
            hovertemplate='<b>%{x}</b><br>Median: %{y:.0f}ms<extra></extra>'
        ),
        row=1, col=2
    )
    
    fig.update_xaxes(title_text="Era", row=1, col=1)
    fig.update_xaxes(title_text="Era", row=1, col=2)
    fig.update_yaxes(title_text="Duration (ms)", row=1, col=1)
    fig.update_yaxes(title_text="Duration (ms)", row=1, col=2)
    
    fig.update_layout(
        title="Pit Stop Evolution Across F1 Eras",
        template="plotly_dark",
        hovermode='x unified',
        height=500,
        showlegend=False,
        font=dict(family="Arial, sans-serif", size=11, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=50, r=50, t=100, b=50)
    )
    
    return fig


def create_pitstop_scatter(pitstop_data: pd.DataFrame,
                          results_data: pd.DataFrame = None) -> go.Figure:
    """
    Create scatter plot of pit stop time vs race position (if available).
    
    Args:
        pitstop_data: Pit stop DataFrame
        results_data: Optional race results for position correlation
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    # If results available, merge for position information
    if results_data is not None:
        # Group pit stops by race and driver
        pit_summary = pitstop_data.groupby(['raceId', 'driver_name']).agg({
            'milliseconds': 'mean'
        }).reset_index()
        pit_summary.columns = ['raceId', 'driver_name', 'avg_pitstop_ms']
        
        # Merge with results
        merged = results_data.merge(pit_summary, left_on='raceId', right_on='raceId', how='inner')
        merged = merged.dropna(subset=['position', 'avg_pitstop_ms'])
        merged['position'] = pd.to_numeric(merged['position'], errors='coerce')
        
        if len(merged) > 0:
            fig.add_trace(go.Scatter(
                x=merged['avg_pitstop_ms'],
                y=merged['position'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=merged['points'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Points Scored"),
                    line=dict(width=1, color='rgba(255, 255, 255, 0.3)')
                ),
                text=merged['driver_name'],
                hovertemplate='<b>%{text}</b><br>Avg Pit: %{x:.0f}ms<br>Position: %{y:.0f}<extra></extra>'
            ))
    else:
        # Simple histogram
        fig.add_trace(go.Histogram(
            x=pitstop_data['milliseconds'],
            name='Pit Stop Time',
            nbinsx=40,
            marker=dict(color='rgba(76, 110, 245, 0.7)')
        ))
    
    fig.update_layout(
        title="Pit Stop Duration vs Final Position",
        xaxis_title="Average Pit Stop Duration (milliseconds)",
        yaxis_title="Final Position",
        template="plotly_dark",
        hovermode='closest',
        height=500,
        font=dict(family="Arial, sans-serif", size=12, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=50, r=100, t=80, b=50)
    )
    
    return fig


def create_consistency_gauge(consistency_score: float,
                            driver_name: str) -> go.Figure:
    """
    Create gauge chart for pit stop consistency.
    
    Args:
        consistency_score: Score 0-100 (100 = perfect consistency)
        driver_name: Name of driver
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=consistency_score,
        title={'text': f"{driver_name} - Consistency Score"},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "rgba(76, 110, 245, 0.8)"},
            'steps': [
                {'range': [0, 25], 'color': "rgba(200, 50, 50, 0.2)"},
                {'range': [25, 50], 'color': "rgba(200, 150, 50, 0.2)"},
                {'range': [50, 75], 'color': "rgba(150, 200, 50, 0.2)"},
                {'range': [75, 100], 'color': "rgba(50, 200, 50, 0.2)"}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': consistency_score
            }
        }
    ))
    
    fig.update_layout(
        template="plotly_dark",
        height=400,
        font=dict(family="Arial, sans-serif", size=12, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


if __name__ == "__main__":
    pass