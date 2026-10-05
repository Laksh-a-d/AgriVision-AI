export interface CropRecommendationRequest {
  N: number;
  P: number;
  K: number;
  temperature: number;
  humidity: number;
  ph: number;
  rainfall: number;
  top_k?: number;
  country?: string;
  state?: string;
  district?: string;
  season?: string;
}

export interface RankedCropProbability {
  crop: string;
  probability: number;
  model_score?: number;
  agronomic_score?: number;
  composite_score?: number;
  suitability?: string;
  is_feasible?: boolean;
  is_perennial?: boolean;
  is_season_compatible?: boolean;
  is_primary?: boolean;
  recommendation_level?: string;
  quadrant?: string;
  rationale?: string;
  rank: number;
}

export interface CropRecommendationResponse {
  recommended_crop: string;
  confidence: number;
  suitability?: string;
  primary_recommendations?: RankedCropProbability[];
  secondary_recommendations?: RankedCropProbability[];
  recommendations: RankedCropProbability[];
  top_recommendations: RankedCropProbability[];
  input_parameters: { [key: string]: number };
  execution_time_ms: number;
  model_type: string;
  out_of_distribution?: boolean;
  ood_warnings?: string[];
  location_context?: {
    country?: string;
    state?: string;
    district?: string;
  };
}
