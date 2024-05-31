import { Component, HostListener } from '@angular/core';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss'],
})
export class NavbarComponent {
  lastScrollTop = 0;
  navbarHidden = false;

  @HostListener('window:scroll', ['$event'])
  onWindowScroll() {
    const currentScrollTop =
      window.pageYOffset || document.documentElement.scrollTop;
    if (currentScrollTop > this.lastScrollTop) {
      // Scrolling down
      this.navbarHidden = true;
    } else {
      // Scrolling up
      this.navbarHidden = false;
    }
    this.lastScrollTop = currentScrollTop <= 0 ? 0 : currentScrollTop; // For Mobile or negative scrolling
  }
}
