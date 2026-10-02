export interface PriceForecastPoint {
  day: number;
  forecasted_price: number;
  predicted_modal_price?: number;
  unit?: string;
  date_offset?: string;
}

export interface PriceForecastRequest {
  commodity: string;
  market: string;
  historical_prices: number[];
  forecast_horizon?: number;
}

export interface PriceForecastResponse {
  commodity: string;
  market: string;
  forecast_horizon_days: number;
  current_price: number;
  last_observed_price?: number;
  forecasted_end_price: number;
  predicted_end_price?: number;
  price_change_absolute: number;
  price_change_percentage: number;
  projected_percentage_change?: number;
  trend_direction: 'UPWARD' | 'DOWNWARD' | 'STABLE' | string;
  forecasts: PriceForecastPoint[];
  execution_time_ms: number;
  model_type?: string;
}
