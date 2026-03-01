import streamlit as st
import numpy as np
import random
import base64

ROW_COUNT = 6
COLUMN_COUNT = 7
PLAYER = 1
AI = 2
EMPTY = 0
WINDOW_LENGTH = 4

def play_sound(file):
    with open(file, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
        <audio autoplay>
        <source src="data:audio/wav;base64,{b64}" type="audio/wav">
        </audio>
        """
        st.markdown(md, unsafe_allow_html=True)



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


def get_valid_locations(board):
    return [c for c in range(COLUMN_COUNT) if is_valid_location(board, c)]

def is_terminal(board):
    return winning_move(board, PLAYER) or winning_move(board, AI) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizing):
    valid = get_valid_locations(board)
    terminal = is_terminal(board)

    if depth == 0 or terminal:
        if terminal:
            if winning_move(board, AI):
                return None, 100000
            elif winning_move(board, PLAYER):
                return None, -100000
            else:
                return None, 0
        return None, 0

    if maximizing:
        value = -np.inf
        column = random.choice(valid)

        for col in valid:
            row = get_next_open_row(board, col)
            temp = board.copy()
            drop_piece(temp, row, col, AI)
            score = minimax(temp, depth-1, alpha, beta, False)[1]

            if score > value:
                value = score
                column = col

            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return column, value

    else:
        value = np.inf
        column = random.choice(valid)

        for col in valid:
            row = get_next_open_row(board, col)
            temp = board.copy()
            drop_piece(temp, row, col, PLAYER)
            score = minimax(temp, depth-1, alpha, beta, True)[1]

            if score < value:
                value = score
                column = col

            beta = min(beta, value)
            if alpha >= beta:
                break

        return column, value


st.set_page_config(layout="centered")

if "board" not in st.session_state:
    st.session_state.board = create_board()
    st.session_state.turn = random.randint(PLAYER, AI)
    st.session_state.game_over = False
    st.session_state.message = ""

st.title("🔵 Connect Four")

st.markdown("""
<style>
.board {
    display: grid;
    grid-template-columns: repeat(7, 70px);
    gap: 10px;
    background-color: #0057b7;
    padding: 15px;
    border-radius: 15px;
}
.cell {
    width: 70px;
    height: 70px;
    border-radius: 50%;
    background-color: white;
}
.red { background-color: #e63946; }
.yellow { background-color: #ffbe0b; }
.clickable {
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

def player_move(col):
    if is_valid_location(st.session_state.board, col):
        row = get_next_open_row(st.session_state.board, col)
        drop_piece(st.session_state.board, row, col, PLAYER)
        play_sound("drop_sound.wav")

        if winning_move(st.session_state.board, PLAYER):
            st.session_state.game_over = True
            st.session_state.message = "🎉 You Win!"
            play_sound("win_sound.wav")
        else:
            st.session_state.turn = AI


board_html = '<div class="board">'

for r in range(ROW_COUNT - 1, -1, -1):
    for c in range(COLUMN_COUNT):
        piece = st.session_state.board[r][c]

        if piece == PLAYER:
            board_html += '<div class="cell red"></div>'
        elif piece == AI:
            board_html += '<div class="cell yellow"></div>'
        else:
            board_html += f'<div class="cell clickable" onclick="window.location.href=\'?col={c}\'"></div>'

board_html += "</div>"

st.markdown(board_html, unsafe_allow_html=True)


query_params = st.query_params
if "col" in query_params and not st.session_state.game_over:
    col = int(query_params["col"])
    player_move(col)
    st.query_params.clear()
    st.rerun()

if st.session_state.turn == AI and not st.session_state.game_over:
    col, _ = minimax(st.session_state.board, 4, -np.inf, np.inf, True)

    if col is not None:
        row = get_next_open_row(st.session_state.board, col)
        drop_piece(st.session_state.board, row, col, AI)
        play_sound("drop_sound.wav")

        if winning_move(st.session_state.board, AI):
            st.session_state.game_over = True
            st.session_state.message = "🤖 AI Wins!"
            play_sound("win_sound.wav")
        else:
            st.session_state.turn = PLAYER

    st.rerun()

if st.session_state.game_over:
    st.subheader(st.session_state.message)
    if st.button("Play Again"):
        st.session_state.board = create_board()
        st.session_state.turn = random.randint(PLAYER, AI)
        st.session_state.game_over = False
        st.session_state.message = ""
        st.rerun()
