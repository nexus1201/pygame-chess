import pygame

WIDTH = 512
HEIGHT = 512
TILE_SIZE = WIDTH // 8

WHITE = "white"
BLACK = "black"

PIECE_SYMBOLS = {
    "K": "♔",
    "Q": "♕",
    "R": "♖",
    "B": "♗",
    "N": "♘",
    "P": "♙",
    "k": "♚",
    "q": "♛",
    "r": "♜",
    "b": "♝",
    "n": "♞",
    "p": "♟",
}

STARTING_BOARD = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p"] * 8,
    ["."] * 8,
    ["."] * 8,
    ["."] * 8,
    ["."] * 8,
    ["P"] * 8,
    ["R", "N", "B", "Q", "K", "B", "N", "R"],
]

LIGHT_COLOR = (235, 235, 208)
DARK_COLOR = (119, 148, 85)
HIGHLIGHT_COLOR = (246, 246, 105)
SELECT_COLOR = (246, 200, 80)
TEXT_COLOR = (20, 20, 20)

pygame.init()
preferred_fonts = ["Segoe UI Symbol", "Arial Unicode MS", "DejaVu Sans", "Symbola"]
font = None
for face in preferred_fonts:
    try:
        font = pygame.font.SysFont(face, 40)
        if font and font.size("♔")[0] > 0:
            break
    except Exception:
        font = None
if not font:
    font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 24)
screen = pygame.display.set_mode((WIDTH, HEIGHT + 40))
pygame.display.set_caption("Chess Game")
clock = pygame.time.Clock()


def draw_board(surface, board, selected, legal_moves):
    for row in range(8):
        for col in range(8):
            color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, color, rect)
            if selected == (row, col):
                pygame.draw.rect(surface, SELECT_COLOR, rect, 6)
            elif (row, col) in legal_moves:
                pygame.draw.rect(surface, HIGHLIGHT_COLOR, rect, 6)

            piece = board[row][col]
            if piece != ".":
                text = font.render(PIECE_SYMBOLS[piece], True, TEXT_COLOR)
                text_rect = text.get_rect(center=rect.center)
                surface.blit(text, text_rect)


def in_bounds(row, col):
    return 0 <= row < 8 and 0 <= col < 8


def piece_color(piece):
    if piece == ".":
        return None
    return WHITE if piece.isupper() else BLACK


def enemy_color(color):
    return BLACK if color == WHITE else WHITE


def generate_moves(board, row, col):
    piece = board[row][col]
    if piece == ".":
        return []

    color = piece_color(piece)
    directions = []
    moves = []

    if piece.upper() == "P":
        step = -1 if color == WHITE else 1
        start_row = 6 if color == WHITE else 1
        forward_row = row + step
        if in_bounds(forward_row, col) and board[forward_row][col] == ".":
            moves.append((forward_row, col))
            if row == start_row:
                double_row = row + 2 * step
                if board[double_row][col] == ".":
                    moves.append((double_row, col))
        for capture_col in (col - 1, col + 1):
            if in_bounds(forward_row, capture_col):
                target = board[forward_row][capture_col]
                if target != "." and piece_color(target) != color:
                    moves.append((forward_row, capture_col))
        return moves

    if piece.upper() == "N":
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
            r, c = row + dr, col + dc
            if in_bounds(r, c) and piece_color(board[r][c]) != color:
                moves.append((r, c))
        return moves

    if piece.upper() == "B":
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    elif piece.upper() == "R":
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    elif piece.upper() == "Q":
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
    elif piece.upper() == "K":
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            r, c = row + dr, col + dc
            if in_bounds(r, c) and piece_color(board[r][c]) != color:
                moves.append((r, c))
        return moves

    for dr, dc in directions:
        r, c = row + dr, col + dc
        while in_bounds(r, c):
            if board[r][c] == ".":
                moves.append((r, c))
            elif piece_color(board[r][c]) != color:
                moves.append((r, c))
                break
            else:
                break
            r += dr
            c += dc
    return moves


def copy_board(board):
    return [row.copy() for row in board]


def find_king(board, color):
    king = "K" if color == WHITE else "k"
    for row in range(8):
        for col in range(8):
            if board[row][col] == king:
                return row, col
    return None


def square_attacked(board, row, col, attacker_color):
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece != "." and piece_color(piece) == attacker_color:
                for move in generate_moves(board, r, c):
                    if move == (row, col):
                        return True
    return False


def in_check(board, color):
    king_pos = find_king(board, color)
    if king_pos is None:
        return True
    return square_attacked(board, king_pos[0], king_pos[1], enemy_color(color))


def legal_moves(board, row, col):
    piece = board[row][col]
    if piece == ".":
        return []
    color = piece_color(piece)
    moves = []
    for target in generate_moves(board, row, col):
        test_board = copy_board(board)
        test_board[target[0]][target[1]] = piece
        test_board[row][col] = "."
        if not in_check(test_board, color):
            moves.append(target)
    return moves


def all_legal_moves(board, color):
    moves = []
    for r in range(8):
        for c in range(8):
            if board[r][c] != "." and piece_color(board[r][c]) == color:
                for target in legal_moves(board, r, c):
                    moves.append(((r, c), target))
    return moves


def apply_move(board, start, end):
    piece = board[start[0]][start[1]]
    board[end[0]][end[1]] = piece
    board[start[0]][start[1]] = "."
    if piece == "P" and end[0] == 0:
        board[end[0]][end[1]] = "Q"
    if piece == "p" and end[0] == 7:
        board[end[0]][end[1]] = "q"


def position_to_square(pos):
    col = pos[0] // TILE_SIZE
    row = pos[1] // TILE_SIZE
    return row, col


def draw_status(surface, message):
    pygame.draw.rect(surface, (220, 220, 220), pygame.Rect(0, HEIGHT, WIDTH, 40))
    status = small_font.render(message, True, TEXT_COLOR)
    surface.blit(status, (10, HEIGHT + 10))


def main():
    board = copy_board(STARTING_BOARD)
    selected = None
    turn = WHITE
    running = True
    legal = []
    game_over = False
    status_message = "White to move"

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                pos = pygame.mouse.get_pos()
                if pos[1] < HEIGHT:
                    row, col = position_to_square(pos)
                    piece = board[row][col]
                    if selected is None:
                        if piece != "." and piece_color(piece) == turn:
                            selected = (row, col)
                            legal = legal_moves(board, row, col)
                        else:
                            selected = None
                            legal = []
                    else:
                        if (row, col) in legal:
                            apply_move(board, selected, (row, col))
                            next_turn = enemy_color(turn)
                            if in_check(board, next_turn):
                                if not all_legal_moves(board, next_turn):
                                    status_message = f"Checkmate! {turn.capitalize()} wins"
                                    game_over = True
                                else:
                                    status_message = f"{next_turn.capitalize()} is in check"
                            else:
                                if not all_legal_moves(board, next_turn):
                                    status_message = "Stalemate!"
                                    game_over = True
                                else:
                                    status_message = f"{next_turn.capitalize()} to move"
                            turn = next_turn
                            legal = []
                            selected = None
                        elif piece != "." and piece_color(piece) == turn:
                            selected = (row, col)
                            legal = legal_moves(board, row, col)
                        else:
                            selected = None
                            legal = []

        screen.fill((0, 0, 0))
        draw_board(screen, board, selected, legal)
        draw_status(screen, status_message)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
