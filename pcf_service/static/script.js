async function loadChart() {
    const response = await fetch("/dashboard/data");
    const data = await response.json();
    const allow = data.filter(e => e.action === "ALLOW").length;
    const block = data.filter(e => e.action === "BLOCK").length;

    const ctx = document.getElementById('chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['ALLOW', 'BLOCK'],
            datasets: [{
                label: '# de Decisões',
                data: [allow, block]
            }]
        }
    });
}
loadChart();
