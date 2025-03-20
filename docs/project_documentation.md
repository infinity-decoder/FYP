#### ***  [ Under Development ]***
# **Intrusion Detection System (IDS) Using Wireshark and Advanced Ensemble Learning Techniques**

## **Table of Contents**

1. [Project Overview](#project-overview)  
2. [Features](#features)  
3. [Installation and Setup](#installation-and-setup)  
4. [Folder Structure](#folder-structure)  
5. [Usage Instructions](#usage-instructions)  
6. [System Architecture](#system-architecture)  
7. [Key Components](#key-components)  
8. [Test Cases](#test-cases)  
9. [Future Enhancements](#future-enhancements)  
10. [Contributors](#contributors)  

---

## **Project Overview**

This project aims to develop a robust Network Intrusion Detection System (IDS) leveraging real-time network traffic data captured by Wireshark. The IDS utilizes advanced ensemble learning models, including TabNet, CatBoost, and LightGBM, to detect malicious network activities. The system integrates a Django-based web application for user interaction, enabling users to upload network data, analyze it for potential threats, and view results in real-time.

---

## **Features**

- **Real-Time Network Traffic Capture:** Data captured via Wireshark in `.pcap` format.
- **Preprocessing:** Automated data cleaning, feature extraction, and normalization.
- **Machine Learning:** Advanced ensemble models (TabNet, CatBoost, LightGBM) for high accuracy.
- **Web Interface:** User-friendly Django web application for file uploads and results display.
- **Visualization:** Displays predictions, confidence scores, and key parameters influencing decisions.
- **Database Integration:** Stores user uploads, model predictions, and associated metadata.

---

## **Installation and Setup**

### **Prerequisites**

1. **Operating System:** Windows 11 & Linux.
2. **Python:** Version 3.8 or later.
3. **Tools:**
   - Wireshark for network traffic capture.
   - Visual Studio Code for development.
4. **Libraries:** Install the required Python libraries:
   
 `pip install django pandas numpy scikit-learn gunicorn pyshark xgboost lightgbm pytorch-tabnet catboost matplotlib seaborn`

**OR** 
`pip install -r requirements. txt`
### **Steps to Set Up**

1. Clone the repository:
   ```bash
   git clone <https://github.com/infinity-decoder/FYP>
   cd FYP
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the Django project:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

5. Access the web app at `http://127.0.0.1:8000/`.


## **Folder Structure** ( Use `tests/schema.py`)



## **Usage Instructions**

### **Capturing Data**
1. Use Wireshark to capture network traffic and save it as a `.pcap` file.
2. Upload the `.pcap` file to the web app.

### **Analyzing Data**
1. The backend will preprocess the file and extract relevant features.
2. The ML model will classify the data into normal or malicious activities.

### **Viewing Results**
Results, including prediction labels and confidence scores, will be displayed on the web interface.

---

## **System Architecture**

The system follows a three-tier architecture:

1. **Presentation Layer:** Django-based web application for user interaction.
2. **Application Layer:** Backend logic for data preprocessing and ML inference.
3. **Data Layer:** Database for storing uploads and results.

---

## **Key Components**

### **1. Preprocessing Module**
- Converts `.pcap` files to CSV.
- Cleans and normalizes the data.
- Extracts relevant features (e.g., protocol types, IP addresses).

### **2. Machine Learning Module**
- Utilizes pre-trained models (e.g., LightGBM) for predictions.
- Implements ensemble techniques for high accuracy.

### **3. Web Interface**
- Enables file uploads and results visualization.
- Provides a simple, intuitive design for user accessibility.

---
To generate a labeled dataset containing both **benign** and **malicious (attack)** network traffic for supervised machine learning-based intrusion detection.



## *Experimental Setup*

| Component        | Description                                  |
|------------------|----------------------------------------------|
| Host Machine     | Windows 11 (Victim machine, Wireshark running) |
| Attacker Machine | Parrot OS running inside VMware (Simulated attacker) |
| Network Adapters | - Host: Built-in Wi-Fi Adapter<br>- VM: External USB Wi-Fi/Ethernet Adapter (Bridged Mode) |

Both machines are connected to the **same LAN (subnet)** to allow direct traffic flow between them.



## *Tools Used*
- **Wireshark**: For packet capture (`.pcap` files).
- **Nmap**: Simulated Port Scanning Attacks.
- **Ping Flood (ICMP)**: Simulated DoS attacks using `ping -f` and `hping3`.



## *Data Capture Procedure*

1. **Start Wireshark on the Host machine.**
   - Capture on the built-in adapter (Wi-Fi/Ethernet).
   - Save captured traffic in `.pcap` format.

2. **Simulate Attack Traffic from the VM:**
   - **Nmap Scans:**
     ```bash
     nmap -sS <host_ip>
     nmap -A <host_ip>
     ```
   - **Ping Flood:**
     ```bash
     ping -f <host_ip>
     sudo hping3 -1 --flood <host_ip>
     ```

3. **Note down the attack start and end timestamps.**
   - This helps in labeling the captured traffic accurately.

4. **Stop Wireshark after attack sessions.**





###  ML learning model usage

| Role                     | Model                             | Purpose                                                                 |
|--------------------------|------------------------------------|-------------------------------------------------------------------------|
| **Base Models (Level-0)**| CatBoost, LightGBM, XGBoost, TabNet| Train on original features and make initial predictions                 |
| **Meta Model (Level-1)**| Logistic Regression / RidgeClassifier| Learns from outputs of base models to make final prediction (**stacking**) |



---

### ✅ Recommended Notebook Structure (For ML models)
➡ **Path:** FYP/models/

| Notebook Name              | Purpose                                                 | Output Format                   |
|---------------------------|----------------------------------------------------------|----------------------------------|

| `01_catboost.ipynb`       | Train and evaluate CatBoost model                        | `.cbm` (native), or `.pkl` if needed |
| `02_lightgbm.ipynb`       | Train and evaluate LightGBM model                        | `.txt` (native), or `.pkl`      |
| `03_xgboost.ipynb`        | Train and evaluate XGBoost model                         | `.json` (native), or `.pkl`     |
| `04_tabnet.ipynb`         | Train and evaluate TabNet model                          | `.zip` (TabNet native), or `.pkl` |
| `05_stacking.ipynb`       | Combine predictions from above models, train meta-model  | `.pkl` (Logistic Regression or RidgeClassifier) |

---

### ✅ Model Saving Formats (Best for your system)

| Model        | Save Format Recommended              | Why                                         |
|--------------|--------------------------------------|----------------------------------------------|
| **CatBoost** | `.cbm` or `.pkl`                     | `.cbm` is native, `.pkl` is cross-compatible |
| **XGBoost**  | `.json` or `.pkl`                    | `.json` is native, `.pkl` better in stack    |
| **LightGBM** | `.txt` or `.pkl`                     | `.txt` is native, `.pkl` better in stack     |
| **TabNet**   | `.zip` or `.pkl`                     | `.zip` is standard, `.pkl` better for stacking |
| **Meta Model**| `.pkl`                              | Lightweight, quick to load & deploy          |

➡ My system **resource constraints (Intel i3, 8GB RAM)** make `.pkl` a great common denominator for loading everything into the stacking model without compatibility issues.

---

### ✅ Notebooks:

| Notebook Name              | Purpose                                                 | Output Format                   |
|---------------------------|----------------------------------------------------------|----------------------------------|

| `01_preprocessing.ipynb`  | Data cleaning, encoding, feature engineering              | Cleaned + encoded dataset (CSV) |
| `02_EDA.ipynb`            | Visualizations, outlier detection, feature distribution   | Charts, insights   




## **Contributors**

<h1 style="font-family: 'poppins'; font-weight: bold; color: Green;">👨‍💻Author: MAHBOOB ALAM</h1>

[![GitHub](https://img.shields.io/badge/GitHub-Profile-blue?style=for-the-badge&logo=github)](https://github.com/infinity-decoder) 
[![Kaggle](https://img.shields.io/badge/Kaggle-Profile-green?style=for-the-badge&logo=kaggle)](https://www.kaggle.com/infinitydecoder) 
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=for-the-badge&logo=linkedin)](https://pk.linkedin.com/in/infinitydecoder)  
[![Facebook](https://img.shields.io/badge/Facebook-Profile-blue?style=for-the-badge&logo=facebook)](https://www.facebook.com/infinitydecoder.me) 
[![Email](https://img.shields.io/badge/Email-Contact%20Me-red?style=for-the-badge&logo=email)](mailto:bc210427835mal@vu.edu.pk)
---

For more details, refer to the docs and media




