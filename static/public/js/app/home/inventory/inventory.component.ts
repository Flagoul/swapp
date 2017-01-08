import {
    Component,
    Input,
    ViewEncapsulation,
    OnInit,
    trigger,
    state,
    style,
    transition,
    animate, OnChanges,
} from '@angular/core';
import { __platform_browser_private__,
    DomSanitizer } from '@angular/platform-browser';

import { ToastsManager } from 'ng2-toastr/ng2-toastr';

import { AuthService } from '../../shared/authentication/authentication.service';
import { InventoryItem } from './inventory-item';
import { ItemsService } from '../items/items.service';
import {Subscription} from "rxjs";
import {User} from "../profile/user";

declare let $: any;

@Component({
    moduleId: module.id,
    selector: 'inventory',
    encapsulation: ViewEncapsulation.None,
    templateUrl: './inventory.component.html',
    animations: [
        trigger('flyInOut', [
            state('in', style({opacity: 1, transform: 'translateX(0)'})),
            transition('void => *', [
                style({
                    opacity: 0,
                    transform: 'translateX(0) scale(0)'
                }),
                animate(200)
            ]),
            transition('* => void', [
                animate(200, style({
                    opacity: 0,
                    transform: 'translateX(0) scale(0)'
                }))
            ])
        ])
    ],
    providers: [__platform_browser_private__.BROWSER_SANITIZATION_PROVIDERS]
})
export class InventoryComponent implements OnInit {

    @Input() loggedIn: boolean;

    owner: User;
    subscription: Subscription;

    private inventory: Array<InventoryItem> = [];
    
    constructor(private authService: AuthService,
                private itemsService: ItemsService,
                public toastr: ToastsManager,
                private sanitizer: DomSanitizer) {}

    ngOnInit(): void {
        this.loggedIn = this.authService.isLoggedIn();

        // Listen for user login. We know that when user is available it means
        // that he successfully logged in
        this.subscription = this.authService.userSelected$.subscribe(
            user => {
                this.owner = user;
                this.inventory = [];
                for(let item of this.owner.items) {
                    let inventoryItem = new InventoryItem(item.id, item.name, item.image_id, item.image_url, item.archived);
                    this.sanitizer.bypassSecurityTrustUrl(item.image_url);
                    this.inventory.push(inventoryItem);
                }
            }
        );
    }

    // We receive the id of the item to add to the inventory
    addItemEvent($event: number) {
        this.itemsService.getDetailedItem(+$event).then(
            item => {
                let inventoryItem = new InventoryItem(item.id, item.name, item.images[0].id, item.images[0].url, item.archived);
                this.sanitizer.bypassSecurityTrustUrl(inventoryItem.image_url);
                this.inventory.push(inventoryItem);
            },
            error => this.toastr.error("Can't get item " + $event, "Error")
        );
    }

    // We receive the id of the item to add to the inventory
    archive(item: InventoryItem) {
        this.itemsService.archiveItem(item.id).then(
            () => {
                this.inventory.find(i => i.id == item.id).archived = true;
            },
            error => this.toastr.error("Error archiving the item " + item, "Error")
        );
    }

    // We receive the id of the item to add to the inventory
    restore(item: InventoryItem) {
        this.itemsService.restoreItem(item.id).then(
            () => {
                this.inventory.find(i => i.id == item.id).archived = false;
            },
            error => this.toastr.error("Error restoring the item " + item, "Error")
        );
    }


    gotoDetail(item_id: number): void {
        console.log("clicked. item_id: " + item_id);

        let service = this.itemsService;
        service.getDetailedItem(item_id)
            .then(
                item => {
                    service.selectItem(item);
                },
                error => console.log(error));

        /*
        service.getOwner(owner_id)
            .then(
                owner => {
                    service.selectOwner(owner);
                },
                error => console.log(error));
                */

        service.getComments(item_id)
            .then(
                comments => {
                    service.selectComments(comments);
                },
                error => console.log(error));
    }

    gotoEdit(item_id: number): void {
        console.log("clicked for edition. item_id: " + item_id);

        let service = this.itemsService;
        service.getDetailedItem(item_id)
            .then(
                item => {
                    service.selectItem(item);
                    $('#edit-item-modal').modal('show');
                },
                error => console.log(error));
    }

    ngOnDestroy() {
        this.subscription.unsubscribe();
    }
}
