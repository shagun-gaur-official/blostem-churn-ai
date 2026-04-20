# blostem-churn-ai
Customer Churn Prediction & Segmentation Engine for Fixed Deposit Platforms

Track: Data Analytics & Insights
Hackathon: Blostem AI Builder Hackathon 2026
Built for: Blostem's fintech infrastructure — powering 30+ platforms across India


🧠 What This Solves
Blostem's API connects 30+ fintech platforms to 10+ banks, handling thousands of Fixed Deposit customers daily. The real problem: nobody knows who's about to leave before they do.
When an FD matures, a customer either:

✅ Renews (high value, retained)
❌ Withdraws & churns (lost revenue for both Blostem and its partners)

ChurnSense AI predicts churn 30 days before maturity — giving Blostem's partners a window to intervene, personalize offers, and retain customers.

🎯 Core Features
FeatureDescriptionChurn Prediction ModelML model predicting FD renewal probability per customerCustomer SegmentationRFM + behavioral clustering into 5 actionable cohortsFunnel Drop-off AnalysisWhere users abandon the FD booking journeyPartner-level DashboardsPer-platform analytics for Blostem's B2B partnersIntervention RecommenderAI-driven nudge suggestions per churn risk segmentREST APIJSON endpoints for any partner to embed predictions

📊 Model Architecture
Raw Event Data (KYC, FD activity, platform signals)
        ↓
  Feature Engineering
  - Tenure, renewal history, platform engagement
  - FD size, interest sensitivity, bank preference
  - Time-since-last-login, support tickets, app activity
        ↓
  Gradient Boosted Classifier (XGBoost)
  + Rule-based override layer for edge cases
        ↓
  Churn Score (0–100) + Segment Label
        ↓
  Intervention API → Partner Dashboards
Validation metrics on synthetic dataset:

Accuracy: 87.4%
ROC-AUC: 0.91
Precision (high-risk): 83.2%
Recall (high-risk): 79.8%
