"""
F1 Intelligence Dashboard - Telemetry & Track Visualization Module

Provides telemetry analysis and track map visualizations.
Note: FastF1 integration is optional - includes fallback visualizations.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Tuple, Optional, Dict
import streamlit as st


def create_track_map_from_lap_data(lap_times_data: pd.DataFrame,
                                   race_id: int,
                                   driver_id: int) -> go.Figure:
    """
    Create a track map visualization from lap time data.
    Uses lap position coordinates if available.
    
    Args:
        lap_times_data: Lap times DataFrame with position info
        race_id: Race to visualize
        driver_id: Driver to visualize
        
    Returns:
        Plotly Figure with track map
    """
    race_lap_data = lap_times_data[
        (lap_times_data['raceId'] == race_id) & 
        (lap_times_data['driverId'] == driver_id)
    ].copy()
    
    if race_lap_data.empty:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(text="No telemetry data available for this race/driver combination")
        return fig
    
    # Create synthetic track position based on lap number progression
    race_lap_data = race_lap_data.sort_values('lap')
    
    # Create circular track approximation
    num_laps = len(race_lap_data)
    angles = np.linspace(0, 2*np.pi, num_laps)
    
    x_pos = np.cos(angles) * 100
    y_pos = np.sin(angles) * 100
    
    fig = go.Figure()
    
    # Plot track
    fig.add_trace(go.Scatter(
        x=x_pos,
        y=y_pos,
        mode='markers+lines',
        name='Track Progression',
        marker=dict(
            size=8,
            color=race_lap_data['milliseconds'].values,
            colorscale='Turbo',
            showscale=True,
            colorbar=dict(
                title="Lap Time<br>(ms)",
                thickness=15,
                len=0.7,
                x=1.1
            ),
            line=dict(width=1, color='rgba(255, 255, 255, 0.3)')
        ),
        line=dict(color='rgba(100, 150, 255, 0.5)', width=1),
        text=race_lap_data['lap'].values,
        hovertemplate='<b>Lap %{text}</b><br>Time: %{marker.color:.0f}ms<extra></extra>'
    ))
    
    fig.update_layout(
        title="Track Progression - Lap Time Heatmap",
        xaxis_title="X Position (arbitrary units)",
        yaxis_title="Y Position (arbitrary units)",
        template="plotly_dark",
        hovermode='closest',
        height=600,
        font=dict(family="Arial, sans-serif", size=11, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=50, r=150, t=80, b=50)
    )
    
    return fig


def create_lap_time_analysis(lap_times_data: pd.DataFrame,
                            race_id: int,
                            driver_id: int) -> go.Figure:
    """
    Create line chart of lap times through a race.
    
    Args:
        lap_times_data: Lap times DataFrame
        race_id: Race to analyze
        driver_id: Driver to analyze
        
    Returns:
        Plotly Figure
    """
    race_lap_data = lap_times_data[
        (lap_times_data['raceId'] == race_id) & 
        (lap_times_data['driverId'] == driver_id)
    ].copy()
    
    if race_lap_data.empty:
        fig = go.Figure()
        fig.add_annotation(text="No lap data available")
        return fig
    
    race_lap_data = race_lap_data.sort_values('lap')
    
    # Convert milliseconds to seconds for readability
    race_lap_data['time_seconds'] = race_lap_data['milliseconds'] / 1000
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=race_lap_data['lap'],
        y=race_lap_data['time_seconds'],
        mode='lines+markers',
        name='Lap Time',
        line=dict(color='rgba(76, 110, 245, 0.8)', width=2),
        marker=dict(size=5, color='rgba(76, 110, 245, 1)'),
        fill='tozeroy',
        fillcolor='rgba(76, 110, 245, 0.1)',
        hovertemplate='<b>Lap %{x}</b><br>Time: %{y:.2f}s<extra></extra>'
    ))
    
    # Add reference line for fastest lap
    fastest_lap = race_lap_data['time_seconds'].min()
    fig.add_hline(
        y=fastest_lap,
        line_dash="dash",
        line_color="rgba(76, 230, 100, 0.8)",
        annotation_text=f"Fastest: {fastest_lap:.2f}s",
        annotation_position="right"
    )
    
    fig.update_layout(
        title="Lap Time Progression Throughout Race",
        xaxis_title="Lap Number",
        yaxis_title="Lap Time (seconds)",
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


def create_speed_distribution(lap_times_data: pd.DataFrame,
                             race_id: int,
                             driver_id: int) -> go.Figure:
    """
    Create histogram of lap time distribution (as proxy for speed consistency).
    
    Args:
        lap_times_data: Lap times DataFrame
        race_id: Race to analyze
        driver_id: Driver to analyze
        
    Returns:
        Plotly Figure
    """
    race_lap_data = lap_times_data[
        (lap_times_data['raceId'] == race_id) & 
        (lap_times_data['driverId'] == driver_id)
    ].copy()
    
    if race_lap_data.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available")
        return fig
    
    race_lap_data['time_seconds'] = race_lap_data['milliseconds'] / 1000
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=race_lap_data['time_seconds'],
        nbinsx=25,
        name='Lap Times',
        marker=dict(
            color='rgba(76, 110, 245, 0.7)',
            line=dict(color='rgba(76, 110, 245, 1)', width=1)
        ),
        hovertemplate='<b>Time Range</b><br>%{x:.2f}s<br>Count: %{y}<extra></extra>'
    ))
    
    mean_time = race_lap_data['time_seconds'].mean()
    fig.add_vline(
        x=mean_time,
        line_dash="dash",
        line_color="rgba(255, 100, 50, 0.8)",
        annotation_text=f"Mean: {mean_time:.2f}s",
        annotation_position="top right"
    )
    
    fig.update_layout(
        title="Lap Time Distribution (Speed Consistency)",
        xaxis_title="Lap Time (seconds)",
        yaxis_title="Frequency",
        template="plotly_dark",
        hovermode='x unified',
        height=500,
        showlegend=False,
        font=dict(family="Arial, sans-serif", size=12, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def create_position_changes_chart(lap_times_data: pd.DataFrame,
                                 race_id: int) -> go.Figure:
    """
    Create visualization showing position changes throughout a race.
    Requires position data from lap_times.
    
    Args:
        lap_times_data: Lap times DataFrame
        race_id: Race to analyze
        
    Returns:
        Plotly Figure
    """
    race_data = lap_times_data[lap_times_data['raceId'] == race_id].copy()
    
    if race_data.empty:
        fig = go.Figure()
        fig.add_annotation(text="No position data available")
        return fig
    
    # Get unique drivers and their position progression
    drivers = race_data['driverId'].unique()
    
    fig = go.Figure()
    
    # Limit to top 10 drivers for clarity
    drivers = drivers[:10] if len(drivers) > 10 else drivers
    
    for driver in drivers:
        driver_data = race_data[race_data['driverId'] == driver].sort_values('lap')
        
        if len(driver_data) > 0:
            fig.add_trace(go.Scatter(
                x=driver_data['lap'],
                y=driver_data['position'],
                mode='lines+markers',
                name=f"Driver {driver}",
                hovertemplate='<b>Driver %{fullData.name}</b><br>Lap: %{x}<br>Position: %{y}<extra></extra>'
            ))
    
    fig.update_layout(
        title="Position Changes Throughout Race",
        xaxis_title="Lap Number",
        yaxis_title="Position",
        template="plotly_dark",
        hovermode='x unified',
        height=600,
        font=dict(family="Arial, sans-serif", size=11, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=50, r=50, t=80, b=50),
        yaxis=dict(autorange="reversed")  # 1st place at top
    )
    
    return fig


def create_comparative_lap_times(lap_times_data: pd.DataFrame,
                                race_id: int,
                                driver_ids: list = None) -> go.Figure:
    """
    Compare lap times of multiple drivers in the same race.
    
    Args:
        lap_times_data: Lap times DataFrame
        race_id: Race to compare
        driver_ids: List of driver IDs to compare (default: top 5)
        
    Returns:
        Plotly Figure
    """
    race_data = lap_times_data[lap_times_data['raceId'] == race_id].copy()
    
    if race_data.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available")
        return fig
    
    # Get top drivers if not specified
    if driver_ids is None:
        driver_ids = race_data['driverId'].value_counts().head(5).index.tolist()
    
    race_data['time_seconds'] = race_data['milliseconds'] / 1000
    
    fig = go.Figure()
    
    for driver_id in driver_ids:
        driver_data = race_data[race_data['driverId'] == driver_id].sort_values('lap')
        
        if not driver_data.empty:
            fig.add_trace(go.Scatter(
                x=driver_data['lap'],
                y=driver_data['time_seconds'],
                mode='lines',
                name=f"Driver {driver_id}",
                hovertemplate='<b>Driver %{fullData.name}</b><br>Lap %{x}: %{y:.2f}s<extra></extra>'
            ))
    
    fig.update_layout(
        title="Comparative Lap Times - Top Drivers",
        xaxis_title="Lap Number",
        yaxis_title="Lap Time (seconds)",
        template="plotly_dark",
        hovermode='x unified',
        height=550,
        font=dict(family="Arial, sans-serif", size=11, color='rgba(255, 255, 255, 0.8)'),
        plot_bgcolor='rgba(10, 10, 20, 1)',
        paper_bgcolor='rgba(10, 10, 20, 1)',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def get_lap_statistics(lap_times_data: pd.DataFrame,
                      race_id: int,
                      driver_id: int) -> Dict:
    """
    Calculate statistics for a driver's lap times in a race.
    
    Args:
        lap_times_data: Lap times DataFrame
        race_id: Race ID
        driver_id: Driver ID
        
    Returns:
        Dictionary with statistics
    """
    race_lap_data = lap_times_data[
        (lap_times_data['raceId'] == race_id) & 
        (lap_times_data['driverId'] == driver_id)
    ]['milliseconds']
    
    if race_lap_data.empty:
        return {}
    
    return {
        'total_laps': len(race_lap_data),
        'fastest_lap_ms': race_lap_data.min(),
        'fastest_lap_s': race_lap_data.min() / 1000,
        'slowest_lap_ms': race_lap_data.max(),
        'slowest_lap_s': race_lap_data.max() / 1000,
        'average_lap_ms': race_lap_data.mean(),
        'average_lap_s': race_lap_data.mean() / 1000,
        'std_dev_ms': race_lap_data.std(),
        'consistency_coefficient': (race_lap_data.std() / race_lap_data.mean()) * 100
    }


if __name__ == "__main__":
    pass