"""
Model Evaluation & Metrics System
Chứng minh độ chính xác, precision, recall, F1-score với logic reasoning
"""
import pandas as pd
import numpy as np
import pickle
import json
from typing import Dict, Any, List, Tuple
from datetime import datetime
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score,
    roc_curve, precision_recall_curve
)
import logging

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Comprehensive model evaluation với reasoning và logic
    """
    
    def __init__(self, model_path: str = "models/model.pkl"):
        self.model_path = model_path
        self.model = None
        self.preprocessor = None
        self._load_model()
    
    def _load_model(self):
        """Load model và preprocessor"""
        try:
            with open(self.model_path, 'rb') as f:
                saved = pickle.load(f)
                self.model = saved['model']
                self.preprocessor = saved['preprocessor']
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
    
    def evaluate(
        self,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        y_pred: np.ndarray = None,
        y_pred_proba: np.ndarray = None
    ) -> Dict[str, Any]:
        """
        Comprehensive evaluation với reasoning
        
        Returns:
            Detailed metrics với explanations
        """
        if y_pred is None:
            X_test_scaled = self.preprocessor.transform(X_test)
            y_pred = self.model.predict(X_test_scaled)
            if hasattr(self.model, 'predict_proba'):
                y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # Basic metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        # ROC AUC (if binary classification)
        roc_auc = None
        if y_pred_proba is not None and len(np.unique(y_test)) == 2:
            try:
                roc_auc = roc_auc_score(y_test, y_pred_proba)
            except:
                pass
        
        # Calculate rates
        total = len(y_test)
        positive_total = y_test.sum()
        negative_total = total - positive_total
        
        # Reasoning và logic
        reasoning = self._generate_reasoning(
            accuracy, precision, recall, f1,
            tn, fp, fn, tp, total, positive_total, negative_total
        )
        
        # Business impact metrics
        business_metrics = self._calculate_business_impact(
            tn, fp, fn, tp, total
        )
        
        return {
            'metrics': {
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'roc_auc': float(roc_auc) if roc_auc else None
            },
            'confusion_matrix': {
                'true_negatives': int(tn),
                'false_positives': int(fp),
                'false_negatives': int(fn),
                'true_positives': int(tp),
                'total': int(total)
            },
            'rates': {
                'true_positive_rate': float(tp / positive_total) if positive_total > 0 else 0,
                'true_negative_rate': float(tn / negative_total) if negative_total > 0 else 0,
                'false_positive_rate': float(fp / negative_total) if negative_total > 0 else 0,
                'false_negative_rate': float(fn / positive_total) if positive_total > 0 else 0,
                'positive_rate': float(positive_total / total) if total > 0 else 0
            },
            'reasoning': reasoning,
            'business_impact': business_metrics,
            'evaluation_date': datetime.utcnow().isoformat()
        }
    
    def _generate_reasoning(
        self,
        accuracy: float,
        precision: float,
        recall: float,
        f1: float,
        tn: int, fp: int, fn: int, tp: int,
        total: int, positive_total: int, negative_total: int
    ) -> Dict[str, Any]:
        """
        Generate reasoning và logic cho metrics
        """
        # Accuracy reasoning
        accuracy_pct = accuracy * 100
        accuracy_explanation = f"""
        **Accuracy ({accuracy_pct:.2f}%):**
        - Model dự đoán đúng {tp + tn} / {total} trường hợp
        - Tỷ lệ dự đoán chính xác tổng thể: {accuracy_pct:.2f}%
        - Logic: (True Positives + True Negatives) / Total
        - Interpretation: {"Excellent" if accuracy >= 0.95 else "Good" if accuracy >= 0.85 else "Acceptable" if accuracy >= 0.75 else "Needs Improvement"}
        """
        
        # Precision reasoning
        precision_pct = precision * 100
        precision_explanation = f"""
        **Precision ({precision_pct:.2f}%):**
        - Khi model dự đoán "Abnormal", có {precision_pct:.2f}% là đúng
        - False Positives: {fp} lần (báo động giả)
        - Logic: True Positives / (True Positives + False Positives)
        - Business Impact: Giảm {fp} lần báo động giả → Tiết kiệm chi phí bảo trì không cần thiết
        - Interpretation: {"Excellent" if precision >= 0.90 else "Good" if precision >= 0.80 else "Acceptable" if precision >= 0.70 else "Needs Improvement"}
        """
        
        # Recall reasoning
        recall_pct = recall * 100
        recall_explanation = f"""
        **Recall ({recall_pct:.2f}%):**
        - Model phát hiện được {recall_pct:.2f}% các trường hợp abnormal thực tế
        - False Negatives: {fn} lần (bỏ sót sự cố)
        - Logic: True Positives / (True Positives + False Negatives)
        - Business Impact: Bỏ sót {fn} sự cố → Có thể gây downtime, hỏng máy
        - Interpretation: {"Excellent" if recall >= 0.90 else "Good" if recall >= 0.80 else "Acceptable" if recall >= 0.70 else "Needs Improvement"}
        """
        
        # F1 Score reasoning
        f1_pct = f1 * 100
        f1_explanation = f"""
        **F1-Score ({f1_pct:.2f}%):**
        - Harmonic mean của Precision và Recall
        - Logic: 2 * (Precision * Recall) / (Precision + Recall)
        - Balance giữa Precision (tránh báo động giả) và Recall (tránh bỏ sót)
        - Interpretation: {"Excellent" if f1 >= 0.90 else "Good" if f1 >= 0.80 else "Acceptable" if f1 >= 0.70 else "Needs Improvement"}
        """
        
        # Overall assessment
        if accuracy >= 0.90 and f1 >= 0.85:
            overall = "EXCELLENT - Model đạt độ chính xác cao, sẵn sàng production"
        elif accuracy >= 0.85 and f1 >= 0.75:
            overall = "GOOD - Model tốt, có thể deploy với monitoring"
        elif accuracy >= 0.75 and f1 >= 0.65:
            overall = "ACCEPTABLE - Model chấp nhận được, cần cải thiện"
        else:
            overall = "NEEDS IMPROVEMENT - Model cần retrain hoặc tuning"
        
        return {
            'accuracy_explanation': accuracy_explanation.strip(),
            'precision_explanation': precision_explanation.strip(),
            'recall_explanation': recall_explanation.strip(),
            'f1_explanation': f1_explanation.strip(),
            'overall_assessment': overall,
            'confidence_level': self._calculate_confidence(accuracy, f1)
        }
    
    def _calculate_confidence(self, accuracy: float, f1: float) -> str:
        """Calculate confidence level"""
        avg_score = (accuracy + f1) / 2
        
        if avg_score >= 0.95:
            return "Very High (95%+)"
        elif avg_score >= 0.90:
            return "High (90-95%)"
        elif avg_score >= 0.85:
            return "Medium-High (85-90%)"
        elif avg_score >= 0.75:
            return "Medium (75-85%)"
        else:
            return "Low (<75%)"
    
    def _calculate_business_impact(
        self,
        tn: int, fp: int, fn: int, tp: int,
        total: int
    ) -> Dict[str, Any]:
        """
        Tính toán business impact của model
        """
        # Cost assumptions (có thể config)
        cost_false_positive = 50  # USD - Chi phí bảo trì không cần thiết
        cost_false_negative = 500  # USD - Chi phí downtime + hỏng máy
        cost_true_positive = 200  # USD - Chi phí bảo trì đúng lúc
        cost_true_negative = 0  # USD - Không có chi phí
        
        # Calculate costs
        total_cost = (
            fp * cost_false_positive +
            fn * cost_false_negative +
            tp * cost_true_positive +
            tn * cost_true_negative
        )
        
        # Ideal cost (perfect model)
        ideal_cost = tp * cost_true_positive
        
        # Cost savings
        cost_savings = ideal_cost - (fp * cost_false_positive + fn * cost_false_negative)
        cost_savings_pct = (cost_savings / ideal_cost * 100) if ideal_cost > 0 else 0
        
        return {
            'false_positive_cost': fp * cost_false_positive,
            'false_negative_cost': fn * cost_false_negative,
            'true_positive_cost': tp * cost_true_positive,
            'total_cost': total_cost,
            'ideal_cost': ideal_cost,
            'cost_savings': cost_savings,
            'cost_savings_percentage': cost_savings_pct,
            'roi': f"{cost_savings_pct:.1f}% cost reduction vs perfect model"
        }
    
    def generate_report(self, evaluation_result: Dict[str, Any]) -> str:
        """
        Generate human-readable evaluation report
        """
        metrics = evaluation_result['metrics']
        reasoning = evaluation_result['reasoning']
        business = evaluation_result['business_impact']
        
        report = f"""
# Model Evaluation Report

## 📊 Performance Metrics

### Overall Accuracy: {metrics['accuracy']*100:.2f}%
{reasoning['accuracy_explanation']}

### Precision: {metrics['precision']*100:.2f}%
{reasoning['precision_explanation']}

### Recall: {metrics['recall']*100:.2f}%
{reasoning['recall_explanation']}

### F1-Score: {metrics['f1_score']*100:.2f}%
{reasoning['f1_explanation']}

## 🎯 Overall Assessment
{reasoning['overall_assessment']}

**Confidence Level:** {reasoning['confidence_level']}

## 💰 Business Impact
- **False Positive Cost:** ${business['false_positive_cost']:,.2f}
- **False Negative Cost:** ${business['false_negative_cost']:,.2f}
- **Total Cost Savings:** ${business['cost_savings']:,.2f} ({business['cost_savings_percentage']:.1f}%)
- **ROI:** {business['roi']}

## 📈 Confusion Matrix
- True Positives: {evaluation_result['confusion_matrix']['true_positives']}
- True Negatives: {evaluation_result['confusion_matrix']['true_negatives']}
- False Positives: {evaluation_result['confusion_matrix']['false_positives']}
- False Negatives: {evaluation_result['confusion_matrix']['false_negatives']}

---
*Generated at: {evaluation_result['evaluation_date']}*
"""
        return report.strip()

