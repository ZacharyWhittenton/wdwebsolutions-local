import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';

export interface ContactFormPayload {
  name: string;
  emailAddress: string;
  message: string;
  company?: string;
  phone?: string;
}

export interface ContactFormResponse {
  message: string;
}

@Injectable({
  providedIn: 'root'
})
export class ContactService {
  private readonly httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json'
    })
  };

  constructor(private readonly http: HttpClient) {}

  submitContactForm(payload: ContactFormPayload): Observable<ContactFormResponse> {
    return this.http.post<ContactFormResponse>(
      environment.contactApiUrl,
      {
        ...payload,
        formType: 'contact'
      },
      this.httpOptions
    );
  }
}
