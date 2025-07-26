"""
Performance optimization and monitoring utilities for Runpod serverless.
Includes GPU memory management, batch processing, and performance metrics.
"""

import time
import torch
import psutil
import gc
from typing import Dict, Any, List, Optional
from loguru import logger
from contextlib import contextmanager
from dataclasses import dataclass


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""

    processing_time: float
    gpu_memory_before: float
    gpu_memory_after: float
    gpu_memory_peak: float
    cpu_usage: float
    system_memory_usage: float
    queue_size: Optional[int] = None


class PerformanceMonitor:
    """Monitor and optimize performance for serverless deployment."""

    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history_size = 1000

    def get_gpu_memory_info(self) -> Dict[str, float]:
        """Get current GPU memory information."""
        if not torch.cuda.is_available():
            return {}

        return {
            "allocated_gb": torch.cuda.memory_allocated() / 1e9,
            "cached_gb": torch.cuda.memory_reserved() / 1e9,
            "max_allocated_gb": torch.cuda.max_memory_allocated() / 1e9,
            "max_cached_gb": torch.cuda.max_memory_reserved() / 1e9,
        }

    def get_system_info(self) -> Dict[str, Any]:
        """Get system resource information."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available_gb": psutil.virtual_memory().available / 1e9,
            "disk_usage_percent": psutil.disk_usage("/").percent,
        }

    @contextmanager
    def measure_performance(self, operation_name: str = "operation"):
        """Context manager for measuring performance metrics."""
        start_time = time.time()

        # Get initial metrics
        gpu_memory_before = torch.cuda.memory_allocated() / 1e9 if torch.cuda.is_available() else 0
        cpu_before = psutil.cpu_percent()
        memory_before = psutil.virtual_memory().percent

        # Reset peak memory tracking
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()

        try:
            yield
        finally:
            # Calculate final metrics
            processing_time = time.time() - start_time
            gpu_memory_after = torch.cuda.memory_allocated() / 1e9 if torch.cuda.is_available() else 0
            gpu_memory_peak = torch.cuda.max_memory_allocated() / 1e9 if torch.cuda.is_available() else 0
            cpu_after = psutil.cpu_percent()
            memory_after = psutil.virtual_memory().percent

            metrics = PerformanceMetrics(
                processing_time=processing_time,
                gpu_memory_before=gpu_memory_before,
                gpu_memory_after=gpu_memory_after,
                gpu_memory_peak=gpu_memory_peak,
                cpu_usage=(cpu_before + cpu_after) / 2,
                system_memory_usage=(memory_before + memory_after) / 2,
            )

            self.record_metrics(metrics)

            logger.info(f"Performance metrics for {operation_name}:")
            logger.info(f"  Processing time: {processing_time:.2f}s")
            logger.info(
                f"  GPU memory: {gpu_memory_before:.2f}GB -> {gpu_memory_after:.2f}GB (peak: {gpu_memory_peak:.2f}GB)"
            )
            logger.info(f"  CPU usage: {metrics.cpu_usage:.1f}%")
            logger.info(f"  Memory usage: {metrics.system_memory_usage:.1f}%")

    def record_metrics(self, metrics: PerformanceMetrics):
        """Record performance metrics."""
        self.metrics_history.append(metrics)

        # Keep only recent metrics
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size :]

    def get_average_metrics(self, last_n: int = 10) -> Dict[str, float]:
        """Get average metrics from recent operations."""
        if not self.metrics_history:
            return {}

        recent_metrics = self.metrics_history[-last_n:]

        return {
            "avg_processing_time": sum(m.processing_time for m in recent_metrics) / len(recent_metrics),
            "avg_gpu_memory_usage": sum(m.gpu_memory_peak for m in recent_metrics) / len(recent_metrics),
            "avg_cpu_usage": sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics),
            "avg_memory_usage": sum(m.system_memory_usage for m in recent_metrics) / len(recent_metrics),
        }


class GPUMemoryManager:
    """Manage GPU memory for optimal performance."""

    @staticmethod
    def cleanup_gpu_memory():
        """Clean up GPU memory."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()
            logger.debug("GPU memory cleaned up")

    @staticmethod
    def get_memory_usage_percentage() -> float:
        """Get GPU memory usage as percentage."""
        if not torch.cuda.is_available():
            return 0.0

        allocated = torch.cuda.memory_allocated()
        total = torch.cuda.get_device_properties(0).total_memory
        return (allocated / total) * 100

    @staticmethod
    def check_memory_pressure() -> bool:
        """Check if GPU memory pressure is high."""
        return GPUMemoryManager.get_memory_usage_percentage() > 80.0

    @contextmanager
    def memory_efficient_context(self):
        """Context manager for memory-efficient operations."""
        # Cleanup before operation
        self.cleanup_gpu_memory()

        initial_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0

        try:
            yield
        finally:
            # Cleanup after operation if memory pressure is high
            if self.check_memory_pressure():
                self.cleanup_gpu_memory()

            final_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
            memory_diff = (final_memory - initial_memory) / 1e9

            if memory_diff > 1.0:  # More than 1GB difference
                logger.warning(f"Large memory allocation detected: {memory_diff:.2f}GB")


class BatchProcessor:
    """Handle batch processing for multiple requests."""

    def __init__(self, max_batch_size: int = 4, max_wait_time: float = 0.1):
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        self.pending_requests = []
        self.last_batch_time = time.time()

    def should_process_batch(self) -> bool:
        """Determine if batch should be processed now."""
        if not self.pending_requests:
            return False

        # Process if batch is full
        if len(self.pending_requests) >= self.max_batch_size:
            return True

        # Process if max wait time exceeded
        if time.time() - self.last_batch_time >= self.max_wait_time:
            return True

        return False

    def add_request(self, request: Dict[str, Any]) -> bool:
        """Add request to batch. Returns True if batch should be processed."""
        self.pending_requests.append(request)
        return self.should_process_batch()

    def get_batch(self) -> List[Dict[str, Any]]:
        """Get current batch and reset."""
        batch = self.pending_requests.copy()
        self.pending_requests.clear()
        self.last_batch_time = time.time()
        return batch


class PerformanceOptimizer:
    """Optimize performance based on system state."""

    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.memory_manager = GPUMemoryManager()
        self.batch_processor = BatchProcessor()

    def optimize_generation_params(self, base_params: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize generation parameters based on current system state."""
        optimized_params = base_params.copy()

        # Reduce parameters if memory pressure is high
        if self.memory_manager.check_memory_pressure():
            logger.warning("High GPU memory pressure detected, reducing generation parameters")

            # Reduce max tokens
            current_max_tokens = optimized_params.get("max_new_tokens", 1024)
            optimized_params["max_new_tokens"] = min(current_max_tokens, 512)

            # Reduce temperature slightly for more focused generation
            current_temp = optimized_params.get("temperature", 0.7)
            optimized_params["temperature"] = max(current_temp - 0.1, 0.1)

        # Optimize based on recent performance
        avg_metrics = self.monitor.get_average_metrics()
        if avg_metrics.get("avg_processing_time", 0) > 10.0:  # If slow
            logger.warning("Slow processing detected, optimizing for speed")
            optimized_params["max_new_tokens"] = min(optimized_params.get("max_new_tokens", 1024), 512)

        return optimized_params

    def should_enable_batching(self) -> bool:
        """Determine if batching should be enabled based on load."""
        avg_metrics = self.monitor.get_average_metrics()

        # Enable batching if CPU usage is low and we have capacity
        cpu_usage = avg_metrics.get("avg_cpu_usage", 100)
        memory_usage = self.memory_manager.get_memory_usage_percentage()

        return cpu_usage < 60 and memory_usage < 70

    def get_optimization_recommendations(self) -> List[str]:
        """Get recommendations for performance optimization."""
        recommendations = []

        # Check GPU memory
        memory_percent = self.memory_manager.get_memory_usage_percentage()
        if memory_percent > 90:
            recommendations.append(
                "Critical: GPU memory usage > 90%. Consider reducing batch size or model parameters."
            )
        elif memory_percent > 80:
            recommendations.append("Warning: GPU memory usage > 80%. Monitor for out-of-memory errors.")

        # Check recent performance
        avg_metrics = self.monitor.get_average_metrics()
        avg_time = avg_metrics.get("avg_processing_time", 0)

        if avg_time > 15:
            recommendations.append("Slow processing detected. Consider optimizing generation parameters.")
        elif avg_time > 10:
            recommendations.append("Moderate processing times. Monitor performance.")

        # Check system resources
        system_info = self.monitor.get_system_info()
        if system_info["memory_percent"] > 90:
            recommendations.append("High system memory usage. Consider adding more RAM.")

        if system_info["cpu_percent"] > 90:
            recommendations.append("High CPU usage. Consider optimizing CPU-bound operations.")

        if not recommendations:
            recommendations.append("Performance looks good! No optimization needed.")

        return recommendations


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
gpu_memory_manager = GPUMemoryManager()
performance_optimizer = PerformanceOptimizer()


def get_performance_summary() -> Dict[str, Any]:
    """Get comprehensive performance summary."""
    return {
        "gpu_memory": gpu_memory_manager.get_memory_usage_percentage(),
        "system_info": performance_monitor.get_system_info(),
        "average_metrics": performance_monitor.get_average_metrics(),
        "recommendations": performance_optimizer.get_optimization_recommendations(),
    }
