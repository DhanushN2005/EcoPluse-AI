/**
 * EcoPulse AI - Unified Live Intelligence Engine
 * Synchronizes Core Sensors + Strategic Analytics + Trend Chart
 */

let trendChart = null;

async function updateDashboard() {
    try {
        const response = await fetch('/api/metrics');
        const rootData = await response.json();

        if (rootData.latest) {
            const latest = rootData.latest;
            const history = rootData.history || [];

            // 1. Core Sensor Cards
            document.getElementById('aqiVal').innerText = Math.round(latest.aqi);
            document.getElementById('pm25Val').innerText = latest.pm25.toFixed(1);
            document.getElementById('co2Val').innerText = Math.round(latest.co2);

            // 2. Health & Badge Logic
            const healthScore = Math.round(latest.health_score || 0);
            const aqiBadge = document.getElementById('aqiBadge');
            const hCircle = document.getElementById('healthCircle');
            const hScore = document.getElementById('healthScore');

            hScore.innerText = healthScore;
            hCircle.style.strokeDashoffset = 226 - (226 * healthScore) / 100;

            if (latest.aqi < 100) {
                aqiBadge.innerText = "Optimal";
                aqiBadge.className = "px-3 py-1 bg-emerald-100 text-emerald-600 rounded-lg text-[10px] font-bold uppercase";
                hCircle.style.color = "#2ECC71";
            } else if (latest.aqi < 200) {
                aqiBadge.innerText = "Warning";
                aqiBadge.className = "px-3 py-1 bg-amber-100 text-amber-600 rounded-lg text-[10px] font-bold uppercase";
                hCircle.style.color = "#F1C40F";
            } else {
                aqiBadge.innerText = "Critical";
                aqiBadge.className = "px-3 py-1 bg-red-100 text-red-600 rounded-lg text-[10px] font-bold uppercase";
                hCircle.style.color = "#E74C3C";
            }

            // 3. Attribution Logic (NEW)
            if (latest.attribution) {
                document.getElementById('attrTrafficVal').innerText = latest.attribution.traffic + '%';
                document.getElementById('attrTrafficBar').style.width = latest.attribution.traffic + '%';
                document.getElementById('attrIndustrialVal').innerText = latest.attribution.industrial + '%';
                document.getElementById('attrIndustrialBar').style.width = latest.attribution.industrial + '%';
                document.getElementById('attrWindVal').innerText = (latest.attribution.wind_impact + latest.attribution.temp_inversion).toFixed(1) + '%';
                document.getElementById('attrWindBar').style.width = (latest.attribution.wind_impact + latest.attribution.temp_inversion) + '%';
            }

            // 4. Strategic Summary (NEW)
            const summaryText = document.getElementById('summaryText');
            if (latest.attribution.traffic > 40) {
                summaryText.innerText = "System Analysis: Pollution surge driven primarily by increasing traffic density in central corridors.";
            } else if (latest.attribution.wind_impact > 30) {
                summaryText.innerText = "System Analysis: Critical atmospheric stagnation detected. Pollutants are failing to disperse due to low wind.";
            } else {
                summaryText.innerText = "System Analysis: Environmental state is currently stable with normal industrial loading.";
            }

            // 5. Map & Carbon
            if (window.updateMapIntensity) window.updateMapIntensity(latest.aqi);

            const carbonDay = document.getElementById('carbonDay');
            if (carbonDay && latest.carbon_footprint) {
                carbonDay.innerText = latest.carbon_footprint.total_equivalent;
                const cBar = document.getElementById('carbonBar');
                const percent = Math.min(100, (latest.carbon_footprint.total_equivalent / 5000) * 100);
                cBar.style.width = percent + '%';
            }

            // 6. Citizen Advisory (Level 5)
            updateAdvisory(latest.aqi);

            // 7. Trend Chart Update (Restored)
            if (history.length > 0) {
                updateTrendChart(history);
            }

            // 8. Incident Log Update (If on Reports Page)
            updateIncidentLog(rootData.alerts);
        }
    } catch (error) {
        console.error("Pulse sync failure:", error);
    }
}

function updateIncidentLog(alerts) {
    const table = document.getElementById('report-table');
    if (!table || !alerts || alerts.length === 0) return;

    // Check if alert already displayed (simple deduplication)
    alerts.forEach(alert => {
        const id = `alert-${alert.type}-${alert.level}`;
        if (document.getElementById(id)) return;

        const row = document.createElement('tr');
        row.id = id;
        row.className = "border-b border-slate-50 bg-red-50/50 animate-pulse";
        row.innerHTML = `
            <td class="py-6 text-slate-600 font-medium">${new Date().toLocaleTimeString()}</td>
            <td class="py-6 font-bold">${alert.type} Surge</td>
            <td class="py-6"><span class="px-3 py-1 bg-red-100 text-red-600 rounded-full text-[10px] font-bold uppercase">${alert.level}</span></td>
            <td class="py-6 text-slate-500">Value: ${alert.value}</td>
            <td class="py-6 text-red-500 font-bold">LIVE ALERT</td>
        `;
        table.prepend(row);

        // Remove pulse after 5s
        setTimeout(() => row.classList.remove('animate-pulse'), 5000);
    });
}

function updateAdvisory(aqi) {
    const container = document.getElementById('advisoryContainer');
    if (!container) return;

    const advisories = [];
    if (aqi > 200) {
        advisories.push({ group: "Elderly & Children", msg: "URGENT: Stay indoors. Hazardous levels.", color: "red", icon: "fa-triangle-exclamation" });
        advisories.push({ group: "Outdoor Workers", msg: "Limit shifts to 30 mins. N95 essential.", color: "red", icon: "fa-hard-hat" });
    } else if (aqi > 100) {
        advisories.push({ group: "Sensitive Citizens", msg: "Moderately high levels. Carry inhalers.", color: "amber", icon: "fa-lungs" });
    } else {
        advisories.push({ group: "Public Access", msg: "Air quality is healthy. Outdoor activity safe.", color: "emerald", icon: "fa-check-circle" });
    }

    container.innerHTML = advisories.map(a => `
        <div class="p-4 bg-${a.color}-50 border border-${a.color}-100 rounded-2xl flex items-start gap-3">
            <i class="fas ${a.icon} mt-1 text-${a.color}-600"></i>
            <div>
                <p class="text-[10px] font-black uppercase text-${a.color}-800 tracking-tighter">${a.group}</p>
                <p class="text-[11px] text-${a.color}-700 leading-tight">${a.msg}</p>
            </div>
        </div>
    `).join('');
}

function updateTrendChart(history) {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;

    const labels = history.slice(-20).map(h => h.timestamp.split('T')[1].substring(0, 5));
    const aqiData = history.slice(-20).map(h => h.aqi);
    const interactionData = history.slice(-20).map(h => h.heat_pollution_index || (h.temperature * h.aqi / 100) || 0);

    if (!trendChart) {
        trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'AQI Pulse',
                        data: aqiData,
                        borderColor: '#0F4C5C',
                        backgroundColor: 'rgba(15, 76, 92, 0.05)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Heat-Pollution Index',
                        data: interactionData,
                        borderColor: '#4FD1C5',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { font: { size: 9 } } },
                    y: { grid: { color: '#f1f5f9' }, ticks: { font: { size: 9 } } }
                }
            }
        });
    } else {
        trendChart.data.labels = labels;
        trendChart.data.datasets[0].data = aqiData;
        trendChart.data.datasets[1].data = interactionData;
        trendChart.update('none');
    }
}

// Start polling
setInterval(updateDashboard, 2000);
document.addEventListener('DOMContentLoaded', updateDashboard);
