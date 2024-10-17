document.addEventListener('DOMContentLoaded', function() {
    fetchMetrics();
});

function fetchMetrics() {
    fetch('/get_metrics')
        .then(response => response.json())
        .then(data => {
            updateMetrics(data);
            createConversationsChart(data.chart_data);
            createCSATChart(data.chart_data);
            createSentimentChart(data.sentiment_data);
        });
}

function updateMetrics(data) {
    document.getElementById('total-conversations').textContent = data.total_conversations;
    document.getElementById('avg-response-time').textContent = `${data.avg_response_time} seconds`;
    document.getElementById('lead-conversion-rate').textContent = `${(data.lead_conversion_rate * 100).toFixed(1)}%`;
    document.getElementById('csat-score').textContent = data.csat_score.toFixed(1);
}

function createConversationsChart(data) {
    new Chart(document.getElementById('conversations-chart'), {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [
                {
                    label: 'Total Conversations',
                    data: data.conversations,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                },
                {
                    label: 'Resolved Queries',
                    data: data.resolved_queries,
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Conversations and Resolved Queries'
                }
            }
        }
    });
}

function createCSATChart(data) {
    new Chart(document.getElementById('csat-chart'), {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [{
                label: 'CSAT Score',
                data: data.csat,
                borderColor: 'rgb(153, 102, 255)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Customer Satisfaction Score Trend'
                }
            },
            scales: {
                y: {
                    min: 0,
                    max: 5
                }
            }
        }
    });
}

function createSentimentChart(data) {
    new Chart(document.getElementById('sentiment-chart'), {
        type: 'doughnut',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: [
                    'rgb(75, 192, 192)',
                    'rgb(255, 205, 86)',
                    'rgb(255, 99, 132)'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Customer Sentiment Analysis'
                }
            }
        }
    });
}