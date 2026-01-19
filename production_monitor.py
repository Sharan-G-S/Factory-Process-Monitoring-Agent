"""
Production Line Monitor
Simulates and monitors production line data with realistic metrics
"""

import random
import time
from datetime import datetime, timedelta
from typing import List, Dict
from data_models import ProductionLine, LineStatus, ProductionMetrics


class ProductionMonitor:
    """Manages production line monitoring and simulation"""
    
    def __init__(self):
        self.production_lines = self._initialize_lines()
        self.start_time = datetime.now()
        
    def _initialize_lines(self) -> List[ProductionLine]:
        """Initialize production lines with default values"""
        lines = []
        line_configs = [
            {"id": "LINE-A1", "name": "Assembly Line A1", "target": 120.0},
            {"id": "LINE-A2", "name": "Assembly Line A2", "target": 120.0},
            {"id": "LINE-B1", "name": "Packaging Line B1", "target": 200.0},
            {"id": "LINE-C1", "name": "Quality Check C1", "target": 150.0},
        ]
        
        for config in line_configs:
            line = ProductionLine(
                line_id=config["id"],
                name=config["name"],
                status=LineStatus.RUNNING.value,
                current_speed=config["target"] * random.uniform(0.85, 1.0),
                target_speed=config["target"],
                efficiency=random.uniform(85, 98),
                uptime=random.uniform(92, 99),
                temperature=random.uniform(20, 35),
                pressure=random.uniform(5.5, 6.5),
                vibration=random.uniform(0.5, 2.0),
                products_produced=random.randint(5000, 15000),
                defects=random.randint(50, 200),
                last_maintenance=(datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
            )
            lines.append(line)
        
        return lines
    
    def update_production_data(self):
        """Update production line data with realistic variations"""
        for line in self.production_lines:
            # Simulate realistic variations
            if line.status == LineStatus.RUNNING.value:
                # Speed variation
                speed_change = random.uniform(-5, 5)
                line.current_speed = max(0, min(line.target_speed * 1.1, 
                                                line.current_speed + speed_change))
                
                # Efficiency calculation
                line.efficiency = (line.current_speed / line.target_speed) * 100
                line.efficiency = max(70, min(100, line.efficiency + random.uniform(-2, 2)))
                
                # Environmental parameters
                line.temperature += random.uniform(-1, 1)
                line.temperature = max(18, min(45, line.temperature))
                
                line.pressure += random.uniform(-0.2, 0.2)
                line.pressure = max(5.0, min(7.0, line.pressure))
                
                line.vibration += random.uniform(-0.3, 0.3)
                line.vibration = max(0.3, min(4.0, line.vibration))
                
                # Production counts
                units_produced = int(line.current_speed / 60 * 5)  # 5 second intervals
                line.products_produced += units_produced
                
                # Defect simulation (higher chance with worse conditions)
                defect_probability = 0.02
                if line.temperature > 38:
                    defect_probability += 0.03
                if line.vibration > 3.0:
                    defect_probability += 0.02
                if line.efficiency < 80:
                    defect_probability += 0.02
                    
                if random.random() < defect_probability:
                    line.defects += random.randint(1, 3)
                
                # Random status changes (rare)
                if random.random() < 0.01:  # 1% chance
                    line.status = random.choice([
                        LineStatus.RUNNING.value,
                        LineStatus.IDLE.value,
                        LineStatus.MAINTENANCE.value
                    ])
            
            elif line.status == LineStatus.IDLE.value:
                line.current_speed = 0
                # Chance to resume
                if random.random() < 0.3:
                    line.status = LineStatus.RUNNING.value
                    
            elif line.status == LineStatus.MAINTENANCE.value:
                line.current_speed = 0
                # Chance to complete maintenance
                if random.random() < 0.1:
                    line.status = LineStatus.RUNNING.value
                    line.last_maintenance = datetime.now().strftime("%Y-%m-%d")
    
    def get_production_lines(self) -> List[Dict]:
        """Get current production line data"""
        return [line.to_dict() for line in self.production_lines]
    
    def get_line_by_id(self, line_id: str) -> ProductionLine:
        """Get specific production line by ID"""
        for line in self.production_lines:
            if line.line_id == line_id:
                return line
        return None
    
    def get_overall_metrics(self) -> Dict:
        """Calculate overall production metrics"""
        total_output = sum(line.products_produced for line in self.production_lines)
        total_defects = sum(line.defects for line in self.production_lines)
        avg_efficiency = sum(line.efficiency for line in self.production_lines) / len(self.production_lines)
        
        # Calculate OEE (Overall Equipment Effectiveness)
        # OEE = Availability × Performance × Quality
        avg_uptime = sum(line.uptime for line in self.production_lines) / len(self.production_lines)
        avg_performance = avg_efficiency
        quality_rate = ((total_output - total_defects) / total_output * 100) if total_output > 0 else 100
        oee = (avg_uptime / 100) * (avg_performance / 100) * (quality_rate / 100) * 100
        
        active_lines = sum(1 for line in self.production_lines if line.status == LineStatus.RUNNING.value)
        
        metrics = ProductionMetrics(
            total_output=total_output,
            total_defects=total_defects,
            overall_oee=round(oee, 2),
            average_efficiency=round(avg_efficiency, 2),
            active_lines=active_lines,
            total_lines=len(self.production_lines),
            critical_alerts=0,  # Will be updated by anomaly detector
            warning_alerts=0
        )
        
        return metrics.to_dict()
    
    def calculate_oee(self, line: ProductionLine) -> float:
        """Calculate OEE for a specific line"""
        availability = line.uptime / 100
        performance = line.efficiency / 100
        quality = ((line.products_produced - line.defects) / line.products_produced) if line.products_produced > 0 else 1.0
        return round(availability * performance * quality * 100, 2)
