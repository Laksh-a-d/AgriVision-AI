import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData } from 'chart.js';
import { CropService } from '../../core/services/crop.service';
import { CropRecommendationResponse, RankedCropProbability } from '../../core/models/crop.model';
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
export class CropRecommendationComponent {
  private fb = inject(FormBuilder);
  private cropService = inject(CropService);

  public isLoading = signal<boolean>(false);
  public errorMessage = signal<string | null>(null);
  public result = signal<CropRecommendationResponse | null>(null);

  public readonly cropCatalog: Record<string, CropAgroInfo> = {
    rice: { type: 'Cereal Grain', season: 'Kharif', soil: 'Clayey / Alluvial Loam', waterNeed: 'High (150-300mm)' },
    maize: { type: 'Cereal / Fodder', season: 'Kharif / Rabi', soil: 'Well-drained Loam', waterNeed: 'Moderate (60-100mm)' },
    chickpea: { type: 'Pulse / Legume', season: 'Rabi', soil: 'Sandy Loam / Black Soil', waterNeed: 'Low (60-90mm)' },
    kidneybeans: { type: 'Pulse / Legume', season: 'Kharif / Rabi', soil: 'Rich Organic Loam', waterNeed: 'Moderate (100-150mm)' },
    pigeonpeas: { type: 'Pulse / Legume', season: 'Kharif', soil: 'Deep Loam / Vertisol', waterNeed: 'Low-Moderate (90-150mm)' },
    mothbeans: { type: 'Arid Pulse', season: 'Kharif', soil: 'Sandy / Arid Loam', waterNeed: 'Very Low (30-60mm)' },
    mungbean: { type: 'Pulse / Legume', season: 'Kharif / Zaid', soil: 'Fertile Loam', waterNeed: 'Low-Moderate (40-60mm)' },
    blackgram: { type: 'Pulse / Legume', season: 'Kharif / Rabi', soil: 'Loamy / Clayey Soil', waterNeed: 'Moderate (60-80mm)' },
    lentil: { type: 'Pulse / Legume', season: 'Rabi', soil: 'Light Loam / Clay Loam', waterNeed: 'Low (40-60mm)' },
    pomegranate: { type: 'Horticulture Fruit', season: 'Perennial', soil: 'Deep Sandy Loam', waterNeed: 'Moderate (100-120mm)' },
    banana: { type: 'Tropical Fruit', season: 'Perennial', soil: 'Rich Well-drained Loam', waterNeed: 'High (150-250mm)' },
    mango: { type: 'Tropical Fruit', season: 'Perennial', soil: 'Alluvial Loam', waterNeed: 'Moderate (80-100mm)' },
    grapes: { type: 'Horticulture Fruit', season: 'Perennial', soil: 'Sandy Loam / Calcareous', waterNeed: 'Moderate (60-80mm)' },
    watermelon: { type: 'Cucurbit / Fruit', season: 'Zaid (Summer)', soil: 'Sandy Riverbed Loam', waterNeed: 'Low-Moderate (40-60mm)' },
    muskmelon: { type: 'Cucurbit / Fruit', season: 'Zaid (Summer)', soil: 'Light Sandy Loam', waterNeed: 'Low (20-30mm)' },
    apple: { type: 'Temperate Fruit', season: 'Perennial', soil: 'Mountain Loam', waterNeed: 'Moderate (100-130mm)' },
    orange: { type: 'Citrus Fruit', season: 'Perennial', soil: 'Well-drained Sandy Loam', waterNeed: 'Moderate (100-120mm)' },
    papaya: { type: 'Tropical Fruit', season: 'Perennial', soil: 'Rich Organic Loam', waterNeed: 'High (140-250mm)' },
    coconut: { type: 'Plantation Crop', season: 'Perennial', soil: 'Coastal Alluvial / Sandy', waterNeed: 'High (150-250mm)' },
    cotton: { type: 'Fiber / Cash Crop', season: 'Kharif', soil: 'Deep Black Cotton (Vertisol)', waterNeed: 'Moderate (60-100mm)' },
    jute: { type: 'Fiber Crop', season: 'Kharif', soil: 'Alluvial Floodplain', waterNeed: 'High (150-200mm)' },
    coffee: { type: 'Plantation Cash Crop', season: 'Perennial', soil: 'Humus-rich Forest Loam', waterNeed: 'High (150-200mm)' }
  };

  public presets: PresetOption[] = [
    {
      name: 'Vidarbha Black Soil (Cotton)',
      region: 'Maharashtra (Vidarbha / Deccan)',
      description: 'High nitrogen, moderate phosphorus, low potassium vertisol suited for cash fiber crops',
      values: { N: 117, P: 46, K: 19, temperature: 24.0, humidity: 79.8, ph: 6.9, rainfall: 90.8, state: 'Maharashtra', district: 'Nagpur' }
    },
    {
      name: 'Gangetic Alluvial (Rice)',
      region: 'West Bengal / Bihar / UP',
      description: 'High moisture, warm temperature and high seasonal monsoon rainfall',
      values: { N: 90, P: 42, K: 43, temperature: 20.9, humidity: 82.0, ph: 6.5, rainfall: 202.9, state: 'West Bengal', district: 'Burdwan' }
    },
    {
      name: 'Plateau Semi-Arid (Maize)',
      region: 'Karnataka / Telangana / MP',
      description: 'Warm temperate loamy soil with balanced moderate NPK and medium rainfall',
      values: { N: 71, P: 54, K: 20, temperature: 22.6, humidity: 65.4, ph: 5.7, rainfall: 82.3, state: 'Karnataka', district: 'Dharwad' }
    },
    {
      name: 'Himalayan Highlands (Apple)',
      region: 'Himachal Pradesh / J&K',
      description: 'High potassium and phosphorus cold temperate mountain loam',
      values: { N: 20, P: 134, K: 199, temperature: 22.7, humidity: 92.3, ph: 5.9, rainfall: 112.7, state: 'Himachal Pradesh', district: 'Shimla' }
    },
    {
      name: 'Dryland Rabi Pulse (Chickpea)',
      region: 'Rajasthan / MP / Maharashtra',
      description: 'Cool dry climate with moderate potassium and alkaline soil pH',
      values: { N: 40, P: 67, K: 79, temperature: 18.8, humidity: 16.8, ph: 7.3, rainfall: 80.1, state: 'Madhya Pradesh', district: 'Indore' }
    },
    {
      name: 'Western Ghats (Coffee)',
      region: 'Karnataka (Coorg) / Kerala',
      description: 'Subtropical highland humus-rich forest loam with high seasonal precipitation',
      values: { N: 101, P: 29, K: 30, temperature: 26.5, humidity: 58.1, ph: 6.8, rainfall: 158.1, state: 'Karnataka', district: 'Kodagu' }
    }
  ];

  public cropForm = this.fb.group({
    country: ['India'],
    state: [''],
    district: [''],
    N: [90, [Validators.required, Validators.min(0), Validators.max(200)]],
    P: [42, [Validators.required, Validators.min(0), Validators.max(200)]],
    K: [43, [Validators.required, Validators.min(0), Validators.max(250)]],
    temperature: [20.9, [Validators.required, Validators.min(0), Validators.max(60)]],
    humidity: [82.0, [Validators.required, Validators.min(0), Validators.max(100)]],
    ph: [6.5, [Validators.required, Validators.min(3.0), Validators.max(10.0)]],
    rainfall: [202.9, [Validators.required, Validators.min(0), Validators.max(500)]]
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
          label: (context) => ` Suitability Probability: ${(Number(context.raw) * 100).toFixed(2)}%`
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
    labels: ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)', 'Temperature', 'Humidity', 'pH', 'Rainfall'],
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

  public applyPreset(preset: PresetOption): void {
    this.cropForm.patchValue({
      N: preset.values.N,
      P: preset.values.P,
      K: preset.values.K,
      temperature: preset.values.temperature,
      humidity: preset.values.humidity,
      ph: preset.values.ph,
      rainfall: preset.values.rainfall,
      state: preset.values.state || '',
      district: preset.values.district || ''
    });
  }

  public getSuitabilityBadge(index: number, prob: number): { label: string; class: string } {
    if (index === 0 && prob >= 0.70) {
      return { label: 'Primary Optimal Match', class: 'badge-optimal' };
    } else if (prob >= 0.30) {
      return { label: 'High Suitability', class: 'badge-high' };
    } else if (prob >= 0.10) {
      return { label: 'Moderate Suitability', class: 'badge-moderate' };
    } else {
      return { label: 'Viable Secondary Crop', class: 'badge-low' };
    }
  }

  public getCropInfo(cropName: string): CropAgroInfo {
    const key = cropName.toLowerCase().trim();
    return this.cropCatalog[key] || {
      type: 'Agricultural Crop',
      season: 'Kharif / Rabi',
      soil: 'Standard Agricultural Loam',
      waterNeed: 'Medium'
    };
  }

  public onSubmit(): void {
    if (this.cropForm.invalid) {
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
      district: formVal.district || undefined
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
    const labels = top.map((t) => t.crop.charAt(0).toUpperCase() + t.crop.slice(1));
    const probs = top.map((t) => t.probability);

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

    const normN = Math.min(100, Math.max(0, (inputs.N / 140) * 100));
    const normP = Math.min(100, Math.max(0, (inputs.P / 145) * 100));
    const normK = Math.min(100, Math.max(0, (inputs.K / 205) * 100));
    const normTemp = Math.min(100, Math.max(0, ((inputs.temperature - 8.8) / (43.7 - 8.8)) * 100));
    const normHum = Math.min(100, Math.max(0, ((inputs.humidity - 14.3) / (100 - 14.3)) * 100));
    const normPh = Math.min(100, Math.max(0, ((inputs.ph - 3.5) / (9.94 - 3.5)) * 100));
    const normRain = Math.min(100, Math.max(0, ((inputs.rainfall - 20) / (298.6 - 20)) * 100));

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

