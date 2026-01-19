/**
 * Factory Process Monitoring Agent - Frontend JavaScript
 * Handles real-time updates via WebSocket and UI interactions
 */

// Initialize Socket.IO connection
const socket = io();

// Chart instances
let productionChart = null;
let qualityChart = null;
let efficiencyChart = null;

// Current filter for alerts
let currentAlertFilter = 'all';

// Connection status handling
socket.on('connect', () => {
    updateConnectionStatus(true);
    console.log('Connected to server');
});

socket.on('disconnect', () => {
    updateConnectionStatus(false);
    console.log('Disconnected from server');
});

// Real-time production updates
socket.on('production_update', (data) => {
    updateLastUpdateTime();
    updateOverallMetrics(data.overall_metrics);
    updateProductionLines(data.production_lines);
    updateAlerts(data.alerts, data.alert_counts);
    updateMachineHealth(data.machine_health);
    updateCharts(data);
});

/**
 * Update connection status indicator
 */
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connectionStatus');
    const statusDot = statusElement.querySelector('.status-dot');
    const statusText = statusElement.querySelector('.status-text');

    if (connected) {
        statusElement.style.background = 'rgba(16, 185, 129, 0.1)';
        statusElement.style.borderColor = 'rgba(16, 185, 129, 0.3)';
        statusText.textContent = 'Connected';
        statusText.style.color = '#10b981';
    } else {
        statusElement.style.background = 'rgba(239, 68, 68, 0.1)';
        statusElement.style.borderColor = 'rgba(239, 68, 68, 0.3)';
        statusText.textContent = 'Disconnected';
        statusText.style.color = '#ef4444';
    }
}

/**
 * Update last update timestamp
 */
function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById('lastUpdate').textContent = `Last update: ${timeString}`;
}

/**
 * Update overall metrics cards
 */
function updateOverallMetrics(metrics) {
    document.getElementById('totalOutput').textContent = metrics.total_output.toLocaleString();
    document.getElementById('overallOEE').textContent = `${metrics.overall_oee}%`;
    document.getElementById('qualityScore').textContent = `${(100 - (metrics.total_defects / metrics.total_output * 100)).toFixed(1)}%`;
    document.getElementById('activeAlerts').textContent = metrics.critical_alerts + metrics.warning_alerts;
    document.getElementById('activeLinesCount').textContent = `${metrics.active_lines}/${metrics.total_lines} Active`;

    // Update alert breakdown
    document.getElementById('alertBreakdown').textContent =
        `${metrics.critical_alerts} critical, ${metrics.warning_alerts} warning`;

    // Update OEE change indicator
    const oeeChange = document.getElementById('oeeChange');
    if (metrics.overall_oee >= 85) {
        oeeChange.textContent = 'Excellent';
        oeeChange.className = 'metric-change positive';
    } else if (metrics.overall_oee >= 70) {
        oeeChange.textContent = 'Good';
        oeeChange.className = 'metric-change';
    } else {
        oeeChange.textContent = 'Needs Improvement';
        oeeChange.className = 'metric-change negative';
    }

    // Update quality change indicator
    const qualityChange = document.getElementById('qualityChange');
    const qualityScore = 100 - (metrics.total_defects / metrics.total_output * 100);
    if (qualityScore >= 95) {
        qualityChange.textContent = 'Excellent';
        qualityChange.className = 'metric-change positive';
    } else if (qualityScore >= 90) {
        qualityChange.textContent = 'Good';
        qualityChange.className = 'metric-change';
    } else {
        qualityChange.textContent = 'Below Target';
        qualityChange.className = 'metric-change negative';
    }
}

/**
 * Update production lines display
 */
function updateProductionLines(lines) {
    const container = document.getElementById('productionLinesGrid');
    container.innerHTML = '';

    lines.forEach(line => {
        const card = createProductionLineCard(line);
        container.appendChild(card);
    });
}

/**
 * Create production line card element
 */
function createProductionLineCard(line) {
    const card = document.createElement('div');
    card.className = `production-line-card status-${line.status}`;

    const efficiency = line.efficiency;
    const speedPercent = (line.current_speed / line.target_speed * 100).toFixed(1);

    card.innerHTML = `
        <div class="line-header">
            <div class="line-title">${line.name}</div>
            <div class="line-status ${line.status}">${line.status}</div>
        </div>
        <div class="line-metrics">
            <div class="line-metric">
                <div class="line-metric-label">Speed</div>
                <div class="line-metric-value">${line.current_speed.toFixed(0)}</div>
                <div class="line-metric-label">units/min</div>
            </div>
            <div class="line-metric">
                <div class="line-metric-label">Efficiency</div>
                <div class="line-metric-value">${efficiency.toFixed(1)}%</div>
            </div>
            <div class="line-metric">
                <div class="line-metric-label">Output</div>
                <div class="line-metric-value">${line.products_produced.toLocaleString()}</div>
            </div>
        </div>
        <div class="line-progress">
            <div class="progress-label">
                <span>Target Speed</span>
                <span>${speedPercent}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${Math.min(speedPercent, 100)}%"></div>
            </div>
        </div>
        <div class="line-progress">
            <div class="progress-label">
                <span>Efficiency</span>
                <span>${efficiency.toFixed(1)}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${Math.min(efficiency, 100)}%"></div>
            </div>
        </div>
    `;

    return card;
}

/**
 * Update alerts display
 */
function updateAlerts(alerts, alertCounts) {
    const container = document.getElementById('alertsContainer');

    // Filter alerts based on current filter
    let filteredAlerts = alerts;
    if (currentAlertFilter !== 'all') {
        filteredAlerts = alerts.filter(alert => alert.severity === currentAlertFilter);
    }

    if (filteredAlerts.length === 0) {
        container.innerHTML = `
            <div class="no-alerts">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M9 11l3 3L22 4" stroke-width="2" stroke-linecap="round"/>
                    <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" stroke-width="2"/>
                </svg>
                <p>No ${currentAlertFilter === 'all' ? '' : currentAlertFilter} alerts</p>
            </div>
        `;
        return;
    }

    container.innerHTML = '';
    filteredAlerts.forEach(alert => {
        const alertElement = createAlertElement(alert);
        container.appendChild(alertElement);
    });
}

/**
 * Create alert element
 */
function createAlertElement(alert) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert-item ${alert.severity}`;

    const timestamp = new Date(alert.timestamp).toLocaleTimeString();

    alertDiv.innerHTML = `
        <div class="alert-header">
            <div class="alert-title">${alert.title}</div>
            <div class="alert-severity ${alert.severity}">${alert.severity}</div>
        </div>
        <div class="alert-message">${alert.message}</div>
        <div class="alert-footer">
            <span>Line: ${alert.line_id}</span>
            <span>${timestamp}</span>
        </div>
    `;

    return alertDiv;
}

/**
 * Update machine health display
 */
function updateMachineHealth(healthData) {
    const container = document.getElementById('machineHealthGrid');
    container.innerHTML = '';

    healthData.forEach(health => {
        const card = createMachineHealthCard(health);
        container.appendChild(card);
    });
}

/**
 * Create machine health card
 */
function createMachineHealthCard(health) {
    const card = document.createElement('div');
    card.className = 'health-card';

    let healthClass = 'good';
    if (health.health_score < 70) {
        healthClass = 'critical';
    } else if (health.health_score < 85) {
        healthClass = 'warning';
    }

    const recommendations = health.recommendations
        .map(rec => `<div class="recommendation-item">${rec}</div>`)
        .join('');

    card.innerHTML = `
        <div class="health-header">
            <div>
                <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.25rem;">
                    ${health.line_id}
                </div>
                <div class="health-score ${healthClass}">${health.health_score.toFixed(1)}%</div>
            </div>
            <div style="text-align: right; font-size: 0.75rem; color: var(--text-muted);">
                Next maintenance<br>
                <span style="color: var(--text-primary); font-weight: 600;">${health.predicted_maintenance_hours}h</span>
            </div>
        </div>
        <div class="health-indicators">
            <div class="health-indicator">
                <div class="indicator-label">Temp</div>
                <div class="indicator-status ${health.temperature_status}">${health.temperature_status}</div>
            </div>
            <div class="health-indicator">
                <div class="indicator-label">Pressure</div>
                <div class="indicator-status ${health.pressure_status}">${health.pressure_status}</div>
            </div>
            <div class="health-indicator">
                <div class="indicator-label">Vibration</div>
                <div class="indicator-status ${health.vibration_status}">${health.vibration_status}</div>
            </div>
        </div>
        <div class="health-recommendations">
            <h4>Recommendations</h4>
            ${recommendations}
        </div>
    `;

    return card;
}

/**
 * Update charts with new data
 */
function updateCharts(data) {
    updateProductionChart(data.production_lines);
    updateQualityChart(data.quality_metrics);
    updateEfficiencyChart(data.production_lines);
}

/**
 * Initialize and update production chart
 */
function updateProductionChart(lines) {
    const ctx = document.getElementById('productionChart');
    if (!ctx) return;

    const labels = lines.map(line => line.line_id);
    const outputData = lines.map(line => line.products_produced);
    const defectData = lines.map(line => line.defects);

    if (productionChart) {
        productionChart.data.labels = labels;
        productionChart.data.datasets[0].data = outputData;
        productionChart.data.datasets[1].data = defectData;
        productionChart.update('none');
    } else {
        productionChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Total Output',
                        data: outputData,
                        backgroundColor: 'rgba(102, 126, 234, 0.6)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 2
                    },
                    {
                        label: 'Defects',
                        data: defectData,
                        backgroundColor: 'rgba(239, 68, 68, 0.6)',
                        borderColor: 'rgba(239, 68, 68, 1)',
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        labels: { color: '#e8eaf6' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#9ca3af' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    x: {
                        ticks: { color: '#9ca3af' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    }
                }
            }
        });
    }
}

/**
 * Initialize and update quality chart
 */
function updateQualityChart(qualityMetrics) {
    const ctx = document.getElementById('qualityChart');
    if (!ctx) return;

    const labels = qualityMetrics.map(qm => qm.line_id);
    const defectRates = qualityMetrics.map(qm => qm.defect_rate);
    const qualityScores = qualityMetrics.map(qm => qm.average_quality_score);

    if (qualityChart) {
        qualityChart.data.labels = labels;
        qualityChart.data.datasets[0].data = defectRates;
        qualityChart.data.datasets[1].data = qualityScores;
        qualityChart.update('none');
    } else {
        qualityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Defect Rate (%)',
                        data: defectRates,
                        borderColor: 'rgba(239, 68, 68, 1)',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Quality Score',
                        data: qualityScores,
                        borderColor: 'rgba(16, 185, 129, 1)',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        labels: { color: '#e8eaf6' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#9ca3af' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    x: {
                        ticks: { color: '#9ca3af' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    }
                }
            }
        });
    }
}

/**
 * Initialize and update efficiency chart
 */
function updateEfficiencyChart(lines) {
    const ctx = document.getElementById('efficiencyChart');
    if (!ctx) return;

    const labels = lines.map(line => line.line_id);
    const efficiencyData = lines.map(line => line.efficiency);
    const uptimeData = lines.map(line => line.uptime);

    if (efficiencyChart) {
        efficiencyChart.data.labels = labels;
        efficiencyChart.data.datasets[0].data = efficiencyData;
        efficiencyChart.data.datasets[1].data = uptimeData;
        efficiencyChart.update('none');
    } else {
        efficiencyChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Efficiency (%)',
                        data: efficiencyData,
                        borderColor: 'rgba(102, 126, 234, 1)',
                        backgroundColor: 'rgba(102, 126, 234, 0.2)',
                        borderWidth: 2
                    },
                    {
                        label: 'Uptime (%)',
                        data: uptimeData,
                        borderColor: 'rgba(16, 185, 129, 1)',
                        backgroundColor: 'rgba(16, 185, 129, 0.2)',
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        labels: { color: '#e8eaf6' }
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { color: '#9ca3af' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        pointLabels: { color: '#9ca3af' }
                    }
                }
            }
        });
    }
}

/**
 * Alert filter button handlers
 */
document.addEventListener('DOMContentLoaded', () => {
    const filterButtons = document.querySelectorAll('.filter-btn');

    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));

            // Add active class to clicked button
            button.classList.add('active');

            // Update current filter
            currentAlertFilter = button.dataset.filter;

            // Note: alerts will be re-filtered on next update
            // For immediate update, we would need to store the last alerts data
        });
    });
});

console.log('Factory Process Monitoring Agent initialized');
