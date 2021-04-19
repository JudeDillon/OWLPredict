import { Component } from '@angular/core';
import { WebService } from './web.service';

@Component( {
    selector: 'form',
    templateUrl: './form.component.html',
    styleUrls: ['./form.component.css']
})
export class FormComponent {
    constructor(public webService: WebService) {}
    ngOnInit() {
        this.webService.getHelloWorld();
    }
}