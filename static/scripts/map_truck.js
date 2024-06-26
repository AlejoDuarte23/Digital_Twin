class MapComponent {
    constructor(apiRoute, mainDivId) {
        this.apiRoute = apiRoute;
        this.mainDivId = mainDivId;
        this.map = null;
        this.geoJsonSourceId = 'geojson-source';
    }

    async fetchData() {
        try {
            const response = await fetch(this.apiRoute);
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Fetch error:', error);
            return null;
        }
    }   

    filterDataByDate(data, startDate, endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);

        const filteredFeatures = data.features.filter(feature => {
            const featureDate = new Date(feature.properties.Datetime);
            return featureDate >= start && featureDate <= end;
        });

        return {
            type: "FeatureCollection",
            features: filteredFeatures
        };
    }

    convertCoordinates(data) {
        proj4.defs("EPSG:3857", "+proj=merc +lon_0=0 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs");
        proj4.defs("EPSG:4326", "+proj=longlat +datum=WGS84 +no_defs");

        data.features.forEach(feature => {
            const [x, y] = feature.geometry.coordinates;
            const [lon, lat] = proj4("EPSG:3857", "EPSG:4326", [x, y]);
            feature.geometry.coordinates = [lon, lat];
        });

        return data;
    }

    createMap() {
        mapboxgl.accessToken = 'pk.eyJ1IjoiYWxlam9kdWFydGUyMyIsImEiOiJja2wxMm1tMHUwYWdwMnd0NGI0emZrYTF5In0.2fceQ8K9H7KwH7tCSz_tWA'; // Replace with your Mapbox access token
        this.map = new mapboxgl.Map({
            container: this.mainDivId,
            style: 'mapbox://styles/mapbox/satellite-v9',
            center: [0, 0],
            zoom: 2,
            attributionControl: false
        });

        this.map.on('load', () => {
            this.map.addSource(this.geoJsonSourceId, {
                type: 'geojson',
                data: null
            });

            this.map.addLayer({
                id: 'geojson-layer',
                type: 'circle',
                source: this.geoJsonSourceId,
                paint: {
                    'circle-radius': 3,
                    'circle-color': "#FF00FF"
                }
            });
        });
    }

    async init() {
        let data = await this.fetchData();
        if (!data) return;

        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;

        if (startDate && endDate) {
            data = this.filterDataByDate(data, startDate, endDate);
        }

        if (!this.map) {
            this.createMap();
            this.map.on('load', () => {
                this.map.getSource(this.geoJsonSourceId).setData(data);
                this.map.fitBounds(turf.bbox(data), { padding: 20 });
            });
        } else {
            this.map.getSource(this.geoJsonSourceId).setData(data);
            this.map.fitBounds(turf.bbox(data), { padding: 20 });
        }
    }

    async applyFilter() {
        await this.init();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const mapComponent = new MapComponent('/data', 'map');
    mapComponent.init();

    document.getElementById('filter-btn').addEventListener('click', () => {
        mapComponent.applyFilter();
    });
});
