import { Component } from '@angular/core';
import { NextElementPointerComponent } from "../../shared/next-element-pointer/next-element-pointer.component";
import { RouterModule } from '@angular/router';
@Component({
    selector: 'app-home-hero',
    standalone: true,
    templateUrl: './home-hero.component.html',
    styleUrl: './home-hero.component.scss',
    imports: [NextElementPointerComponent, RouterModule]
})
export class HomeHeroComponent {

  
}
