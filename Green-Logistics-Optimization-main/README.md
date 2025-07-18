# Green Logistics Optimization


This project focuses on enhancing the ecological sustainability of logistics operations. Our primary objective is to identify the most efficient paths to reach delivery points from specific warehouses, significantly reducing both travel time and carbon emissions while adhering to vehicle capacity constraints. Our approach involves a dual-phase strategy: initially devising optimized routes through our green routing algorithm, followed by leveraging this data to strategically plan warehouse locations. While prior research extensively addressed the Vehicle Routing Problem, our methodology presents a holistic solution. We not only optimize routes but dynamically adjust warehouse locations based on feedback derived from route analysis. This integrated approach harmonizes route planning and warehouse allocation, fostering a more streamlined, environmentally conscious delivery system.

## Authors

Paper Available at [Link](https://drive.google.com/file/d/1omr9UL-Z4-8LTENHKA-orQcDTRKO2V-l/view?usp=sharing)

- [Subham Subhasis Sahoo - 2020CSB1317 ](https://www.linkedin.com/in/subham-subhasis-sahoo-6456871bb/)
- [Aman Pankaj Adatia - 2020CSB1154 ](https://www.linkedin.com/in/aman-adatia-b49103146/)
- [Vinay Kumar - 2020CSB1141 ](https://www.linkedin.com/in/kvinay07/)

## Usage

### 1. Data Collection and Preprocessing

**Dataset**: To predict emissions accurately, we required data on
both distance and duration. Our dataset was con-
structed by leveraging the USA road network dataset [Link](https://www.diag.uniroma1.it/challenge9/download.shtml)
as a foundation. Subsequently, we utilized the Open-
StreetMap (OSM) API to retrieve information on the
distance and duration for our analysis and combined them to create our own dataset. The dataset is published at [Kaggle Link](https://www.kaggle.com/datasets/subham200271/usa-road-dataset-distance-and-duration/data) 

The scripts related to this are avaialable under the `world` directory. The dataset and its different versions generated from our scripts are stored inside the `data` directory.

### 2. Emissions Prediction Module

This module is contained inside the `ml-modules` directory.`Emission.ipynb` file contains the model training and testing code. The model is save inside the `models` directory inside it. It is later used by our routing module to get the carbon emissions.


### 3. Green Routing Algorithm

This module is contained inside the `routing` directory. Green Routing Algorithm is deifned in the `routingGA.py` file. The `lcal_routing.py` script is designed to test it. 

### 4. Genetic Algorithm for our Packaged Solution

This module is contained inside the `routing` directory. The `warehouseGA.py` file contians the genetic algorithm which utilizes the green routing module and graph connectivity properties to model the fitness function. The `warehouse_planning.py` script is designed to run our packaged solution. We use this to run our experiments. 

### 5. Results and Logging

The `results` directory is a centralized hub housing our conclusive findings, including final clustering configurations and logs detailing each iteration's progress. 

## How to Run

1. Clone the repository to your local machine.
2. Install the required dependencies.
3. To start the experiment setup, you can run the `warehouse_planning.py` file directly.


