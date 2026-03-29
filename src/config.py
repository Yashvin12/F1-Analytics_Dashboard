"""
F1 Intelligence Dashboard - Configuration & Utilities Module

Centralized configuration, constants, and utility functions.
"""

import streamlit as st
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

class Config:
    """Central configuration for the dashboard."""
    
    # Data
    DATA_DIR = "/mnt/project"
    CACHE_TTL = 3600  # seconds
    
    # UI
    PAGE_LAYOUT = "wide"
    THEME = "dark"
    
    # Styling
    PRIMARY_COLOR = "#4C6EF5"
    SECONDARY_COLOR = "#4CE664"
    ACCENT_COLOR = "#FF6432"
    BACKGROUND_COLOR = "#0A0A14"
    TEXT_COLOR = "#FFFFFF"
    
    # Chart Settings
    CHART_HEIGHT = 500
    CHART_HEIGHT_LARGE = 600
    CHART_TEMPLATE = "plotly_dark"
    COLOR_SCALES = {
        'performance': 'Viridis',
        'speed': 'Turbo',
        'risk': 'RdYlGn_r',
        'correlation': 'RdBu'
    }
    
    # Data Processing
    MIN_DATA_POINTS = 10
    ROLLING_WINDOW = 50
    Z_SCORE_THRESHOLD = 2.5
    
    # Era Classification
    ERAS = {
        'Early': (0, 2010),
        'Refueling': (2010, 2014),
        'Hybrid': (2014, 2020),
        'Modern': (2020, 2030)
    }


class ChartType(Enum):
    """Chart type enumeration."""
    HISTOGRAM = "histogram"
    BOX_PLOT = "box"
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    RADAR = "radar"


@dataclass
class MetricInfo:
    """Metadata for a metric."""
    name: str
    unit: str
    description: str
    lower_is_better: bool = False


# ============================================================================
# METRIC DEFINITIONS
# ============================================================================

METRICS = {
    'pit_time': MetricInfo(
        name='Pit Stop Time',
        unit='milliseconds',
        description='Duration of pit stop',
        lower_is_better=True
    ),
    'consistency': MetricInfo(
        name='Consistency Score',
        unit='0-100',
        description='Consistency of pit stops (higher is better)',
        lower_is_better=False
    ),
    'speed_score': MetricInfo(
        name='Speed Score',
        unit='0-100',
        description='Pit stop speed ranking',
        lower_is_better=False
    ),
    'reliability': MetricInfo(
        name='Reliability Score',
        unit='0-100',
        description='Absence of anomalies',
        lower_is_better=False
    )
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_milliseconds(ms: float, decimals: int = 1) -> str:
    """
    Format milliseconds to human-readable format.
    
    Args:
        ms: Milliseconds value
        decimals: Decimal places
        
    Returns:
        Formatted string
    """
    if ms is None or ms != ms:  # Check for NaN
        return "N/A"
    
    seconds = ms / 1000
    return f"{seconds:.{decimals}f}s"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format percentage value.
    
    Args:
        value: Percentage value
        decimals: Decimal places
        
    Returns:
        Formatted string
    """
    if value is None or value != value:  # Check for NaN
        return "N/A"
    
    return f"{value:.{decimals}f}%"


def get_color_by_value(value: float, 
                       min_val: float = 0, 
                       max_val: float = 100,
                       reverse: bool = False) -> str:
    """
    Get color based on value (gradient).
    
    Args:
        value: Value to color
        min_val: Minimum value
        max_val: Maximum value
        reverse: Reverse color gradient
        
    Returns:
        RGB color string
    """
    if value is None or value != value:  # NaN check
        return "rgba(100, 100, 100, 0.8)"
    
    normalized = (value - min_val) / (max_val - min_val)
    normalized = max(0, min(1, normalized))  # Clamp 0-1
    
    if reverse:
        normalized = 1 - normalized
    
    # Green (good) to Red (bad)
    r = int(255 * normalized)
    g = int(255 * (1 - normalized))
    b = 0
    
    return f"rgba({r}, {g}, {b}, 0.8)"


def get_performance_badge(score: float) -> str:
    """
    Get performance badge emoji based on score.
    
    Args:
        score: Score 0-100
        
    Returns:
        Emoji badge
    """
    if score >= 90:
        return "🥇"  # Gold
    elif score >= 75:
        return "🥈"  # Silver
    elif score >= 50:
        return "🥉"  # Bronze
    else:
        return "📊"  # Chart


def get_trend_indicator(current: float, 
                       previous: float) -> Tuple[str, str]:
    """
    Get trend indicator and direction.
    
    Args:
        current: Current value
        previous: Previous value
        
    Returns:
        Tuple of (emoji, direction)
    """
    if current is None or previous is None:
        return "➡️", "neutral"
    
    change = current - previous
    
    if change > 0:
        return "📈", "up"
    elif change < 0:
        return "📉", "down"
    else:
        return "➡️", "neutral"


# ============================================================================
# DATA VALIDATION & CLEANING
# ============================================================================

def validate_data(df, required_columns: List[str]) -> Tuple[bool, str]:
    """
    Validate DataFrame has required columns and data.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        Tuple of (is_valid, message)
    """
    if df is None or df.empty:
        return False, "Dataset is empty"
    
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        return False, f"Missing columns: {', '.join(missing)}"
    
    return True, "Valid"


def clean_numeric_column(series, fill_method: str = 'drop') -> pd.Series:
    """
    Clean numeric column of invalid values.
    
    Args:
        series: Pandas Series
        fill_method: 'drop', 'mean', 'median', 'forward_fill'
        
    Returns:
        Cleaned series
    """
    import pandas as pd
    import numpy as np
    
    # Convert to numeric
    series = pd.to_numeric(series, errors='coerce')
    
    if fill_method == 'drop':
        return series.dropna()
    elif fill_method == 'mean':
        return series.fillna(series.mean())
    elif fill_method == 'median':
        return series.fillna(series.median())
    elif fill_method == 'forward_fill':
        return series.fillna(method='ffill')
    else:
        return series


# ============================================================================
# CACHING & PERFORMANCE
# ============================================================================

def estimate_memory_usage(df) -> str:
    """
    Estimate memory usage of DataFrame.
    
    Args:
        df: DataFrame
        
    Returns:
        Formatted memory string
    """
    bytes_used = df.memory_usage(deep=True).sum()
    
    if bytes_used < 1024:
        return f"{bytes_used:.0f} B"
    elif bytes_used < 1024**2:
        return f"{bytes_used/1024:.1f} KB"
    elif bytes_used < 1024**3:
        return f"{bytes_used/1024**2:.1f} MB"
    else:
        return f"{bytes_used/1024**3:.1f} GB"


def get_cache_status() -> Dict:
    """
    Get current cache status.
    
    Returns:
        Dictionary with cache information
    """
    return {
        'cached_items': len(st.session_state),
        'memory_estimate': "See browser console"
    }


# ============================================================================
# FORMATTING & DISPLAY
# ============================================================================

def create_info_card(title: str, 
                    value: str, 
                    subtitle: str = "",
                    emoji: str = "📊") -> str:
    """
    Create formatted info card HTML.
    
    Args:
        title: Card title
        value: Main value
        subtitle: Subtitle/description
        emoji: Emoji icon
        
    Returns:
        HTML string
    """
    html = f"""
    <div style="
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(76, 110, 245, 0.3);
        text-align: center;
    ">
        <div style="font-size: 24px; margin-bottom: 10px;">{emoji}</div>
        <div style="font-size: 12px; color: rgba(255, 255, 255, 0.6);">{title}</div>
        <div style="font-size: 24px; color: #4C6EF5; font-weight: bold;">{value}</div>
        {f'<div style="font-size: 11px; color: rgba(255, 255, 255, 0.4);">{subtitle}</div>' if subtitle else ''}
    </div>
    """
    return html


def get_season_range_display(min_year: int, max_year: int) -> str:
    """
    Get display string for season range.
    
    Args:
        min_year: Minimum year
        max_year: Maximum year
        
    Returns:
        Display string
    """
    return f"{min_year}-{max_year} Seasons ({max_year - min_year + 1} years)"


# ============================================================================
# ANALYSIS HELPERS
# ============================================================================

def percentile_rank(value: float, series: list) -> float:
    """
    Calculate percentile rank of value in series.
    
    Args:
        value: Value to rank
        series: List/array of values
        
    Returns:
        Percentile (0-100)
    """
    import numpy as np
    return (np.sum(np.array(series) <= value) / len(series)) * 100


def calculate_improvement_ratio(old_value: float, 
                               new_value: float) -> float:
    """
    Calculate improvement ratio (percentage change).
    
    Args:
        old_value: Original value
        new_value: New value
        
    Returns:
        Percentage change
    """
    if old_value == 0 or old_value != old_value:  # NaN check
        return 0
    
    return ((old_value - new_value) / old_value) * 100


def get_statistical_significance(p_value: float) -> str:
    """
    Interpret p-value significance.
    
    Args:
        p_value: P-value from test
        
    Returns:
        Significance interpretation
    """
    if p_value < 0.001:
        return "Highly Significant ***"
    elif p_value < 0.01:
        return "Very Significant **"
    elif p_value < 0.05:
        return "Significant *"
    else:
        return "Not Significant"


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def prepare_export_data(df, format: str = 'csv') -> str:
    """
    Prepare data for export.
    
    Args:
        df: DataFrame to export
        format: Export format ('csv', 'json')
        
    Returns:
        Formatted string
    """
    if format == 'csv':
        return df.to_csv(index=False)
    elif format == 'json':
        return df.to_json(orient='records', indent=2)
    else:
        return df.to_string()


# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    defaults = {
        'selected_driver': 'All Drivers',
        'selected_year': 2024,
        'page': '📊 Pit Stop Analytics',
        'theme': 'dark',
        'show_advanced': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_session_value(key: str, default=None):
    """
    Safely get session state value.
    
    Args:
        key: Session key
        default: Default value if key not found
        
    Returns:
        Session value or default
    """
    return st.session_state.get(key, default)


def set_session_value(key: str, value):
    """
    Safely set session state value.
    
    Args:
        key: Session key
        value: Value to set
    """
    st.session_state[key] = value


if __name__ == "__main__":
    # Test utilities
    import pandas as pd
    
    test_df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    print(f"Memory: {estimate_memory_usage(test_df)}")
    print(f"Format: {format_milliseconds(2500)}")
    print(f"Improvement: {calculate_improvement_ratio(100, 70)}%")