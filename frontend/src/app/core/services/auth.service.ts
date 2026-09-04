import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, catchError, of, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ApiResponse } from '../models/common.model';
import { User } from '../models/user.model';
import {
  UserRegisterRequest,
  UserLoginRequest,
  TokenResponse,
  LogoutResponse
} from '../models/auth.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly TOKEN_KEY = 'agripulse_jwt_token';
  private readonly USER_KEY = 'agripulse_user_profile';
  private readonly baseUrl = `${environment.apiBaseUrl}/auth`;

  public currentUser = signal<User | null>(this.getStoredUser());
  public isAuthenticatedSignal = signal<boolean>(!!this.getToken());

  constructor(private http: HttpClient) {}

  public register(request: UserRegisterRequest): Observable<ApiResponse<User>> {
    return this.http.post<ApiResponse<User>>(`${this.baseUrl}/register`, request);
  }

  public login(request: UserLoginRequest): Observable<ApiResponse<TokenResponse>> {
    return this.http.post<ApiResponse<TokenResponse>>(`${this.baseUrl}/login`, request).pipe(
      tap((response) => {
        if (response.success && response.data) {
          this.setSession(response.data);
        }
      })
    );
  }

  public logout(): Observable<ApiResponse<LogoutResponse>> {
    const token = this.getToken();
    if (!token) {
      this.clearSession();
      return of({ success: true, message: 'Logged out successfully' });
    }

    return this.http.post<ApiResponse<LogoutResponse>>(`${this.baseUrl}/logout`, {}).pipe(
      tap(() => this.clearSession()),
      catchError((err) => {
        this.clearSession();
        return of({ success: true, message: 'Logged out successfully' });
      })
    );
  }

  public fetchCurrentUser(): Observable<ApiResponse<User>> {
    return this.http.get<ApiResponse<User>>(`${this.baseUrl}/me`).pipe(
      tap((response) => {
        if (response.success && response.data) {
          this.setUser(response.data);
        }
      })
    );
  }

  public setSession(tokenData: TokenResponse): void {
    localStorage.setItem(this.TOKEN_KEY, tokenData.access_token);
    this.setUser(tokenData.user);
    this.isAuthenticatedSignal.set(true);
  }

  public setUser(user: User): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    this.currentUser.set(user);
  }

  public clearSession(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    this.currentUser.set(null);
    this.isAuthenticatedSignal.set(false);
  }

  public getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  public isAuthenticated(): boolean {
    return !!this.getToken();
  }

  private getStoredUser(): User | null {
    try {
      const stored = localStorage.getItem(this.USER_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  }
}
