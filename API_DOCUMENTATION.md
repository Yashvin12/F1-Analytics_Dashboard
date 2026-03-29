# F1 Intelligence Dashboard - Complete API Documentation

## Table of Contents

1. [Data Loading Module](#data-loading-module)
2. [Analysis Modules](#analysis-modules)
3. [Visualization Modules](#visualization-modules)
4. [Configuration & Utilities](#configuration--utilities)
5. [Testing Module](#testing-module)
6. [Examples](#examples)

---

## Data Loading Module

**Location**: `src/data_loader.py`

### Core Functions

#### `load_all_datasets(data_dir: str) -> Dict[str, pd.DataFrame]`

Loads all F1 datasets from CSV files with Streamlit caching.

**Parameters**:
- `data_dir` (str): Path to directory containing CSV files (default: "/mnt/project")

**Returns**:
- Dict with keys: 'drivers', 'races', 'results', 'pit_stops', 'constructors', 'circuits'

**Example**:
```python
datasets = load_all_datasets()
pitstop_data = datasets['pit_stops']
```

#### `prepare_pitstop_data(datasets: Dict) -> pd.DataFrame`

Preprocesses pit stop data with merges and feature engineering.

**Features**:
- Merges with drivers and races data
- Adds driver names and codes
- Creates era classifications
- Type conversion and null handling

**Returns**:
- DataFrame with columns: raceId, driverId, driver_name, driver_code, year, era, milliseconds, etc.

#### `prepare_race_results_data(datasets: Dict) -> pd.DataFrame`

Prepares race results with full context.

**Features**:
- Merges drivers, constructors, races, circuits
- Standardizes position and points
- Adds driver identifiers
- Temporal data parsing

**Returns**:
- DataFrame with race result information and context

### Filtering Functions

#### `filter_data_by_driver_year(pitstop_data, driver=None, year=None) -> pd.DataFrame`

Applies sidebar filters to pit stop data.

**Parameters**:
- `driver` (str): Driver name or "All Drivers"
- `year` (int): Year or 0 for all years

**Returns**:
- Filtered DataFrame

#### `get_unique_drivers(pitstop_data) -> list`

Gets sorted list of unique driver names.

#### `get_years_range(pitstop_data) -> Tuple[int, int]`

Returns min and max years in dataset.

### Statistics Functions

#### `get_driver_pitstop_stats(pitstop_data) -> pd.DataFrame`

Calculates comprehensive driver statistics.

**Columns**:
- driver_name
- avg_time_ms
- fastest_stop_ms
- slowest_stop_ms
- std_dev_ms
- total_stops
- last_year

#### `get_pitstop_time_trend(pitstop_data, window=50) -> pd.DataFrame`

Calculates rolling average pit stop times over seasons.

**Parameters**:
- `window` (int): Rolling window size (default: 50)

**Returns**:
- DataFrame with year, milliseconds, rolling_avg

---

## Analysis Modules

### Basic Pit Stop Analysis

**Location**: `src/analysis/pitstop.py`

#### `get_top_pit_crews(pitstop_data, year_filter=None, limit=10) -> pd.DataFrame`

Identifies fastest pit crews.

**Returns**:
- Top N crews sorted by average pit stop time

#### `get_pitstop_distribution(pitstop_data, year_filter=None) -> pd.DataFrame`

Gets pit stop duration distribution for visualization.

#### `get_pitstop_per_stop_number(pitstop_data, year_filter=None) -> pd.DataFrame`

Analyzes pit stop duration by stop sequence (1st, 2nd, 3rd).

#### `get_era_comparison(pitstop_data) -> pd.DataFrame`

Compares pit stop times across F1 eras.

**Eras**:
- 2009-2010
- 2011-2014
- 2015-2020
- 2021+

#### `calculate_pitstop_consistency(pitstop_data, driver) -> Dict`

Calculates consistency metrics for a driver.

**Returns**:
```python
{
    'mean': float,           # Average pit time (ms)
    'std': float,            # Standard deviation
    'cv': float,             # Coefficient of variation (%)
    'consistency_score': float,  # 0-100 score
    'sample_size': int
}
```

#### `get_pitstop_improvements(pitstop_data, driver, year_window=3) -> pd.DataFrame`

Tracks improvements over seasons.

**Returns**:
- DataFrame with year, avg_stop_ms, improvement_ms, improvement_pct

#### `get_pitstop_risk_analysis(pitstop_data, year_filter=None) -> pd.DataFrame`

Analyzes pit stop reliability using outlier detection.

**Returns**:
- risk_score, outlier_percentage, consistency_rating

### Advanced Statistical Analysis

**Location**: `src/analysis/advanced_stats.py`

#### `perform_correlation_analysis(pitstop_data, results_data) -> Dict`

Correlates pit stop efficiency with race outcomes.

**Returns**:
```python
{
    'pit_position_correlation': float,
    'pit_points_correlation': float,
    'regression_slope': float,
    'regression_r_squared': float,
    'interpretation': str
}
```

#### `calculate_team_efficiency_score(pitstop_data, results_data) -> pd.DataFrame`

Comprehensive team efficiency scoring (0-100).

**Scoring**:
- 40% Speed (inverse of average time)
- 35% Consistency (coefficient of variation)
- 25% Reliability (absence of outliers)

#### `predict_optimal_pitstop_window(pitstop_data, driver=None) -> Dict`

Identifies optimal lap numbers for pit stops.

**Returns**:
- peak_lap, mean_lap, common_lap_ranges

#### `calculate_driver_performance_index(pitstop_data) -> pd.DataFrame`

Multi-factor performance scoring for all drivers.

**Components** (weighted):
- 30% Speed Score
- 30% Consistency Score
- 20% Experience Score
- 20% Improvement Score

#### `detect_performance_anomalies(pitstop_data, sensitivity=2.5) -> pd.DataFrame`

Detects unusual pit stop times using z-score method.

**Parameters**:
- `sensitivity` (float): Z-score threshold (default: 2.5)

#### `forecast_pit_performance_trend(pitstop_data, driver, periods=5) -> pd.DataFrame`

Forecasts future pit stop performance using linear regression.

#### `calculate_pit_strategy_efficiency(pitstop_data, results_data) -> Dict`

Analyzes effectiveness of different pit strategies (1-stop, 2-stop, 3-stop).

**Returns**:
- win_percentage, podium_percentage, avg_points per strategy

### Telemetry Analysis

**Location**: `src/analysis/telemetry.py`

#### `create_lap_time_analysis(lap_times_data, race_id, driver_id) -> go.Figure`

Creates lap progression visualization.

#### `create_speed_distribution(lap_times_data, race_id, driver_id) -> go.Figure`

Visualizes lap time distribution (speed consistency).

#### `create_position_changes_chart(lap_times_data, race_id) -> go.Figure`

Shows position changes throughout race.

#### `get_lap_statistics(lap_times_data, race_id, driver_id) -> Dict`

Calculates lap-by-lap statistics.

**Returns**:
```python
{
    'total_laps': int,
    'fastest_lap_s': float,
    'average_lap_s': float,
    'consistency_coefficient': float
}
```

---

## Visualization Modules

### Basic Pit Stop Visualizations

**Location**: `src/visuals/pitstop_viz.py`

All functions return `plotly.graph_objects.Figure` objects.

#### `create_pitstop_histogram(pitstop_data, year_filter=None) -> go.Figure`

Histogram of pit stop durations.

#### `create_pitstop_boxplot(pitstop_data, year_filter=None, top_n=12) -> go.Figure`

Box plot comparison of drivers.

#### `create_pitstop_trend(trend_data) -> go.Figure`

Line chart of pit stop evolution over years.

#### `create_pitstop_by_stop_number(stop_stats) -> go.Figure`

Bar chart of duration by stop sequence.

#### `create_top_crews_chart(top_crews) -> go.Figure`

Horizontal bar chart of fastest crews.

#### `create_era_comparison_chart(era_stats) -> go.Figure`

Multi-panel comparison of pit stop eras.

#### `create_consistency_gauge(consistency_score, driver_name) -> go.Figure`

Gauge chart for consistency scoring (0-100).

### Advanced Visualizations

**Location**: `src/visuals/advanced_viz.py`

#### `create_pitstop_heatmap(pitstop_data, metric='milliseconds') -> go.Figure`

Heatmap of pit stop metrics by driver/year.

#### `create_performance_index_chart(performance_data) -> go.Figure`

Stacked bar chart showing performance components.

#### `create_correlation_matrix_chart(correlation_data) -> go.Figure`

Heatmap of metric correlations.

#### `create_strategy_effectiveness_chart(strategy_data) -> go.Figure`

Multi-panel strategy effectiveness comparison.

#### `create_anomaly_detection_chart(anomalies) -> go.Figure`

Scatter plot highlighting detected anomalies.

#### `create_forecast_chart(forecast_data, driver_name) -> go.Figure`

Line chart with historical and forecast data.

#### `create_team_efficiency_radar(team_data) -> go.Figure`

Radar chart for team comparison.

#### `create_lap_window_analysis(window_data) -> go.Figure`

Bar chart of optimal pit stop lap windows.

---

## Configuration & Utilities

**Location**: `src/config.py`

### Configuration Class

#### `Config` (dataclass)

Central configuration constants:

```python
Config.DATA_DIR              # Data directory path
Config.PAGE_LAYOUT          # "wide" for full-width
Config.CHART_HEIGHT         # Default: 500
Config.CHART_TEMPLATE       # "plotly_dark"
Config.Z_SCORE_THRESHOLD    # 2.5 for anomalies
Config.ROLLING_WINDOW       # 50 for moving average
```

### Utility Functions

#### `format_milliseconds(ms: float, decimals=1) -> str`

Converts milliseconds to seconds string (e.g., "2.1s").

#### `format_percentage(value: float, decimals=1) -> str`

Formats percentage (e.g., "45.2%").

#### `get_color_by_value(value, min_val=0, max_val=100, reverse=False) -> str`

Returns RGB color gradient based on value.

#### `get_performance_badge(score: float) -> str`

Returns emoji badge (🥇 🥈 🥉 📊) based on score.

#### `get_trend_indicator(current, previous) -> Tuple[str, str]`

Returns trend emoji (📈 📉 ➡️) and direction.

#### `validate_data(df, required_columns) -> Tuple[bool, str]`

Validates DataFrame structure and data.

#### `calculate_improvement_ratio(old_value, new_value) -> float`

Calculates percentage change.

#### `percentile_rank(value, series) -> float`

Returns percentile rank (0-100).

---

## Testing Module

**Location**: `src/testing.py`

### Validation Classes

#### `DataValidator`

**Methods**:
- `validate_pitstop_data(df) -> Dict`: Checks data integrity
- `validate_race_results(df) -> Dict`: Validates race result structure

#### `DataQualityTests`

**Methods**:
- `test_pitstop_consistency(df) -> bool`
- `test_driver_pit_count(df, min_stops=5) -> bool`
- `test_race_completeness(df, min_drivers=5) -> bool`
- `test_temporal_continuity(df) -> bool`

#### `PerformanceTests`

**Methods**:
- `measure_load_time(function, *args) -> float`: Returns execution time
- `test_memory_efficiency(df, max_memory_mb=100) -> bool`
- `test_query_performance(df, max_time_ms=100) -> bool`

#### `StatisticalTests`

**Methods**:
- `test_distribution_normality(series) -> Tuple[float, str]`
- `test_outlier_proportion(series, threshold_sigma=3.0) -> float`

#### `RegressionTests`

**Methods**:
- `test_pitstop_analysis_pipeline(pitstop_df, results_df) -> bool`
- `test_visualization_pipeline(pitstop_df) -> bool`

### Master Test Function

#### `run_all_tests(pitstop_df, results_df) -> Dict[str, bool]`

Executes comprehensive test suite, returns results.

---

## Examples

### Basic Usage

```python
from src.data_loader import load_all_datasets, prepare_pitstop_data
from src.analysis.pitstop import get_top_pit_crews
from src.visuals.pitstop_viz import create_top_crews_chart

# Load data
datasets = load_all_datasets()
pitstop_data = prepare_pitstop_data(datasets)

# Analyze
top_crews = get_top_pit_crews(pitstop_data, limit=10)

# Visualize
fig = create_top_crews_chart(top_crews)
fig.show()
```

### Advanced Analysis

```python
from src.analysis.advanced_stats import (
    calculate_driver_performance_index,
    perform_correlation_analysis
)

# Performance index for all drivers
perf_index = calculate_driver_performance_index(pitstop_data)

# Correlation with race results
race_results = prepare_race_results_data(datasets)
correlations = perform_correlation_analysis(pitstop_data, race_results)

print(f"Pit Time ↔ Position Correlation: {correlations['pit_position_correlation']}")
print(f"R² Value: {correlations['regression_r_squared']}")
```

### Anomaly Detection

```python
from src.analysis.advanced_stats import detect_performance_anomalies

# Find unusual pit stops
anomalies = detect_performance_anomalies(pitstop_data, sensitivity=2.5)

print(f"Found {len(anomalies)} anomalies")
print(anomalies[['driver_name', 'milliseconds', 'z_score']])
```

### Team Analysis

```python
from src.analysis.advanced_stats import calculate_team_efficiency_score
from src.visuals.advanced_viz import create_team_efficiency_radar

# Score teams
team_scores = calculate_team_efficiency_score(pitstop_data, race_results)

# Visualize
fig = create_team_efficiency_radar(team_scores)
fig.show()
```

### Data Validation

```python
from src.testing import DataValidator, run_all_tests

# Validate data
validator = DataValidator()
pitstop_valid = validator.validate_pitstop_data(pitstop_data)

if pitstop_valid['is_valid']:
    print("✓ Data validation passed")
else:
    print(f"✗ Errors: {pitstop_valid['errors']}")

# Run full test suite
test_results = run_all_tests(pitstop_data, race_results)
for test_name, passed in test_results.items():
    status = "✓" if passed else "✗"
    print(f"{status} {test_name}")
```

---

## Streamlit Integration

### Page Navigation

```python
page = st.radio(
    "Select Analysis",
    ["📊 Pit Stop Analytics", "🏁 Telemetry", "🎯 Driver Insights"]
)

if page == "📊 Pit Stop Analytics":
    render_pitstop_page()
elif page == "🏁 Telemetry":
    render_telemetry_page()
else:
    render_driver_page()
```

### Interactive Filtering

```python
col1, col2 = st.columns(2)

with col1:
    selected_driver = st.selectbox("Driver", get_unique_drivers(pitstop_data))

with col2:
    selected_year = st.slider("Year", 2009, 2024, 2024)

# Apply filters
filtered = filter_data_by_driver_year(pitstop_data, selected_driver, selected_year)
```

### Chart Display

```python
# Single chart
st.plotly_chart(
    create_pitstop_histogram(pitstop_data),
    use_container_width=True
)

# Tabbed interface
tab1, tab2, tab3 = st.tabs(["Distribution", "Trends", "Comparisons"])

with tab1:
    st.plotly_chart(create_pitstop_histogram(...), use_container_width=True)

with tab2:
    st.plotly_chart(create_pitstop_trend(...), use_container_width=True)

with tab3:
    st.plotly_chart(create_pitstop_boxplot(...), use_container_width=True)
```

---

## Best Practices

### Data Loading
- Always use `@st.cache_data` for datasets
- Call once per session
- Use `@st.cache_resource` for expensive computations

### Analysis
- Filter data early to reduce memory usage
- Use vectorized pandas operations
- Handle NaN/None values explicitly

### Visualization
- Use consistent dark theme
- Include hover templates for interactivity
- Set appropriate height/width for readability

### Testing
- Run validation tests on data import
- Monitor performance metrics
- Log errors and warnings

---

**Last Updated**: March 25, 2024
**API Version**: 1.0.0
**Status**: Production Ready ✅