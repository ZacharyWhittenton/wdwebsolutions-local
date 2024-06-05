import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common'; // Import CommonModule

@Component({
  selector: 'app-next-element-pointer',
  standalone: true,
  imports: [CommonModule], // Include CommonModule in the imports array
  templateUrl: './next-element-pointer.component.html',
  styleUrls: ['./next-element-pointer.component.scss']
})
export class NextElementPointerComponent {
  @Input() displayText?: string;
  @Input() elementID?: string;

  scrollToNextElement() {
    if (this.elementID) {
      const element = document.getElementById(this.elementID);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    } else {
      window.scrollTo({
        top: window.innerHeight,
        behavior: 'smooth'
      });
    }
  }
}
