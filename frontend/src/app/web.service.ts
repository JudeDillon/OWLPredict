import { HttpClient} from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable()
export class WebService {
    private privateHello;
    private helloSubject = new Subject();
    hello = this.helloSubject.asObservable();

    private privatePrediction;
    private predictionSubject = new Subject();
    prediction = this.predictionSubject.asObservable();

    constructor(private http: HttpClient) {}
    getPrediction(team1, team2, numberOfNeighbours, season) {
        return this.http.get('http://localhost:5000/predict/'+ team1 +'/' + team2 + '/no' + '?neighbours=' + numberOfNeighbours + '&season=' + season).subscribe(response=>
        {
            this.privatePrediction = response;
            this.predictionSubject.next(this.privatePrediction);
        })
    }
}
