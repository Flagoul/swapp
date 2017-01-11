import { Injectable } from '@angular/core';
import { Http, Response, Headers, RequestOptions } from '@angular/http';

@Injectable()
export class GoogleService {

    searchLocation = "New+York";

    constructor(private http: Http) {}

    testgoogle(): Promise<any> {
        let url = 'https://maps.googleapis.com/maps/api/geocode/json?address='+this.searchLocation+'&key=AIzaSyDNi0DkJRcQiOhJzSitoV5GhlacK6fNtKs';
        return this.http.get(url).toPromise().then(this.extractData).catch(this.handleError);
    }

    testgetItems(): Promise<any> {
        return this.http.get('/api/items/').toPromise().then(this.extractData).catch(this.handleError);
    }

    private extractData(res: Response) {
        let body = res.json();
        return body || { };
    }

    private handleError (error: Response | any) {
        // TODO : In a real world app, we might use a remote logging infrastructure
        let errMsg: string;
        if (error instanceof Response) {
            const body = error.json() || '';
            errMsg = body[0];
        } else {
            errMsg = error.message ? error.message : error.toString();
        }
        console.error(errMsg);
        return Promise.reject(errMsg);
    }
}