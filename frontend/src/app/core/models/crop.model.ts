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
}

export interface RankedCropProbability {
  crop: string;
  probability: number;
  rank: number;
}

export interface CropRecommendationResponse {
  recommended_crop: string;
  confidence: number;
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

