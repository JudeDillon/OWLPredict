import { Component } from '@angular/core';
import { WebService } from './web.service';
import { FormBuilder, Validators } from '@angular/forms';

@Component( {
    selector: 'predict',
    templateUrl: './predict.component.html',
    styleUrls: ['./predict.component.css']
})
export class PredictComponent {

    predictForm;
    numbers = [];

    constructor(public webService: WebService, private formBuilder: FormBuilder) {
        this.numbers = Array(50).fill(0).map((x,i)=>i+i+1);
    }

    ngOnInit() {
        this.predictForm = this.formBuilder.group({
            team1: ['', Validators.required],
            team2: ['', Validators.required],
            numberOfNeighbours: 33
        });
        this.webService.getHelloWorld();
    }

    onSubmit() 
    {
        this.webService.getPrediction(this.predictForm.value.team1, this.predictForm.value.team2, this.predictForm.value.numberOfNeighbours);
        //console.log(this.webService.prediction)
    }

    isInvalid(control) {
        return this.predictForm.controls[control].invalid && this.predictForm.controls[control].touched;
    }

    isUntouched() {
        return this.predictForm.controls.team1.pristine || this.predictForm.controls.team2.pristine;
    }

    isIncomplete() {
        return this.isInvalid('team1') || this.isInvalid('team2') || this.isUntouched();
    }
}