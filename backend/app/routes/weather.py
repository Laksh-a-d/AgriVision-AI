from fastapi import APIRouter, Query, status, HTTPException
from app.schemas.common import ApiResponse
from app.schemas.weather import WeatherData
from app.services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["Weather & Climate Intelligence"])


@router.get(
    "",
    response_model=ApiResponse[WeatherData],
    status_code=status.HTTP_200_OK,
    summary="Get District Weather and Annual Rainfall",
    description=(
        "Retrieves real-time atmospheric conditions (Temperature, Humidity) "
        "and official IMD normal annual rainfall for a specified Indian State and District."
    )
)
@router.get(
    "/current",
    response_model=ApiResponse[WeatherData],
    status_code=status.HTTP_200_OK,
    summary="Get Current District Weather and Annual Rainfall",
    description="Alias endpoint to retrieve real-time weather and IMD normal rainfall."
)
def get_district_weather(
    state: str = Query(..., min_length=2, description="Indian State / Union Territory name (e.g. Maharashtra, Punjab)"),
    district: str = Query(..., min_length=2, description="District name (e.g. Nagpur, Ludhiana)")
) -> ApiResponse[WeatherData]:
    if not state.strip() or not district.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State and District parameters must not be empty."
        )

    try:
        data = WeatherService.get_weather(state=state, district=district)
        return ApiResponse[WeatherData](
            success=True,
            data=data,
            message=f"Weather and climate data retrieved for {district}, {state}."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve weather data for {district}, {state}: {str(e)}"
        )
