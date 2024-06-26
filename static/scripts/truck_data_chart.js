class TruckDataChart {
    constructor(apiRoute, mainDiv, rows, cols, parameters, units) {
        this.apiRoute = apiRoute;
        this.mainDiv = document.getElementById(mainDiv);
        this.rows = rows;
        this.cols = cols;
        this.parameters = parameters;
        this.units = units;
        this.chartData = {};
        this.charts = [];

        this.init();
    }

    async fetchData() {
        try {
            const response = await fetch(this.apiRoute);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching data:', error);
            return null;
        }
    }

    synchronizeCharts(baseChart) {
        baseChart.timeScale().subscribeVisibleTimeRangeChange((newRange) => {
            if (this.synchronizing) return;
            this.synchronizing = true;
            this.charts.forEach(({ chart }) => {
                if (chart !== baseChart) {
                    chart.timeScale().setVisibleLogicalRange(newRange);
                }
            });
            this.synchronizing = false;
        });
    }

    createChart(container, title, unit) {
        const chart = LightweightCharts.createChart(container, {
            width: container.clientWidth,
            height: container.clientHeight,
            grid: {
                vertLines: {
                    visible: false,
                },
                horzLines: {
                    visible: false,
                },
            },
            
            timeScale: {
                timeVisible: true,
                secondsVisible: true,
                rightOffset: 2,
                borderVisible: false,
                minBarSpacing: 0.00001,
            },
            layout: {
                textColor: '#000000',
                backgroundColor: '#000000',
            },
            priceScale: {
                borderColor: '#000000',
                mode: LightweightCharts.PriceScaleMode.Normal,
                drawTicks: true,
                drawAxisLabels: true,
                invertScale: false,
            },
        });

        
        
        const lineSeries = chart.addLineSeries({
            title: title,
            color: '#2962FF'
        });

        // Create and add legend
        const legend = document.createElement('div');
        legend.className = 'legend';
        legend.innerHTML = `<strong>${title}</strong> (${unit})`;
        container.style.position = 'relative'; // Ensure the container is positioned relative to place the legend correctly
        container.appendChild(legend);

        // Add units to the y-axis
        chart.applyOptions({
            localization: {
                priceFormatter: price => `${price} ${unit}`
            }
        });

        return { chart, lineSeries };
    }

    async init() {
        const data = await this.fetchData();
        if (!data) return;

        this.mainDiv.innerHTML = ''; // Clear existing content

        const chartContainer = document.createElement('div');
        chartContainer.classList.add('chart-container');
        chartContainer.style.gridTemplateRows = `repeat(${this.rows}, 1fr)`;
        chartContainer.style.gridTemplateColumns = `repeat(${this.cols}, 1fr)`;

        this.mainDiv.appendChild(chartContainer);

        this.parameters.forEach((param, index) => {
            const chartDiv = document.createElement('div');
            chartDiv.classList.add('chart');
            chartContainer.appendChild(chartDiv);

            const { chart, lineSeries } = this.createChart(chartDiv, param, this.units[index]);
            this.charts.push({ chart, lineSeries });

            const seriesData = Object.keys(data).map(timestamp => {
                return {
                    time: new Date(timestamp).getTime() / 1000,
                    value: data[timestamp][param],
                };
            });

            lineSeries.setData(seriesData);
            chart.timeScale().fitContent();
        });

        this.initControls();
    }

    initControls() {
        const startDateInput = document.getElementById('start-date');
        const endDateInput = document.getElementById('end-date');
        const updateButton = document.getElementById('update-charts');

        updateButton.addEventListener('click', () => {
            const startDate = new Date(startDateInput.value).getTime() / 1000;
            const endDate = new Date(endDateInput.value).getTime() / 1000;

            this.charts.forEach(({ chart }) => {
                chart.timeScale().setVisibleRange({
                    from: startDate,
                    to: endDate,
                });
            });
        });
    }
}

// Example usage
document.addEventListener('DOMContentLoaded', () => {
    const apiRoute = '/truck_data';
    const mainDiv = 'main-container';
    const rows = 2;
    const cols = 2;
    const parameters = ['Ground Speed', 'Payload', 'Right Front Suspension Cylinder','Left Front Suspension Cylinder','Right Rear Suspension Cylinder','Left Rear Suspension Cylinder' ];
    const units = ['km/h', 'Tons', 'Pressure','Pressure','Pressure','Pressure'];

    new TruckDataChart(apiRoute, mainDiv, rows, cols, parameters, units);
});
