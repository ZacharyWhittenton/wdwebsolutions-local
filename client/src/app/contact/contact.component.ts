import { Component } from '@angular/core';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button'; 

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [CardModule, ButtonModule],
  templateUrl: './contact.component.html',
  styleUrl: './contact.component.scss'
})
export class ContactComponent {
  constructor() { }

  sendEmail() {
    window.location.href = 'mailto:zachw@wdwebsolutions.com,derekd@wdwebsolutions'; // Replace with your email
  }
}
