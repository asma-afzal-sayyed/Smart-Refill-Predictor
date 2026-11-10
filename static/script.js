const ctx = document.getElementById('usageChart');

const labels = JSON.parse(
    document.getElementById("graph-labels").textContent
);

const values = JSON.parse(
    document.getElementById("graph-values").textContent
);

new Chart(ctx, {

    type: 'line',

    data: {

        labels: labels,

        datasets: [{

            label: 'Daily Usage',

            data: values,

            borderColor: 'blue',

            backgroundColor: 'rgba(0,0,255,0.2)',

            tension: 0.4,

            fill: true
        }]
    }
});

const today = new Date();

document.getElementById("todayDate").innerHTML =
today.toDateString();