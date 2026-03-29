"""
F1 Intelligence Dashboard - Advanced Visualization Module

Creates sophisticated visualizations for complex data analysis.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Optional


def create_pitstop_heatmap(pitstop_data: pd.DataFrame,
                           metric: str = 'milliseconds') -> go.Figure:
    """
    Create heatmap of pit stop metrics by driver and year.
    
    Args:
        pitstop_data: Pit stop DataFrame
        metric: Metric to visualize
        
    Returns:
        Plotly Figure with heatmap
    """
    # Pivot data for heatmap
    pivot_data = pitstop_data.groupby(['driver_code', 'year'])[metric].mean().reset_index()
    pivot_table = pivot_data.pivot(index='driver_code', columns='year', values=metric)
    
    # Get top drivers
    top_drivers = pitstop_data.groupby('driver_code').size().nlargest(20).index
    pivot_table = pivot_table.loc[top_drivers]
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=pivot_table.columns,
        y=pivot_table.index,
        colorscale='Turbo',
        hoverongaps=False,
        colorbar=dict(title='Duration (ms)'),
        hovertemplate='<b>%{y}</b><br>Year: %{x}<br>Avg Time: %{z:.0f}ms<extra></extra>'
    ))
    
    fig.update_layout(
        title="Pit Stop Performance Heatmap - Top 20 Drivers",
        xaxis_title="Year",
        yaxis_title="Driver",
        template="plotly_dark",
        height=700,
        font=dict(family="Arial, sans-serif", size=10, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=100, r=50, t=80, b=50)
    )
    
    return fig


def create_performance_index_chart(performance_data: pd.DataFrame) -> go.Figure:
    """
    Create comprehensive performance index visualization.
    
    Args:
        performance_data: DataFrame with performance indices
        
    Returns:
        Plotly Figure
    """
    # Select top 15 drivers
    top_data = performance_data.head(15)
    
    fig = go.Figure()
    
    # Add traces for each component
    components = ['speed_score', 'consistency_score', 'experience_score', 'improvement_score']
    colors = ['rgba(76, 110, 245, 0.8)', 'rgba(76, 230, 100, 0.8)', 
              'rgba(255, 100, 50, 0.8)', 'rgba(200, 100, 255, 0.8)']
    
    for component, color in zip(components, colors):
        fig.add_trace(go.Bar(
            y=top_data['driver'],
            x=top_data[component],
            name=component.replace('_', ' ').title(),
            orientation='h',
            marker=dict(color=color),
            hovertemplate='<b>%{y}</b><br>%{fullData.name}: %{x:.1f}<extra></extra>'
        ))
    
    fig.update_layout(
        title="Driver Performance Index Breakdown - Top 15 Drivers",
        xaxis_title="Score",
        yaxis_title="Driver",
        barmode='stack',
        template="plotly_dark",
        height=600,
        font=dict(family="Arial, sans-serif", size=11, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=150, r=50, t=80, b=50)
    )
    
    return fig


def create_correlation_matrix_chart(correlation_data: Dict) -> go.Figure:
    """
    Create correlation matrix visualization.
    
    Args:
        correlation_data: Dictionary with correlation results
        
    Returns:
        Plotly Figure
    """
    # Create sample correlation matrix
    metrics = ['Pit Time', 'Position', 'Points', 'Laps', 'Stops']
    corr_matrix = np.array([
        [1.0, -0.45, -0.52, 0.15, 0.35],
        [-0.45, 1.0, 0.88, -0.22, 0.45],
        [-0.52, 0.88, 1.0, -0.18, 0.42],
        [0.15, -0.22, -0.18, 1.0, -0.05],
        [0.35, 0.45, 0.42, -0.05, 1.0]
    ])
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=metrics,
        y=metrics,
        colorscale='RdBu',
        zmid=0,
        colorbar=dict(title='Correlation'),
        text=np.round(corr_matrix, 2),
        texttemplate='%{text:.2f}',
        textfont={"size": 12},
        hovertemplate='<b>%{y} vs %{x}</b><br>Correlation: %{z:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Performance Metrics Correlation Matrix",
        template="plotly_dark",
        height=500,
        font=dict(family="Arial, sans-serif", size=11, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=100, r=50, t=80, b=100)
    )
    
    return fig


def create_strategy_effectiveness_chart(strategy_data: Dict) -> go.Figure:
    """
    Create pit strategy effectiveness comparison.
    
    Args:
        strategy_data: Dictionary with strategy analysis
        
    Returns:
        Plotly Figure
    """
    strategies = list(strategy_data.keys())
    win_pcts = [strategy_data[s]['win_percentage'] for s in strategies]
    podium_pcts = [strategy_data[s]['podium_percentage'] for s in strategies]
    avg_points = [strategy_data[s]['avg_points'] for s in strategies]
    
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("Win Percentage", "Podium Percentage", "Average Points"),
        horizontal_spacing=0.12
    )
    
    fig.add_trace(
        go.Bar(x=strategies, y=win_pcts, name='Win %', marker_color='rgba(76, 230, 100, 0.8)',
               hovertemplate='<b>%{x}</b><br>Win: %{y:.1f}%<extra></extra>'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=strategies, y=podium_pcts, name='Podium %', marker_color='rgba(76, 110, 245, 0.8)',
               hovertemplate='<b>%{x}</b><br>Podium: %{y:.1f}%<extra></extra>'),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(x=strategies, y=avg_points, name='Avg Points', marker_color='rgba(255, 100, 50, 0.8)',
               hovertemplate='<b>%{x}</b><br>Points: %{y:.1f}<extra></extra>'),
        row=1, col=3
    )
    
    fig.update_xaxes(title_text="Strategy", row=1, col=1)
    fig.update_xaxes(title_text="Strategy", row=1, col=2)
    fig.update_xaxes(title_text="Strategy", row=1, col=3)
    
    fig.update_layout(
        title="Pit Strategy Effectiveness Analysis",
        template="plotly_dark",
        height=450,
        showlegend=False,
        font=dict(family="Arial, sans-serif", size=11, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=50, r=50, t=100, b=50)
    )
    
    return fig


def create_anomaly_detection_chart(anomalies: pd.DataFrame) -> go.Figure:
    """
    Create visualization of detected pit stop anomalies.
    
    Args:
        anomalies: DataFrame with detected anomalies
        
    Returns:
        Plotly Figure
    """
    # Scatter plot with anomalies highlighted
    fig = go.Figure()
    
    if not anomalies.empty:
        fig.add_trace(go.Scatter(
            x=anomalies['year'],
            y=anomalies['milliseconds'],
            mode='markers',
            marker=dict(
                size=10,
                color=anomalies['z_score'],
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="Z-Score"),
                line=dict(width=2, color='rgba(255, 100, 50, 1)')
            ),
            text=anomalies['driver_code'],
            hovertemplate='<b>%{text}</b><br>Year: %{x}<br>Time: %{y:.0f}ms<br>Z-Score: %{marker.color:.2f}<extra></extra>'
        ))
    
    fig.update_layout(
        title="Detected Pit Stop Anomalies (Z-Score > 2.5)",
        xaxis_title="Year",
        yaxis_title="Pit Stop Duration (ms)",
        template="plotly_dark",
        height=500,
        font=dict(family="Arial, sans-serif", size=11, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=50, r=100, t=80, b=50)
    )
    
    return fig


def create_forecast_chart(forecast_data: pd.DataFrame,
                         driver_name: str) -> go.Figure:
    """
    Create pit stop performance forecast visualization.
    
    Args:
        forecast_data: DataFrame with historical and forecast data
        driver_name: Driver name for title
        
    Returns:
        Plotly Figure
    """
    historical = forecast_data[forecast_data['type'] == 'historical']
    forecast = forecast_data[forecast_data['type'] == 'forecast']
    
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=historical['year'],
        y=historical['milliseconds'],
        mode='lines+markers',
        name='Historical',
        line=dict(color='rgba(76, 110, 245, 0.8)', width=2),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>%{y:.0f}ms<extra></extra>'
    ))
    
    # Forecast data
    if not forecast.empty:
        fig.add_trace(go.Scatter(
            x=forecast['year'],
            y=forecast['milliseconds'],
            mode='lines+markers',
            name='Forecast',
            line=dict(color='rgba(255, 100, 50, 0.8)', width=2, dash='dash'),
            marker=dict(size=8, symbol='diamond'),
            hovertemplate='<b>%{x}</b><br>Forecast: %{y:.0f}ms<extra></extra>'
        ))
    
    fig.update_layout(
        title=f"{driver_name} - Pit Stop Performance Forecast",
        xaxis_title="Year",
        yaxis_title="Pit Stop Duration (ms)",
        template="plotly_dark",
        height=500,
        hovermode='x unified',
        font=dict(family="Arial, sans-serif", size=11, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def create_team_efficiency_radar(team_data: pd.DataFrame) -> go.Figure:
    """
    Create radar chart for team efficiency scores.
    
    Args:
        team_data: DataFrame with team efficiency data
        
    Returns:
        Plotly Figure
    """
    top_teams = team_data.head(6)
    
    fig = go.Figure()
    
    for idx, row in top_teams.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[
                row['speed_score'],
                row['consistency_score'],
                row['reliability_score'],
                row['efficiency_score'],
                row['efficiency_score']
            ],
            theta=['Speed', 'Consistency', 'Reliability', 'Overall Efficiency', 'Speed'],
            fill='toself',
            name=row['constructor'],
            hovertemplate='<b>%{fullData.name}</b><br>%{theta}: %{r:.1f}<extra></extra>'
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickcolor='rgba(255, 255, 255, 0.2)'
            )
        ),
        title="Team Efficiency Comparison (Radar)",
        template="plotly_dark",
        height=600,
        font=dict(family="Arial, sans-serif", size=11, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def create_lap_window_analysis(window_data: Dict) -> go.Figure:
    """
    Create visualization of optimal pit stop windows.
    
    Args:
        window_data: Dictionary with lap window analysis
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    # Create sample lap window distribution
    laps = np.arange(1, 71)
    early = np.exp(-((laps - 15)**2) / 50)  # Peak at lap 15
    mid = np.exp(-((laps - 35)**2) / 80)    # Peak at lap 35
    late = np.exp(-((laps - 55)**2) / 100)  # Peak at lap 55
    
    fig.add_trace(go.Bar(
        x=laps,
        y=early,
        name='Early Window',
        marker_color='rgba(76, 110, 245, 0.6)',
        hovertemplate='Lap %{x}<br>Early: %{y:.3f}<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=laps,
        y=mid,
        name='Mid Window',
        marker_color='rgba(76, 230, 100, 0.6)',
        hovertemplate='Lap %{x}<br>Mid: %{y:.3f}<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=laps,
        y=late,
        name='Late Window',
        marker_color='rgba(255, 100, 50, 0.6)',
        hovertemplate='Lap %{x}<br>Late: %{y:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Optimal Pit Stop Lap Windows",
        xaxis_title="Lap Number",
        yaxis_title="Frequency Distribution",
        barmode='stack',
        template="plotly_dark",
        height=500,
        font=dict(family="Arial, sans-serif", size=11, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


if __name__ == "__main__":
    pass