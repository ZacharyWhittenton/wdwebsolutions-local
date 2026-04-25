import {
  AfterViewInit,
  Component,
  ElementRef,
  HostListener,
  NgZone,
  OnDestroy,
} from '@angular/core';
import { NextElementPointerComponent } from "../../shared/next-element-pointer/next-element-pointer.component";
import { RouterModule } from '@angular/router';
@Component({
    selector: 'app-home-hero',
    standalone: true,
    templateUrl: './home-hero.component.html',
    styleUrl: './home-hero.component.scss',
    imports: [NextElementPointerComponent, RouterModule]
})
export class HomeHeroComponent implements AfterViewInit, OnDestroy {
  private animationFrameId: number | null = null;
  private targetX = 0;
  private targetY = 0;
  private currentX = 0;
  private currentY = 0;

  constructor(
    private readonly elementRef: ElementRef<HTMLElement>,
    private readonly ngZone: NgZone
  ) {}

  ngAfterViewInit(): void {
    this.setPointer(window.innerWidth / 2, window.innerHeight / 2);
    this.ngZone.runOutsideAngular(() => this.animateMotion());
  }

  ngOnDestroy(): void {
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
    }
  }

  @HostListener('window:pointermove', ['$event'])
  onPointerMove(event: PointerEvent): void {
    this.setPointer(event.clientX, event.clientY);
  }

  @HostListener('window:pointerleave')
  onPointerLeave(): void {
    this.targetX = 0;
    this.targetY = 0;
  }

  @HostListener('window:resize')
  onWindowResize(): void {
    this.setPointer(window.innerWidth / 2, window.innerHeight / 2);
  }

  private setPointer(clientX: number, clientY: number): void {
    const width = Math.max(window.innerWidth, 1);
    const height = Math.max(window.innerHeight, 1);

    this.targetX = (clientX / width - 0.5) * 2;
    this.targetY = (clientY / height - 0.5) * 2;
  }

  private animateMotion = (): void => {
    this.currentX += (this.targetX - this.currentX) * 0.08;
    this.currentY += (this.targetY - this.currentY) * 0.08;

    const host = this.elementRef.nativeElement;
    host.style.setProperty('--hero-x', this.currentX.toFixed(4));
    host.style.setProperty('--hero-y', this.currentY.toFixed(4));

    this.animationFrameId = requestAnimationFrame(this.animateMotion);
  };
}
