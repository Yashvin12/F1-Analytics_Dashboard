"""
F1 Intelligence Dashboard - Advanced Statistical Analysis Module

Provides deeper statistical analysis, ML-ready features, and advanced insights.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
import streamlit as st


@st.cache_data
def perform_correlation_analysis(pitstop_data: pd.DataFrame,
                                 results_data: pd.DataFrame) -> Dict:
    """
    Perform correlation analysis between pit stop efficiency and race outcomes.
    
    Args:
        pitstop_data: Pit stop DataFrame
        results_data: Race results DataFrame
        
    Returns:
        Dictionary with correlation results
    """
    # Aggregate pit stops per race and driver
    pit_summary = pitstop_data.groupby(['raceId', 'driverId']).agg({
        'milliseconds': ['mean', 'count', 'std']
    }).reset_index()
    pit_summary.columns = ['raceId', 'driverId', 'avg_pitstop_ms', 'num_stops', 'pitstop_std']
    
    # Merge with race results
    merged = results_data.merge(pit_summary, on=['raceId', 'driverId'], how='inner')
    merged = merged.dropna(subset=['position', 'avg_pitstop_ms', 'points'])
    
    if len(merged) < 10:
        return {'error': 'Insufficient data for correlation analysis'}
    
    # Convert position to numeric
    merged['position'] = pd.to_numeric(merged['position'], errors='coerce')
    merged = merged.dropna(subset=['position'])
    
    # Correlation calculations
    correlation_pit_position = merged['avg_pitstop_ms'].corr(merged['position'])
    correlation_pit_points = merged['avg_pitstop_ms'].corr(merged['points'])
    
    # Linear regression: pit stops vs position
    x = merged['avg_pitstop_ms'].values.reshape(-1, 1)
    y = merged['position'].values
    
    if len(x) > 2 and np.std(x) > 0:
        slope, intercept, r_value, p_value, std_err = stats.linregress(x.flatten(), y)
    else:
        slope, intercept, r_value, p_value, std_err = 0, 0, 0, 1, 0
    
    return {
        'pit_position_correlation': correlation_pit_position,
        'pit_points_correlation': correlation_pit_points,
        'regression_slope': slope,
        'regression_r_squared': r_value ** 2,
        'regression_p_value': p_value,
        'sample_size': len(merged),
        'interpretation': _interpret_correlation(correlation_pit_position)
    }


def _interpret_correlation(corr_value: float) -> str:
    """Interpret correlation value."""
    if corr_value is None or np.isnan(corr_value):
        return "Insufficient data"
    
    abs_corr = abs(corr_value)
    if abs_corr < 0.1:
        return "Negligible"
    elif abs_corr < 0.3:
        return "Weak"
    elif abs_corr < 0.5:
        return "Moderate"
    elif abs_corr < 0.7:
        return "Strong"
    else:
        return "Very Strong"


@st.cache_data
def calculate_team_efficiency_score(pitstop_data: pd.DataFrame,
                                    results_data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate comprehensive efficiency score for each team/constructor.
    Combines pit stop speed, consistency, and correlation with results.
    
    Args:
        pitstop_data: Pit stop DataFrame
        results_data: Race results DataFrame
        
    Returns:
        DataFrame with team efficiency scores
    """
    # Get constructor from results
    constructor_map = results_data[['driverId', 'constructorId', 'name']].drop_duplicates()
    
    # Merge pit stops with constructor
    merged = pitstop_data.merge(constructor_map, on='driverId', how='left')
    
    scores = []
    
    for constructor_id, group in merged.groupby('constructorId'):
        if constructor_id != constructor_id:  # Check for NaN
            continue
        
        # Speed score (inverse of average time, normalized 0-100)
        avg_time = group['milliseconds'].mean()
        global_avg = merged['milliseconds'].mean()
        speed_score = max(0, min(100, (global_avg / avg_time) * 100))
        
        # Consistency score
        cv = (group['milliseconds'].std() / avg_time) * 100 if avg_time > 0 else 0
        consistency_score = max(0, 100 - cv)
        
        # Reliability score (inverse outlier percentage)
        outliers = ((group['milliseconds'] > avg_time + 3*group['milliseconds'].std()) |
                   (group['milliseconds'] < avg_time - 3*group['milliseconds'].std())).sum()
        outlier_pct = (outliers / len(group)) * 100 if len(group) > 0 else 0
        reliability_score = max(0, 100 - outlier_pct)
        
        # Combined efficiency score (weighted average)
        efficiency_score = (
            speed_score * 0.4 +
            consistency_score * 0.35 +
            reliability_score * 0.25
        )
        
        constructor_name = group['name'].iloc[0] if 'name' in group.columns else f"ID {constructor_id}"
        
        scores.append({
            'constructor': constructor_name,
            'efficiency_score': round(efficiency_score, 2),
            'speed_score': round(speed_score, 2),
            'consistency_score': round(consistency_score, 2),
            'reliability_score': round(reliability_score, 2),
            'avg_pitstop_ms': round(avg_time, 2),
            'total_stops': len(group)
        })
    
    return pd.DataFrame(scores).sort_values('efficiency_score', ascending=False)


@st.cache_data
def predict_optimal_pitstop_window(pitstop_data: pd.DataFrame,
                                   driver: str = None) -> Dict:
    """
    Analyze optimal lap for pit stop based on historical data.
    Uses lap distribution analysis.
    
    Args:
        pitstop_data: Pit stop DataFrame
        driver: Optional specific driver
        
    Returns:
        Dictionary with lap distribution insights
    """
    data = pitstop_data.copy()
    
    if driver:
        data = data[data['driver_name'] == driver]
    
    if data.empty:
        return {'error': 'No data available'}
    
    # Analyze lap distribution
    lap_dist = data['lap'].value_counts().sort_index()
    
    # Find peak pit stop laps
    peak_lap = lap_dist.idxmax()
    peak_frequency = lap_dist.max()
    
    # Calculate lap statistics
    lap_stats = {
        'mean_lap': data['lap'].mean(),
        'median_lap': data['lap'].median(),
        'std_dev_lap': data['lap'].std(),
        'peak_lap': int(peak_lap),
        'peak_frequency': int(peak_frequency),
        'common_lap_ranges': _identify_pit_windows(data['lap'].values)
    }
    
    return lap_stats


def _identify_pit_windows(lap_values: np.ndarray) -> List[str]:
    """Identify common pit stop timing windows."""
    windows = []
    
    early_stops = (lap_values <= 20).sum()
    mid_stops = ((lap_values > 20) & (lap_values <= 40)).sum()
    late_stops = (lap_values > 40).sum()
    
    if early_stops > 0:
        windows.append(f"Early (Lap 1-20): {early_stops} stops")
    if mid_stops > 0:
        windows.append(f"Mid (Lap 21-40): {mid_stops} stops")
    if late_stops > 0:
        windows.append(f"Late (Lap 40+): {late_stops} stops")
    
    return windows


@st.cache_data
def analyze_wet_weather_impact(pitstop_data: pd.DataFrame) -> Dict:
    """
    Analyze potential weather impact on pit stop times.
    Uses statistical clustering of pit stop durations.
    
    Args:
        pitstop_data: Pit stop DataFrame
        
    Returns:
        Dictionary with weather impact analysis
    """
    data = pitstop_data.dropna(subset=['milliseconds'])
    
    # Use bimodal distribution to detect potential weather changes
    times = data['milliseconds'].values
    
    # K-means clustering (2 clusters: normal vs bad conditions)
    from scipy.cluster.hierarchy import fclusterdata
    
    try:
        clusters = fclusterdata(times.reshape(-1, 1), t=2, criterion='distance', method='complete')
        
        cluster_stats = []
        for cluster_id in np.unique(clusters):
            cluster_data = times[clusters == cluster_id]
            cluster_stats.append({
                'cluster': cluster_id,
                'size': len(cluster_data),
                'mean': cluster_data.mean(),
                'std': cluster_data.std(),
                'percentage': (len(cluster_data) / len(times)) * 100
            })
        
        return {
            'clusters': sorted(cluster_stats, key=lambda x: x['mean']),
            'bimodal_detected': len(cluster_stats) > 1,
            'potential_weather_impact': 'Yes' if len(cluster_stats) > 1 else 'Minimal'
        }
    
    except:
        return {'error': 'Insufficient data for clustering'}


@st.cache_data
def calculate_driver_performance_index(pitstop_data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate comprehensive performance index combining multiple metrics.
    
    Args:
        pitstop_data: Pit stop DataFrame
        
    Returns:
        DataFrame with performance indices
    """
    drivers = pitstop_data['driver_name'].unique()
    
    indices = []
    
    for driver in drivers:
        driver_data = pitstop_data[pitstop_data['driver_name'] == driver]
        
        # Speed component (lower is better, so invert)
        avg_time = driver_data['milliseconds'].mean()
        global_avg = pitstop_data['milliseconds'].mean()
        speed_component = (global_avg / avg_time) * 100 if avg_time > 0 else 0
        
        # Consistency component (coefficient of variation)
        cv = (driver_data['milliseconds'].std() / avg_time) * 100 if avg_time > 0 else 0
        consistency_component = max(0, 100 - cv)
        
        # Experience component (normalized number of stops)
        num_stops = len(driver_data)
        max_stops = pitstop_data.groupby('driver_name').size().max()
        experience_component = (num_stops / max_stops) * 100
        
        # Improvement component (trend analysis)
        yearly_data = driver_data.groupby('year')['milliseconds'].mean()
        if len(yearly_data) > 1:
            improvement = (yearly_data.iloc[0] - yearly_data.iloc[-1]) / yearly_data.iloc[0] * 100
            improvement_component = max(0, min(50, improvement))  # Cap at 50
        else:
            improvement_component = 0
        
        # Weighted index
        performance_index = (
            speed_component * 0.3 +
            consistency_component * 0.3 +
            experience_component * 0.2 +
            improvement_component * 0.2
        )
        
        indices.append({
            'driver': driver,
            'performance_index': round(performance_index, 2),
            'speed_score': round(speed_component, 2),
            'consistency_score': round(consistency_component, 2),
            'experience_score': round(experience_component, 2),
            'improvement_score': round(improvement_component, 2),
            'total_stops': num_stops
        })
    
    return pd.DataFrame(indices).sort_values('performance_index', ascending=False)


@st.cache_data
def detect_performance_anomalies(pitstop_data: pd.DataFrame,
                                 sensitivity: float = 2.5) -> pd.DataFrame:
    """
    Detect anomalous pit stop times using statistical methods.
    
    Args:
        pitstop_data: Pit stop DataFrame
        sensitivity: Z-score threshold (default 2.5)
        
    Returns:
        DataFrame with detected anomalies
    """
    data = pitstop_data.dropna(subset=['milliseconds']).copy()
    
    # Calculate z-scores
    data['z_score'] = np.abs(stats.zscore(data['milliseconds']))
    
    # Detect anomalies
    anomalies = data[data['z_score'] > sensitivity].copy()
    anomalies = anomalies.sort_values('z_score', ascending=False)
    
    return anomalies[[
        'driver_name', 'driver_code', 'year', 'milliseconds', 'z_score', 'race_id'
    ]].head(50)


@st.cache_data
def forecast_pit_performance_trend(pitstop_data: pd.DataFrame,
                                  driver: str,
                                  periods: int = 5) -> pd.DataFrame:
    """
    Simple trend forecasting for driver pit stop performance.
    Uses moving average extrapolation.
    
    Args:
        pitstop_data: Pit stop DataFrame
        driver: Driver name
        periods: Number of periods to forecast
        
    Returns:
        DataFrame with historical and forecasted data
    """
    driver_data = pitstop_data[pitstop_data['driver_name'] == driver].copy()
    
    if driver_data.empty:
        return pd.DataFrame()
    
    # Aggregate by year
    yearly = driver_data.groupby('year')['milliseconds'].mean().reset_index()
    yearly = yearly.sort_values('year')
    
    if len(yearly) < 2:
        return yearly
    
    # Linear trend (simple extrapolation)
    years = yearly['year'].values
    times = yearly['milliseconds'].values
    
    z = np.polyfit(years, times, 1)
    p = np.poly1d(z)
    
    # Forecast
    last_year = years[-1]
    forecast_years = np.arange(last_year + 1, last_year + periods + 1)
    forecast_times = p(forecast_years)
    
    forecast_df = pd.DataFrame({
        'year': forecast_years,
        'milliseconds': forecast_times,
        'type': 'forecast'
    })
    
    yearly['type'] = 'historical'
    
    combined = pd.concat([yearly, forecast_df], ignore_index=True)
    
    return combined


@st.cache_data
def calculate_pit_strategy_efficiency(pitstop_data: pd.DataFrame,
                                     results_data: pd.DataFrame) -> Dict:
    """
    Analyze pit strategy effectiveness (1-stop vs 2-stop vs 3-stop races).
    
    Args:
        pitstop_data: Pit stop DataFrame
        results_data: Race results DataFrame
        
    Returns:
        Dictionary with strategy analysis
    """
    # Count stops per driver per race
    stops_per_race = pitstop_data.groupby(['raceId', 'driverId']).size().reset_index(name='stops')
    
    # Merge with results
    merged = results_data.merge(stops_per_race, on=['raceId', 'driverId'], how='left')
    merged['stops'] = merged['stops'].fillna(0).astype(int)
    merged = merged.dropna(subset=['position', 'points'])
    
    strategy_analysis = {}
    
    for num_stops in sorted(merged['stops'].unique()):
        if num_stops < 0:
            continue
        
        strategy_data = merged[merged['stops'] == num_stops]
        
        strategy_analysis[f'{int(num_stops)}-stop'] = {
            'races': len(strategy_data),
            'avg_position': round(strategy_data['position'].mean(), 2),
            'avg_points': round(strategy_data['points'].mean(), 2),
            'win_percentage': round((strategy_data['position'] == 1).sum() / len(strategy_data) * 100, 2),
            'podium_percentage': round((strategy_data['position'] <= 3).sum() / len(strategy_data) * 100, 2)
        }
    
    return strategy_analysis


if __name__ == "__main__":
    pass