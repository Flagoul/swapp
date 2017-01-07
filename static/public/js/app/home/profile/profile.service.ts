import { Injectable } from '@angular/core';
import { Response } from '@angular/http';

@Injectable()
export class ProfileService {

    constructor() {
    }

    // We must add csrftoken in header manually when we user XMLHttpRequest.
    // Without XHR, images can't be upload with enctype multipart/form-data
    addImage(formData: FormData): Promise<any> {
        
        let csrftoken: string = this.getCookie("csrftoken");

        return new Promise(function (resolve, reject) {
            let req = new XMLHttpRequest();
            req.open("POST", "/api/images/");
            req.setRequestHeader("enctype", "multipart/form-data");
            req.setRequestHeader("X-CSRFToken", csrftoken);
            req.send(formData);

            req.onreadystatechange = () => {
                if(req.readyState === 4) {
                    if(req.status === 201) {
                        resolve(req.response);
                    } else {
                        reject(req.response);
                    }
                }
            }
        })
        .catch(this.handleError);
    }

    // Get cookie value from its name
    getCookie(name: string): string {
        let value = "; " + document.cookie;
        let parts = value.split("; " + name + "=");
        if (parts.length == 2) return parts.pop().split(";").shift();
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
