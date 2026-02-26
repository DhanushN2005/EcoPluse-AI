// State Management
let currentMetric = 'aqi';
const metricConfig = {
    aqi: { label: 'AQI Index', color: '#10b981', gradient: ['rgba(16, 185, 129, 0.4)', 'rgba(16, 185, 129, 0)'] },
    pm25: { label: 'PM 2.5', color: '#06b6d4', gradient: ['rgba(6, 182, 212, 0.4)', 'rgba(6, 182, 212, 0)'] }
};

// Chart Initialization
const ctx = document.getElementById('trendChart').getContext('2d');
const chartGradient = ctx.createLinearGradient(0, 0, 0, 400);
chartGradient.addColorStop(0, metricConfig[currentMetric].gradient[0]);
chartGradient.addColorStop(1, metricConfig[currentMetric].gradient[1]);

const trendChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: metricConfig[currentMetric].label,
            data: [],
            borderColor: metricConfig[currentMetric].color,
            backgroundColor: chartGradient,
            borderWidth: 3,
            tension: 0.4,
            fill: true,
            pointRadius: 2,
            pointBackgroundColor: metricConfig[currentMetric].color,
            pointBorderColor: 'rgba(255,255,255,0.1)',
            pointHoverRadius: 6,
            pointHoverBackgroundColor: '#fff',
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
            padding: { top: 10, bottom: 0, left: 10, right: 10 }
        },
        plugins: {
            legend: { display: false },
            tooltip: {
                enabled: true,
                backgroundColor: 'rgba(30, 41, 59, 0.9)',
                titleColor: '#94a3b8',
                bodyColor: '#fff',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                padding: 12,
                displayColors: false,
                callbacks: {
                    label: (context) => `${context.dataset.label}: ${context.parsed.y.toFixed(1)}`
                }
            }
        },
        scales: {
            x: {
                grid: { display: false },
                ticks: {
                    color: '#64748b',
                    maxRotation: 0,
                    autoSkip: true,
                    maxTicksLimit: 8
                }
            },
            y: {
                grid: { color: 'rgba(255, 255, 255, 0.03)' },
                ticks: {
                    color: '#94a3b8',
                    padding: 10
                },
                beginAtZero: false
            }
        }
    }
});

// Metric Switching Logic
document.querySelectorAll('[data-metric]').forEach(btn => {
    btn.addEventListener('click', () => {
        const metric = btn.getAttribute('data-metric');
        if (metric === currentMetric) return;

        currentMetric = metric;

        // Update button styles
        document.querySelectorAll('[data-metric]').forEach(b => {
            if (b.getAttribute('data-metric') === metric) {
                b.classList.add('bg-emerald-500/20', 'text-emerald-400', 'border-emerald-500/30');
                b.classList.remove('text-slate-400');
            } else {
                b.classList.remove('bg-emerald-500/20', 'text-emerald-400', 'border-emerald-500/30');
                b.classList.add('text-slate-400');
            }
        });

        // Update chart colors
        const config = metricConfig[currentMetric];
        const newGradient = ctx.createLinearGradient(0, 0, 0, 400);
        newGradient.addColorStop(0, config.gradient[0]);
        newGradient.addColorStop(1, config.gradient[1]);

        trendChart.data.datasets[0].label = config.label;
        trendChart.data.datasets[0].borderColor = config.color;
        trendChart.data.datasets[0].backgroundColor = newGradient;
        trendChart.data.datasets[0].pointBackgroundColor = config.color;
        trendChart.update();
    });
});

// Update UI Function
async function updateDashboard() {
    try {
        const response = await fetch('/api/metrics');
        const data = await response.json();

        if (data.error) throw new Error(data.error);

        document.getElementById('connection-status').classList.remove('opacity-0');

        // Update Values
        const latest = data.latest;
        const healthScore = Math.round(latest.health_score);
        document.getElementById('health-score').innerText = healthScore;

        // Dynamic health color
        const healthEl = document.getElementById('health-score');
        if (healthScore > 80) healthEl.className = 'text-6xl font-bold text-emerald-400 stat-value';
        else if (healthScore > 50) healthEl.className = 'text-6xl font-bold text-amber-400 stat-value';
        else healthEl.className = 'text-6xl font-bold text-red-400 stat-value';

        document.getElementById('aqi-value').innerText = Math.round(latest.aqi);
        document.getElementById('pm25-val').innerText = `${latest.pm25.toFixed(1)}`;
        document.getElementById('co2-val').innerText = `${Math.round(latest.co2)}`;
        document.getElementById('aqi-forecast').innerText = `Forecast: ${Math.round(data.forecast)}`;

        // Update Alerts
        const alertList = document.getElementById('alert-list');
        if (data.alerts && data.alerts.length > 0) {
            alertList.innerHTML = data.alerts.map(alert => `
                <div class="p-4 rounded-xl bg-${alert.severity === 'Emergency' ? 'red' : 'amber'}-500/10 border border-${alert.severity === 'Emergency' ? 'red' : 'amber'}-500/20 animate-slide-up">
                    <div class="flex justify-between items-center text-[10px] font-bold uppercase text-${alert.severity === 'Emergency' ? 'red' : 'amber'}-400 mb-1 tracking-widest">
                        <span>${alert.severity}</span>
                        <span>${alert.metric}</span>
                    </div>
                    <div class="text-lg font-bold text-slate-100">${alert.value.toFixed(1)}</div>
                </div>
            `).join('');
        } else {
            alertList.innerHTML = `
                <div class="flex flex-col items-center justify-center p-8 rounded-2xl bg-emerald-500/5 border border-emerald-500/10 text-center">
                    <div class="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center mb-3">
                        <span class="text-emerald-400 text-xl">✓</span>
                    </div>
                    <p class="text-emerald-400/80 font-semibold text-sm">Environment Stable</p>
                    <p class="text-slate-500 text-xs mt-1">No anomalies detected</p>
                </div>
            `;
        }

        // Update Chart
        const history = data.history;
        trendChart.data.labels = history.map(h => {
            const date = new Date(h.timestamp);
            return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`;
        });
        trendChart.data.datasets[0].data = history.map(h => h[currentMetric]);
        trendChart.update('none');

    } catch (err) {
        console.error('Update Error:', err);
    }
}

// Chat Logic
const chatInput = document.getElementById('chat-input');
const chatBox = document.getElementById('chat-box');
const sendBtn = document.getElementById('send-btn');

async function sendQuery() {
    const query = chatInput.value.trim();
    if (!query) return;

    chatBox.innerHTML += `
        <div class="flex justify-end animate-slide-up">
            <div class="bg-emerald-600/20 border border-emerald-500/20 p-3 rounded-2xl text-emerald-100 max-w-[85%] rounded-br-none shadow-lg shadow-emerald-900/10">
                ${query}
            </div>
        </div>
    `;
    chatInput.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;

    const loadingId = 'loading-' + Date.now();
    chatBox.innerHTML += `
        <div id="${loadingId}" class="flex gap-2 p-3 bg-slate-800/50 rounded-2xl rounded-bl-none self-start border border-white/5 animate-pulse">
            <span class="text-slate-400 italic">EcoPulse is thinking...</span>
        </div>
    `;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        const result = await response.json();

        document.getElementById(loadingId).remove();
        chatBox.innerHTML += `
            <div class="bg-slate-800/80 p-4 rounded-2xl rounded-bl-none border border-white/5 animate-slide-up shadow-xl">
                <div class="text-emerald-400 text-[10px] font-bold uppercase tracking-widest mb-2 flex items-center gap-1">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> COPILOT ADVISORY
                </div>
                <div class="text-slate-200 leading-relaxed">${result.response}</div>
            </div>
        `;
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
        document.getElementById(loadingId).innerHTML = `<span class="text-red-400">Communication error with Copilot.</span>`;
    }
}

sendBtn.addEventListener('click', sendQuery);
chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendQuery(); });

// Initial Polling
setInterval(updateDashboard, 2000);
updateDashboard();
