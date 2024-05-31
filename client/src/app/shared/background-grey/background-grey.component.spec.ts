import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BackgroundGreyComponent } from './background-grey.component';

describe('BackgroundGreyComponent', () => {
  let component: BackgroundGreyComponent;
  let fixture: ComponentFixture<BackgroundGreyComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BackgroundGreyComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(BackgroundGreyComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
