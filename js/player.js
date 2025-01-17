class Player {
    constructor(game) {
        this.game = game;
        this.x = 20;
        this.y = 0;
        this.spriteWidth = 200;
        this.spriteHeight = 200;    
        this.width;
        this.height;    
        this.speedY;
        this.flapSpeed;
        this.collisionX;  //Collision
        this.collisionY;   //Collision
        this.collisionRadius;   //Collision
        this.collided;   //Collision
    }

    draw() {
        this.game.ctx.fillRect(this.x, this.y, this.width, this.height);
        this.game.ctx.beginPath();   //Collision
        this.game.ctx.arc(this.collisionX, this.collisionY, this.collisionRadius, 0, Math.PI * 2);   //Collision
        this.game.ctx.stroke();   //Collision
    }

    update() {
        this.y += this.speedY;

        if(this.isTouchingBottom())    {
            this.y = this.game.height - this.height;
        }
        else    {
            this.speedY += this.game.gravity;
        }

        this.collisionY = this.y + this.height * 0.5;   //Collision
    }

    resize() {
        this.width = this.spriteWidth * this.game.ratio;
        this.height = this.spriteHeight * this.game.ratio;
        this.y = this.game.height * 0.5 - this.height * 0.5;
        this.speedY = -8 * this.game.ratio;
        this.flapSpeed = 6 * this.game.ratio;
        this.collisionX = this.x + this.width * 0.5;   //Collision
        this.collisionRadius = this.width * 0.5;   //Collision
        this.collided = false;   //Collision
    }

    isTouchingBottom()  {
        return this.y >= this.game.height - this.height;
    }

    isTouchingTop() {
        return this.y <= 0;
    }

    flap()  {
        if(!this.isTouchingTop())    {
            this.speedY = -this.flapSpeed;
        }
    }
}