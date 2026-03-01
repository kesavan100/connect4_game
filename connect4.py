import streamlit as st
import numpy as np
import random

ROW_COUNT = 6
COLUMN_COUNT = 7
PLAYER = 1
AI = 2
EMPTY = 0
WINDOW_LENGTH = 4

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
    # Horizontal
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all(board[r][c+i] == piece for i in range(WINDOW_LENGTH)):
                return True

    # Vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r+i][c] == piece for i in range(WINDOW_LENGTH)):
                return True

    # Positive diagonal
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if all(board[r+i][c+i] == piece for i in range(WINDOW_LENGTH)):
                return True

    # Negative diagonal
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if all(board[r-i][c+i] == piece for i in range(WINDOW_LENGTH)):
                return True

    return False


def get_valid_locations(board):
    return [c for c in range(COLUMN_COUNT) if is_valid_location(board, c)]

def is_terminal_node(board):
    return winning_move(board, PLAYER) or winning_move(board, AI) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizing):
    valid_locations = get_valid_locations(board)
    terminal = is_terminal_node(board)

    if depth == 0 or terminal:
        if terminal:
            if winning_move(board, AI):
                return None, 100000
            elif winning_move(board, PLAYER):
                return None, -100000
            else:
                return None, 0
        else:
            return None, 0

    if maximizing:
        value = -np.inf
        column = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp = board.copy()
            drop_piece(temp, row, col, AI)
            new_score = minimax(temp, depth-1, alpha, beta, False)[1]

            if new_score > value:
                value = new_score
                column = col

            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return column, value

    else:
        value = np.inf
        column = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp = board.copy()
            drop_piece(temp, row, col, PLAYER)
            new_score = minimax(temp, depth-1, alpha, beta, True)[1]

            if new_score < value:
                value = new_score
                column = col

            beta = min(beta, value)
            if alpha >= beta:
                break

        return column, value


st.set_page_config(page_title="Connect Four", layout="centered")

if "board" not in st.session_state:
    st.session_state.board = create_board()
    st.session_state.turn = random.randint(PLAYER, AI)
    st.session_state.game_over = False
    st.session_state.message = ""
    st.session_state.play_drop = False
    st.session_state.play_win = False

st.title("🔴🟡 Connect Four – Click Column to Drop. You Vs Ai")

# ---------- DRAW BOARD ----------

def draw_board(board):
    symbols = {0: "⚪", 1: "🔴", 2: "🟡"}

    click_cols = st.columns(COLUMN_COUNT)
    for c in range(COLUMN_COUNT):
        if click_cols[c].button("⬇️", key=f"col{c}") and not st.session_state.game_over:
            handle_player_move(c)

    
    for r in range(ROW_COUNT - 1, -1, -1):
        cols = st.columns(COLUMN_COUNT)
        for c in range(COLUMN_COUNT):
            with cols[c]:
                st.markdown(
                    f"<div style='font-size:35px;text-align:center'>{symbols[board[r][c]]}</div>",
                    unsafe_allow_html=True
                )


def handle_player_move(col):
    if st.session_state.turn != PLAYER:
        return

    if is_valid_location(st.session_state.board, col):
        row = get_next_open_row(st.session_state.board, col)
        drop_piece(st.session_state.board, row, col, PLAYER)
        st.session_state.play_drop = True

        if winning_move(st.session_state.board, PLAYER):
            st.session_state.game_over = True
            st.session_state.message = "🎉 You Win!"
            st.session_state.play_win = True
        elif len(get_valid_locations(st.session_state.board)) == 0:
            st.session_state.game_over = True
            st.session_state.message = "🤝 It's a Tie!"
        else:
            st.session_state.turn = AI


draw_board(st.session_state.board)

# Play sounds AFTER rendering
if st.session_state.play_drop:
    st.audio("drop_sound.wav", autoplay=True)
    st.session_state.play_drop = False

if st.session_state.play_win:
    st.audio("win_sound.wav", autoplay=True)
    st.session_state.play_win = False

# AI Turn
if st.session_state.turn == AI and not st.session_state.game_over:
    col, _ = minimax(st.session_state.board, 4, -np.inf, np.inf, True)

    if col is not None:
        row = get_next_open_row(st.session_state.board, col)
        drop_piece(st.session_state.board, row, col, AI)
        st.session_state.play_drop = True

        if winning_move(st.session_state.board, AI):
            st.session_state.game_over = True
            st.session_state.message = "🤖 AI Wins!"
            st.session_state.play_win = True
        elif len(get_valid_locations(st.session_state.board)) == 0:
            st.session_state.game_over = True
            st.session_state.message = "🤝 It's a Tie!"
        else:
            st.session_state.turn = PLAYER

    st.rerun()

# ---------- GAME OVER ----------

if st.session_state.game_over:
    st.subheader(st.session_state.message)
    if st.button("🔁 Play Again"):
        st.session_state.board = create_board()
        st.session_state.turn = random.randint(PLAYER, AI)
        st.session_state.game_over = False
        st.session_state.message = ""
        st.rerun()
