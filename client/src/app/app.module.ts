import { NgModule } from '@angular/core';
import { provideAnimations } from '@angular/platform-browser/animations'


import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { NavbarComponent } from './navbar/navbar.component';
import { ButtonComponent } from './shared/button/button.component'; 
import { CardComponent } from './shared/card/card.component';
import { BackgroundGreyComponent } from './shared/background-grey/background-grey.component';

import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { ToolbarModule } from 'primeng/toolbar';
import { AvatarModule } from 'primeng/avatar'; 
import { ButtonModule } from 'primeng/button'; 
import { SplitButtonModule } from 'primeng/splitbutton';
import { CardModule } from 'primeng/card';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    NavbarComponent,
    

  ],

  imports: [
    BrowserModule,
    AppRoutingModule,
    ToolbarModule,
    AvatarModule,
    ButtonModule,
    SplitButtonModule,
    ButtonComponent,
    CardModule,
    CardComponent,
    BackgroundGreyComponent,
  ],
  exports: [
  ],
  providers: [
    provideAnimations()
  ],

  bootstrap: [AppComponent]
})
export class AppModule { }
