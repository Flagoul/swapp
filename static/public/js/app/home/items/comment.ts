import { CommentCreationDTO } from './comment-creation-dto';

export class Comment {
    id: number;
    content: string;
    date: Date;
    user: number;
    item: number;
    username: string;
    user_fullname: string;
    user_profile_picture: string;

    constructor() {
        this.id = null;
        this.content = "";
        this.date = null;
        this.user = null;
        this.item = null;
        this.username = "";
        this.user_fullname = "";
        this.user_profile_picture = null;
    }

    fromCreationDTO(commentCreationDTO: CommentCreationDTO) {
        this.user = commentCreationDTO.user;
        this.content = commentCreationDTO.content;
    }
}