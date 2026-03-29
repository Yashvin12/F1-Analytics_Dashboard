"""
F1 Intelligence Dashboard - Pit Stop Analysis Module

Provides statistical analysis and insights on pit stop performance.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import streamlit as st


@st.cache_data
def get_top_pit_crews(pitstop_data: pd.DataFrame, 
                      year_filter: int = None,
                      limit: int = 10) -> pd.DataFrame:
    """
    Identify fastest pit crews (by average pit stop duration).
    
    Args:
        pitstop_data: Prepared pit stop DataFrame
        year_filter: Optional year to filter by
        limit: Number of top crews to return
        
    Returns:
        DataFrame of top pit crews
    """
    data = pitstop_data.copy()
    
    if year_filter:
        data = data[data['year'] == year_filter]
    
    crews = data.groupby('driver_code').agg({
        'milliseconds': ['mean', 'count', 'min'],
        'driver_name': 'first',
        'year': 'max'
    }).round(2)
    
    crews.columns = ['avg_stop_ms', 'total_stops', 'fastest_stop_ms', 
                     'driver', 'last_year']
    crews = crews.reset_index(drop=True)
    crews = crews.sort_values('avg_stop_ms').head(limit)
    
    return crews


@st.cache_data
def get_pitstop_distribution(pitstop_data: pd.DataFrame,
                              year_filter: int = None) -> pd.DataFrame:
    """
    Get pit stop duration distribution for visualization.
    
    Args:
        pitstop_data: Prepared pit stop DataFrame
        year_filter: Optional year to filter by
        
    Returns:
        DataFrame with distribution data
    """
    data = pitstop_data.copy()
    
    if year_filter:
        data = data[data['year'] == year_filter]
    
    data = data.dropna(subset=['milliseconds', 'driver_code'])
    
    return data[['milliseconds', 'driver_code', 'driver_name', 'year']]


@st.cache_data
def get_pitstop_by_lap(pitstop_data: pd.DataFrame,
                       driver: str = None,
                       year: int = None) -> pd.DataFrame:
    """
    Get pit stop data aggregated by lap number.
    Useful for understanding lap timing patterns.
    
    Args:
        pitstop_data: Prepared pit stop DataFrame
        driver: Optional driver filter
        year: Optional year filter
        
    Returns:
        DataFrame grouped by lap
    """
    data = pitstop_data.copy()
    
    if driver:
        data = data[data['driver_name'] == driver]
    if year:
        data = data[data['year'] == year]
    
    lap_stats = data.groupby('lap').agg({
        'milliseconds': ['mean', 'min', 'max', 'count']
    }).round(2)
    
    lap_stats.columns = ['avg_duration', 'fastest', 'slowest', 'count']
    lap_stats = lap_stats.reset_index()
    
    return lap_stats


@st.cache_data
def get_pitstop_per_stop_number(pitstop_data: pd.DataFrame,
                                 year_filter: int = None) -> pd.DataFrame:
    """
    Analyze pit stop duration by stop number (1st, 2nd, 3rd stop, etc).
    
    Args:
        pitstop_data: Prepared pit stop DataFrame
        year_filter: Optional year to filter by
        
    Returns:
        DataFrame with statistics by stop number
    """
    data = pitstop_data.copy()
    
    if year_filter:
        data = data[data['year'] == year_filter]
    
    stop_stats = data.groupby('stop').agg({
        'milliseconds': ['mean', 'median', 'std', 'count']
    }).round(2)
    
    stop_stats.columns = ['avg_time_ms', 'median_time_ms', 'std_dev_ms', 'total_stops']
    stop_stats = stop_stats.reset_index()
    stop_stats['stop'] = stop_stats['stop'].astype(int)
    
    return stop_stats


@st.cache_data
def get_era_comparison(pitstop_data: pd.DataFrame) -> pd.DataFrame:
    """
    Compare pit stop times across different F1 eras.
    
    Args:
        pitstop_data: Prepared pit stop DataFrame
        
    Returns:
        DataFrame with era statistics
    """
    era_stats = pitstop_data.dropna(subset=['era']).groupby('era').agg({
        'milliseconds': ['mean', 'median', 'std', 'min', 'max', 'count']
    }).round(2)
    
    era_stats.columns = ['mean_time', 'median_time', 'std_dev', 'fastest', 'slowest', 'count']
    era_stats = era_stats.reset_index()
    
    return era_stats


@st.cache_data
def get_constructor_pitstop_analysis(pitstop_data: pd.DataFrame,
                                      results_data: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze pit stop efficiency by constructor team.
    
    Args:
        pitstop_data: Prepared pit stop DataFrame
        results_data: Race results DataFrame
        
    Returns:
        DataFrame with constructor pit stop analysis
    """
    # Get constructor info from results
    constructor_info = results_data[['driverId', 'name']].rename(
        columns={'name': 'constructor'}
    ).drop_duplicates()
    
    # Merge pit stops with constructor
    analysis = pitstop_data.merge(constructor_info, on='driverId', how='left')
    
    # Calculate statistics
    constructor_stats = analysis.dropna(subset=['constructor']).groupby('constructor').agg({
        'milliseconds': ['mean', 'count', 'min'],
        'driver_name': 'nunique'
    }).round(2)
    
    constructor_stats.columns = ['avg_stop_ms', 'total_stops', 'fastest_stop_ms', 'num_drivers']
    constructor_stats = constructor_stats.reset_index()
    constructor_stats = constructor_stats.sort_values('avg_stop_ms')
    
    return constructor_stats


def calculate_pitstop_consistency(pitstop_data: pd.DataFrame,
                                   driver: str) -> Dict:
    """
    Calculate consistency metrics for a specific driver's pit stops.
    Lower coefficient of variation = more consistent.
    
    Args:
        pitstop_data: Prepared pit stop DataFrame
        driver: Driver name
        
    Returns:
        Dictionary with consistency metrics
    """
    driver_stops = pitstop_data[pitstop_data['driver_name'] == driver]['milliseconds']
    
    if len(driver_stops) < 2:
        return {
            'mean': driver_stops.mean(),
            'std': 0,
            'cv': 0,  # Coefficient of variation
            'consistency_score': 100,
            'sample_size': len(driver_stops)
        }
    
    mean_val = driver_stops.mean()
    std_val = driver_stops.std()
    cv = (std_val / mean_val) * 100 if mean_val > 0 else 0
    consistency_score = max(0, 100 - cv)  # Higher = more consistent
    
    return {
        'mean': round(mean_val, 2),
        'std': round(std_val, 2),
        'cv': round(cv, 2),
        'consistency_score': round(consistency_score, 2),
        'sample_size': len(driver_stops)
    }


def get_pitstop_improvements(pitstop_data: pd.DataFrame,
                              driver: str,
                              year_window: int = 3) -> pd.DataFrame:
    """
    Track pit stop time improvements over recent seasons for a driver.
    
    Args:
        pitstop_data: Prepared pit stop DataFrame
        driver: Driver name
        year_window: Number of years to compare
        
    Returns:
        DataFrame with year-over-year improvements
    """
    driver_data = pitstop_data[pitstop_data['driver_name'] == driver].copy()
    
    yearly_avg = driver_data.groupby('year').agg({
        'milliseconds': ['mean', 'count']
    }).round(2)
    
    yearly_avg.columns = ['avg_stop_ms', 'num_stops']
    yearly_avg = yearly_avg.reset_index()
    yearly_avg = yearly_avg.sort_values('year')
    
    # Calculate year-over-year change
    yearly_avg['improvement_ms'] = yearly_avg['avg_stop_ms'].diff()
    yearly_avg['improvement_pct'] = (yearly_avg['improvement_ms'] / 
                                       yearly_avg['avg_stop_ms'].shift()) * 100
    
    return yearly_avg


def get_pitstop_risk_analysis(pitstop_data: pd.DataFrame,
                               year_filter: int = None) -> pd.DataFrame:
    """
    Analyze pit stop risk (outliers and consistency issues).
    Uses 3-sigma rule to identify problematic pit stops.
    
    Args:
        pitstop_data: Prepared pit stop DataFrame
        year_filter: Optional year to filter by
        
    Returns:
        DataFrame with risk metrics per driver
    """
    data = pitstop_data.copy()
    
    if year_filter:
        data = data[data['year'] == year_filter]
    
    risk_metrics = []
    
    for driver in data['driver_name'].unique():
        driver_stops = data[data['driver_name'] == driver]['milliseconds'].dropna()
        
        if len(driver_stops) < 2:
            continue
        
        mean = driver_stops.mean()
        std = driver_stops.std()
        
        # Count outliers (3-sigma rule)
        outliers = ((driver_stops > mean + 3 * std) | 
                    (driver_stops < mean - 3 * std)).sum()
        
        # Percentage of stops that are outliers
        outlier_pct = (outliers / len(driver_stops)) * 100
        
        risk_metrics.append({
            'driver': driver,
            'total_stops': len(driver_stops),
            'outlier_count': outliers,
            'outlier_percentage': round(outlier_pct, 2),
            'risk_score': round(outlier_pct, 2),  # Lower = better
            'consistency': 'High' if outlier_pct < 5 else ('Medium' if outlier_pct < 15 else 'Low')
        })
    
    return pd.DataFrame(risk_metrics).sort_values('risk_score')


if __name__ == "__main__":
    from src.data_loader import load_all_datasets, prepare_pitstop_data
    
    # Test analysis functions
    datasets = load_all_datasets()
    pitstop_data = prepare_pitstop_data(datasets)
    
    print("Top pit crews:")
    print(get_top_pit_crews(pitstop_data))
    print("\nEra comparison:")
    print(get_era_comparison(pitstop_data))