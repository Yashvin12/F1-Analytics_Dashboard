"""
F1 Intelligence Dashboard - Data Loader Module

Handles loading, caching, and preprocessing of F1 datasets.
Implements Streamlit caching for optimal performance.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
import streamlit as st
from datetime import datetime


@st.cache_data
def load_all_datasets(data_dir: str = "data") -> Dict[str, pd.DataFrame]:
    """
    Load all F1 datasets with caching.
    
    Args:
        data_dir: Path to the directory containing CSV files
        
    Returns:
        Dictionary of DataFrames with dataset names as keys
    """
    datasets = {}
    
    # Core datasets required for analysis
    required_files = [
        'drivers',
        'races',
        'results',
        'pit_stops',
        'constructors',
        'circuits'
    ]
    
    for filename in required_files:
        filepath = Path(data_dir) / f"{filename}.csv"
        if filepath.exists():
            datasets[filename] = pd.read_csv(filepath)
        else:
            st.warning(f"Warning: {filename}.csv not found")
    
    return datasets


@st.cache_data
def prepare_pitstop_data(datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Prepare and merge pit stop data with driver and race information.
    
    Args:
        datasets: Dictionary of loaded datasets
        
    Returns:
        Merged DataFrame with pit stop analysis data
    """
    pit_stops = datasets['pit_stops'].copy()
    drivers = datasets['drivers'][['driverId', 'code', 'forename', 'surname']].copy()
    races = datasets['races'][['raceId', 'year', 'date', 'name']].copy()
    
    # Merge data
    pit_stops = pit_stops.merge(drivers, on='driverId', how='left')
    pit_stops = pit_stops.merge(races, on='raceId', how='left')
    
    # Data cleaning and feature engineering
    pit_stops['duration'] = pd.to_numeric(pit_stops['duration'], errors='coerce')
    pit_stops['milliseconds'] = pd.to_numeric(pit_stops['milliseconds'], errors='coerce')
    pit_stops['date'] = pd.to_datetime(pit_stops['date'], errors='coerce')
    
    # Create driver identifier
    pit_stops['driver_name'] = pit_stops['forename'] + ' ' + pit_stops['surname']
    pit_stops['driver_code'] = pit_stops['code'].fillna('UNK')
    
    # Add era classification
    pit_stops['era'] = pd.cut(pit_stops['year'], 
                               bins=[0, 2010, 2014, 2020, 2030],
                               labels=['2009-2010', '2011-2014', '2015-2020', '2021+'])
    
    return pit_stops


@st.cache_data
def prepare_race_results_data(datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Prepare race results with driver and constructor information.
    
    Args:
        datasets: Dictionary of loaded datasets
        
    Returns:
        Merged DataFrame with race results
    """
    results = datasets['results'].copy()
    drivers = datasets['drivers'][['driverId', 'code', 'forename', 'surname', 'nationality']].copy()
    constructors = datasets['constructors'][['constructorId', 'name']].copy()
    races = datasets['races'][['raceId', 'year', 'date', 'name', 'circuitId']].copy()
    circuits = datasets['circuits'][['circuitId', 'location', 'country']].copy()
    
    # Merge all data
    results = results.merge(drivers, on='driverId', how='left')
    results = results.merge(constructors, on='constructorId', how='left')
    results = results.merge(races, on='raceId', how='left')
    results = results.merge(circuits, on='circuitId', how='left')
    
    # Data cleaning
    results['position'] = pd.to_numeric(results['position'], errors='coerce')
    results['grid'] = pd.to_numeric(results['grid'], errors='coerce')
    results['points'] = pd.to_numeric(results['points'], errors='coerce')
    results['date'] = pd.to_datetime(results['date'], errors='coerce')
    
    # Create driver identifier
    results['driver_name'] = results['forename'] + ' ' + results['surname']
    results['driver_code'] = results['code'].fillna('UNK')
    
    return results


@st.cache_data
def get_unique_drivers(pitstop_data: pd.DataFrame) -> list:
    """Get sorted list of unique drivers from pit stop data."""
    return sorted(pitstop_data['driver_name'].dropna().unique().tolist())


@st.cache_data
def get_years_range(pitstop_data: pd.DataFrame) -> Tuple[int, int]:
    """Get min and max years from pit stop data."""
    years = pitstop_data['year'].dropna().astype(int)
    return int(years.min()), int(years.max())


@st.cache_data
def get_races_by_year(datasets: Dict[str, pd.DataFrame], year: int) -> list:
    """Get list of races for a given year."""
    races = datasets['races']
    year_races = races[races['year'] == year]['name'].unique().tolist()
    return sorted(year_races)


def filter_data_by_driver_year(pitstop_data: pd.DataFrame, 
                                driver: str = None, 
                                year: int = None) -> pd.DataFrame:
    """
    Filter pit stop data by driver and/or year.
    
    Args:
        pitstop_data: Prepared pit stop DataFrame
        driver: Driver name (optional)
        year: Year (optional)
        
    Returns:
        Filtered DataFrame
    """
    filtered = pitstop_data.copy()
    
    if driver and driver != "All Drivers":
        filtered = filtered[filtered['driver_name'] == driver]
    
    if year and year != 0:
        filtered = filtered[filtered['year'] == year]
    
    return filtered


def get_driver_pitstop_stats(pitstop_data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate pit stop statistics per driver across all time.
    
    Args:
        pitstop_data: Prepared pit stop DataFrame
        
    Returns:
        DataFrame with driver statistics
    """
    stats = pitstop_data.groupby('driver_name').agg({
        'milliseconds': ['mean', 'min', 'max', 'std', 'count'],
        'duration': 'mean',
        'year': 'max'
    }).round(3)
    
    stats.columns = ['avg_time_ms', 'fastest_stop_ms', 'slowest_stop_ms', 
                     'std_dev_ms', 'total_stops', 'last_year']
    stats = stats.reset_index()
    stats = stats.sort_values('avg_time_ms').reset_index(drop=True)
    
    return stats


def get_pitstop_time_trend(pitstop_data: pd.DataFrame, 
                           window: int = 50) -> pd.DataFrame:
    """
    Calculate rolling average of pit stop times across F1 history.
    
    Args:
        pitstop_data: Prepared pit stop DataFrame
        window: Rolling window size
        
    Returns:
        DataFrame with trend data
    """
    trend = pitstop_data[['year', 'milliseconds']].dropna().copy()
    trend = trend.sort_values('year')
    trend['rolling_avg'] = trend['milliseconds'].rolling(window=window, min_periods=1).mean()
    
    return trend.groupby('year').agg({
        'milliseconds': 'mean',
        'rolling_avg': 'mean'
    }).reset_index()


def correlate_pitstop_position(results_data: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze correlation between pit stop efficiency and final position.
    Requires pit stop data merged with race results.
    
    Args:
        results_data: Race results DataFrame
        
    Returns:
        DataFrame for correlation analysis
    """
    # Clean data
    analysis = results_data.dropna(subset=['position', 'grid']).copy()
    analysis['position'] = pd.to_numeric(analysis['position'], errors='coerce')
    analysis['grid'] = pd.to_numeric(analysis['grid'], errors='coerce')
    
    # Calculate position change
    analysis['position_change'] = analysis['grid'] - analysis['position']
    
    return analysis


if __name__ == "__main__":
    # Test data loading
    datasets = load_all_datasets()
    print(f"Loaded {len(datasets)} datasets")
    for name, df in datasets.items():
        print(f"  {name}: {len(df)} rows, {len(df.columns)} columns")