import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BackgroundWhiteComponent } from './background-white.component';

describe('BackgroundWhiteComponent', () => {
  let component: BackgroundWhiteComponent;
  let fixture: ComponentFixture<BackgroundWhiteComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BackgroundWhiteComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(BackgroundWhiteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
