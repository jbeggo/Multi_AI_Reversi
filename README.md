<h1 align="center">⚫ Othello/Reversi ⚪ </h1>

A GUI-equipped, [Othello/Reversi](https://www.worldothello.org/about/about-othello/othello-rules/official-rules/english) game made in **Python3** using the `pygame` library. Featuring PvP as well as AI.

## Description
Reversi is played on an 8x8 board, with 64 discs that are black on one side and white on the other. Each player gets 32 such discs, out of which 2 from each player are kept on the board in the following manner:

![image](https://github.com/TERNION-1121/Othello-Reversi-Game/assets/97667653/ea03fdd8-9abc-4b14-bdc9-7d983fb38041)

<br>

A move consists of "outflanking" your opponent's disc(s), then flipping the "outflanked" disc(s) to your color.
To outflank means, if your disc is kept on square X, and you have another disc on square Y, such that:
- X and Y lie on the same row, or
- X and Y lie on the same column, or
- X and Y lie on the same diagonal,

If any one (or more) of the above is the case while playing, then the Opponent's discs between X and Y get flipped to your color.

<br>

Example:

> Here White disc A was already present on the board, after placing White disc B, the row of Black discs between White disc A and B got outflanked,

![06a8330dc692b7631a2e50660e4a7346](https://github.com/TERNION-1121/Othello-Reversi-Game/assets/97667653/84feed70-ee16-4f4f-baad-39a3ecc148ed)

> And thus the outflanked Black discs flipped to White.

![cd51ed676fb49538035a8bf006ffbe96](https://github.com/TERNION-1121/Othello-Reversi-Game/assets/97667653/bafe9059-7a32-4d93-aaa2-bfc97a311fce)

For a more comprehensive explanation of the game rules, check out this [link](https://www.worldothello.org/about/about-othello/othello-rules/official-rules/english).

### The "Why" of the project

It had been a long time since I had coded in Python, and I got reminded of Othello out of the blue. Thus I implemented the game in Python. 
This not only got my `pygame` GUI skills freshen up, but it also was a great experience to design the board elements myself.

P.S. If you have got any suggestions/features to add, whether it's about the two-player gameplay, or about the Othello AI itself, I would be more than grateful to you for your contribution!

<br>

### 🎯 Game Modes

#### ⚔ Two-Player Mode 
Two players can play the game, alternating their turns.

#### 🤖 Play with Computer
Play with the computer! It makes use of the minimax algorithm with alpha-beta pruning. 

Currently the algorithm makes use of the following heuristics for a position's evaluation:
- Coin parity
- Mobility
- Corner Values

> Thanks to [@Zhe Xun](https://github.com/HersheyZinc) for their help in improving the A.I Player's minimax algorithm!

### How to Play the Game 🎮
1. Download the source code. (Either clone the repository or download the whole code from GitHub)
2. Make sure to install Python3 on your Computer along with `pip`. (Python3.10+ is required)
3. Open your terminal, navigate to `~/Othello-Reversi-Game` and type the command:
   ```
   pip install -r requirements
   ```
5. Navigate to the `src` directory, run the `main.py` file and play the game!
> P.S. You can change color modes using the 'L' key!
