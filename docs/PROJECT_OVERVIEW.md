# 📌 Livestock Biometric Registry

## Project Overview

---

## 1. Project Summary

The **Livestock Biometric Registry** is a deep learning–based identification system designed to provide permanent, non-invasive biometric identity for cattle.

The system uses image-based feature embeddings extracted via a pretrained convolutional neural network and performs identity matching using cosine similarity with calibrated threshold selection.

Unlike traditional livestock identification methods (ear tags, branding, RFID), this system treats livestock identification as a **biometric verification problem**, enabling scalable and tamper-resistant registry management.

---

## 2. Problem Statement

Livestock management systems face major challenges:

- Livestock theft
- Tag removal or forgery
- Ownership disputes
- Manual record-keeping errors
- Lack of permanent identity mechanisms

Existing identification systems rely on removable or forgeable physical markers.  
This project proposes a biometric alternative using visual identity features.

---

## 3. System Objectives

The objectives of this project are to:

- Create a biometric-based livestock identity registry
- Enable secure livestock registration and verification
- Prevent duplicate registrations
- Enforce role-based access control
- Demonstrate measurable biometric performance through quantitative evaluation

---

## 4. Technical Approach

### 4.1 Embedding-Based Biometric Architecture

The system does not use traditional classification. Instead, it implements:

1. **MobileNetV2 backbone (pretrained on ImageNet)**
2. Feature extraction from convolutional layers
3. Global Average Pooling to generate 1280-dimensional embeddings
4. L2 normalization of feature vectors
5. Cosine similarity for identity matching
6. Threshold-based decision mechanism

This embedding-based approach supports **open-set recognition**, meaning new livestock can be added without retraining the entire model.

---

## 5. System Architecture

### 5.1 Processing Pipeline

### 5.2 Layered Design

The system follows a modular layered structure:

- **GUI Layer** (Tkinter multi-screen interface)
- **Core ML Layer** (Embedding & Similarity Engine)
- **Authentication Layer** (Role-based access control)
- **Data Layer** (JSON-based registry abstraction)

This separation ensures future migration to database systems such as MongoDB without redesigning the ML engine.

---

## 6. Role-Based Access Control

Two user roles are implemented:

### Authority

- Register livestock
- Perform global registry search
- Detect duplicates before registration
- Override duplicate alerts when necessary

### Farmer

- Login securely
- View only owned livestock
- Perform scoped verification limited to owned animals

This ensures ownership isolation and prevents unauthorized cross-access.

---

## 7. Duplicate Detection Mechanism

Before livestock registration:

1. An embedding is generated from the submitted image.
2. Cosine similarity is computed against stored embeddings.
3. If similarity ≥ selected threshold → duplicate alert is triggered.

This protects registry integrity and prevents identity conflicts.

---

## 8. Evaluation & Performance Validation

To validate the biometric engine, the system was tested using:

- 300 cattle identities
- 13,122 genuine comparisons
- 44,850 impostor comparisons

Multiple thresholds were evaluated to analyze biometric trade-offs.

### 8.1 Selected Operating Threshold: 0.78

Performance at this threshold:

- **False Accept Rate (FAR): 0.67%**
- **False Reject Rate (FRR): 31.16%**
- **Accuracy: 92.43%**

These results demonstrate:

- Strong duplicate protection (low FAR)
- Expected intra-class sensitivity due to lack of domain-specific fine-tuning
- Valid biometric trade-off behavior

---

## 9. Current Limitations

- Model is not fine-tuned on cattle-specific data
- No Siamese network training performed yet
- No FAISS-based vector indexing for large-scale search
- JSON storage (MongoDB migration planned)
- CPU-only evaluation

These limitations define the next phase of system enhancement.

---

## 10. Future Work

Planned improvements include:

- Siamese fine-tuning for improved intra-class robustness
- MongoDB vector storage integration
- FAISS indexing for scalable search
- Cloud deployment
- Mobile application for farmer access
- Integration with national livestock registry frameworks

---

## 11. Conclusion

The Livestock Biometric Registry demonstrates a structured, embedding-based biometric identification system with quantitative validation and scalable architecture.

The project delivers:

- A functional MVP
- Open-set biometric verification
- Role-based registry management
- Threshold calibration analysis
- Measurable biometric performance

This establishes a strong foundation for future research, deployment, and national-scale livestock identity systems.
