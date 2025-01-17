class Game {
    constructor(canvas, context) {
        this.canvas = canvas;
        this.ctx = context;
        this.width = this.canvas.width;
        this.height = this.canvas.height;
        this.baseHeight = 720;
        this.ratio = this.height / this.baseHeight;
        this.background = new Background(this);
        this.player = new Player(this);
        this.obstacles = [];
        this.numberOfObstacles = 10;
        this.gravity;
        this.speed;
        this.score;
        this.gameOver;
        this.timer;
        this.message1;  //Win or Lose
        this.message2;  //Win or Lose

        this.resize(window.innerWidth, window.innerHeight);

        window.addEventListener('resize', e => {
            this.resize(e.currentTarget.innerWidth, e.currentTarget.innerHeight);
        });

        // Mouse controls
        this.canvas.addEventListener('mousedown', e => {
            this.player.flap();
        });

        // Keyboard controls
        window.addEventListener('keydown', e => {
            if((e.key === ' ') || (e.key === 'Enter'))  {
                this.player.flap();
            }
        });

        // Touch controls
        this.canvas.addEventListener('touchstart', e => {
            this.player.flap();
        });
    }

    resize(width, height)    {
        this.canvas.width = width;
        this.canvas.height = height;
        this.width = this.canvas.width;
        this.height = this.canvas.height;
        this.ctx.fillStyle = '#5995F2';
        this.ctx.font = '15px Bungee';
        this.ctx.textAlign = 'right';
        this.ctx.lineWidth = 3;   //Collision
        this.ctx.strokeStyle = 'white';   //Collision
        this.ratio = this.height / this.baseHeight;

        this.gravity = 0.15 * this.ratio;
        this.speed = 3 * this.ratio;
        this.background.resize();
        this.player.resize();
        this.createObstacles();
        this.obstacles.forEach(obstacle => {
            obstacle.resize();
        });

        this.score = 0;
        this.gameOver = false;
        this.timer = 0;
    }

    render(deltaTime) {
        console.log(deltaTime);
        if(!this.gameOver) this.timer += deltaTime;
        this.background.update();
        this.background.draw();
        this.drawStatusText();
        this.player.update();
        this.player.draw();
        this.obstacles.forEach(obstacle => {
            obstacle.update();
            obstacle.draw();
        });
    }

    createObstacles()   {
        this.obstacles = [];
        const firstX = this.baseHeight * this.ratio;
        const obstacleSpacing = 600 * this.ratio;

        for(let i = 0; i < this.numberOfObstacles; i++)   {
            this.obstacles.push(new Obstacle(this, firstX + i * obstacleSpacing));
        }
    }

    formatTimer()   {
        return (this.timer * 0.001).toFixed(1);
    }

    drawStatusText()    {
        this.ctx.save();
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.fillText('Score: ' + this.score, this.width - 10, 30);
        this.ctx.textAlign = 'left';
        this.ctx.fillText('Timer: ' + this.formatTimer(), 10, 30);
        
        if(this.gameOver) {
            if(this.player.collided)    {  //Win or Lose
                this.message1 = "Getting rusty?";  //Win or Lose
                this.message2 = "Collison time " + this.formatTimer() + " seconds!";  //Win or Lose
            }  //Win or Lose
            else    {  //Win or Lose
                this.message1 = "Nailed it!";  //Win or Lose
                this.message2 = "Can you do it faster than " + this.formatTimer() + " seconds?";  //Win or Lose
            }  //Win or Lose

            this.ctx.font = '30px Bungee';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(this.message1, this.width * 0.5, this.height * 0.5 - 40);  //Win or Lose
            this.ctx.font = '15px Bungee';  //Win or Lose
            this.ctx.fillText(this.message2, this.width * 0.5, this.height * 0.5 - 20);  //Win or Lose
            this.ctx.fillText("Press 'R' to try again!", this.width * 0.5, this.height * 0.5);  //Win or Lose
        }

        this.ctx.restore();
    }

    checkCollision(a, b)    {   //Collision
        const dx = a.collisionX - b.collisionX;   //Collision
        const dy = a.collisionY - b.collisionY;   //Collision
        const distance = Math.sqrt(dx * dx + dy * dy);   //Collision
        //const distance = Math.hypot(dx, dy);   //Collision
        const sumOfRadii = a.collisionRadius + b.collisionRadius;   //Collision
        return distance <= sumOfRadii;   //Collision
    }
}

window.addEventListener('load', function() {
    const canvas = document.getElementById('game-layout');
    const ctx = canvas.getContext('2d');
    canvas.width = 720;
    canvas.height = 720;

    const game = new Game(canvas, ctx);

    let lastTime = 0;
    function animate(timeStamp) {
        const deltaTime = timeStamp - lastTime;
        lastTime = timeStamp;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        game.render(deltaTime);
        requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
});