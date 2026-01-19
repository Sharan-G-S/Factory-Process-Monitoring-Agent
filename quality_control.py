"""
Quality Control System
Manages quality metrics, defect tracking, and quality analysis
"""

import random
from typing import Dict, List
from data_models import QualityMetrics, ProductionLine


class QualityControl:
    """Quality control and analysis system"""
    
    def __init__(self):
        self.defect_categories = [
            "Dimensional Error",
            "Surface Defect",
            "Assembly Error",
            "Material Defect",
            "Packaging Error"
        ]
        self.historical_defect_rates = {}
    
    def analyze_quality(self, line: ProductionLine) -> QualityMetrics:
        """Analyze quality metrics for a production line"""
        total_inspected = line.products_produced
        failed = line.defects
        passed = total_inspected - failed
        
        defect_rate = (failed / total_inspected * 100) if total_inspected > 0 else 0
        
        # Generate defect type distribution
        defect_types = self._generate_defect_distribution(failed)
        
        # Calculate quality score (0-100)
        quality_score = max(0, 100 - defect_rate * 10)
        
        # Determine trend
        trend = self._calculate_trend(line.line_id, defect_rate)
        
        metrics = QualityMetrics(
            line_id=line.line_id,
            total_inspected=total_inspected,
            passed=passed,
            failed=failed,
            defect_rate=round(defect_rate, 2),
            defect_types=defect_types,
            average_quality_score=round(quality_score, 2),
            trend=trend
        )
        
        return metrics
    
    def _generate_defect_distribution(self, total_defects: int) -> Dict[str, int]:
        """Generate realistic defect type distribution"""
        if total_defects == 0:
            return {category: 0 for category in self.defect_categories}
        
        distribution = {}
        remaining = total_defects
        
        # Weighted distribution (some defects more common than others)
        weights = [0.35, 0.25, 0.20, 0.15, 0.05]
        
        for i, category in enumerate(self.defect_categories[:-1]):
            count = int(total_defects * weights[i])
            distribution[category] = count
            remaining -= count
        
        # Assign remaining to last category
        distribution[self.defect_categories[-1]] = max(0, remaining)
        
        return distribution
    
    def _calculate_trend(self, line_id: str, current_rate: float) -> str:
        """Calculate quality trend based on historical data"""
        if line_id not in self.historical_defect_rates:
            self.historical_defect_rates[line_id] = []
        
        history = self.historical_defect_rates[line_id]
        history.append(current_rate)
        
        # Keep last 10 readings
        if len(history) > 10:
            history.pop(0)
        
        if len(history) < 3:
            return "stable"
        
        # Calculate trend from last 5 readings
        recent = history[-5:]
        avg_old = sum(recent[:2]) / 2
        avg_new = sum(recent[-2:]) / 2
        
        if avg_new < avg_old * 0.9:
            return "improving"
        elif avg_new > avg_old * 1.1:
            return "declining"
        else:
            return "stable"
    
    def get_all_quality_metrics(self, production_lines: List[ProductionLine]) -> List[Dict]:
        """Get quality metrics for all production lines"""
        metrics = []
        for line in production_lines:
            quality_metrics = self.analyze_quality(line)
            metrics.append(quality_metrics.to_dict())
        return metrics
    
    def get_quality_summary(self, production_lines: List[ProductionLine]) -> Dict:
        """Get overall quality summary"""
        all_metrics = self.get_all_quality_metrics(production_lines)
        
        total_inspected = sum(m['total_inspected'] for m in all_metrics)
        total_failed = sum(m['failed'] for m in all_metrics)
        
        overall_defect_rate = (total_failed / total_inspected * 100) if total_inspected > 0 else 0
        avg_quality_score = sum(m['average_quality_score'] for m in all_metrics) / len(all_metrics) if all_metrics else 0
        
        # Aggregate defect types
        all_defect_types = {}
        for metrics in all_metrics:
            for defect_type, count in metrics['defect_types'].items():
                all_defect_types[defect_type] = all_defect_types.get(defect_type, 0) + count
        
        return {
            "total_inspected": total_inspected,
            "total_passed": total_inspected - total_failed,
            "total_failed": total_failed,
            "overall_defect_rate": round(overall_defect_rate, 2),
            "average_quality_score": round(avg_quality_score, 2),
            "defect_distribution": all_defect_types,
            "lines_with_issues": sum(1 for m in all_metrics if m['defect_rate'] > 5.0)
        }
