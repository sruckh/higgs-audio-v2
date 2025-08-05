#!/usr/bin/env python3
"""
RunPod Serverless Health Monitoring and Metrics Collection
Provides comprehensive monitoring for Higgs Audio V2 serverless deployment.
"""

import asyncio
import json
import os
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from loguru import logger
import torch
import GPUtil

try:
    import prometheus_client as prometheus
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("Prometheus client not available, metrics will be logged only")


@dataclass
class HealthMetrics:
    """Health metrics data structure"""
    timestamp: float
    status: str
    memory_usage_gb: float
    gpu_memory_gb: float
    gpu_utilization_percent: float
    container_size_gb: float
    models_loaded: bool
    active_requests: int
    total_requests: int
    error_rate: float
    average_response_time: float


@dataclass
class RequestMetrics:
    """Individual request metrics"""
    request_id: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None
    voice_used: Optional[str] = None
    audio_duration: Optional[float] = None
    text_length: Optional[int] = None


class HealthMonitor:
    """Comprehensive health monitoring for RunPod serverless deployment"""
    
    def __init__(self, port: int = 9090):
        self.port = port
        self.start_time = time.time()
        self.request_history: List[RequestMetrics] = []
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        # Thread-safe metrics
        self._metrics_lock = threading.RLock()
        self._active_requests_count = 0
        
        # Prometheus metrics (if available)
        if PROMETHEUS_AVAILABLE:
            self._setup_prometheus_metrics()
        
        # Background tasks
        self._monitoring_task = None
        self._cleanup_task = None
        
        logger.info("Health Monitor initialized")
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics collection"""
        try:
            # Request metrics
            self.prom_requests_total = prometheus.Counter(
                'higgs_audio_requests_total',
                'Total number of requests',
                ['voice', 'status']
            )
            
            self.prom_request_duration = prometheus.Histogram(
                'higgs_audio_request_duration_seconds',
                'Request duration in seconds',
                ['voice'],
                buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
            )
            
            # Resource metrics
            self.prom_memory_usage = prometheus.Gauge(
                'higgs_audio_memory_usage_gb',
                'Memory usage in GB'
            )
            
            self.prom_gpu_memory = prometheus.Gauge(
                'higgs_audio_gpu_memory_gb',
                'GPU memory usage in GB'
            )
            
            self.prom_gpu_utilization = prometheus.Gauge(
                'higgs_audio_gpu_utilization_percent',
                'GPU utilization percentage'
            )
            
            self.prom_active_requests = prometheus.Gauge(
                'higgs_audio_active_requests',
                'Number of active requests'
            )
            
            logger.info("Prometheus metrics initialized")
        except Exception as e:
            logger.error(f"Failed to setup Prometheus metrics: {e}")
            self.prom_enabled = False
        else:
            self.prom_enabled = True
    
    async def start_monitoring(self):
        """Start background monitoring tasks"""
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Background monitoring started")
    
    async def stop_monitoring(self):
        """Stop background monitoring tasks"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        logger.info("Background monitoring stopped")
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while True:
            try:
                metrics = self.collect_metrics()
                self._log_metrics(metrics)
                
                if self.prom_enabled:
                    self._update_prometheus_metrics(metrics)
                
                await asyncio.sleep(10)  # Monitor every 10 seconds
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _cleanup_loop(self):
        """Cleanup old metrics periodically"""
        while True:
            try:
                await self._cleanup_old_metrics()
                await asyncio.sleep(300)  # Cleanup every 5 minutes
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
                await asyncio.sleep(600)
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics data"""
        current_time = time.time()
        with self._metrics_lock:
            # Keep only last 1000 requests
            if len(self.request_history) > 1000:
                self.request_history = self.request_history[-1000:]
            
            # Remove requests older than 1 hour
            self.request_history = [
                req for req in self.request_history
                if current_time - req.start_time < 3600
            ]
    
    def collect_metrics(self) -> HealthMetrics:
        """Collect current health metrics"""
        try:
            # Memory usage
            memory_info = psutil.virtual_memory()
            memory_usage_gb = memory_info.used / (1024 ** 3)
            
            # GPU metrics
            gpu_memory_gb = 0.0
            gpu_utilization_percent = 0.0
            
            try:
                if torch.cuda.is_available():
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]  # Use first GPU
                        gpu_memory_gb = gpu.memoryUsed / 1024  # MB to GB
                        gpu_utilization_percent = gpu.load * 100
            except Exception as e:
                logger.warning(f"GPU metrics collection failed: {e}")
            
            # Container size (approximate)
            container_size_gb = self._get_container_size()
            
            # Request metrics
            with self._metrics_lock:
                active_requests = self._active_requests_count
                total_requests = self.total_requests
                error_rate = (self.failed_requests / total_requests * 100) if total_requests > 0 else 0.0
                
                # Calculate average response time
                completed_requests = [r for r in self.request_history if r.duration is not None]
                avg_response_time = (
                    sum(r.duration for r in completed_requests) / len(completed_requests)
                    if completed_requests else 0.0
                )
            
            return HealthMetrics(
                timestamp=time.time(),
                status=self._get_health_status(memory_usage_gb, gpu_memory_gb),
                memory_usage_gb=memory_usage_gb,
                gpu_memory_gb=gpu_memory_gb,
                gpu_utilization_percent=gpu_utilization_percent,
                container_size_gb=container_size_gb,
                models_loaded=self._check_models_loaded(),
                active_requests=active_requests,
                total_requests=total_requests,
                error_rate=error_rate,
                average_response_time=avg_response_time
            )
            
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return HealthMetrics(
                timestamp=time.time(),
                status="error",
                memory_usage_gb=0.0,
                gpu_memory_gb=0.0,
                gpu_utilization_percent=0.0,
                container_size_gb=0.0,
                models_loaded=False,
                active_requests=0,
                total_requests=0,
                error_rate=0.0,
                average_response_time=0.0
            )
    
    def _get_container_size(self) -> float:
        """Estimate container size in GB"""
        try:
            # Check container size by examining app directory
            result = os.popen("du -sh /app 2>/dev/null || echo '0'").read().strip()
            size_str = result.split()[0] if result.split() else "0"
            
            if size_str.endswith('G'):
                return float(size_str[:-1])
            elif size_str.endswith('M'):
                return float(size_str[:-1]) / 1024
            elif size_str.endswith('K'):
                return float(size_str[:-1]) / (1024 * 1024)
            else:
                return float(size_str) / (1024 * 1024 * 1024)
        except:
            return 0.0
    
    def _get_health_status(self, memory_gb: float, gpu_memory_gb: float) -> str:
        """Determine overall health status"""
        # Check memory usage
        if memory_gb > 15:  # High memory usage
            return "degraded"
        
        # Check GPU memory
        if gpu_memory_gb > 10:  # High GPU memory
            return "degraded"
        
        # Check error rate
        with self._metrics_lock:
            if self.total_requests > 10:
                recent_error_rate = (self.failed_requests / self.total_requests) * 100
                if recent_error_rate > 20:  # High error rate
                    return "degraded"
        
        return "healthy"
    
    def _check_models_loaded(self) -> bool:
        """Check if models are loaded"""
        try:
            return torch.cuda.is_available() and torch.cuda.memory_allocated() > 0
        except:
            return False
    
    def _log_metrics(self, metrics: HealthMetrics):
        """Log metrics to stdout"""
        logger.info(
            f"Health Check: {metrics.status} | "
            f"Memory: {metrics.memory_usage_gb:.1f}GB | "
            f"GPU: {metrics.gpu_memory_gb:.1f}GB ({metrics.gpu_utilization_percent:.1f}%) | "
            f"Requests: {metrics.active_requests} active, {metrics.total_requests} total | "
            f"Error Rate: {metrics.error_rate:.1f}% | "
            f"Avg Response: {metrics.average_response_time:.2f}s"
        )
    
    def _update_prometheus_metrics(self, metrics: HealthMetrics):
        """Update Prometheus metrics"""
        try:
            self.prom_memory_usage.set(metrics.memory_usage_gb)
            self.prom_gpu_memory.set(metrics.gpu_memory_gb)
            self.prom_gpu_utilization.set(metrics.gpu_utilization_percent)
            self.prom_active_requests.set(metrics.active_requests)
        except Exception as e:
            logger.error(f"Failed to update Prometheus metrics: {e}")
    
    def start_request(self, request_id: str, voice: str = "unknown", text_length: int = 0):
        """Track the start of a new request"""
        with self._metrics_lock:
            self._active_requests_count += 1
            self.total_requests += 1
            
            request = RequestMetrics(
                request_id=request_id,
                start_time=time.time(),
                voice_used=voice,
                text_length=text_length
            )
            self.request_history.append(request)
    
    def end_request(self, request_id: str, success: bool, 
                    error_message: Optional[str] = None,
                    audio_duration: Optional[float] = None):
        """Track the end of a request"""
        with self._metrics_lock:
            self._active_requests_count -= 1
            
            # Find the request in history
            for request in self.request_history:
                if request.request_id == request_id and request.end_time is None:
                    request.end_time = time.time()
                    request.duration = request.end_time - request.start_time
                    request.success = success
                    request.error_message = error_message
                    request.audio_duration = audio_duration
                    
                    if success:
                        self.successful_requests += 1
                    else:
                        self.failed_requests += 1
                    
                    # Update Prometheus
                    if self.prom_enabled:
                        self.prom_requests_total.labels(
                            voice=request.voice_used or "unknown",
                            status="success" if success else "error"
                        ).inc()
                        
                        if request.duration:
                            self.prom_request_duration.labels(
                                voice=request.voice_used or "unknown"
                            ).observe(request.duration)
                    
                    break
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary"""
        metrics = self.collect_metrics()
        uptime = time.time() - self.start_time
        
        with self._metrics_lock:
            recent_requests = [r for r in self.request_history 
                            if time.time() - r.start_time < 3600]
            
            recent_success_rate = (
                sum(1 for r in recent_requests if r.success) / len(recent_requests) * 100
                if recent_requests else 100.0
            )
        
        return {
            "status": metrics.status,
            "uptime_seconds": uptime,
            "uptime_formatted": str(timedelta(seconds=int(uptime))),
            "metrics": asdict(metrics),
            "recent_performance": {
                "requests_last_hour": len(recent_requests),
                "success_rate_last_hour": recent_success_rate,
                "average_duration_last_hour": (
                    sum(r.duration for r in recent_requests if r.duration) / len(recent_requests)
                    if recent_requests and any(r.duration for r in recent_requests) else 0.0
                )
            },
            "version": "1.0.0",
            "monitoring_enabled": True
        }
    
    def get_detailed_metrics(self) -> Dict[str, Any]:
        """Get detailed metrics for analysis"""
        metrics = self.collect_metrics()
        
        with self._metrics_lock:
            recent_errors = [
                {
                    "request_id": r.request_id,
                    "error": r.error_message,
                    "timestamp": r.start_time,
                    "voice": r.voice_used
                }
                for r in self.request_history 
                if not r.success and r.error_message and time.time() - r.start_time < 3600
            ]
            
            voice_usage = {}
            for r in self.request_history:
                if r.voice_used:
                    voice_usage[r.voice_used] = voice_usage.get(r.voice_used, 0) + 1
        
        return {
            "current_metrics": asdict(metrics),
            "recent_errors": recent_errors[-10:],  # Last 10 errors
            "voice_usage": voice_usage,
            "performance_by_voice": self._get_performance_by_voice(),
            "system_info": self._get_system_info()
        }
    
    def _get_performance_by_voice(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics broken down by voice"""
        with self._metrics_lock:
            voice_metrics = {}
            
            for voice in set(r.voice_used for r in self.request_history if r.voice_used):
                voice_requests = [r for r in self.request_history if r.voice_used == voice and r.duration]
                
                if voice_requests:
                    voice_metrics[voice] = {
                        "request_count": len(voice_requests),
                        "average_duration": sum(r.duration for r in voice_requests) / len(voice_requests),
                        "success_rate": sum(1 for r in voice_requests if r.success) / len(voice_requests) * 100,
                        "average_audio_duration": (
                            sum(r.audio_duration or 0 for r in voice_requests) / len(voice_requests)
                        )
                    }
        
        return voice_metrics
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            return {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / (1024 ** 3),
                "disk_usage_gb": psutil.disk_usage('/').used / (1024 ** 3),
                "python_version": os.sys.version,
                "torch_version": torch.__version__,
                "cuda_available": torch.cuda.is_available(),
                "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
                "prometheus_enabled": self.prom_enabled
            }
        except Exception as e:
            logger.error(f"System info collection failed: {e}")
            return {"error": str(e)}


# Global health monitor instance
health_monitor = HealthMonitor()


def get_health_monitor() -> HealthMonitor:
    """Get the global health monitor instance"""
    return health_monitor


async def start_health_monitoring():
    """Start health monitoring (call during startup)"""
    await health_monitor.start_monitoring()


async def stop_health_monitoring():
    """Stop health monitoring (call during shutdown)"""
    await health_monitor.stop_monitoring()