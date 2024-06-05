import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WhyWebsiteComponent } from './why-website.component';

describe('WhyWebsiteComponent', () => {
  let component: WhyWebsiteComponent;
  let fixture: ComponentFixture<WhyWebsiteComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WhyWebsiteComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(WhyWebsiteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
