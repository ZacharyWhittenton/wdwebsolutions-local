import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';

import { ContactFormPayload, ContactService } from './contact.service';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './contact.component.html',
  styleUrl: './contact.component.scss'
})
export class ContactComponent {
  isSubmitting = false;
  successMessage = '';
  errorMessage = '';

  readonly contactForm = this.formBuilder.nonNullable.group({
    name: ['', [Validators.required, Validators.maxLength(200)]],
    emailAddress: ['', [Validators.required, Validators.email, Validators.maxLength(254)]],
    company: ['', [Validators.maxLength(200)]],
    phone: ['', [Validators.maxLength(40)]],
    message: ['', [Validators.required, Validators.maxLength(4000)]]
  });

  constructor(
    private readonly formBuilder: FormBuilder,
    private readonly contactService: ContactService
  ) { }

  submitContactForm(): void {
    this.successMessage = '';
    this.errorMessage = '';

    if (this.contactForm.invalid) {
      this.contactForm.markAllAsTouched();
      return;
    }

    this.isSubmitting = true;
    const formValue = this.contactForm.getRawValue();
    const payload: ContactFormPayload = {
      name: formValue.name,
      emailAddress: formValue.emailAddress,
      message: formValue.message,
      company: formValue.company || undefined,
      phone: formValue.phone || undefined
    };

    this.contactService.submitContactForm(payload)
      .pipe(finalize(() => {
        this.isSubmitting = false;
      }))
      .subscribe({
        next: response => {
          this.successMessage = response.message || 'Your message has been sent.';
          this.contactForm.reset();
        },
        error: error => {
          this.errorMessage = error?.error?.message || 'Your message could not be sent. Please try again.';
        }
      });
  }

  hasError(controlName: keyof typeof this.contactForm.controls): boolean {
    const control = this.contactForm.controls[controlName];
    return control.invalid && (control.touched || control.dirty);
  }
}
