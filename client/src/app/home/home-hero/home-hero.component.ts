import { Component } from '@angular/core';
import { NextElementPointerComponent } from "../../shared/next-element-pointer/next-element-pointer.component";

@Component({
    selector: 'app-home-hero',
    standalone: true,
    templateUrl: './home-hero.component.html',
    styleUrl: './home-hero.component.scss',
    imports: [NextElementPointerComponent]
})
export class HomeHeroComponent {

  
}
