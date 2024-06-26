class SCENE3D {
    constructor(MAIN_CONTAINER_ID) {
        this.MAIN_CONTAINER_ID = MAIN_CONTAINER_ID;
        this.nodes = [];
        this.conect = {};
        this.colored = 'random';
        this.width = '50%';
        this.lines = [];
        this.nodesArray = [];
        this.cross_section = [];
        this.mainContainer = document.getElementById(MAIN_CONTAINER_ID);
        this.mouse = new THREE.Vector2();
        this.raycaster = new THREE.Raycaster();
        this.intersected = null;
        this.onMouseMove = this.onMouseMove.bind(this);

    }

    create_scene = () => {
        this.container = document.createElement('div');
        const container = this.container;
        container.style.width = this.width;
        container.style.height = '1200px';
        container.style.position = 'relative';

        this.mainContainer.appendChild(container);

        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        const renderer = this.renderer;

        this.scene = new THREE.Scene();
        const scene = this.scene;
        renderer.setPixelRatio(1.2);

        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.physicallyCorrectLights = false;
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.0;
        renderer.outputEncoding = THREE.sRGBEncoding;

        scene.background = new THREE.Color("#474747");

        const light = new THREE.DirectionalLight(0xffffff, 0.5);
        light.position.set(0, -1500, 700);
        scene.add(light);

        const light2 = new THREE.DirectionalLight(0xffffff, 0.5);
        light2.position.set(0, 1500, 700);
        scene.add(light2);

        const light3 = new THREE.DirectionalLight(0xffffff, 0.5);
        light3.position.set(0, 0, -700);
        scene.add(light3);

        const light4 = new THREE.DirectionalLight(0xffffff, 0.5);
        light4.position.set(0, 0, 700);
        scene.add(light4);

        const lightA = new THREE.HemisphereLight(0xffffff, 0xffffff, 0.1);
        scene.add(lightA);

        let width = container.clientWidth;
        let height = container.clientHeight;

        this.camera = new THREE.PerspectiveCamera(
            75, // Field of view
            width / height, // Aspect ratio
            0.1, // Near clipping plane
            100000 // Far clipping plane
        );
        const camera = this.camera;
        this.controls = new THREE.OrbitControls(camera, renderer.domElement);
        const controls = this.controls;
        this.controls.enableDamping = false;
        //this.controls.dampingFactor = 0.9;

        this.camera.position.set(1490, -1980, 2000);

        this.centerVector = new THREE.Vector3(1500, 0, 250);
        controls.target = this.centerVector;

        this.controls.update();

        container.appendChild(renderer.domElement);
        renderer.domElement.addEventListener('mousemove', this.onMouseMove, false);

        const animate = () => {
            requestAnimationFrame(animate);
            controls.update(); // Only required if controls.enableDamping or controls.autoRotate are set to true
            renderer.render(scene, camera);
        };
        animate();
    }

    scene_gltf_loader = () => {
        const loader = new THREE.STLLoader();
        loader.load('/static/models/truck.stl', (geometry) => {
            const material = new THREE.MeshPhongMaterial({ color: "#FFA500" });
            const mesh = new THREE.Mesh(geometry, material);
            mesh.name = "CAT 793"
            this.scene.add(mesh);
            
        },
        (xhr) => {
            console.log((xhr.loaded / xhr.total) * 100 + '% loaded');
        },
        (error) => {
            console.log(error);
        });
    }

    /*
    onMouseMove = (event) => {
        event.preventDefault();

        const rect = this.container.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.scene.children);

        if (intersects.length > 0) {
            console.log(`Intersection at ${intersects[0].point.x}, ${intersects[0].point.y}, ${intersects[0].point.z}`);
        } else {
            const point = new THREE.Vector3();
            this.raycaster.ray.at(10, point); // 10 units from the camera
            console.log(`Ray at ${point.x}, ${point.y}, ${point.z}`);
        }
    }
    */

    onMouseMove = (event) => {
        event.preventDefault();
    
        const rect = this.container.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.scene.children);
    
        if (intersects.length > 0) {
            if (this.intersected !== intersects[0].object) {
                if (this.intersected) {
                    // Reset previous intersection object's material or color if needed
                }
    
                this.intersected = intersects[0].object;
    
                // Show tooltip
                if (this.intersected.name !== "CAT 793"){
                const tooltip = document.getElementById('tooltip');
                tooltip.style.display = 'block';
                tooltip.style.left = `${event.clientX}px`;
                tooltip.style.top = `${event.clientY}px`;
                tooltip.textContent = this.intersected.name;
                } // Assuming the name of the sphere is set to something meaningful
            }
        } else {
            if (this.intersected) {
                // Reset intersection object's material or color if needed
                this.intersected = null;
    
                // Hide tooltip
                const tooltip = document.getElementById('tooltip');
                tooltip.style.display = 'none';
            }
        }
    }

    render = () => {
        this.renderer.render(this.scene, this.camera);
    }

    createNode = (node)=> {
        console.log(node)
        console.log(node.x,node.y,node.z)

        const geometry = new THREE.SphereGeometry(50, 50, 50);
        const material = new THREE.MeshBasicMaterial({ color: 0xff0000 });
        const sphere = new THREE.Mesh(geometry, material);

        sphere.position.set(node.x, node.y, node.z);
        sphere.name = `Monitoring Point: #${node.id}`;
        this.scene.add(sphere);



    }


}