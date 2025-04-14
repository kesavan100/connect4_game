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
    return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def winning_move(board, piece):
    # Check horizontal
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all(board[r][c+i] == piece for i in range(WINDOW_LENGTH)):
                return True
    # Check vertical
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

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER if piece == AI else AI
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4
    return score

def score_position(board, piece):
    score = 0
    # Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    score += center_array.count(piece) * 3

    # Score horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Positive diagonals
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Negative diagonals
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def get_valid_locations(board):
    return [c for c in range(COLUMN_COUNT) if is_valid_location(board, c)]

def is_terminal_node(board):
    return winning_move(board, PLAYER) or winning_move(board, AI) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    terminal = is_terminal_node(board)
    if depth == 0 or terminal:
        if terminal:
            if winning_move(board, AI):
                return (None, 100000000000)
            elif winning_move(board, PLAYER):
                return (None, -100000000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, AI))

    if maximizingPlayer:
        value = -np.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
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
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

# Initialize Streamlit
st.set_page_config(page_title="Connect Four: You vs AI", layout="centered")

if "board" not in st.session_state:
    st.session_state.board = create_board()
    st.session_state.game_over = False
    st.session_state.turn = random.randint(PLAYER, AI)
    st.session_state.message = "Your Turn" if st.session_state.turn == PLAYER else "AI Turn"

st.title("🔴🟡 Connect Four – You vs AI")

def draw_board(board):
    symbols = {0: "⚪", 1: "🔴", 2: "🟡"}
    for r in range(ROW_COUNT-1, -1, -1):
        cols = st.columns(COLUMN_COUNT)
        for c in range(COLUMN_COUNT):
            with cols[c]:
                st.markdown(f"<div style='font-size: 30px; text-align: center'>{symbols[board[r][c]]}</div>", unsafe_allow_html=True)

draw_board(st.session_state.board)
st.markdown("---")

if st.session_state.game_over:
    st.subheader(st.session_state.message)
    if st.button("🔁 Play Again"):
        st.session_state.board = create_board()
        st.session_state.game_over = False
        st.session_state.turn = random.randint(PLAYER, AI)
        st.session_state.message = "Your Turn" if st.session_state.turn == PLAYER else "AI Turn"
    st.stop()

# Player's turn
if st.session_state.turn == PLAYER:
    cols = st.columns(COLUMN_COUNT)
    for c in range(COLUMN_COUNT):
        if cols[c].button(f"Drop in {c+1}"):
            if is_valid_location(st.session_state.board, c):
                row = get_next_open_row(st.session_state.board, c)
                drop_piece(st.session_state.board, row, c, PLAYER)
                if winning_move(st.session_state.board, PLAYER):
                    st.session_state.game_over = True
                    st.session_state.message = "🎉 You Win!"
                elif len(get_valid_locations(st.session_state.board)) == 0:
                    st.session_state.game_over = True
                    st.session_state.message = "🤝 It's a Tie!"
                else:
                    st.session_state.turn = AI
            st.experimental_rerun()

# AI's turn
elif st.session_state.turn == AI and not st.session_state.game_over:
    col, _ = minimax(st.session_state.board, 4, -np.inf, np.inf, True)
    if col is not None and is_valid_location(st.session_state.board, col):
        row = get_next_open_row(st.session_state.board, col)
        drop_piece(st.session_state.board, row, col, AI)
        if winning_move(st.session_state.board, AI):
            st.session_state.game_over = True
            st.session_state.message = "🤖 AI Wins!"
        elif len(get_valid_locations(st.session_state.board)) == 0:
            st.session_state.game_over = True
            st.session_state.message = "🤝 It's a Tie!"
        else:
            st.session_state.turn = PLAYER
    st.experimental_rerun()
