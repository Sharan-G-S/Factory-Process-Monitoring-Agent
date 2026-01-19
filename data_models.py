"""
Data models for Factory Process Monitoring Agent
Defines data structures for production lines, quality metrics, and alerts
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class LineStatus(Enum):
    """Production line status enumeration"""
    RUNNING = "running"
    IDLE = "idle"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ProductionLine:
    """Production line data model"""
    line_id: str
    name: str
    status: str
    current_speed: float  # units per minute
    target_speed: float
    efficiency: float  # percentage
    uptime: float  # percentage
    temperature: float  # celsius
    pressure: float  # bar
    vibration: float  # mm/s
    products_produced: int
    defects: int
    last_maintenance: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class QualityMetrics:
    """Quality control metrics"""
    line_id: str
    total_inspected: int
    passed: int
    failed: int
    defect_rate: float  # percentage
    defect_types: Dict[str, int]
    average_quality_score: float
    trend: str  # "improving", "stable", "declining"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Alert:
    """Alert/notification model"""
    alert_id: str
    line_id: str
    severity: str
    title: str
    message: str
    timestamp: str
    acknowledged: bool = False
    resolved: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ProductionMetrics:
    """Overall production metrics"""
    total_output: int
    total_defects: int
    overall_oee: float  # Overall Equipment Effectiveness
    average_efficiency: float
    active_lines: int
    total_lines: int
    critical_alerts: int
    warning_alerts: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class MachineHealth:
    """Machine health monitoring data"""
    line_id: str
    health_score: float  # 0-100
    temperature_status: str  # "normal", "warning", "critical"
    pressure_status: str
    vibration_status: str
    predicted_maintenance_hours: int
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
