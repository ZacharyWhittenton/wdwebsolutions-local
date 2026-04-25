import { Component } from '@angular/core';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [],
  templateUrl: './contact.component.html',
  styleUrl: './contact.component.scss'
})
export class ContactComponent {
  constructor() { }

  sendEmail() {
    const subject = encodeURIComponent('New WD Web Solutions project');
    const body = encodeURIComponent('Hi WD Web Solutions,\n\nI would like to talk about a custom software, website, or integration project.\n\n');

    window.location.href = `mailto:zachw@wdwebsolutions.com,derekd@wdwebsolutions.com?subject=${subject}&body=${body}`;
  }
}
