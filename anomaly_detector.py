"""
Anomaly Detection System
Detects anomalies in production data and generates alerts
"""

import random
from datetime import datetime
from typing import List, Dict
from data_models import ProductionLine, Alert, AlertSeverity, MachineHealth


class AnomalyDetector:
    """Detects anomalies and generates alerts"""
    
    def __init__(self):
        self.alerts = []
        self.alert_counter = 0
        self.thresholds = {
            "temperature": {"warning": 38, "critical": 42},
            "pressure": {"warning_low": 5.2, "warning_high": 6.8, "critical_low": 5.0, "critical_high": 7.0},
            "vibration": {"warning": 3.0, "critical": 3.5},
            "efficiency": {"warning": 75, "critical": 65},
            "defect_rate": {"warning": 5.0, "critical": 8.0}
        }
    
    def detect_anomalies(self, line: ProductionLine) -> List[Alert]:
        """Detect anomalies in production line data"""
        new_alerts = []
        
        # Temperature anomalies
        if line.temperature >= self.thresholds["temperature"]["critical"]:
            new_alerts.append(self._create_alert(
                line.line_id,
                AlertSeverity.CRITICAL.value,
                "Critical Temperature",
                f"Temperature at {line.temperature:.1f}°C exceeds critical threshold"
            ))
        elif line.temperature >= self.thresholds["temperature"]["warning"]:
            new_alerts.append(self._create_alert(
                line.line_id,
                AlertSeverity.WARNING.value,
                "High Temperature",
                f"Temperature at {line.temperature:.1f}°C above normal range"
            ))
        
        # Pressure anomalies
        if line.pressure <= self.thresholds["pressure"]["critical_low"] or \
           line.pressure >= self.thresholds["pressure"]["critical_high"]:
            new_alerts.append(self._create_alert(
                line.line_id,
                AlertSeverity.CRITICAL.value,
                "Critical Pressure",
                f"Pressure at {line.pressure:.1f} bar outside safe operating range"
            ))
        elif line.pressure <= self.thresholds["pressure"]["warning_low"] or \
             line.pressure >= self.thresholds["pressure"]["warning_high"]:
            new_alerts.append(self._create_alert(
                line.line_id,
                AlertSeverity.WARNING.value,
                "Pressure Deviation",
                f"Pressure at {line.pressure:.1f} bar deviating from optimal range"
            ))
        
        # Vibration anomalies
        if line.vibration >= self.thresholds["vibration"]["critical"]:
            new_alerts.append(self._create_alert(
                line.line_id,
                AlertSeverity.CRITICAL.value,
                "Excessive Vibration",
                f"Vibration at {line.vibration:.1f} mm/s indicates potential mechanical failure"
            ))
        elif line.vibration >= self.thresholds["vibration"]["warning"]:
            new_alerts.append(self._create_alert(
                line.line_id,
                AlertSeverity.WARNING.value,
                "High Vibration",
                f"Vibration at {line.vibration:.1f} mm/s above normal levels"
            ))
        
        # Efficiency anomalies
        if line.efficiency <= self.thresholds["efficiency"]["critical"]:
            new_alerts.append(self._create_alert(
                line.line_id,
                AlertSeverity.CRITICAL.value,
                "Critical Efficiency Drop",
                f"Efficiency at {line.efficiency:.1f}% requires immediate attention"
            ))
        elif line.efficiency <= self.thresholds["efficiency"]["warning"]:
            new_alerts.append(self._create_alert(
                line.line_id,
                AlertSeverity.WARNING.value,
                "Low Efficiency",
                f"Efficiency at {line.efficiency:.1f}% below target"
            ))
        
        # Status-based alerts
        if line.status == "error":
            new_alerts.append(self._create_alert(
                line.line_id,
                AlertSeverity.CRITICAL.value,
                "Line Error",
                f"Production line {line.name} has encountered an error"
            ))
        elif line.status == "maintenance":
            new_alerts.append(self._create_alert(
                line.line_id,
                AlertSeverity.INFO.value,
                "Maintenance Mode",
                f"Production line {line.name} is under maintenance"
            ))
        
        # Add new alerts to the list
        self.alerts.extend(new_alerts)
        
        # Keep only recent alerts (last 50)
        if len(self.alerts) > 50:
            self.alerts = self.alerts[-50:]
        
        return new_alerts
    
    def detect_quality_anomalies(self, quality_metrics: Dict) -> List[Alert]:
        """Detect quality-related anomalies"""
        new_alerts = []
        
        defect_rate = quality_metrics.get('defect_rate', 0)
        line_id = quality_metrics.get('line_id', 'UNKNOWN')
        
        if defect_rate >= self.thresholds["defect_rate"]["critical"]:
            new_alerts.append(self._create_alert(
                line_id,
                AlertSeverity.CRITICAL.value,
                "Critical Defect Rate",
                f"Defect rate at {defect_rate:.1f}% exceeds acceptable limits"
            ))
        elif defect_rate >= self.thresholds["defect_rate"]["warning"]:
            new_alerts.append(self._create_alert(
                line_id,
                AlertSeverity.WARNING.value,
                "High Defect Rate",
                f"Defect rate at {defect_rate:.1f}% above target"
            ))
        
        if quality_metrics.get('trend') == 'declining':
            new_alerts.append(self._create_alert(
                line_id,
                AlertSeverity.WARNING.value,
                "Quality Declining",
                "Quality metrics show declining trend"
            ))
        
        self.alerts.extend(new_alerts)
        return new_alerts
    
    def _create_alert(self, line_id: str, severity: str, title: str, message: str) -> Alert:
        """Create a new alert"""
        self.alert_counter += 1
        alert = Alert(
            alert_id=f"ALT-{self.alert_counter:05d}",
            line_id=line_id,
            severity=severity,
            title=title,
            message=message,
            timestamp=datetime.now().isoformat(),
            acknowledged=False,
            resolved=False
        )
        return alert
    
    def get_active_alerts(self) -> List[Dict]:
        """Get all active (unresolved) alerts"""
        active = [alert for alert in self.alerts if not alert.resolved]
        return [alert.to_dict() for alert in active]
    
    def get_alert_counts(self) -> Dict[str, int]:
        """Get count of alerts by severity"""
        active = [alert for alert in self.alerts if not alert.resolved]
        return {
            "critical": sum(1 for a in active if a.severity == AlertSeverity.CRITICAL.value),
            "warning": sum(1 for a in active if a.severity == AlertSeverity.WARNING.value),
            "info": sum(1 for a in active if a.severity == AlertSeverity.INFO.value)
        }
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                return True
        return False
    
    def assess_machine_health(self, line: ProductionLine) -> MachineHealth:
        """Assess overall machine health"""
        health_score = 100.0
        recommendations = []
        
        # Temperature assessment
        temp_status = "normal"
        if line.temperature >= self.thresholds["temperature"]["critical"]:
            temp_status = "critical"
            health_score -= 30
            recommendations.append("Immediate cooling system inspection required")
        elif line.temperature >= self.thresholds["temperature"]["warning"]:
            temp_status = "warning"
            health_score -= 10
            recommendations.append("Monitor cooling system")
        
        # Pressure assessment
        pressure_status = "normal"
        if line.pressure <= self.thresholds["pressure"]["critical_low"] or \
           line.pressure >= self.thresholds["pressure"]["critical_high"]:
            pressure_status = "critical"
            health_score -= 30
            recommendations.append("Critical pressure adjustment needed")
        elif line.pressure <= self.thresholds["pressure"]["warning_low"] or \
             line.pressure >= self.thresholds["pressure"]["warning_high"]:
            pressure_status = "warning"
            health_score -= 10
            recommendations.append("Pressure calibration recommended")
        
        # Vibration assessment
        vibration_status = "normal"
        if line.vibration >= self.thresholds["vibration"]["critical"]:
            vibration_status = "critical"
            health_score -= 35
            recommendations.append("Immediate mechanical inspection required")
        elif line.vibration >= self.thresholds["vibration"]["warning"]:
            vibration_status = "warning"
            health_score -= 15
            recommendations.append("Schedule bearing inspection")
        
        # Efficiency impact
        if line.efficiency < 80:
            health_score -= 10
            recommendations.append("Performance optimization needed")
        
        # Predict maintenance hours (simplified model)
        predicted_hours = int(200 - (100 - health_score) * 10)
        predicted_hours = max(24, predicted_hours)
        
        if not recommendations:
            recommendations.append("All systems operating normally")
        
        health = MachineHealth(
            line_id=line.line_id,
            health_score=max(0, round(health_score, 1)),
            temperature_status=temp_status,
            pressure_status=pressure_status,
            vibration_status=vibration_status,
            predicted_maintenance_hours=predicted_hours,
            recommendations=recommendations
        )
        
        return health
