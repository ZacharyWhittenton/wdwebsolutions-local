import { NgModule } from '@angular/core';
import { provideAnimations } from '@angular/platform-browser/animations'
import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { NavbarComponent } from './navbar/navbar.component';
import { ButtonComponent } from './shared/button/button.component'; 
import { CardComponent } from './shared/card/card.component';
import { BackgroundGreyComponent } from './shared/background-grey/background-grey.component';
import { BackgroundWhiteComponent } from './shared/background-white/background-white.component';
import { ContactComponent } from './contact/contact.component'; // Import the ContactComponent
import { BrowserModule } from '@angular/platform-browser';
import { provideHttpClient } from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { ToolbarModule } from 'primeng/toolbar';
import { AvatarModule } from 'primeng/avatar'; 
import { ButtonModule } from 'primeng/button'; 
import { SplitButtonModule } from 'primeng/splitbutton';
import { CardModule } from 'primeng/card';
import { HomeHeroComponent } from './home/home-hero/home-hero.component';
import { WhyWebsiteComponent } from './home/why-website/why-website.component';
import { FooterComponent } from './footer/footer.component';
import { OrganizationChartModule } from 'primeng/organizationchart';
import { SplitterModule } from 'primeng/splitter';
import { DividerModule } from 'primeng/divider';
import { LoginComponent } from './auth/login/login.component';
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
    BackgroundWhiteComponent,
    HomeHeroComponent,
    ContactComponent,
    WhyWebsiteComponent,
    FooterComponent,
    OrganizationChartModule,
    SplitterModule,
    DividerModule,
    LoginComponent
    
  ],
  exports: [
  ],
  providers: [
    provideAnimations(),
    provideHttpClient()
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
