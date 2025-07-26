"""
Production monitoring and logging system for Runpod serverless.
Includes error tracking, performance alerts, and operational metrics.
"""

import json
import time
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from loguru import logger
from collections import defaultdict, deque
from threading import Lock


@dataclass
class ErrorEvent:
    """Represents an error event for tracking."""

    timestamp: float
    error_type: str
    error_message: str
    endpoint_type: str
    request_id: Optional[str] = None
    stack_trace: Optional[str] = None
    user_input_length: Optional[int] = None


@dataclass
class RequestEvent:
    """Represents a request event for tracking."""

    timestamp: float
    endpoint_type: str
    processing_time: float
    success: bool
    input_length: int
    audio_length_seconds: Optional[float] = None
    memory_usage_gb: Optional[float] = None
    request_id: Optional[str] = None


@dataclass
class SystemHealth:
    """System health status."""

    timestamp: float
    gpu_memory_usage_percent: float
    cpu_usage_percent: float
    system_memory_usage_percent: float
    disk_usage_percent: float
    models_loaded: bool
    total_requests: int
    error_rate_1h: float
    avg_response_time_1h: float


class ProductionMonitor:
    """Production monitoring system for serverless deployment."""

    def __init__(self, max_events: int = 10000):
        self.max_events = max_events
        self.lock = Lock()

        # Event storage
        self.error_events: deque = deque(maxlen=max_events)
        self.request_events: deque = deque(maxlen=max_events)
        self.health_checks: deque = deque(maxlen=1000)

        # Counters
        self.counters = defaultdict(int)
        self.endpoint_counters = defaultdict(int)
        self.error_counters = defaultdict(int)

        # Performance tracking
        self.response_times = defaultdict(list)

        logger.info("Production monitor initialized")

    def log_request(
        self,
        endpoint_type: str,
        processing_time: float,
        success: bool,
        input_length: int,
        audio_length_seconds: Optional[float] = None,
        memory_usage_gb: Optional[float] = None,
        request_id: Optional[str] = None,
    ):
        """Log a request event."""
        with self.lock:
            event = RequestEvent(
                timestamp=time.time(),
                endpoint_type=endpoint_type,
                processing_time=processing_time,
                success=success,
                input_length=input_length,
                audio_length_seconds=audio_length_seconds,
                memory_usage_gb=memory_usage_gb,
                request_id=request_id,
            )

            self.request_events.append(event)

            # Update counters
            self.counters["total_requests"] += 1
            self.endpoint_counters[endpoint_type] += 1

            if success:
                self.counters["successful_requests"] += 1
            else:
                self.counters["failed_requests"] += 1

            # Track response times
            self.response_times[endpoint_type].append(processing_time)
            if len(self.response_times[endpoint_type]) > 100:  # Keep only recent 100
                self.response_times[endpoint_type] = self.response_times[endpoint_type][-100:]

    def log_error(
        self,
        error_type: str,
        error_message: str,
        endpoint_type: str,
        stack_trace: Optional[str] = None,
        user_input_length: Optional[int] = None,
        request_id: Optional[str] = None,
    ):
        """Log an error event."""
        with self.lock:
            event = ErrorEvent(
                timestamp=time.time(),
                error_type=error_type,
                error_message=error_message,
                endpoint_type=endpoint_type,
                stack_trace=stack_trace,
                user_input_length=user_input_length,
                request_id=request_id,
            )

            self.error_events.append(event)
            self.error_counters[error_type] += 1
            self.counters["total_errors"] += 1

            # Log to standard logger as well
            logger.error(f"Error in {endpoint_type}: {error_type} - {error_message}")

    def log_health_check(self, health_data: Dict[str, Any]):
        """Log a health check event."""
        with self.lock:
            health = SystemHealth(
                timestamp=time.time(),
                gpu_memory_usage_percent=health_data.get("gpu_memory_usage_percent", 0),
                cpu_usage_percent=health_data.get("cpu_usage_percent", 0),
                system_memory_usage_percent=health_data.get("system_memory_usage_percent", 0),
                disk_usage_percent=health_data.get("disk_usage_percent", 0),
                models_loaded=health_data.get("models_loaded", False),
                total_requests=self.counters["total_requests"],
                error_rate_1h=self.get_error_rate(hours=1),
                avg_response_time_1h=self.get_average_response_time(hours=1),
            )

            self.health_checks.append(health)

    def get_error_rate(self, hours: int = 1) -> float:
        """Get error rate for the last N hours."""
        cutoff_time = time.time() - (hours * 3600)

        with self.lock:
            recent_requests = [e for e in self.request_events if e.timestamp >= cutoff_time]
            if not recent_requests:
                return 0.0

            failed_requests = sum(1 for e in recent_requests if not e.success)
            return (failed_requests / len(recent_requests)) * 100

    def get_average_response_time(self, hours: int = 1, endpoint_type: Optional[str] = None) -> float:
        """Get average response time for the last N hours."""
        cutoff_time = time.time() - (hours * 3600)

        with self.lock:
            recent_requests = [e for e in self.request_events if e.timestamp >= cutoff_time]
            if endpoint_type:
                recent_requests = [e for e in recent_requests if e.endpoint_type == endpoint_type]

            if not recent_requests:
                return 0.0

            return sum(e.processing_time for e in recent_requests) / len(recent_requests)

    def get_endpoint_stats(self) -> Dict[str, Any]:
        """Get statistics by endpoint type."""
        stats = {}

        with self.lock:
            for endpoint in self.endpoint_counters:
                endpoint_events = [e for e in self.request_events if e.endpoint_type == endpoint]
                if endpoint_events:
                    successful = sum(1 for e in endpoint_events if e.success)
                    avg_time = sum(e.processing_time for e in endpoint_events) / len(endpoint_events)

                    stats[endpoint] = {
                        "total_requests": len(endpoint_events),
                        "successful_requests": successful,
                        "success_rate": (successful / len(endpoint_events)) * 100,
                        "average_response_time": avg_time,
                        "recent_response_time": self.get_average_response_time(hours=1, endpoint_type=endpoint),
                    }

        return stats

    def get_recent_errors(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent error events."""
        cutoff_time = time.time() - (hours * 3600)

        with self.lock:
            recent_errors = [e for e in self.error_events if e.timestamp >= cutoff_time]
            return [asdict(e) for e in recent_errors]

    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours."""
        recent_errors = self.get_recent_errors(hours)

        error_types = defaultdict(int)
        endpoints = defaultdict(int)

        for error in recent_errors:
            error_types[error["error_type"]] += 1
            endpoints[error["endpoint_type"]] += 1

        return {
            "total_errors": len(recent_errors),
            "error_types": dict(error_types),
            "endpoints_with_errors": dict(endpoints),
            "error_rate": self.get_error_rate(hours),
        }

    def check_alerts(self) -> List[str]:
        """Check for alert conditions."""
        alerts = []

        # High error rate alert
        error_rate_1h = self.get_error_rate(1)
        if error_rate_1h > 10:  # >10% error rate
            alerts.append(f"HIGH ERROR RATE: {error_rate_1h:.1f}% in last hour")
        elif error_rate_1h > 5:  # >5% error rate
            alerts.append(f"Elevated error rate: {error_rate_1h:.1f}% in last hour")

        # Slow response time alert
        avg_response_time = self.get_average_response_time(1)
        if avg_response_time > 30:  # >30 seconds
            alerts.append(f"SLOW RESPONSE: {avg_response_time:.1f}s average in last hour")
        elif avg_response_time > 15:  # >15 seconds
            alerts.append(f"Elevated response time: {avg_response_time:.1f}s average in last hour")

        # Recent errors alert
        recent_errors = self.get_recent_errors(1)
        if len(recent_errors) > 50:  # >50 errors in last hour
            alerts.append(f"HIGH ERROR COUNT: {len(recent_errors)} errors in last hour")

        return alerts

    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get comprehensive monitoring summary."""
        with self.lock:
            return {
                "timestamp": time.time(),
                "counters": dict(self.counters),
                "endpoint_stats": self.get_endpoint_stats(),
                "error_summary_24h": self.get_error_summary(24),
                "error_summary_1h": self.get_error_summary(1),
                "recent_alerts": self.check_alerts(),
                "health_status": {
                    "error_rate_1h": self.get_error_rate(1),
                    "avg_response_time_1h": self.get_average_response_time(1),
                    "total_requests": self.counters["total_requests"],
                    "total_errors": self.counters["total_errors"],
                },
            }

    def export_metrics(self, filename: Optional[str] = None) -> str:
        """Export metrics to JSON file."""
        summary = self.get_monitoring_summary()

        if filename is None:
            timestamp = int(time.time())
            filename = f"/tmp/higgs_audio_metrics_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Metrics exported to {filename}")
        return filename


class AlertManager:
    """Manage alerts and notifications."""

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("ALERT_WEBHOOK_URL")
        self.alert_cooldown = 300  # 5 minutes
        self.last_alerts = {}

    def should_send_alert(self, alert_type: str) -> bool:
        """Check if alert should be sent (cooldown management)."""
        last_sent = self.last_alerts.get(alert_type, 0)
        return time.time() - last_sent > self.alert_cooldown

    def send_alert(self, alert_message: str, alert_type: str = "general"):
        """Send alert notification."""
        if not self.should_send_alert(alert_type):
            return

        logger.warning(f"ALERT [{alert_type}]: {alert_message}")

        # Update last sent time
        self.last_alerts[alert_type] = time.time()

        # Send webhook if configured
        if self.webhook_url:
            try:
                import requests

                payload = {"text": f"🚨 Higgs Audio Alert [{alert_type}]: {alert_message}", "timestamp": time.time()}
                requests.post(self.webhook_url, json=payload, timeout=10)
                logger.info(f"Alert sent to webhook: {alert_type}")
            except Exception as e:
                logger.error(f"Failed to send webhook alert: {e}")


# Global monitoring instances
production_monitor = ProductionMonitor()
alert_manager = AlertManager()


def monitor_request(endpoint_type: str, processing_time: float, success: bool, input_length: int, **kwargs):
    """Monitor a request (convenience function)."""
    production_monitor.log_request(endpoint_type, processing_time, success, input_length, **kwargs)


def monitor_error(error_type: str, error_message: str, endpoint_type: str, **kwargs):
    """Monitor an error (convenience function)."""
    production_monitor.log_error(error_type, error_message, endpoint_type, **kwargs)

    # Send alert for critical errors
    if "out of memory" in error_message.lower() or "cuda" in error_message.lower():
        alert_manager.send_alert(f"Critical error in {endpoint_type}: {error_message}", "critical")


def get_monitoring_dashboard() -> Dict[str, Any]:
    """Get monitoring dashboard data."""
    summary = production_monitor.get_monitoring_summary()

    # Add alerts
    alerts = production_monitor.check_alerts()
    for alert in alerts:
        if "HIGH" in alert or "SLOW" in alert:
            alert_manager.send_alert(alert, "performance")

    return summary
