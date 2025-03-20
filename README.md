#### ***  [ Under Development ]***
# **Intrusion Detection System (IDS) Using Wireshark and Advanced Ensemble Learning Techniques**

***Clone the Repository if needed.***
[![GitHub](https://img.shields.io/badge/GitHub-visit_repository-indigo?style=for-the-badge&logo=github)](https://github.com/infinity-decoder/FYP) 

## **📁 Project Info**
Visit `/docs/project_documentation.md` For details.

## **🟢 Assignment files F24PROJECTA686A (BC210427835)**

| **Project File** | **Status** | **Details** |
|-----------------|------------|------------|
| **1️⃣ SRS** | ✅ **Completed** | (Submitied on  `08DEC2024`),(Stored at `/docs`). |
| **2️⃣ Design Document** | ✅ **Completed** | (Submitied on  `03MAR2025`),(Stored at `/docs`). |
| **3️⃣ Prototype Phase** | ✅ **Completed** | Submitied on  `18MAR2025`. |
| **4️⃣ Final Deliverable** | ❌ **Incompleted** | Under Development. |



## **🟢 Steps Taken for Django webapp**

| **Django app Development** | **Status** | **Details** |
|-----------------|------------|------------|
| **1️⃣ Project** | ✅ **Completed** | (Handled in `webapp/IDS_Project`). |
| **2️⃣ webapp** | ✅ **Completed** | (Handled in `webapp/IDS`). |
| **3️⃣ Front End** | ✅ **Completed** | structure files (Handled in `webapp/IDS/templates/IDS`) design files (Handled in `webapp/IDS/static/css`). |


## **🟢 Steps Implemented for ML models**
| **Prototype Step** | **Status** | **Details** |
|-----------------|------------|------------|
| **1️⃣ Capture Network Traffic & Convert to CSV** | ✅ **Completed** | Wireshark captures `.pcap` files, which are converted to `.csv` (Handled in `notebooks/pcap_to_csv.ipynb`), (`.pcap`stored at `data/raw`), (`csv` stored at `data/processed`)  |
| **2️⃣ Data Preprocessing** | ✅ **Completed** | Data cleaning, encoding, and normalization (Handled in `notebooks/data_preparation.ipynb`) |
| **3️⃣ Final Dataset Creation** | ✅ **Completed** | Structured dataset with normal/malicious labels stored at **`/FYP/data/datasets/final_dataset.csv`**. |
| **4️⃣ Model Training (TabNet, CatBoost, LightGBM, Stacking Ensemble)** | ✅ **Continue** | Each model trained separately (Handled in `notebooks/TabNet.ipynb`, `CatBoost.ipynb`, `LightGBM.ipynb`, `Stacking_ensemble.ipynb`). |
| **5️⃣ Model Evaluation (Metrics Calculation & Comparison)** | ❌ **Incompleted**  | Evaluation script implemented (Handled in `notebooks/evaluation_metrics.ipynb`). |



## **🟡 Under Development**
1. **Getting more data using wireshark**
2. **Training Models**  

## **🔴 Not completed yet**
1. **Connecting ML Trained models to webapp** to ensure user can interact with app. 
2. **Fine-tune the models** for better performance?
3. **Final Report**
4. **Final Presentation**

## **📁 Folder Schema**
D:\FYP
├── README.md
├── configs
│   └── model_config.json
├── data
│   ├── datasets
│   │   ├── final_dataset_01.csv
│   │   └── final_dataset_02.csv
│   ├── processed
│   │   ├── Attack_ICMP.csv
│   │   ├── Attack_synflood.csv
│   │   ├── Wireshark_01.csv
│   │   ├── Wireshark_02.csv
│   │   ├── attack_traffic_01.csv
│   │   ├── p3.csv
│   │   ├── parrot_traffic_01.csv
│   │   ├── parrot_traffic_02.csv
│   │   ├── wireshark_dataset_01.csv
│   │   └── wireshark_dataset_02.csv
│   └── raw
│       ├── Attack_ICMP.pcapng
│       ├── Attack_synflood.pcapng
│       ├── Wireshark_01.pcapng
│       ├── Wireshark_02.pcapng
│       ├── attack_traffic.pcapng
│       ├── attack_traffic_01.pcapng
│       ├── parrot_traffic_01.pcapng
│       └── parrot_traffic_02.pcapng
├── docs
│   ├── DD_F24PROJECTA686A (BC210427835).pdf
│   ├── SRS_F24PROJECTA686A (BC210427835).pdf
│   └── project_documentation.md
├── folder_structure.txt
├── image.png
├── logs
│   └── app.log
├── media
├── models
│   ├── CatBoost.ipynb
│   ├── LightGBM.ipynb
│   ├── LightGBMn.ipynb
│   ├── Stacking_ensemble.ipynb
│   ├── XGBoost.ipynb
│   ├── XGBoostn.ipynb
│   ├── ensemble.ipynb
│   └── trained_models
│       ├── evaluation_results.csv
│       ├── lightgbm_intrusion_detection.pkl
│       ├── meta_scaler.pkl
│       ├── tabnet_meta_model.pkl
│       └── xgboost_native_model.pkl
├── notebooks
│   ├── data_preprocessing.ipynb
│   ├── evaluation_metrics.ipynb
│   ├── exploratory_data_analysis.ipynb
│   └── pcap_to_csv.ipynb
├── requirements.txt
├── src
│   ├── __init__.py
│   ├── data_processing.py
│   ├── feature_extraction.py
│   ├── model_inference.py
│   ├── model_training.py
│   ├── pcap_to_csv.py
│   └── visualization.py
├── temp
│   ├── TabNet.ipynb
│   ├── data_preparation.ipynb
│   └── pcap_to_csv.py
├── tests
│   ├── data_operations.ipynb
│   ├── folder_schema.ipynb
│   ├── pyshark_csv.py
│   ├── schema.py
│   └── tshark_csv.py
└── webapp
    ├── IDS
    │   ├── __init__.py
    │   ├── __pycache__
    │   │   ├── __init__.cpython-313.pyc
    │   │   ├── admin.cpython-313.pyc
    │   │   ├── apps.cpython-313.pyc
    │   │   ├── models.cpython-313.pyc
    │   │   ├── urls.cpython-313.pyc
    │   │   └── views.cpython-313.pyc
    │   ├── admin.py
    │   ├── apps.py
    │   ├── migrations
    │   │   ├── __init__.py
    │   │   └── __pycache__
    │   │       └── __init__.cpython-313.pyc
    │   ├── models.py
    │   ├── static
    │   │   └── css
    │   │       └── custom.css
    │   ├── templates
    │   │   └── IDS
    │   │       ├── about_us.html
    │   │       ├── analysis_report.html
    │   │       ├── base.html
    │   │       ├── contact_us.html
    │   │       ├── dashboard.html
    │   │       ├── file_upload.html
    │   │       ├── home.html
    │   │       ├── login.html
    │   │       └── register.html
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── IDS_Project
    │   ├── __init__.py
    │   ├── __pycache__
    │   │   ├── __init__.cpython-313.pyc
    │   │   ├── settings.cpython-313.pyc
    │   │   ├── urls.cpython-313.pyc
    │   │   └── wsgi.cpython-313.pyc
    │   ├── asgi.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── db.sqlite3
    └── manage.py


<h1 style="font-family: 'poppins'; font-weight: bold; color: Green;">👨‍💻Author: MAHBOOB ALAM</h1>

[![GitHub](https://img.shields.io/badge/GitHub-Profile-blue?style=for-the-badge&logo=github)](https://github.com/infinity-decoder) 
[![Kaggle](https://img.shields.io/badge/Kaggle-Profile-green?style=for-the-badge&logo=kaggle)](https://www.kaggle.com/infinitydecoder) 
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=for-the-badge&logo=linkedin)](https://pk.linkedin.com/in/infinitydecoder)  
[![Facebook](https://img.shields.io/badge/Facebook-Profile-blue?style=for-the-badge&logo=facebook)](https://www.facebook.com/infinitydecoder.me) 
[![Email](https://img.shields.io/badge/Email-Contact%20Me-red?style=for-the-badge&logo=email)](mailto:bc210427835mal@vu.edu.pk)
inshallah will be finalized till 09MAY2025! 🚀