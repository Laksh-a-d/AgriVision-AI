import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ApiResponse } from '../models/common.model';
import { WeatherData } from '../models/weather.model';

@Injectable({
  providedIn: 'root'
})
export class WeatherService {
  private http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiBaseUrl}/weather`;

  public getWeather(state: string, district: string): Observable<ApiResponse<WeatherData>> {
    const params = new HttpParams()
      .set('state', state)
      .set('district', district);
    return this.http.get<ApiResponse<WeatherData>>(this.baseUrl, { params });
  }
}
