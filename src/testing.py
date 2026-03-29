"""
F1 Intelligence Dashboard - Testing & Quality Assurance Module

Unit tests and data validation functions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class DataValidator:
    """Validates F1 data integrity and quality."""
    
    @staticmethod
    def validate_pitstop_data(df: pd.DataFrame) -> Dict[str, any]:
        """
        Validate pit stop data integrity.
        
        Args:
            df: Pit stop DataFrame
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        # Check required columns
        required_cols = ['raceId', 'driverId', 'stop', 'lap', 'duration', 'milliseconds']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            results['is_valid'] = False
            results['errors'].append(f"Missing columns: {missing_cols}")
            return results
        
        # Check data types
        numeric_cols = ['milliseconds', 'duration', 'lap', 'stop']
        for col in numeric_cols:
            if not pd.api.types.is_numeric_dtype(df[col]):
                results['warnings'].append(f"Column {col} is not numeric")
        
        # Check for duplicates
        duplicates = df.duplicated(subset=['raceId', 'driverId', 'stop']).sum()
        if duplicates > 0:
            results['warnings'].append(f"Found {duplicates} duplicate pit stops")
        
        # Check value ranges
        if (df['milliseconds'] < 0).any():
            results['errors'].append("Found negative pit stop times")
            results['is_valid'] = False
        
        if (df['stop'] < 1).any():
            results['errors'].append("Stop numbers should be >= 1")
            results['is_valid'] = False
        
        # Statistics
        results['statistics'] = {
            'total_records': len(df),
            'null_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100),
            'unique_races': df['raceId'].nunique(),
            'unique_drivers': df['driverId'].nunique(),
            'avg_pit_time_ms': df['milliseconds'].mean(),
            'min_pit_time_ms': df['milliseconds'].min(),
            'max_pit_time_ms': df['milliseconds'].max()
        }
        
        return results
    
    @staticmethod
    def validate_race_results(df: pd.DataFrame) -> Dict[str, any]:
        """
        Validate race results data integrity.
        
        Args:
            df: Race results DataFrame
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        # Required columns
        required_cols = ['raceId', 'driverId', 'position', 'points']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            results['is_valid'] = False
            results['errors'].append(f"Missing columns: {missing_cols}")
            return results
        
        # Position validation
        valid_positions = df['position'].dropna()
        if not all(valid_positions > 0):
            results['warnings'].append("Some positions are not positive")
        
        # Points validation
        if (df['points'] < 0).any():
            results['errors'].append("Found negative points")
            results['is_valid'] = False
        
        # Statistics
        results['statistics'] = {
            'total_records': len(df),
            'unique_races': df['raceId'].nunique(),
            'unique_drivers': df['driverId'].nunique(),
            'avg_points': df['points'].mean(),
            'null_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
        }
        
        return results


class DataQualityTests:
    """Unit tests for data quality."""
    
    @staticmethod
    def test_pitstop_consistency(df: pd.DataFrame) -> bool:
        """
        Test pit stop time consistency (no extreme outliers).
        
        Args:
            df: Pit stop DataFrame
            
        Returns:
            True if test passes
        """
        mean = df['milliseconds'].mean()
        std = df['milliseconds'].std()
        
        # Check if more than 1% are 5 sigma away
        outliers = ((df['milliseconds'] > mean + 5*std) | 
                   (df['milliseconds'] < mean - 5*std)).sum()
        outlier_pct = (outliers / len(df)) * 100
        
        return outlier_pct < 1.0
    
    @staticmethod
    def test_driver_pit_count(df: pd.DataFrame, min_stops: int = 5) -> bool:
        """
        Test that drivers have reasonable number of pit stops.
        
        Args:
            df: Pit stop DataFrame
            min_stops: Minimum required pit stops per driver
            
        Returns:
            True if test passes
        """
        driver_stops = df.groupby('driverId').size()
        return (driver_stops >= min_stops).all()
    
    @staticmethod
    def test_race_completeness(df: pd.DataFrame, min_drivers_per_race: int = 5) -> bool:
        """
        Test that races have minimum number of drivers.
        
        Args:
            df: Race results DataFrame
            min_drivers_per_race: Minimum drivers per race
            
        Returns:
            True if test passes
        """
        drivers_per_race = df.groupby('raceId')['driverId'].nunique()
        return (drivers_per_race >= min_drivers_per_race).all()
    
    @staticmethod
    def test_temporal_continuity(df: pd.DataFrame) -> bool:
        """
        Test that data is temporally continuous (no large gaps).
        
        Args:
            df: DataFrame with year column
            
        Returns:
            True if test passes
        """
        if 'year' not in df.columns:
            return True
        
        years = sorted(df['year'].unique())
        gaps = [years[i+1] - years[i] for i in range(len(years)-1)]
        
        # Allow up to 2-year gap (for seasons skipped)
        return all(gap <= 2 for gap in gaps)


class PerformanceTests:
    """Performance and efficiency tests."""
    
    @staticmethod
    def measure_load_time(load_function, *args) -> float:
        """
        Measure function execution time.
        
        Args:
            load_function: Function to measure
            *args: Arguments to function
            
        Returns:
            Execution time in seconds
        """
        import time
        
        start = time.time()
        load_function(*args)
        end = time.time()
        
        return end - start
    
    @staticmethod
    def test_memory_efficiency(df: pd.DataFrame, 
                              max_memory_mb: int = 100) -> bool:
        """
        Test that DataFrame doesn't exceed memory limit.
        
        Args:
            df: DataFrame to test
            max_memory_mb: Maximum allowed memory in MB
            
        Returns:
            True if memory usage is acceptable
        """
        memory_bytes = df.memory_usage(deep=True).sum()
        memory_mb = memory_bytes / (1024**2)
        
        return memory_mb <= max_memory_mb
    
    @staticmethod
    def test_query_performance(df: pd.DataFrame, 
                              max_time_ms: float = 100) -> bool:
        """
        Test basic query performance.
        
        Args:
            df: DataFrame to test
            max_time_ms: Maximum query time in milliseconds
            
        Returns:
            True if performance is acceptable
        """
        import time
        
        start = time.time()
        _ = df.groupby('driverId').size()
        elapsed_ms = (time.time() - start) * 1000
        
        return elapsed_ms <= max_time_ms


class StatisticalTests:
    """Statistical validation tests."""
    
    @staticmethod
    def test_distribution_normality(series: pd.Series) -> Tuple[float, str]:
        """
        Test if data follows normal distribution (Shapiro-Wilk test).
        
        Args:
            series: Pandas Series
            
        Returns:
            Tuple of (p_value, interpretation)
        """
        from scipy import stats
        
        sample = series.dropna()
        if len(sample) < 3:
            return None, "Insufficient data"
        
        statistic, p_value = stats.shapiro(sample[:5000])  # Limit to 5000 for speed
        
        if p_value > 0.05:
            interpretation = "Normal distribution"
        else:
            interpretation = "Non-normal distribution"
        
        return p_value, interpretation
    
    @staticmethod
    def test_outlier_proportion(series: pd.Series, 
                               threshold_sigma: float = 3.0) -> float:
        """
        Calculate proportion of outliers using z-score method.
        
        Args:
            series: Pandas Series
            threshold_sigma: Z-score threshold
            
        Returns:
            Proportion of outliers (0-1)
        """
        from scipy import stats
        
        sample = series.dropna()
        z_scores = np.abs(stats.zscore(sample))
        outlier_count = (z_scores > threshold_sigma).sum()
        
        return outlier_count / len(sample)


class RegressionTests:
    """Integration tests for key functionality."""
    
    @staticmethod
    def test_pitstop_analysis_pipeline(pitstop_df: pd.DataFrame,
                                       results_df: pd.DataFrame) -> bool:
        """
        Test complete pit stop analysis pipeline.
        
        Args:
            pitstop_df: Pit stop data
            results_df: Race results data
            
        Returns:
            True if pipeline completes without errors
        """
        try:
            # Test data loading
            assert len(pitstop_df) > 0
            assert len(results_df) > 0
            
            # Test merging
            merged = pitstop_df.merge(results_df, on=['raceId', 'driverId'], how='inner')
            assert len(merged) > 0
            
            # Test aggregations
            driver_stats = pitstop_df.groupby('driver_name').agg({
                'milliseconds': ['mean', 'std', 'min', 'max', 'count']
            })
            assert len(driver_stats) > 0
            
            # Test filtering
            filtered = pitstop_df[pitstop_df['year'] >= 2020]
            assert len(filtered) >= 0
            
            return True
        
        except Exception as e:
            print(f"Pipeline test failed: {e}")
            return False
    
    @staticmethod
    def test_visualization_pipeline(pitstop_df: pd.DataFrame) -> bool:
        """
        Test visualization creation pipeline.
        
        Args:
            pitstop_df: Pit stop data
            
        Returns:
            True if visualizations create without errors
        """
        try:
            from src.visuals.pitstop_viz import (
                create_pitstop_histogram,
                create_pitstop_boxplot,
                create_top_crews_chart
            )
            from src.analysis.pitstop import get_top_pit_crews
            
            # Test histogram
            fig1 = create_pitstop_histogram(pitstop_df)
            assert fig1 is not None
            
            # Test boxplot
            fig2 = create_pitstop_boxplot(pitstop_df)
            assert fig2 is not None
            
            # Test crew chart
            crews = get_top_pit_crews(pitstop_df)
            fig3 = create_top_crews_chart(crews)
            assert fig3 is not None
            
            return True
        
        except Exception as e:
            print(f"Visualization test failed: {e}")
            return False


def run_all_tests(pitstop_df: pd.DataFrame,
                 results_df: pd.DataFrame) -> Dict[str, bool]:
    """
    Run comprehensive test suite.
    
    Args:
        pitstop_df: Pit stop DataFrame
        results_df: Race results DataFrame
        
    Returns:
        Dictionary with test results
    """
    results = {
        'data_validation_pitstop': DataValidator.validate_pitstop_data(pitstop_df)['is_valid'],
        'data_validation_results': DataValidator.validate_race_results(results_df)['is_valid'],
        'pit_consistency': DataQualityTests.test_pitstop_consistency(pitstop_df),
        'driver_pit_count': DataQualityTests.test_driver_pit_count(pitstop_df),
        'race_completeness': DataQualityTests.test_race_completeness(results_df),
        'temporal_continuity': DataQualityTests.test_temporal_continuity(pitstop_df),
        'memory_efficiency': PerformanceTests.test_memory_efficiency(pitstop_df),
        'query_performance': PerformanceTests.test_query_performance(pitstop_df),
        'pipeline_integration': RegressionTests.test_pitstop_analysis_pipeline(pitstop_df, results_df),
        'visualization_pipeline': RegressionTests.test_visualization_pipeline(pitstop_df)
    }
    
    return results


if __name__ == "__main__":
    # Example usage
    print("Quality Assurance Module for F1 Intelligence Dashboard")
    print("=" * 60)
    print("Ready to run tests on F1 datasets")