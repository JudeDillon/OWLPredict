import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppComponent } from './app.component';
import { FormComponent } from './form.component';
import { WebService } from './web.service';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { HomeComponent } from './home.component';

var routes = [
    {
        path: '',
        component: HomeComponent
    },
    {
        path: 'prediction',
        component: FormComponent
    }
];

@NgModule({
  declarations: [
    AppComponent, FormComponent, HomeComponent
  ],
  imports: [
    BrowserModule, HttpClientModule, RouterModule.forRoot(routes)
  ],
  providers: [WebService],
  bootstrap: [AppComponent]
})
export class AppModule { }
