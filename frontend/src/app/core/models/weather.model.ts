export interface WeatherData {
  state: string;
  district: string;
  location_name: string;
  latitude: number;
  longitude: number;
  temperature: number;
  humidity: number;
  annual_rainfall: number;
  rainfall: number;
  weather_condition?: string;
  source: string;
  fetched_at: string;
}
