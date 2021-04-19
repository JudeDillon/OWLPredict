import { HttpClient} from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable()
export class WebService {
    private privateHello;
    private helloSubject = new Subject();
    hello = this.helloSubject.asObservable();

    constructor(private http: HttpClient) {}
    getHelloWorld() {
        return this.http.get('http://localhost:5000/').subscribe(response=>
        {
            this.privateHello = response;
            this.helloSubject.next(this.privateHello);
        })
    }
}
