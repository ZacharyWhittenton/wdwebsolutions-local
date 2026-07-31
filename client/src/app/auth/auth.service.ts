
import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs';

export interface User {
  email: string;
  role: 'admin' | 'user';
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  currentUser = signal<User | null>(null);

  constructor(private http: HttpClient) {}

  signup(email: string, password: string) {
    return this.http
      .post<User>('/auth/signup', { email, password }, { withCredentials: true })
      .pipe(tap((user) => this.currentUser.set(user)));
  }

  login(email: string, password: string) {
    return this.http
      .post<User>('/auth/login', { email, password }, { withCredentials: true })
      .pipe(tap((user) => this.currentUser.set(user)));
  }

  logout() {
    return this.http
      .post('/auth/logout', {}, { withCredentials: true })
      .pipe(tap(() => this.currentUser.set(null)));
  }

  fetchMe() {
    return this.http
      .get<User>('/auth/me', { withCredentials: true })
      .pipe(tap((user) => this.currentUser.set(user)));
  }
}
