"""
Example: Integrating Scraping Metrics into Ingestion Service

This example shows how to add scraping metrics to your existing ingestion workflow.
"""

import time
from pathlib import Path
from typing import Dict, Any

# Import monitoring
from monitoring import get_monitoring_service
from monitoring.helpers.scraping_metrics import ScrapingIterationTracker, ScrapingMetricsHelper

# Your existing imports (examples)
# from services.ingestion import IngestionService
# from services.github_service import GitHubService
# from db.vector_client import VectorClient


class MonitoredIngestionService:
    """
    Example wrapper for your ingestion service with metrics tracking.
    
    You can either:
    1. Wrap your existing service (shown here)
    2. Add metrics directly to your existing service
    """
    
    def __init__(self, ingestion_service, monitoring_service=None):
        """
        Initialize monitored ingestion service.
        
        Args:
            ingestion_service: Your existing IngestionService instance
            monitoring_service: MonitoringService instance (optional, gets global if not provided)
        """
        self.ingestion = ingestion_service
        self.monitoring = monitoring_service or get_monitoring_service()
        self.scraping_metrics = ScrapingMetricsHelper(self.monitoring)
        
        # Set expected interval (e.g., run every hour)
        self.scraping_metrics.set_interval(3600)
    
    def run_scheduled_ingestion(self, repo_owner: str, repo_name: str) -> Dict[str, Any]:
        """
        Run a scheduled ingestion with full metrics tracking.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
        
        Returns:
            Dictionary with ingestion results and metrics
        """
        results = {
            'success': False,
            'files_processed': 0,
            'files_skipped': 0,
            'errors': [],
            'duration': 0
        }
        
        # Track the entire iteration
        with ScrapingIterationTracker(self.monitoring) as tracker:
            start_time = time.time()
            
            try:
                # Step 1: Reload/refresh configuration if needed
                try:
                    self._reload_configuration()
                except Exception as e:
                    self.monitoring.log_error(
                        f"Failed to reload configuration: {e}",
                        logger_type='ingestion'
                    )
                    tracker.record_reload_failure()
                    raise
                
                # Step 2: Run the actual ingestion
                self.monitoring.log_info(
                    f"Starting ingestion for {repo_owner}/{repo_name}",
                    logger_type='ingestion'
                )
                
                ingestion_result = self.ingestion.ingest_repository(
                    owner=repo_owner,
                    repo=repo_name
                )
                
                # Step 3: Process results and track skipped items
                results['files_processed'] = ingestion_result.get('processed', 0)
                results['files_skipped'] = ingestion_result.get('skipped', 0)
                
                # Track skipped files
                if results['files_skipped'] > 0:
                    tracker.record_skipped_scrape(results['files_skipped'])
                    self.monitoring.log_warning(
                        f"Skipped {results['files_skipped']} files during ingestion",
                        logger_type='ingestion'
                    )
                
                # Step 4: Mark as successful
                duration = time.time() - start_time
                results['duration'] = duration
                results['success'] = True
                
                tracker.mark_success(duration)
                
                self.monitoring.log_info(
                    f"Ingestion completed successfully in {duration:.2f}s",
                    logger_type='ingestion',
                    files_processed=results['files_processed'],
                    files_skipped=results['files_skipped']
                )
                
            except Exception as e:
                duration = time.time() - start_time
                results['duration'] = duration
                results['errors'].append(str(e))
                
                tracker.mark_failure()
                
                self.monitoring.log_error(
                    f"Ingestion failed: {e}",
                    logger_type='ingestion',
                    exc_info=True
                )
                
                raise
        
        return results
    
    def run_single_file_ingestion(self, file_path: str) -> bool:
        """
        Ingest a single file with metrics tracking.
        
        Args:
            file_path: Path to file
        
        Returns:
            True if successful, False if skipped/failed
        """
        start_time = time.time()
        
        try:
            # Check if file should be skipped
            if self._should_skip_file(file_path):
                self.scraping_metrics.skipped_scrape()
                self.monitoring.log_info(
                    f"Skipped file: {file_path}",
                    logger_type='ingestion'
                )
                return False
            
            # Process the file
            self.ingestion.process_file(file_path)
            
            # Record success
            duration = time.time() - start_time
            self.monitoring.record_scrape_complete(duration, success=True)
            
            return True
            
        except Exception as e:
            # Record failure
            duration = time.time() - start_time
            self.monitoring.record_scrape_complete(duration, success=False)
            self.scraping_metrics.skipped_scrape()
            
            self.monitoring.log_error(
                f"Failed to process file {file_path}: {e}",
                logger_type='ingestion'
            )
            
            return False
    
    def check_health(self) -> Dict[str, Any]:
        """
        Get health status of scraping operations.
        
        Returns:
            Health status dictionary
        """
        health = self.scraping_metrics.health()
        
        # Log if unhealthy
        if not health['healthy']:
            self.monitoring.log_warning(
                "Scraping health check failed",
                logger_type='ingestion',
                **health['metrics']
            )
        
        return health
    
    def _reload_configuration(self):
        """Reload configuration (example)."""
        # Your config reload logic here
        # If it fails, it will be caught and tracked as reload_failure
        pass
    
    def _should_skip_file(self, file_path: str) -> bool:
        """
        Determine if a file should be skipped.
        
        Args:
            file_path: Path to file
        
        Returns:
            True if file should be skipped
        """
        # Example skip conditions
        path = Path(file_path)
        
        # Skip if file doesn't exist
        if not path.exists():
            return True
        
        # Skip if file is too large (e.g., > 10MB)
        if path.stat().st_size > 10 * 1024 * 1024:
            return True
        
        # Skip certain file types
        if path.suffix in ['.exe', '.bin', '.so']:
            return True
        
        return False


# Example usage in your main script
def example_usage():
    """Example of how to use the monitored ingestion service."""
    
    # Get monitoring service
    monitoring = get_monitoring_service()
    
    # Initialize your existing services
    # vector_client = VectorClient(...)
    # github_service = GitHubService(...)
    # ingestion_service = IngestionService(...)
    
    # Wrap with monitoring
    # monitored_ingestion = MonitoredIngestionService(
    #     ingestion_service=ingestion_service,
    #     monitoring_service=monitoring
    # )
    
    # Run scheduled ingestion
    # result = monitored_ingestion.run_scheduled_ingestion(
    #     repo_owner="NadeeshaMedagama",
    #     repo_name="python_Sample"
    # )
    
    # Check health
    # health = monitored_ingestion.check_health()
    # print(f"Scraping Health: {health}")
    
    pass


# Alternative: Simple decorator approach for existing functions
def example_decorator_usage():
    """Example using decorators on existing functions."""
    from monitoring.helpers.scraping_metrics import track_scraping_iteration, track_scrape
    
    monitoring = get_monitoring_service()
    
    # Decorate your existing ingestion function
    @track_scraping_iteration(monitoring)
    def run_ingestion_job():
        """Your existing ingestion logic."""
        # Do ingestion work
        pass
    
    # Decorate individual file processing
    @track_scrape(monitoring)
    def process_file(file_path):
        """Process a single file."""
        # Process file
        pass
    
    # Run it
    run_ingestion_job()


if __name__ == "__main__":
    print("This is an example file showing integration patterns.")
    print("See the code for implementation details.")
    print("\nFor full documentation, see: backend/monitoring/docs/SCRAPING_METRICS_GUIDE.md")

