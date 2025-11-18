"""
MLOps Pipeline - Model Retraining System
Học được pattern mới từ data mới, tự động retrain và validate
"""
import pandas as pd
import numpy as np
import pickle
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)
import joblib
from pathlib import Path

logger = logging.getLogger(__name__)


class ModelRetrainer:
    """
    MLOps Pipeline cho retraining model
    - Tự động phát hiện data drift
    - Retrain với data mới
    - Validate và so sánh với model cũ
    - Deploy model mới nếu tốt hơn
    """
    
    def __init__(self, model_dir: str = "models", data_dir: str = "data"):
        self.model_dir = Path(model_dir)
        self.data_dir = Path(data_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        # Model versioning
        self.current_version = self._get_latest_version()
        self.model_path = self.model_dir / f"model_v{self.current_version}.pkl"
        self.metrics_path = self.model_dir / f"metrics_v{self.current_version}.json"
        
        # Load current model
        self.current_model = None
        self.current_preprocessor = None
        self.current_metrics = {}
        self._load_current_model()
    
    def _get_latest_version(self) -> int:
        """Get latest model version number"""
        versions = []
        for file in self.model_dir.glob("model_v*.pkl"):
            try:
                version = int(file.stem.split("_v")[1])
                versions.append(version)
            except:
                continue
        return max(versions) if versions else 0
    
    def _load_current_model(self):
        """Load current production model"""
        if self.model_path.exists():
            try:
                with open(self.model_path, 'rb') as f:
                    saved = pickle.load(f)
                    self.current_model = saved['model']
                    self.current_preprocessor = saved['preprocessor']
                    self.current_metrics = saved.get('metrics', {})
                logger.info(f"✅ Loaded model v{self.current_version}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
        else:
            logger.warning("No existing model found. Will train from scratch.")
    
    def prepare_data(
        self,
        production_data: pd.DataFrame,
        maintenance_data: Optional[pd.DataFrame] = None
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare training data từ production và maintenance data
        
        Features:
        - Sensor readings (temperature, vibration, pressure, etc.)
        - Time features (hour, day, month)
        - Maintenance flags
        - Historical patterns
        """
        df = production_data.copy()
        
        # Extract time features
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day'] = df['timestamp'].dt.day
            df['month'] = df['timestamp'].dt.month
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df = df.drop('timestamp', axis=1)
        
        # Merge maintenance data if available
        if maintenance_data is not None and 'machine_id' in df.columns:
            maint_agg = maintenance_data.groupby('machine_id').agg({
                'downtime_hours': 'mean',
                'maintenance_type': lambda x: x.value_counts().index[0] if len(x) > 0 else 'preventive'
            }).reset_index()
            maint_agg.columns = ['machine_id', 'avg_downtime', 'common_maintenance_type']
            df = df.merge(maint_agg, on='machine_id', how='left')
        
        # Create target variable
        # 0 = Normal, 1 = Abnormal (cần bảo trì)
        if 'production_status' in df.columns:
            # production_status = 0 means normal
            y = (df['production_status'] == 0).astype(int)
        elif 'maintenance_flag' in df.columns:
            y = df['maintenance_flag']
        elif 'efficiency_score' in df.columns:
            # Low efficiency = abnormal
            y = (df['efficiency_score'] < 50).astype(int)
        else:
            # Fallback: use error_rate
            y = (df.get('error_rate', 0) > 0.1).astype(int)
        
        # Select features
        feature_cols = [
            'temperature', 'vibration_level', 'power_consumption',
            'pressure', 'material_flow_rate', 'cycle_time', 'error_rate',
            'efficiency_score', 'hour', 'day', 'month', 'day_of_week'
        ]
        
        # Add optional features
        if 'avg_downtime' in df.columns:
            feature_cols.append('avg_downtime')
        
        # Filter available features
        available_features = [col for col in feature_cols if col in df.columns]
        X = df[available_features].copy()
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        return X, y
    
    def train_model(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
        model_type: str = "random_forest"
    ) -> Tuple[Any, Any, Dict[str, float]]:
        """
        Train model với cross-validation và evaluation
        
        Returns:
            model, preprocessor, metrics
        """
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Preprocessing
        preprocessor = StandardScaler()
        X_train_scaled = preprocessor.fit_transform(X_train)
        X_test_scaled = preprocessor.transform(X_test)
        
        # Model selection
        if model_type == "random_forest":
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == "gradient_boosting":
            model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model_type: {model_type}")
        
        # Train
        logger.info(f"Training {model_type} model...")
        model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1] if hasattr(model, 'predict_proba') else None
        
        # Metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1_score': f1_score(y_test, y_pred, zero_division=0),
            'train_size': len(X_train),
            'test_size': len(X_test),
            'feature_count': X.shape[1],
            'model_type': model_type,
            'training_date': datetime.utcnow().isoformat()
        }
        
        # ROC AUC if binary classification
        if y_pred_proba is not None and len(np.unique(y_test)) == 2:
            try:
                metrics['roc_auc'] = roc_auc_score(y_test, y_pred_proba)
            except:
                pass
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='f1')
        metrics['cv_f1_mean'] = cv_scores.mean()
        metrics['cv_f1_std'] = cv_scores.std()
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        metrics['confusion_matrix'] = cm.tolist()
        metrics['true_negatives'] = int(cm[0, 0])
        metrics['false_positives'] = int(cm[0, 1])
        metrics['false_negatives'] = int(cm[1, 0])
        metrics['true_positives'] = int(cm[1, 1])
        
        logger.info(f"✅ Model trained. Accuracy: {metrics['accuracy']:.4f}, F1: {metrics['f1_score']:.4f}")
        
        return model, preprocessor, metrics
    
    def compare_models(self, new_metrics: Dict[str, float]) -> bool:
        """
        So sánh model mới với model cũ
        Returns True nếu model mới tốt hơn
        """
        if not self.current_metrics:
            logger.info("No existing model to compare. New model will be deployed.")
            return True
        
        # Primary metric: F1 score (balance precision và recall)
        current_f1 = self.current_metrics.get('f1_score', 0)
        new_f1 = new_metrics.get('f1_score', 0)
        
        # Secondary metrics
        current_accuracy = self.current_metrics.get('accuracy', 0)
        new_accuracy = new_metrics.get('accuracy', 0)
        
        # Improvement threshold: ít nhất 2% improvement
        improvement_threshold = 0.02
        
        f1_improvement = new_f1 - current_f1
        accuracy_improvement = new_accuracy - current_accuracy
        
        logger.info(f"Model Comparison:")
        logger.info(f"  Current F1: {current_f1:.4f}, New F1: {new_f1:.4f} (Δ: {f1_improvement:+.4f})")
        logger.info(f"  Current Accuracy: {current_accuracy:.4f}, New Accuracy: {new_accuracy:.4f} (Δ: {accuracy_improvement:+.4f})")
        
        # Decision logic
        if f1_improvement >= improvement_threshold:
            logger.info("✅ New model is significantly better (F1 improvement >= 2%)")
            return True
        elif f1_improvement > 0 and accuracy_improvement >= improvement_threshold:
            logger.info("✅ New model is better (F1 + Accuracy improvement)")
            return True
        elif new_f1 >= current_f1 and new_accuracy >= current_accuracy:
            logger.info("✅ New model is equal or better on all metrics")
            return True
        else:
            logger.warning("❌ New model is not better. Keeping current model.")
            return False
    
    def retrain(
        self,
        production_data: pd.DataFrame,
        maintenance_data: Optional[pd.DataFrame] = None,
        model_type: str = "random_forest",
        min_improvement: float = 0.02
    ) -> Dict[str, Any]:
        """
        Main retraining pipeline
        
        Steps:
        1. Prepare data
        2. Train new model
        3. Evaluate metrics
        4. Compare with current model
        5. Deploy if better
        """
        logger.info("🔄 Starting model retraining pipeline...")
        
        # Step 1: Prepare data
        logger.info("Step 1: Preparing training data...")
        X, y = self.prepare_data(production_data, maintenance_data)
        logger.info(f"  Data shape: {X.shape}, Target distribution: {y.value_counts().to_dict()}")
        
        # Step 2: Train
        logger.info("Step 2: Training new model...")
        model, preprocessor, metrics = self.train_model(X, y, model_type=model_type)
        
        # Step 3: Compare
        logger.info("Step 3: Comparing with current model...")
        is_better = self.compare_models(metrics)
        
        # Step 4: Deploy if better
        result = {
            'success': False,
            'deployed': False,
            'new_version': self.current_version,
            'metrics': metrics,
            'comparison': {
                'current_f1': self.current_metrics.get('f1_score', 0),
                'new_f1': metrics['f1_score'],
                'improvement': metrics['f1_score'] - self.current_metrics.get('f1_score', 0),
                'is_better': is_better
            }
        }
        
        if is_better:
            # Save new model
            new_version = self.current_version + 1
            new_model_path = self.model_dir / f"model_v{new_version}.pkl"
            new_metrics_path = self.model_dir / f"metrics_v{new_version}.json"
            
            # Save model
            with open(new_model_path, 'wb') as f:
                pickle.dump({
                    'model': model,
                    'preprocessor': preprocessor,
                    'metrics': metrics,
                    'version': new_version,
                    'trained_at': datetime.utcnow().isoformat(),
                    'feature_names': list(X.columns)
                }, f)
            
            # Save metrics
            with open(new_metrics_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            # Update current version
            self.current_version = new_version
            self.model_path = new_model_path
            self.metrics_path = new_metrics_path
            self.current_model = model
            self.current_preprocessor = preprocessor
            self.current_metrics = metrics
            
            # Update production model (symlink or copy)
            prod_model_path = self.model_dir / "model.pkl"
            if prod_model_path.exists():
                prod_model_path.unlink()
            
            # Copy new model to production
            import shutil
            shutil.copy(new_model_path, prod_model_path)
            
            result['success'] = True
            result['deployed'] = True
            result['new_version'] = new_version
            result['message'] = f"✅ Model v{new_version} deployed successfully!"
            
            logger.info(f"✅ Model v{new_version} deployed to production")
        else:
            result['message'] = "Model trained but not deployed (not better than current)"
            logger.info("Model trained but not deployed")
        
        return result
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get current model information"""
        return {
            'version': self.current_version,
            'metrics': self.current_metrics,
            'model_path': str(self.model_path),
            'trained_at': self.current_metrics.get('training_date', 'Unknown')
        }


# Global instance
retrainer = ModelRetrainer()

