import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NextElementPointerComponent } from './next-element-pointer.component';

describe('NextElementPointerComponent', () => {
  let component: NextElementPointerComponent;
  let fixture: ComponentFixture<NextElementPointerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NextElementPointerComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(NextElementPointerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
