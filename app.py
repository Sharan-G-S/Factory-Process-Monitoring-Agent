"""
Factory Process Monitoring Agent - Main Application
Flask server with real-time WebSocket updates
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
import time
from datetime import datetime
from production_monitor import ProductionMonitor
from quality_control import QualityControl
from anomaly_detector import AnomalyDetector
from report_generator import ReportGenerator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'factory-monitoring-secret-key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize monitoring systems
production_monitor = ProductionMonitor()
quality_control = QualityControl()
anomaly_detector = AnomalyDetector()
report_generator = ReportGenerator()

# Background thread for real-time updates
update_thread = None
update_thread_running = False


def background_update_task():
    """Background task to update production data and emit to clients"""
    global update_thread_running
    
    while update_thread_running:
        # Update production data
        production_monitor.update_production_data()
        
        # Get current data
        production_lines = production_monitor.get_production_lines()
        overall_metrics = production_monitor.get_overall_metrics()
        quality_metrics = quality_control.get_all_quality_metrics(production_monitor.production_lines)
        quality_summary = quality_control.get_quality_summary(production_monitor.production_lines)
        
        # Detect anomalies
        new_alerts = []
        machine_health_data = []
        
        for line in production_monitor.production_lines:
            alerts = anomaly_detector.detect_anomalies(line)
            new_alerts.extend(alerts)
            
            # Get machine health
            health = anomaly_detector.assess_machine_health(line)
            machine_health_data.append(health.to_dict())
        
        # Check quality anomalies
        for qm in quality_metrics:
            quality_alerts = anomaly_detector.detect_quality_anomalies(qm)
            new_alerts.extend(quality_alerts)
        
        # Update overall metrics with alert counts
        alert_counts = anomaly_detector.get_alert_counts()
        overall_metrics['critical_alerts'] = alert_counts['critical']
        overall_metrics['warning_alerts'] = alert_counts['warning']
        
        # Emit updates to all connected clients
        socketio.emit('production_update', {
            'production_lines': production_lines,
            'overall_metrics': overall_metrics,
            'quality_metrics': quality_metrics,
            'quality_summary': quality_summary,
            'alerts': anomaly_detector.get_active_alerts(),
            'alert_counts': alert_counts,
            'machine_health': machine_health_data
        })
        
        # Update every 3 seconds
        time.sleep(3)


@app.route('/')
def index():
    """Serve the main dashboard"""
    return render_template('index.html')


@app.route('/api/production-lines')
def get_production_lines():
    """Get current production line data"""
    return jsonify(production_monitor.get_production_lines())


@app.route('/api/production-lines/<line_id>')
def get_production_line(line_id):
    """Get specific production line data"""
    line = production_monitor.get_line_by_id(line_id)
    if line:
        return jsonify(line.to_dict())
    return jsonify({"error": "Line not found"}), 404


@app.route('/api/overall-metrics')
def get_overall_metrics():
    """Get overall production metrics"""
    metrics = production_monitor.get_overall_metrics()
    alert_counts = anomaly_detector.get_alert_counts()
    metrics['critical_alerts'] = alert_counts['critical']
    metrics['warning_alerts'] = alert_counts['warning']
    return jsonify(metrics)


@app.route('/api/quality-metrics')
def get_quality_metrics():
    """Get quality metrics for all lines"""
    metrics = quality_control.get_all_quality_metrics(production_monitor.production_lines)
    return jsonify(metrics)


@app.route('/api/quality-summary')
def get_quality_summary():
    """Get overall quality summary"""
    summary = quality_control.get_quality_summary(production_monitor.production_lines)
    return jsonify(summary)


@app.route('/api/alerts')
def get_alerts():
    """Get all active alerts"""
    return jsonify(anomaly_detector.get_active_alerts())


@app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    success = anomaly_detector.acknowledge_alert(alert_id)
    if success:
        return jsonify({"status": "acknowledged"})
    return jsonify({"error": "Alert not found"}), 404


@app.route('/api/alerts/<alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """Resolve an alert"""
    success = anomaly_detector.resolve_alert(alert_id)
    if success:
        return jsonify({"status": "resolved"})
    return jsonify({"error": "Alert not found"}), 404


@app.route('/api/machine-health')
def get_machine_health():
    """Get machine health for all lines"""
    health_data = []
    for line in production_monitor.production_lines:
        health = anomaly_detector.assess_machine_health(line)
        health_data.append(health.to_dict())
    return jsonify(health_data)


@app.route('/api/machine-health/<line_id>')
def get_line_health(line_id):
    """Get machine health for specific line"""
    line = production_monitor.get_line_by_id(line_id)
    if line:
        health = anomaly_detector.assess_machine_health(line)
        return jsonify(health.to_dict())
    return jsonify({"error": "Line not found"}), 404


@app.route('/api/analytics')
def get_analytics():
    """Get analytics data"""
    production_lines = production_monitor.production_lines
    
    # Calculate analytics
    analytics = {
        "production_by_line": [
            {
                "line_id": line.line_id,
                "name": line.name,
                "output": line.products_produced,
                "defects": line.defects,
                "efficiency": line.efficiency
            }
            for line in production_lines
        ],
        "efficiency_trends": [
            {
                "line_id": line.line_id,
                "current_efficiency": line.efficiency,
                "target": 90.0,
                "oee": production_monitor.calculate_oee(line)
            }
            for line in production_lines
        ],
        "quality_by_line": quality_control.get_all_quality_metrics(production_lines)
    }
    
    return jsonify(analytics)


@app.route('/api/export/pdf')
def export_pdf():
    """Export production report as PDF"""
    production_lines = production_monitor.get_production_lines()
    quality_metrics = quality_control.get_all_quality_metrics(production_monitor.production_lines)
    overall_metrics = production_monitor.get_overall_metrics()
    alert_counts = anomaly_detector.get_alert_counts()
    overall_metrics['critical_alerts'] = alert_counts['critical']
    overall_metrics['warning_alerts'] = alert_counts['warning']
    alerts = anomaly_detector.get_active_alerts()
    
    pdf_buffer = report_generator.generate_pdf_report(
        production_lines, quality_metrics, overall_metrics, alerts
    )
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'factory_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    )


@app.route('/api/export/excel')
def export_excel():
    """Export production report as Excel"""
    production_lines = production_monitor.get_production_lines()
    quality_metrics = quality_control.get_all_quality_metrics(production_monitor.production_lines)
    overall_metrics = production_monitor.get_overall_metrics()
    alert_counts = anomaly_detector.get_alert_counts()
    overall_metrics['critical_alerts'] = alert_counts['critical']
    overall_metrics['warning_alerts'] = alert_counts['warning']
    alerts = anomaly_detector.get_active_alerts()
    
    excel_buffer = report_generator.generate_excel_report(
        production_lines, quality_metrics, overall_metrics, alerts
    )
    
    return send_file(
        excel_buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'factory_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    global update_thread, update_thread_running
    
    print('Client connected')
    
    # Start background update thread if not running
    if update_thread is None or not update_thread_running:
        update_thread_running = True
        update_thread = threading.Thread(target=background_update_task)
        update_thread.daemon = True
        update_thread.start()
    
    # Send initial data
    emit('production_update', {
        'production_lines': production_monitor.get_production_lines(),
        'overall_metrics': production_monitor.get_overall_metrics(),
        'quality_metrics': quality_control.get_all_quality_metrics(production_monitor.production_lines),
        'quality_summary': quality_control.get_quality_summary(production_monitor.production_lines),
        'alerts': anomaly_detector.get_active_alerts(),
        'alert_counts': anomaly_detector.get_alert_counts(),
        'machine_health': [anomaly_detector.assess_machine_health(line).to_dict() 
                          for line in production_monitor.production_lines]
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


if __name__ == '__main__':
    print("=" * 60)
    print("Factory Process Monitoring Agent")
    print("=" * 60)
    print("Starting server on http://localhost:5001")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, use_reloader=False)
