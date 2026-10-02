import time
import logging
from typing import Dict, Any, List, Optional
from app.schemas.crop import (
    CropRecommendationRequest,
    CropRecommendationItem,
    CropRecommendationResponse
)
from ml.crop_recommendation.model.predict import predict_crop_recommendation

logger = logging.getLogger("agripulse.services.crop")


class CropRecommendationService:
    """
    Business service layer executing AI crop recommendation inference,
    out-of-distribution anomaly diagnostics, and location contextualization.
    """

    @staticmethod
    def _detect_ood_anomalies(request: CropRecommendationRequest) -> List[str]:
        """
        Diagnoses out-of-distribution (OOD) inputs relative to the training dataset envelope.
        Does NOT alter raw neural network inference, but provides transparent agronomic feedback.
        """
        warnings: List[str] = []

        # Rainfall analysis (Training bounds: 20.21mm - 298.56mm)
        if request.rainfall > 298.56:
            warnings.append(
                f"Rainfall ({request.rainfall:.1f} mm) exceeds the training dataset envelope (max 298.6 mm). "
                f"Note: Subsystem 3A expects seasonal crop-cycle rainfall rather than cumulative annual rainfall."
            )
        elif request.rainfall < 20.21:
            warnings.append(
                f"Rainfall ({request.rainfall:.1f} mm) is below training dataset minimum (20.2 mm)."
            )

        # Potassium analysis (Training bounds: 5.0 - 205.0 kg/ha)
        if request.K > 205.0:
            warnings.append(
                f"Potassium ({request.K:.1f} kg/ha) exceeds training maximum (205 kg/ha)."
            )
        elif request.K >= 190.0 and (request.N > 60.0 or request.P < 100.0):
            warnings.append(
                f"Potassium ({request.K:.1f} kg/ha) is extremely high for standard field crops. "
                f"In the training dataset, K >= 190 kg/ha occurs exclusively in plantation fruits (apple, grapes) "
                f"with high phosphorus (P > 120) and low nitrogen (N < 40). "
                f"Field crops like cotton or maize typically require K between 15-30 kg/ha."
            )

        # Nitrogen bounds (0 - 140 kg/ha)
        if request.N > 140.0:
            warnings.append(
                f"Nitrogen ({request.N:.1f} kg/ha) exceeds training maximum (140 kg/ha)."
            )

        # Phosphorus bounds (5 - 145 kg/ha)
        if request.P > 145.0:
            warnings.append(
                f"Phosphorus ({request.P:.1f} kg/ha) exceeds training maximum (145 kg/ha)."
            )
        elif request.P < 5.0:
            warnings.append(
                f"Phosphorus ({request.P:.1f} kg/ha) is below training minimum (5 kg/ha)."
            )

        # Temperature bounds (8.83 - 43.68 °C)
        if request.temperature > 43.68 or request.temperature < 8.83:
            warnings.append(
                f"Temperature ({request.temperature:.1f} °C) is outside typical training range (8.8 °C - 43.7 °C)."
            )

        # Humidity bounds (14.26 - 100.0 %)
        if request.humidity < 14.26:
            warnings.append(
                f"Humidity ({request.humidity:.1f} %) is below training dataset minimum (14.3 %)."
            )

        # Soil pH bounds (3.50 - 9.94)
        if request.ph > 9.94 or request.ph < 3.50:
            warnings.append(
                f"Soil pH ({request.ph:.1f}) is outside typical training bounds (3.5 - 9.9)."
            )

        return warnings

    @classmethod
    def recommend(cls, request: CropRecommendationRequest) -> CropRecommendationResponse:
        t0 = time.time()
        logger.debug(f"Processing crop recommendation for inputs: {request.model_dump()}")

        raw_preds = predict_crop_recommendation(
            n=request.N,
            p=request.P,
            k=request.K,
            temperature=request.temperature,
            humidity=request.humidity,
            ph=request.ph,
            rainfall=request.rainfall,
            top_k=request.top_k
        )

        execution_ms = round((time.time() - t0) * 1000.0, 2)
        top_crop = raw_preds[0]["crop"]
        top_confidence = raw_preds[0]["probability"]

        items = [
            CropRecommendationItem(
                crop=item["crop"],
                probability=item["probability"],
                rank=idx + 1
            )
            for idx, item in enumerate(raw_preds)
        ]

        ood_warnings = cls._detect_ood_anomalies(request)
        is_ood = len(ood_warnings) > 0

        location_ctx = None
        if request.state or request.district or request.country:
            location_ctx = {
                "country": request.country or "India",
                "state": request.state,
                "district": request.district
            }

        input_params = {
            "N": request.N,
            "P": request.P,
            "K": request.K,
            "temperature": request.temperature,
            "humidity": request.humidity,
            "ph": request.ph,
            "rainfall": request.rainfall
        }

        logger.info(
            f"Subsystem 3A Recommended {top_crop} ({top_confidence * 100:.1f}%) "
            f"in {execution_ms}ms | OOD={is_ood}"
        )

        return CropRecommendationResponse(
            recommended_crop=top_crop,
            confidence=top_confidence,
            recommendations=items,
            top_recommendations=items,
            input_parameters=input_params,
            execution_time_ms=execution_ms,
            model_type="Bidirectional LSTM (22 classes)",
            out_of_distribution=is_ood,
            ood_warnings=ood_warnings,
            location_context=location_ctx
        )
