import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { NavbarComponent } from './navbar/navbar.component';

import { ToolbarModule } from 'primeng/toolbar';
import { AvatarModule } from 'primeng/avatar'; 
import { ButtonModule } from 'primeng/button'; 
import { SplitButtonModule } from 'primeng/splitbutton';

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
    SplitButtonModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
