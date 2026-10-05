import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';
import { CropRecommendationComponent } from './crop-recommendation.component';
import { CropService } from '../../core/services/crop.service';
import { WeatherService } from '../../core/services/weather.service';
import { STATE_DISTRICTS } from '../../core/constants/locations.constant';

describe('CropRecommendationComponent', () => {
  let component: CropRecommendationComponent;
  let cropServiceSpy: any;
  let weatherServiceSpy: any;

  beforeEach(async () => {
    cropServiceSpy = {
      recommendCrop: () => of({
        success: true,
        data: {
          recommended_crop: 'soybean',
          confidence: 0.88,
          suitability: 'Highly Suitable',
          recommendations: [
            { crop: 'soybean', probability: 0.88, model_score: 0.88, agronomic_score: 95.0, composite_score: 91.5, suitability: 'Highly Suitable', rank: 1 },
            { crop: 'cotton', probability: 0.08, model_score: 0.08, agronomic_score: 75.0, composite_score: 41.5, suitability: 'Suitable', rank: 2 }
          ],
          top_recommendations: [
            { crop: 'soybean', probability: 0.88, model_score: 0.88, agronomic_score: 95.0, composite_score: 91.5, suitability: 'Highly Suitable', rank: 1 },
            { crop: 'cotton', probability: 0.08, model_score: 0.08, agronomic_score: 75.0, composite_score: 41.5, suitability: 'Suitable', rank: 2 }
          ],
          input_parameters: { N: 35, P: 70, K: 45, temperature: 26.0, humidity: 68.0, ph: 6.7, rainfall: 1050.0 },
          execution_time_ms: 10.5,
          model_type: 'Bidirectional LSTM (30 classes) + ICAR Agronomic Suitability Engine'
        }
      })
    };

    weatherServiceSpy = {
      getWeather: (state: string, district: string) => of({
        success: true,
        data: {
          state: state,
          district: district,
          location_name: `${district}, ${state}, India`,
          latitude: 21.1458,
          longitude: 79.0882,
          temperature: 31.5,
          humidity: 58.0,
          annual_rainfall: 1050.0,
          rainfall: 1050.0,
          weather_condition: 'Clear sky',
          source: 'Open-Meteo & IMD Climate Normals',
          fetched_at: '2026-10-05T12:00:00Z'
        }
      })
    };

    await TestBed.configureTestingModule({
      imports: [CropRecommendationComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: CropService, useValue: cropServiceSpy },
        { provide: WeatherService, useValue: weatherServiceSpy }
      ]
    }).compileComponents();

    const fixture = TestBed.createComponent(CropRecommendationComponent);
    component = fixture.componentInstance;
    component.ngOnInit();
  });

  it('should initialize with default parameters and dependent districts populated', () => {
    expect(component).toBeTruthy();
    expect(component.cropForm.valid).toBe(true);
    expect(component.cropForm.get('N')?.value).toBe(35);
    expect(component.cropForm.get('state')?.value).toBe('Maharashtra');
    expect(component.cropForm.get('district')?.value).toBe('Nagpur');
    expect(component.availableDistricts().length).toBeGreaterThan(0);
    expect(component.availableDistricts()).toContain('Nagpur');
  });

  it('should filter districts when state changes and reset district & weather values', () => {
    // Change state to Gujarat
    component.onStateChange('Gujarat');

    // 1. Verify district field is cleared
    expect(component.cropForm.get('district')?.value).toBe('');

    // 2. Verify weather values are reset
    expect(component.cropForm.get('temperature')?.value).toBeNull();
    expect(component.cropForm.get('humidity')?.value).toBeNull();
    expect(component.cropForm.get('rainfall')?.value).toBeNull();

    // 3. Verify available districts contain ONLY Gujarat districts
    const gujaratDistricts = STATE_DISTRICTS['Gujarat'];
    expect(component.availableDistricts()).toEqual(gujaratDistricts);
    expect(component.availableDistricts()).toContain('Ahmedabad');
    expect(component.availableDistricts()).not.toContain('Nagpur');
  });

  it('should auto-fetch and populate weather & annual rainfall when district is selected', () => {
    component.onStateChange('Maharashtra');
    component.onDistrictChange('Nagpur');

    expect(component.isWeatherLoading()).toBe(false);
    expect(component.weatherData()).toBeTruthy();
    expect(component.weatherData()?.district).toBe('Nagpur');
    expect(component.cropForm.get('temperature')?.value).toBe(31.5);
    expect(component.cropForm.get('humidity')?.value).toBe(58.0);
    expect(component.cropForm.get('rainfall')?.value).toBe(1050.0);
  });

  it('should handle weather API failure and display error message', () => {
    weatherServiceSpy.getWeather = () => throwError(() => new Error('Network error'));
    component.fetchWeather('Maharashtra', 'Akola');

    expect(component.isWeatherLoading()).toBe(false);
    expect(component.weatherError()).toBe('Unable to fetch weather data for this location. Please try again.');
  });

  it('should apply presets correctly with state and district mapping', () => {
    const wheatPreset = component.presets.find((p) => p.name.includes('Wheat'));
    expect(wheatPreset).toBeDefined();
    component.applyPreset(wheatPreset!);
    expect(component.cropForm.get('N')?.value).toBe(110);
    expect(component.cropForm.get('P')?.value).toBe(55);
    expect(component.cropForm.get('state')?.value).toBe('Punjab');
    expect(component.cropForm.get('district')?.value).toBe('Ludhiana');
    expect(component.availableDistricts()).toContain('Ludhiana');
  });

  it('should trigger inference and update chart data', () => {
    component.onSubmit();
    expect(component.result()).toBeTruthy();
    expect(component.result()?.recommended_crop).toBe('soybean');
    expect(component.barChartData.labels?.length).toBe(2);
  });
});
