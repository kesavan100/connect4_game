import numpy as np
import pygame
import sys
import math
import random

# Game settings
ROW_COUNT = 6
COLUMN_COUNT = 7
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)

# Colors
BLUE = (0, 102, 204)
BLACK = (0, 0, 0)
RED = (255, 87, 34)
YELLOW = (255, 235, 59)
WHITE = (255, 255, 255)
LIGHT_BLUE = (173, 216, 230)
GREEN = (0, 255, 0)
DARK_BLUE = (0, 51, 102)

PLAYER = 0
AI = 1
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2
WINDOW_LENGTH = 4

pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Connect Four: You vs AI")
myfont = pygame.font.SysFont("monospace", 75)

# Load sounds
pygame.mixer.init()
try:
    drop_sound = pygame.mixer.Sound("drop_sound.wav")
    win_sound = pygame.mixer.Sound("win_sound.wav")
except:
    drop_sound = win_sound = None

def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def winning_move(board, piece):
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all(board[r][c+i] == piece for i in range(4)):
                return True
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r+i][c] == piece for i in range(4)):
                return True
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if all(board[r+i][c+i] == piece for i in range(4)):
                return True
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if all(board[r-i][c+i] == piece for i in range(4)):
                return True
    return False

def draw_board(board, winner=None):
    screen.fill(LIGHT_BLUE)
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, (r+1)*SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int((r+1)*SQUARESIZE+SQUARESIZE/2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height - int((r)*SQUARESIZE + SQUARESIZE/2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height - int((r)*SQUARESIZE + SQUARESIZE/2)), RADIUS)

    pygame.draw.rect(screen, DARK_BLUE, (0, 0, width, SQUARESIZE))

    if winner is not None:
        text = "You Win!" if winner == PLAYER else "AI Wins!"
        color = GREEN if winner == PLAYER else RED
        label = myfont.render(text, True, color)
        screen.blit(label, (width // 2 - label.get_width() // 2, 10))

    pygame.display.update()

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 80
    return score

def score_position(board, piece):
    score = 0
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    score += center_array.count(piece) * 3

    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def get_valid_locations(board):
    return [c for c in range(COLUMN_COUNT) if is_valid_location(board, c)]

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -100000000000)
            else:
                return (None, 0)
        return (None, score_position(board, AI_PIECE))

    if maximizingPlayer:
        value = -math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value
    else:
        value = math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value

# Game start
board = create_board()
game_over = False
turn = random.randint(PLAYER, AI)
draw_board(board)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, DARK_BLUE, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            pygame.draw.circle(screen, RED, (posx, SQUARESIZE // 2), RADIUS)
            pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            pygame.draw.rect(screen, DARK_BLUE, (0, 0, width, SQUARESIZE))
            if turn == PLAYER:
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)
                    if drop_sound:
                        drop_sound.play()
                    if winning_move(board, PLAYER_PIECE):
                        draw_board(board, winner=PLAYER)
                        if win_sound:
                            win_sound.play()
                        pygame.time.wait(2000)
                        board = create_board()
                        draw_board(board)
                        turn = random.randint(PLAYER, AI)
                    elif len(get_valid_locations(board)) == 0:
                        draw_board(board)
                        label = myfont.render("Draw!", True, WHITE)
                        screen.blit(label, (width // 2 - label.get_width() // 2, 10))
                        pygame.display.update()
                        pygame.time.wait(2000)
                        board = create_board()
                        draw_board(board)
                        turn = random.randint(PLAYER, AI)
                    else:
                        draw_board(board)
                        turn = AI

    if turn == AI and not game_over:
        pygame.time.wait(500)
        col, _ = minimax(board, 4, -math.inf, math.inf, True)
        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)
            if drop_sound:
                drop_sound.play()
            if winning_move(board, AI_PIECE):
                draw_board(board, winner=AI)
                if win_sound:
                    win_sound.play()
                pygame.time.wait(2000)
                board = create_board()
                draw_board(board)
                turn = random.randint(PLAYER, AI)
            elif len(get_valid_locations(board)) == 0:
                draw_board(board)
                label = myfont.render("Draw!", True, WHITE)
                screen.blit(label, (width // 2 - label.get_width() // 2, 10))
                pygame.display.update()
                pygame.time.wait(2000)
                board = create_board()
                draw_board(board)
                turn = random.randint(PLAYER, AI)
            else:
                draw_board(board)
                turn = PLAYER
