import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from './services/api.service';
import { HealthResponse } from './models/health.model';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  private apiService = inject(ApiService);

  protected readonly title = 'AgriPulse';
  protected readonly subtitle = 'Precision Agriculture Using Deep Learning';
  
  protected isChecking = signal<boolean>(true);
  protected isConnected = signal<boolean>(false);
  protected healthData = signal<HealthResponse | null>(null);
  protected lastCheckedTime = signal<string>('');

  ngOnInit(): void {
    this.checkBackendHealth();
  }

  checkBackendHealth(): void {
    this.isChecking.set(true);
    this.apiService.getHealth().subscribe({
      next: (response) => {
        this.isChecking.set(false);
        this.lastCheckedTime.set(new Date().toLocaleTimeString());
        if (response && response.status === 'ok') {
          this.isConnected.set(true);
          this.healthData.set(response);
        } else {
          this.isConnected.set(false);
          this.healthData.set(null);
        }
      },
      error: () => {
        this.isChecking.set(false);
        this.isConnected.set(false);
        this.healthData.set(null);
        this.lastCheckedTime.set(new Date().toLocaleTimeString());
      }
    });
  }
}
