import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData } from 'chart.js';
import { CropService } from '../../core/services/crop.service';
import { WeatherService } from '../../core/services/weather.service';
import { CropRecommendationResponse, RankedCropProbability } from '../../core/models/crop.model';
import { WeatherData } from '../../core/models/weather.model';
import { STATE_DISTRICTS } from '../../core/constants/locations.constant';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';

interface PresetOption {
  name: string;
  region: string;
  description: string;
  values: {
    N: number;
    P: number;
    K: number;
    temperature: number;
    humidity: number;
    ph: number;
    rainfall: number;
    state?: string;
    district?: string;
  };
}

interface CropAgroInfo {
  type: string;
  season: string;
  soil: string;
  waterNeed: string;
}

@Component({
  selector: 'app-crop-recommendation',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, BaseChartDirective, LoadingSpinnerComponent],
  templateUrl: './crop-recommendation.component.html',
  styleUrl: './crop-recommendation.component.css'
})
export class CropRecommendationComponent implements OnInit {
  private fb = inject(FormBuilder);
  private cropService = inject(CropService);
  private weatherService = inject(WeatherService);

  public isLoading = signal<boolean>(false);
  public isWeatherLoading = signal<boolean>(false);
  public weatherError = signal<string | null>(null);
  public weatherData = signal<WeatherData | null>(null);
  public errorMessage = signal<string | null>(null);
  public result = signal<CropRecommendationResponse | null>(null);

  public readonly states: string[] = Object.keys(STATE_DISTRICTS).sort();
  public availableDistricts = signal<string[]>([]);

  public readonly cropCatalog: Record<string, CropAgroInfo> = {
    rice: { type: 'Cereal Grain', season: 'Kharif', soil: 'Clayey / Alluvial Loam', waterNeed: 'High (1000-2500 mm/yr)' },
    wheat: { type: 'Rabi Cereal', season: 'Rabi', soil: 'Well-drained Fertile Loam', waterNeed: 'Low-Moderate (350-750 mm/yr)' },
    maize: { type: 'Cereal / Fodder', season: 'Kharif / Rabi', soil: 'Well-drained Loam', waterNeed: 'Moderate (500-1000 mm/yr)' },
    soybean: { type: 'Oilseed / Legume', season: 'Kharif', soil: 'Fertile Loam / Black Soil', waterNeed: 'Moderate (600-1100 mm/yr)' },
    cotton: { type: 'Fiber / Cash Crop', season: 'Kharif', soil: 'Deep Black Cotton (Vertisol)', waterNeed: 'Moderate (600-1100 mm/yr)' },
    chickpea: { type: 'Rabi Pulse', season: 'Rabi', soil: 'Sandy Loam / Black Soil', waterNeed: 'Low (350-700 mm/yr)' },
    pigeonpeas: { type: 'Pulse / Legume', season: 'Kharif', soil: 'Deep Loam / Vertisol', waterNeed: 'Moderate (600-1000 mm/yr)' },
    sorghum: { type: 'Coarse Millet (Jowar)', season: 'Kharif / Rabi', soil: 'Medium to Heavy Loam', waterNeed: 'Low-Moderate (400-800 mm/yr)' },
    pearl_millet: { type: 'Arid Millet (Bajra)', season: 'Kharif', soil: 'Light Sandy Loam', waterNeed: 'Low (300-650 mm/yr)' },
    groundnut: { type: 'Oilseed / Legume', season: 'Kharif / Summer', soil: 'Sandy Loam / Red Soil', waterNeed: 'Moderate (500-950 mm/yr)' },
    mustard: { type: 'Rabi Oilseed', season: 'Rabi', soil: 'Alluvial Loam / Sandy Loam', waterNeed: 'Low-Moderate (350-650 mm/yr)' },
    sunflower: { type: 'Oilseed Crop', season: 'Kharif / Rabi', soil: 'Well-drained Fertile Loam', waterNeed: 'Moderate (450-850 mm/yr)' },
    sugarcane: { type: 'Commercial Cash Crop', season: 'Perennial (12-18m)', soil: 'Deep Rich Loam / Alluvium', waterNeed: 'High (1200-2500 mm/yr)' },
    kidneybeans: { type: 'Pulse / Legume', season: 'Kharif / Rabi', soil: 'Rich Organic Loam', waterNeed: 'Moderate (500-1200 mm/yr)' },
    mothbeans: { type: 'Arid Pulse', season: 'Kharif', soil: 'Sandy / Arid Loam', waterNeed: 'Very Low (250-600 mm/yr)' },
    mungbean: { type: 'Pulse / Legume', season: 'Kharif / Zaid', soil: 'Fertile Loam', waterNeed: 'Low-Moderate (350-850 mm/yr)' },
    blackgram: { type: 'Pulse / Legume', season: 'Kharif / Rabi', soil: 'Loamy / Clayey Soil', waterNeed: 'Moderate (400-900 mm/yr)' },
    lentil: { type: 'Rabi Pulse', season: 'Rabi', soil: 'Light Loam / Clay Loam', waterNeed: 'Low (300-700 mm/yr)' },
    jute: { type: 'Fiber Crop', season: 'Kharif', soil: 'Alluvial Floodplain', waterNeed: 'High (1000-2100 mm/yr)' },
    coffee: { type: 'Plantation Cash Crop', season: 'Perennial', soil: 'Humus-rich Forest Loam', waterNeed: 'High (1200-2600 mm/yr)' },
    banana: { type: 'Tropical Fruit', season: 'Perennial', soil: 'Rich Well-drained Loam', waterNeed: 'High (1000-2200 mm/yr)' },
    mango: { type: 'Tropical Fruit', season: 'Perennial', soil: 'Alluvial Loam', waterNeed: 'Moderate (700-1800 mm/yr)' },
    grapes: { type: 'Horticulture Fruit', season: 'Perennial', soil: 'Sandy Loam / Calcareous', waterNeed: 'Moderate (500-950 mm/yr)' },
    apple: { type: 'Temperate Fruit', season: 'Perennial', soil: 'Mountain Loam', waterNeed: 'Moderate (750-1500 mm/yr)' },
    orange: { type: 'Citrus Fruit', season: 'Perennial', soil: 'Well-drained Sandy Loam', waterNeed: 'Moderate (600-1250 mm/yr)' },
    papaya: { type: 'Tropical Fruit', season: 'Perennial', soil: 'Rich Organic Loam', waterNeed: 'High (900-1950 mm/yr)' },
    coconut: { type: 'Plantation Crop', season: 'Perennial', soil: 'Coastal Alluvial / Sandy', waterNeed: 'High (1200-2600 mm/yr)' },
    pomegranate: { type: 'Arid Fruit', season: 'Perennial', soil: 'Deep Sandy Loam', waterNeed: 'Low-Moderate (400-800 mm/yr)' },
    watermelon: { type: 'Cucurbit / Fruit', season: 'Zaid (Summer)', soil: 'Sandy Riverbed Loam', waterNeed: 'Low-Moderate (350-750 mm/yr)' },
    muskmelon: { type: 'Cucurbit / Fruit', season: 'Zaid (Summer)', soil: 'Light Sandy Loam', waterNeed: 'Low (300-700 mm/yr)' }
  };

  public presets: PresetOption[] = [
    {
      name: 'Vidarbha Soybean/Cotton',
      region: 'Maharashtra (Nagpur / Vidarbha)',
      description: 'Fertile black soil with moderate NPK, warm climate, and ~1050 mm annual rainfall',
      values: { N: 35, P: 70, K: 45, temperature: 26.0, humidity: 68.0, ph: 6.7, rainfall: 1050.0, state: 'Maharashtra', district: 'Nagpur' }
    },
    {
      name: 'Punjab Fertile Alluvium (Wheat)',
      region: 'Punjab (Ludhiana / Malwa)',
      description: 'High nitrogen, cool rabi temperature, moderate humidity and ~650 mm annual rainfall',
      values: { N: 110, P: 55, K: 38, temperature: 18.5, humidity: 55.0, ph: 6.8, rainfall: 650.0, state: 'Punjab', district: 'Ludhiana' }
    },
    {
      name: 'Bengal Floodplain (Rice)',
      region: 'West Bengal (Bardhaman / Gangetic)',
      description: 'High moisture, warm temperature and high annual monsoon rainfall (>1600 mm)',
      values: { N: 80, P: 45, K: 40, temperature: 25.0, humidity: 82.0, ph: 6.3, rainfall: 1600.0, state: 'West Bengal', district: 'Bardhaman' }
    },
    {
      name: 'Rajasthan Arid (Pearl Millet/Bajra)',
      region: 'Rajasthan (Jodhpur / Marwar)',
      description: 'Hot semi-arid climate, low nitrogen/phosphorus, alkaline soil and low annual rainfall (~450 mm)',
      values: { N: 60, P: 30, K: 25, temperature: 31.0, humidity: 42.0, ph: 7.6, rainfall: 450.0, state: 'Rajasthan', district: 'Jodhpur' }
    },
    {
      name: 'Maharashtra Sugarcane (Kolhapur)',
      region: 'Maharashtra (Kolhapur / Western)',
      description: 'High nitrogen and potassium, warm temperature, high annual precipitation (>1600 mm)',
      values: { N: 140, P: 60, K: 90, temperature: 28.0, humidity: 72.0, ph: 6.8, rainfall: 1650.0, state: 'Maharashtra', district: 'Kolhapur' }
    },
    {
      name: 'Madhya Pradesh Pulse (Chickpea)',
      region: 'Madhya Pradesh (Indore / Malwa)',
      description: 'Cool rabi season, balanced phosphorus, alkaline soil and ~600 mm annual rainfall',
      values: { N: 32, P: 65, K: 40, temperature: 20.0, humidity: 35.0, ph: 7.3, rainfall: 600.0, state: 'Madhya Pradesh', district: 'Indore' }
    }
  ];

  public cropForm = this.fb.group({
    country: ['India'],
    state: ['Maharashtra', Validators.required],
    district: ['Nagpur', Validators.required],
    season: ['Kharif', Validators.required],
    N: [35, [Validators.required, Validators.min(0), Validators.max(200)]],
    P: [70, [Validators.required, Validators.min(0), Validators.max(200)]],
    K: [45, [Validators.required, Validators.min(0), Validators.max(250)]],
    temperature: [26.0 as number | null, [Validators.required, Validators.min(0), Validators.max(60)]],
    humidity: [68.0 as number | null, [Validators.required, Validators.min(0), Validators.max(100)]],
    ph: [6.7, [Validators.required, Validators.min(3.0), Validators.max(10.0)]],
    rainfall: [1050.0 as number | null, [Validators.required, Validators.min(0), Validators.max(3500)]]
  });

  // Top 5 Probabilities Horizontal Bar Chart
  public barChartType = 'bar' as const;
  public barChartData: ChartData<'bar'> = {
    labels: [],
    datasets: [
      {
        data: [],
        backgroundColor: ['#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#ccfbf1'],
        borderRadius: 8,
        barThickness: 24
      }
    ]
  };

  public barChartOptions: ChartConfiguration<'bar'>['options'] = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context) => ` Model Confidence: ${(Number(context.raw) * 100).toFixed(2)}%`
        },
        backgroundColor: '#0f172a',
        borderColor: '#334155',
        borderWidth: 1,
        titleColor: '#f8fafc',
        bodyColor: '#34d399'
      }
    },
    scales: {
      x: {
        min: 0,
        max: 1,
        grid: { color: 'rgba(51, 65, 85, 0.4)' },
        ticks: {
          color: '#94a3b8',
          callback: (value) => `${(Number(value) * 100).toFixed(0)}%`
        }
      },
      y: {
        grid: { display: false },
        ticks: { color: '#f8fafc', font: { weight: 'bold' } }
      }
    }
  };

  // Radar Chart for Normalized Soil Profile
  public radarChartType = 'radar' as const;
  public radarChartData: ChartData<'radar'> = {
    labels: ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)', 'Temperature', 'Humidity', 'pH', 'Annual Rainfall'],
    datasets: [
      {
        data: [],
        label: 'Input Soil & Climate Profile (%)',
        backgroundColor: 'rgba(16, 185, 129, 0.25)',
        borderColor: '#10b981',
        pointBackgroundColor: '#34d399',
        pointBorderColor: '#ffffff',
        borderWidth: 2
      }
    ]
  };

  public radarChartOptions: ChartConfiguration<'radar'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#cbd5e1' }
      }
    },
    scales: {
      r: {
        min: 0,
        max: 100,
        ticks: { display: false, stepSize: 20 },
        grid: { color: 'rgba(51, 65, 85, 0.5)' },
        angleLines: { color: 'rgba(51, 65, 85, 0.5)' },
        pointLabels: {
          color: '#cbd5e1',
          font: { size: 11, weight: 'bold' }
        }
      }
    }
  };

  public ngOnInit(): void {
    const initialState = this.cropForm.get('state')?.value || 'Maharashtra';
    if (STATE_DISTRICTS[initialState]) {
      this.availableDistricts.set(STATE_DISTRICTS[initialState]);
    }
    const initialDistrict = this.cropForm.get('district')?.value || 'Nagpur';
    this.weatherData.set({
      state: initialState,
      district: initialDistrict,
      location_name: `${initialDistrict}, ${initialState}, India`,
      latitude: 21.1458,
      longitude: 79.0882,
      temperature: 26.0,
      humidity: 68.0,
      annual_rainfall: 1050.0,
      rainfall: 1050.0,
      weather_condition: 'Agro-Climatic Normal Profile',
      source: 'IMD LPA District Normal Rainfall (1050 mm)',
      fetched_at: new Date().toISOString()
    });
  }

  public onStateChange(selectedState: string): void {
    // 1. Clear previous district and weather values
    this.cropForm.patchValue({
      state: selectedState,
      district: '',
      temperature: null,
      humidity: null,
      rainfall: null
    });
    this.weatherData.set(null);
    this.weatherError.set(null);

    // 2. Filter districts to ONLY districts belonging to selected state
    if (selectedState && STATE_DISTRICTS[selectedState]) {
      this.availableDistricts.set(STATE_DISTRICTS[selectedState]);
    } else {
      this.availableDistricts.set([]);
    }
  }

  public onDistrictChange(selectedDistrict: string): void {
    this.cropForm.patchValue({ district: selectedDistrict });
    const currentState = this.cropForm.get('state')?.value;
    if (currentState && selectedDistrict) {
      this.fetchWeather(currentState, selectedDistrict);
    }
  }

  public fetchWeather(state: string, district: string): void {
    if (!state || !district) return;

    this.isWeatherLoading.set(true);
    this.weatherError.set(null);

    this.weatherService.getWeather(state, district).subscribe({
      next: (response) => {
        this.isWeatherLoading.set(false);
        if (response.success && response.data) {
          this.weatherData.set(response.data);
          this.cropForm.patchValue({
            temperature: response.data.temperature,
            humidity: response.data.humidity,
            rainfall: response.data.annual_rainfall
          });
        } else {
          this.weatherError.set(response.error?.message || 'Unable to fetch weather data for this location. Please try again.');
        }
      },
      error: () => {
        this.isWeatherLoading.set(false);
        this.weatherError.set('Unable to fetch weather data for this location. Please try again.');
      }
    });
  }

  public retryWeather(): void {
    const currentState = this.cropForm.get('state')?.value;
    const currentDistrict = this.cropForm.get('district')?.value;
    if (currentState && currentDistrict) {
      this.fetchWeather(currentState, currentDistrict);
    }
  }

  public applyPreset(preset: PresetOption): void {
    if (preset.values.state) {
      this.availableDistricts.set(STATE_DISTRICTS[preset.values.state] || []);
    }

    this.cropForm.patchValue({
      state: preset.values.state || '',
      district: preset.values.district || '',
      N: preset.values.N,
      P: preset.values.P,
      K: preset.values.K,
      temperature: preset.values.temperature,
      humidity: preset.values.humidity,
      ph: preset.values.ph,
      rainfall: preset.values.rainfall
    });

    this.weatherError.set(null);
    if (preset.values.state && preset.values.district) {
      this.weatherData.set({
        state: preset.values.state,
        district: preset.values.district,
        location_name: `${preset.values.district}, ${preset.values.state}, India`,
        latitude: 0,
        longitude: 0,
        temperature: preset.values.temperature,
        humidity: preset.values.humidity,
        annual_rainfall: preset.values.rainfall,
        rainfall: preset.values.rainfall,
        weather_condition: 'Agro-Climatic Preset Profile',
        source: 'Regional Preset Benchmark',
        fetched_at: new Date().toISOString()
      });
    }
  }

  public getSuitabilityBadge(item: RankedCropProbability): { label: string; class: string } {
    const level = item.suitability || '';
    if (level === 'Highly Suitable') {
      return { label: 'Highly Suitable', class: 'badge-optimal' };
    } else if (level === 'Suitable') {
      return { label: 'Suitable', class: 'badge-high' };
    } else if (level === 'Moderately Suitable') {
      return { label: 'Moderately Suitable', class: 'badge-moderate' };
    } else {
      return { label: 'Marginally Suitable', class: 'badge-low' };
    }
  }

  public getCropInfo(cropName: string): CropAgroInfo {
    const key = cropName.toLowerCase().trim().replace(/ /g, '_');
    return this.cropCatalog[key] || {
      type: 'Agricultural Crop',
      season: 'Kharif / Rabi',
      soil: 'Standard Agricultural Loam',
      waterNeed: 'Medium'
    };
  }

  public onSubmit(): void {
    if (this.cropForm.invalid || this.isWeatherLoading()) {
      this.cropForm.markAllAsTouched();
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set(null);

    const formVal = this.cropForm.getRawValue();
    const req = {
      N: Number(formVal.N),
      P: Number(formVal.P),
      K: Number(formVal.K),
      temperature: Number(formVal.temperature),
      humidity: Number(formVal.humidity),
      ph: Number(formVal.ph),
      rainfall: Number(formVal.rainfall),
      top_k: 5,
      country: formVal.country || 'India',
      state: formVal.state || undefined,
      district: formVal.district || undefined,
      season: formVal.season || undefined
    };

    this.cropService.recommendCrop(req).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        if (response.success && response.data) {
          this.result.set(response.data);
          this.updateCharts(response.data, req);
        } else {
          this.errorMessage.set(response.error?.message || 'Crop recommendation inference failed.');
        }
      },
      error: (err) => {
        this.isLoading.set(false);
        this.errorMessage.set(
          err.error?.detail || err.error?.error?.message || 'Failed to connect to Crop Recommendation service.'
        );
      }
    });
  }

  private updateCharts(res: CropRecommendationResponse, inputs: any): void {
    const top = res.recommendations || res.top_recommendations || [];
    const labels = top.map((t) => t.crop.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()));
    const probs = top.map((t) => (t.model_score !== undefined ? t.model_score : t.probability));

    this.barChartData = {
      labels,
      datasets: [
        {
          data: probs,
          backgroundColor: ['#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#ccfbf1'],
          borderRadius: 8,
          barThickness: 24
        }
      ]
    };

    const normN = Math.min(100, Math.max(0, (inputs.N / 180) * 100));
    const normP = Math.min(100, Math.max(0, (inputs.P / 160) * 100));
    const normK = Math.min(100, Math.max(0, (inputs.K / 225) * 100));
    const normTemp = Math.min(100, Math.max(0, ((inputs.temperature - 4.0) / (45.0 - 4.0)) * 100));
    const normHum = Math.min(100, Math.max(0, ((inputs.humidity - 15.0) / (100.0 - 15.0)) * 100));
    const normPh = Math.min(100, Math.max(0, ((inputs.ph - 4.5) / (9.0 - 4.5)) * 100));
    const normRain = Math.min(100, Math.max(0, ((inputs.rainfall - 200) / (3000 - 200)) * 100));

    this.radarChartData = {
      labels: ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)', 'Temperature', 'Humidity', 'pH', 'Rainfall'],
      datasets: [
        {
          data: [normN, normP, normK, normTemp, normHum, normPh, normRain],
          label: 'Input Soil & Climate Profile (%)',
          backgroundColor: 'rgba(16, 185, 129, 0.25)',
          borderColor: '#10b981',
          pointBackgroundColor: '#34d399',
          pointBorderColor: '#ffffff',
          borderWidth: 2
        }
      ]
    };
  }
}
