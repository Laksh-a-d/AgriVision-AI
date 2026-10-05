import time
import logging
from typing import Dict, Any, List, Optional
from app.schemas.crop import (
    CropRecommendationRequest,
    CropRecommendationItem,
    CropRecommendationResponse
)
from ml.crop_recommendation.model.predict import predict_all_crop_probabilities
from ml.crop_recommendation.agronomic_suitability import (
    rank_recommendations_with_suitability,
    calculate_crop_agronomic_suitability
)

logger = logging.getLogger("agripulse.services.crop")


class CropRecommendationService:
    """
    Business service layer executing AI crop recommendation inference,
    ICAR agronomic suitability ranking, out-of-distribution anomaly diagnostics,
    and location contextualization.
    """

    @staticmethod
    def _detect_ood_anomalies(request: CropRecommendationRequest) -> List[str]:
        """
        Diagnoses out-of-distribution (OOD) inputs relative to the ICAR training dataset envelope.
        Does NOT alter raw neural network inference, but provides transparent agronomic feedback.
        """
        warnings: List[str] = []

        # Rainfall analysis (Annual bounds: 200 mm - 3200 mm)
        if request.rainfall > 3200.0:
            warnings.append(
                f"Rainfall ({request.rainfall:.1f} mm) exceeds typical Indian agricultural bounds (max 3200 mm/year)."
            )
        elif request.rainfall < 200.0:
            warnings.append(
                f"Rainfall ({request.rainfall:.1f} mm) is extremely low (<200 mm/year), representing hyper-arid desert conditions."
            )

        # Potassium analysis (bounds: 5.0 - 225.0 kg/ha)
        if request.K > 225.0:
            warnings.append(
                f"Potassium ({request.K:.1f} kg/ha) exceeds typical ICAR crop maximum (225 kg/ha)."
            )

        # Nitrogen bounds (0 - 180 kg/ha)
        if request.N > 180.0:
            warnings.append(
                f"Nitrogen ({request.N:.1f} kg/ha) is extremely high (>180 kg/ha), suitable mainly for intensive sugarcane."
            )

        # Phosphorus bounds (5 - 160 kg/ha)
        if request.P > 160.0:
            warnings.append(
                f"Phosphorus ({request.P:.1f} kg/ha) exceeds standard crop envelopes (160 kg/ha)."
            )
        elif request.P < 5.0:
            warnings.append(
                f"Phosphorus ({request.P:.1f} kg/ha) is critically deficient (<5 kg/ha)."
            )

        # Temperature bounds (4.0 - 45.0 °C)
        if request.temperature > 45.0 or request.temperature < 4.0:
            warnings.append(
                f"Temperature ({request.temperature:.1f} °C) is outside viable crop cultivation envelope (4 °C - 45 °C)."
            )

        # Humidity bounds (15.0 - 98.0 %)
        if request.humidity < 15.0:
            warnings.append(
                f"Relative Humidity ({request.humidity:.1f} %) is below 15% (extreme arid desiccation risk)."
            )

        # Soil pH bounds (4.5 - 9.0)
        if request.ph > 9.0 or request.ph < 4.5:
            warnings.append(
                f"Soil pH ({request.ph:.1f}) is outside typical agricultural limits (4.5 - 9.0)."
            )

        return warnings

    @classmethod
    def recommend(cls, request: CropRecommendationRequest) -> CropRecommendationResponse:
        t0 = time.time()
        logger.debug(f"Processing crop recommendation for inputs: {request.model_dump()}")

        # 1. Obtain raw neural network probabilities for all 30 classes (completely unmanipulated)
        all_raw_preds = predict_all_crop_probabilities(
            n=request.N,
            p=request.P,
            k=request.K,
            temperature=request.temperature,
            humidity=request.humidity,
            ph=request.ph,
            rainfall=request.rainfall
        )

        # 2. Evaluate and rank recommendations through the ICAR Agronomic Suitability Engine
        ranked_results = rank_recommendations_with_suitability(
            raw_model_predictions=all_raw_preds,
            n=request.N,
            p=request.P,
            k=request.K,
            temperature=request.temperature,
            humidity=request.humidity,
            ph=request.ph,
            rainfall=request.rainfall,
            season=request.season,
            top_k=request.top_k
        )

        execution_ms = round((time.time() - t0) * 1000.0, 2)
        top_crop = ranked_results[0]["crop"]
        top_confidence = ranked_results[0]["probability"]
        top_suitability = ranked_results[0]["suitability"]

        items = [
            CropRecommendationItem(
                crop=item["crop"],
                probability=item["probability"],
                model_score=item["model_score"],
                agronomic_score=item["agronomic_score"],
                composite_score=item["composite_score"],
                suitability=item["suitability"],
                is_feasible=item["is_feasible"],
                is_perennial=item.get("is_perennial", False),
                is_season_compatible=item.get("is_season_compatible", True),
                is_primary=item.get("is_primary", True),
                recommendation_level=item.get("recommendation_level", "PRIMARY"),
                quadrant=item.get("quadrant"),
                rationale=item["rationale"],
                rank=item["rank"]
            )
            for item in ranked_results
        ]

        primary_items = [it for it in items if it.is_primary]
        secondary_items = [it for it in items if not it.is_primary]

        # Top crop is the leading primary recommendation
        top_crop_item = primary_items[0] if primary_items else items[0]
        top_crop = top_crop_item.crop
        top_confidence = top_crop_item.probability
        top_suitability = top_crop_item.suitability

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
            f"Subsystem 3A Recommended {top_crop} (Model: {top_confidence * 100:.1f}%, "
            f"Suitability: {top_suitability}, Primary={len(primary_items)}, Secondary={len(secondary_items)}) in {execution_ms}ms | OOD={is_ood}"
        )

        return CropRecommendationResponse(
            recommended_crop=top_crop,
            confidence=top_confidence,
            suitability=top_suitability,
            primary_recommendations=primary_items,
            secondary_recommendations=secondary_items,
            recommendations=primary_items if primary_items else items,
            top_recommendations=primary_items if primary_items else items,
            input_parameters=input_params,
            execution_time_ms=execution_ms,
            model_type="Bidirectional LSTM (30 classes) + ICAR Agronomic Suitability Engine",
            out_of_distribution=is_ood,
            ood_warnings=ood_warnings,
            location_context=location_ctx
        )
