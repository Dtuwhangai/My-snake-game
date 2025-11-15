import sys
import random
import json
import os
import pygame
from pygame.locals import *
import colorsys
import math
# test

# Game configuration
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
CELL_SIZE = 20
assert WINDOW_WIDTH % CELL_SIZE == 0, "Window width must be a multiple of cell size"
assert WINDOW_HEIGHT % CELL_SIZE == 0, "Window height must be a multiple of cell size"
CELL_WIDTH = WINDOW_WIDTH // CELL_SIZE
CELL_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 155, 0)

# Directions
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

# Settings file
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), 'settings.json')
DEFAULT_SETTINGS = {
    'color': [0, 255, 0],
    'head_color': [0, 155, 0],
    'difficulty': 'Normal',
    'show_grid': True
}


def load_settings():
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, 'r') as f:
                data = json.load(f)
                # validate minimal shape
                if 'color' in data and 'head_color' in data and 'difficulty' in data:
                    return data
    except Exception:
        pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    try:
        with open(SETTINGS_PATH, 'w') as f:
            json.dump(settings, f)
    except Exception:
        pass


# High score persistence
HIGH_SCORES_PATH = os.path.join(os.path.dirname(__file__), 'high_scores.json')


def load_high_scores():
    try:
        if os.path.exists(HIGH_SCORES_PATH):
            with open(HIGH_SCORES_PATH, 'r') as f:
                data = json.load(f)
                return data
    except Exception:
        pass
    # default structure
    return {'Easy': 0, 'Normal': 0, 'Hard': 0}


def save_high_scores(scores):
    try:
        with open(HIGH_SCORES_PATH, 'w') as f:
            json.dump(scores, f)
    except Exception:
        pass


def modal_color_picker(screen, clock, font, initial_rgb):
    # Simple modal with three text inputs (R,G,B) and OK/Cancel
    r, g, b = initial_rgb
    input_active = [False, False, False]
    input_text = [str(r), str(g), str(b)]

    title_font = pygame.font.SysFont(None, 40)
    title = title_font.render('Custom Color (0-255)', True, BLACK)
    title_rect = title.get_rect()
    title_rect.center = (WINDOW_WIDTH // 2, 80)

    box_w, box_h = 80, 40
    boxes = []
    start_x = WINDOW_WIDTH // 2 - (box_w * 3 + 20) // 2
    y = 140
    for i in range(3):
        rect = pygame.Rect(start_x + i * (box_w + 10), y, box_w, box_h)
        boxes.append(rect)

    ok_rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, y + 100, 100, 40)
    cancel_rect = pygame.Rect(WINDOW_WIDTH // 2 + 20, y + 100, 100, 40)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                # toggle active box
                for i, rect in enumerate(boxes):
                    if rect.collidepoint(mouse_pos):
                        input_active = [False, False, False]
                        input_active[i] = True
                if ok_rect.collidepoint(mouse_pos):
                    try:
                        nr = max(0, min(255, int(input_text[0])))
                        ng = max(0, min(255, int(input_text[1])))
                        nb = max(0, min(255, int(input_text[2])))
                        return (nr, ng, nb)
                    except Exception:
                        pass
                if cancel_rect.collidepoint(mouse_pos):
                    return initial_rgb
            elif event.type == KEYDOWN:
                for i in range(3):
                    if input_active[i]:
                        if event.key == K_BACKSPACE:
                            input_text[i] = input_text[i][:-1]
                        elif event.unicode.isdigit():
                            input_text[i] += event.unicode
                        elif event.key == K_RETURN:
                            input_active = [False, False, False]

        # draw modal
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((220, 220, 220))
        screen.blit(overlay, (0, 0))

        screen.blit(title, title_rect)
        labels = ['R', 'G', 'B']
        for i, rect in enumerate(boxes):
            pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            txt = font.render(input_text[i] if input_text[i] != '' else '0', True, BLACK)
            txt_rect = txt.get_rect()
            txt_rect.center = rect.center
            screen.blit(txt, txt_rect)
            lbl = font.render(labels[i], True, BLACK)
            screen.blit(lbl, (rect.x - 20, rect.y + 8))

        pygame.draw.rect(screen, (100, 200, 100), ok_rect)
        pygame.draw.rect(screen, BLACK, ok_rect, 2)
        ok_txt = font.render('OK', True, BLACK)
        ok_rect_txt = ok_txt.get_rect()
        ok_rect_txt.center = ok_rect.center
        screen.blit(ok_txt, ok_rect_txt)

        pygame.draw.rect(screen, (200, 100, 100), cancel_rect)
        pygame.draw.rect(screen, BLACK, cancel_rect, 2)
        c_txt = font.render('Cancel', True, BLACK)
        c_rect_txt = c_txt.get_rect()
        c_rect_txt.center = cancel_rect.center
        screen.blit(c_txt, c_rect_txt)

        pygame.display.update()
        clock.tick(30)


def modal_color_wheel(screen, clock, font, initial_rgb):
    """Modal color wheel picker.
    Shows a hue/saturation wheel at left, brightness and saturation sliders at right,
    live preview, and OK/Cancel buttons. Returns (r,g,b) or None on cancel.
    """
    width, height = screen.get_size()
    modal_w = min(740, width - 80)
    modal_h = min(480, height - 80)
    modal_x = (width - modal_w) // 2
    modal_y = (height - modal_h) // 2

    wheel_radius = min(200, modal_h // 2 - 20)
    wheel_center = (modal_x + 40 + wheel_radius, modal_y + modal_h // 2)

    # initial HSV
    r0, g0, b0 = [c / 255.0 for c in initial_rgb]
    h0, s0, v0 = colorsys.rgb_to_hsv(r0, g0, b0)

    hue = h0
    sat = s0
    val = v0

    # helper: draw wheel into a surface once
    wheel_surf = pygame.Surface((wheel_radius * 2, wheel_radius * 2), pygame.SRCALPHA)
    for y in range(wheel_radius * 2):
        for x in range(wheel_radius * 2):
            dx = x - wheel_radius
            dy = y - wheel_radius
            dist = math.hypot(dx, dy)
            if 0 < dist <= wheel_radius:
                angle = (math.atan2(dy, dx) + math.pi) / (2 * math.pi)
                # angle -> hue
                h = angle
                s = dist / wheel_radius
                rr, gg, bb = colorsys.hsv_to_rgb(h, s, 1.0)
                wheel_surf.set_at((x, y), (int(rr * 255), int(gg * 255), int(bb * 255), 255))
            else:
                wheel_surf.set_at((x, y), (0, 0, 0, 0))

    # slider rects
    slider_w = 220
    slider_h = 18
    sat_slider = pygame.Rect(modal_x + modal_w - slider_w - 30, modal_y + 80, slider_w, slider_h)
    val_slider = pygame.Rect(sat_slider.x, sat_slider.y + 40, slider_w, slider_h)

    ok_btn = pygame.Rect(modal_x + modal_w - 120, modal_y + modal_h - 50, 100, 36)
    cancel_btn = pygame.Rect(ok_btn.x - 120, ok_btn.y, 100, 36)

    dragging_wheel = False
    dragging_sat = False
    dragging_val = False
    # explicit indicator position so clicks set it and brightness changes don't move it
    ind_x = wheel_center[0] + math.cos(hue * 2 * math.pi) * (sat * wheel_radius)
    ind_y = wheel_center[1] + math.sin(hue * 2 * math.pi) * (sat * wheel_radius)

    while True:
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # wheel
                dx = mx - wheel_center[0]
                dy = my - wheel_center[1]
                if dx * dx + dy * dy <= wheel_radius * wheel_radius:
                    dragging_wheel = True
                    # update hue/sat
                    angle = (math.atan2(dy, dx) + math.pi) / (2 * math.pi)
                    hue = angle % 1.0
                    sat = min(1.0, math.hypot(dx, dy) / wheel_radius)
                elif sat_slider.collidepoint((mx, my)):
                    dragging_sat = True
                    rel = (mx - sat_slider.x) / sat_slider.w
                    sat = max(0.0, min(1.0, rel))
                elif val_slider.collidepoint((mx, my)):
                    dragging_val = True
                    rel = (mx - val_slider.x) / val_slider.w
                    val = max(0.0, min(1.0, rel))
                elif ok_btn.collidepoint((mx, my)):
                    rr, gg, bb = colorsys.hsv_to_rgb(hue, sat, val)
                    return (int(rr * 255), int(gg * 255), int(bb * 255))
                elif cancel_btn.collidepoint((mx, my)):
                    return None
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                dragging_wheel = dragging_sat = dragging_val = False
            elif event.type == MOUSEMOTION:
                mx, my = event.pos
                if dragging_wheel:
                    dx = mx - wheel_center[0]
                    dy = my - wheel_center[1]
                    # update hue/sat from pointer and also store explicit indicator coords
                    hue = (math.atan2(dy, dx) + math.pi) / (2 * math.pi)
                    sat = min(1.0, math.hypot(dx, dy) / wheel_radius)
                    ind_x = wheel_center[0] + math.cos(hue * 2 * math.pi) * (sat * wheel_radius)
                    ind_y = wheel_center[1] + math.sin(hue * 2 * math.pi) * (sat * wheel_radius)
                elif dragging_sat:
                    rel = (mx - sat_slider.x) / sat_slider.w
                    sat = max(0.0, min(1.0, rel))
                    # update indicator radial distance to match new sat while preserving hue
                    ind_x = wheel_center[0] + math.cos(hue * 2 * math.pi) * (sat * wheel_radius)
                    ind_y = wheel_center[1] + math.sin(hue * 2 * math.pi) * (sat * wheel_radius)
                elif dragging_val:
                    rel = (mx - val_slider.x) / val_slider.w
                    val = max(0.0, min(1.0, rel))
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return None

        # draw modal background
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        modal = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
        pygame.draw.rect(screen, (240, 240, 240), modal)
        pygame.draw.rect(screen, BLACK, modal, 2)
        # draw wheel and controls (all indented inside the modal loop)
        screen.blit(wheel_surf, (wheel_center[0] - wheel_radius, wheel_center[1] - wheel_radius))
        # compute preview color from current HSV (use for preview box and indicator fill)
        rr, gg, bb = colorsys.hsv_to_rgb(hue, sat, val)
        preview_col = (int(rr * 255), int(gg * 255), int(bb * 255))
        # indicator on wheel: filled with the preview color and outlined with a contrasting ring
        ind_radius = 8
        pygame.draw.circle(screen, preview_col, (int(ind_x), int(ind_y)), ind_radius)
        # choose outline color for contrast
        lum = (0.2126 * preview_col[0] + 0.7152 * preview_col[1] + 0.0722 * preview_col[2])
        outline = BLACK if lum > 140 else WHITE
        pygame.draw.circle(screen, outline, (int(ind_x), int(ind_y)), ind_radius, 2)

        # draw sliders
        # saturation slider background: gradient from gray (0) to hue color (1)
        for i in range(sat_slider.w):
            t = i / sat_slider.w
            rr, gg, bb = colorsys.hsv_to_rgb(hue, t, 1.0)
            pygame.draw.line(screen, (int(rr * 255), int(gg * 255), int(bb * 255)), (sat_slider.x + i, sat_slider.y), (sat_slider.x + i, sat_slider.y + sat_slider.h - 1))
        pygame.draw.rect(screen, BLACK, sat_slider, 1)
        # sat handle
        hx = sat_slider.x + int(sat * sat_slider.w)
        pygame.draw.rect(screen, BLACK, (hx - 4, sat_slider.y - 3, 8, sat_slider.h + 6))

        # value slider gradient (black to hue color)
        for i in range(val_slider.w):
            t = i / val_slider.w
            rr, gg, bb = colorsys.hsv_to_rgb(hue, sat, t)
            pygame.draw.line(screen, (int(rr * 255), int(gg * 255), int(bb * 255)), (val_slider.x + i, val_slider.y), (val_slider.x + i, val_slider.y + val_slider.h - 1))
        pygame.draw.rect(screen, BLACK, val_slider, 1)
        vx = val_slider.x + int(val * val_slider.w)
        pygame.draw.rect(screen, BLACK, (vx - 4, val_slider.y - 3, 8, val_slider.h + 6))

        # preview box
        pr = pygame.Rect(modal_x + modal_w - 120, modal_y + 20, 80, 40)
        pygame.draw.rect(screen, preview_col, pr)
        pygame.draw.rect(screen, BLACK, pr, 1)

        # buttons
        pygame.draw.rect(screen, (200, 200, 200), ok_btn)
        pygame.draw.rect(screen, BLACK, ok_btn, 1)
        ok_s = font.render('OK', True, BLACK)
        ok_sr = ok_s.get_rect(center=ok_btn.center)
        screen.blit(ok_s, ok_sr)

        pygame.draw.rect(screen, (200, 200, 200), cancel_btn)
        pygame.draw.rect(screen, BLACK, cancel_btn, 1)
        can_s = font.render('Cancel', True, BLACK)
        can_sr = can_s.get_rect(center=cancel_btn.center)
        screen.blit(can_s, can_sr)

        pygame.display.flip()
        clock.tick(30)


def settings_screen(screen, clock, font):
    settings = load_settings()
    custom = tuple(settings.get('color', [0, 255, 0]))
    head = tuple(settings.get('head_color', [0, 155, 0]))
    selected_difficulty = settings.get('difficulty', 'Normal')

    # grid visibility toggle (persisted)
    show_grid = settings.get('show_grid', True)
    # layout rects: grid toggle, custom button, save/cancel
    grid_toggle_rect = pygame.Rect(WINDOW_WIDTH // 2 - 110, 200, 220, 30)
    custom_btn = pygame.Rect(WINDOW_WIDTH // 2 - 110, 240, 220, 40)
    save_btn = pygame.Rect(WINDOW_WIDTH // 2 - 120, 320, 100, 40)
    cancel_btn = pygame.Rect(WINDOW_WIDTH // 2 + 20, 320, 100, 40)

    # difficulty rects (reuse layout)
    difficulties = ['Easy', 'Normal', 'Hard']
    diff_w = 120
    diff_h = 40
    diff_rects = []
    diff_start_x = WINDOW_WIDTH // 2 - ((diff_w + 10) * len(difficulties) // 2)
    for i, d in enumerate(difficulties):
        r = pygame.Rect(diff_start_x + i * (diff_w + 10), 160, diff_w, diff_h)
        diff_rects.append((r, d))

    done = False
    while not done:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return settings
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                # difficulty select
                for r, d in diff_rects:
                    if r.collidepoint(mouse_pos):
                        selected_difficulty = d
                # toggle grid visibility
                if grid_toggle_rect.collidepoint(mouse_pos):
                    show_grid = not show_grid
                # custom color editor
                if custom_btn.collidepoint(mouse_pos):
                    newcol = modal_color_picker(screen, clock, font, custom)
                    if newcol is not None:
                        custom = newcol
                # save / cancel
                if save_btn.collidepoint(mouse_pos):
                    settings['color'] = list(custom)
                    settings['head_color'] = [max(0, custom[0] - 40), max(0, custom[1] - 40), max(0, custom[2] - 40)]
                    settings['difficulty'] = selected_difficulty
                    settings['show_grid'] = bool(show_grid)
                    save_settings(settings)
                    return settings
                if cancel_btn.collidepoint(mouse_pos):
                    return settings

        screen.fill(WHITE)
        title_font = pygame.font.SysFont(None, 60)
        title = title_font.render('Settings', True, BLACK)
        title_rect = title.get_rect()
        title_rect.center = (WINDOW_WIDTH // 2, 80)
        screen.blit(title, title_rect)

        # Draw difficulty
        diff_label = font.render('Default Difficulty:', True, BLACK)
        diff_label_rect = diff_label.get_rect()
        diff_label_rect.center = (WINDOW_WIDTH // 2, 140)
        screen.blit(diff_label, diff_label_rect)
        for r, d in diff_rects:
            is_sel = (d == selected_difficulty)
            pygame.draw.rect(screen, (100, 100, 100) if is_sel else (180, 180, 180), r)
            pygame.draw.rect(screen, BLACK, r, 2)
            lbl = font.render(d, True, BLACK)
            lbl_rect = lbl.get_rect()
            lbl_rect.center = r.center
            screen.blit(lbl, lbl_rect)
        # Grid visibility toggle
        pygame.draw.rect(screen, (240, 240, 240), grid_toggle_rect)
        pygame.draw.rect(screen, BLACK, grid_toggle_rect, 1)
        # checkbox indicator inside toggle
        chk_rect = pygame.Rect(grid_toggle_rect.x + 8, grid_toggle_rect.y + 6, 18, 18)
        if show_grid:
            pygame.draw.rect(screen, (100, 200, 100), chk_rect)
        else:
            pygame.draw.rect(screen, WHITE, chk_rect)
        pygame.draw.rect(screen, BLACK, chk_rect, 1)
        g_lbl = font.render('Show grid', True, BLACK)
        g_lbl_rect = g_lbl.get_rect()
        g_lbl_rect.midleft = (chk_rect.right + 10, grid_toggle_rect.centery)
        screen.blit(g_lbl, g_lbl_rect)

        # Custom color button
        pygame.draw.rect(screen, custom, custom_btn)
        pygame.draw.rect(screen, BLACK, custom_btn, 2)
        cr_lbl = font.render('Edit Custom Color', True, WHITE)
        cr_lbl_rect = cr_lbl.get_rect()
        cr_lbl_rect.center = custom_btn.center
        screen.blit(cr_lbl, cr_lbl_rect)

        # Save/Cancel
        pygame.draw.rect(screen, (100, 200, 100), save_btn)
        pygame.draw.rect(screen, BLACK, save_btn, 2)
        pygame.draw.rect(screen, (200, 100, 100), cancel_btn)
        pygame.draw.rect(screen, BLACK, cancel_btn, 2)
        screen.blit(font.render('Save', True, BLACK), (save_btn.x + 20, save_btn.y + 8))
        screen.blit(font.render('Back', True, BLACK), (cancel_btn.x + 25, cancel_btn.y + 8))

        pygame.display.update()
        clock.tick(30)


def draw_grid(surface):
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, BLACK, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, BLACK, (0, y), (WINDOW_WIDTH, y))


class Snake:
    def __init__(self, color=GREEN, head_color=DARK_GREEN):
        self.startx = CELL_WIDTH // 2
        self.starty = CELL_HEIGHT // 2
        self.segments = [(self.startx, self.starty), (self.startx - 1, self.starty), (self.startx - 2, self.starty)]
        self.direction = RIGHT
        self.color = color
        self.head_color = head_color

    def get_head_position(self):
        return self.segments[0]

    def turn(self, dir):
        # Prevent reversing
        opposite = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
        if dir == opposite.get(self.direction):
            return
        self.direction = dir

    def move(self, grow=False):
        head_x, head_y = self.get_head_position()
        if self.direction == UP:
            new_head = (head_x, head_y - 1)
        elif self.direction == DOWN:
            new_head = (head_x, head_y + 1)
        elif self.direction == LEFT:
            new_head = (head_x - 1, head_y)
        elif self.direction == RIGHT:
            new_head = (head_x + 1, head_y)
        else:
            new_head = (head_x, head_y)

        self.segments.insert(0, new_head)
        if not grow:
            self.segments.pop()

    def collides_with_self(self):
        return self.get_head_position() in self.segments[1:]


class Food:
    def __init__(self, snake):
        """
        Initializes the Food object and immediately randomizes its position
        so that it does not overlap with the provided snake.
        """
        self.position = (0, 0)
        self.randomize_position(snake)

    def randomize_position(self, snake):
        while True:
            pos = (random.randint(0, CELL_WIDTH - 1), random.randint(0, CELL_HEIGHT - 1))
            if pos not in snake.segments:
                self.position = pos
                return


def draw_snake(surface, snake):
    for i, segment in enumerate(snake.segments):
        x, y = segment
        r = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        color = snake.head_color if i == 0 else snake.color
        pygame.draw.rect(surface, color, r)
        pygame.draw.rect(surface, BLACK, r, 1)


def menu_select_color(screen, clock, font):
    # Define available colors
    options = [
        ("Green", (0, 255, 0), (0, 155, 0)),
        ("Blue", (0, 120, 255), (0, 80, 180)),
        ("Purple", (160, 64, 255), (120, 40, 200)),
        ("Orange", (255, 140, 0), (200, 100, 0)),
    ]

    buttons = []
    button_w, button_h = 220, 50
    start_y = 160
    gap = 20
    for i, (label, col, head_col) in enumerate(options):
        rect = pygame.Rect(0, 0, button_w, button_h)
        rect.center = (WINDOW_WIDTH // 2, start_y + i * (button_h + gap))
        buttons.append((rect, label, col, head_col))

    title_font = pygame.font.SysFont(None, 60)
    title = title_font.render('Snake', True, BLACK)
    title_rect = title.get_rect()
    title_rect.center = (WINDOW_WIDTH // 2, 80)

    # Setup preview snake (small animation at bottom)
    preview_y = CELL_HEIGHT - 3
    preview_startx = CELL_WIDTH // 2 - 3
    preview_segments = [(preview_startx + i, preview_y) for i in range(3)][::-1]
    preview_dir = RIGHT
    preview_tick = 0
    preview_move_delay = 8  # frames between moves

    key_to_index = {K_1: 0, K_2: 1, K_3: 2, K_4: 3}

    selected_index = 0
    # Load persisted settings
    settings = load_settings()
    # initial custom RGB values
    custom_r, custom_g, custom_b = settings.get('color', [0, 255, 0])
    selected_difficulty = settings.get('difficulty', 'Normal')

    # Difficulty options
    difficulties = ['Easy', 'Normal', 'Hard']
    diff_rects = []
    diff_w = 120
    diff_h = 40
    diff_start_x = WINDOW_WIDTH // 2 - ((diff_w + 10) * len(difficulties) // 2)
    for i, d in enumerate(difficulties):
        r = pygame.Rect(diff_start_x + i * (diff_w + 10), 130, diff_w, diff_h)
        diff_rects.append((r, d))

    # Custom color button: place under the last option (Orange) to avoid overlap
    # Compute position based on last option rect
    last_rect = buttons[-1][0]
    custom_rect = pygame.Rect(last_rect.x, last_rect.bottom + 16, last_rect.w, 40)
    while True:
        mouse_pos = pygame.mouse.get_pos()
        is_click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                # Keyboard shortcuts 1-4 to pick colors
                elif event.key in key_to_index:
                    idx = key_to_index[event.key]
                    _, col, head_col = options[idx]
                    return col, head_col
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                is_click = True

    # Update preview snake movement
        preview_tick += 1
        if preview_tick >= preview_move_delay:
            preview_tick = 0
            head_x, head_y = preview_segments[0]
            if preview_dir == RIGHT:
                new_head = (head_x + 1, head_y)
            else:
                new_head = (head_x - 1, head_y)
            # Reverse direction at edges of a small preview area
            if new_head[0] >= CELL_WIDTH - 2:
                preview_dir = LEFT
                new_head = (head_x - 1, head_y)
            elif new_head[0] <= 2:
                preview_dir = RIGHT
                new_head = (head_x + 1, head_y)
            preview_segments.insert(0, new_head)
            preview_segments.pop()

        screen.fill(WHITE)
        screen.blit(title, title_rect)

        # Draw difficulty selectors
        diff_label = font.render('Difficulty:', True, BLACK)
        diff_label_rect = diff_label.get_rect()
        diff_label_rect.center = (WINDOW_WIDTH // 2 - 180, 150)
        screen.blit(diff_label, diff_label_rect)
        for r, d in diff_rects:
            is_sel = (d == selected_difficulty)
            pygame.draw.rect(screen, (100, 100, 100) if is_sel else (180, 180, 180), r)
            pygame.draw.rect(screen, BLACK, r, 2)
            lbl = font.render(d, True, BLACK)
            lbl_rect = lbl.get_rect()
            lbl_rect.center = r.center
            screen.blit(lbl, lbl_rect)


        # Draw buttons and detect hover/click
        for i, (rect, label, col, head_col) in enumerate(buttons):
            hover = rect.collidepoint(mouse_pos)
            # highlight hovered option slightly by using head_col
            pygame.draw.rect(screen, head_col if hover else col, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            lbl = font.render(f'{i+1}. {label}', True, WHITE)
            lbl_rect = lbl.get_rect()
            lbl_rect.center = rect.center
            screen.blit(lbl, lbl_rect)

            if is_click and hover:
                # persist and return
                settings['color'] = list(col)
                settings['head_color'] = list(head_col)
                settings['difficulty'] = selected_difficulty
                save_settings(settings)
                return col, head_col, selected_difficulty


    # Draw preview label
        preview_label = font.render('Preview', True, BLACK)
        preview_label_rect = preview_label.get_rect()
        preview_label_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 80)
        screen.blit(preview_label, preview_label_rect)

        # Draw preview snake using current hovered or default color
        # If hovering an option, use that color; otherwise use selected_index
        hover_index = None
        for i, (rect, _, _, _) in enumerate(buttons):
            if rect.collidepoint(mouse_pos):
                hover_index = i
                break

        if hover_index is not None:
            px_col, px_head = buttons[hover_index][2], buttons[hover_index][3]
        else:
            px_col, px_head = buttons[selected_index][2], buttons[selected_index][3]

        # Draw custom color button (swatch) positioned below the options
        current_custom = (custom_r, custom_g, custom_b)
        pygame.draw.rect(screen, current_custom, custom_rect)
        pygame.draw.rect(screen, BLACK, custom_rect, 2)

        # label text on the left, choose readable color based on luminance
        luminance = (0.2126 * current_custom[0] + 0.7152 * current_custom[1] + 0.0722 * current_custom[2])
        lbl_color = BLACK if luminance > 160 else WHITE
        cr_lbl = font.render('custom colour', True, lbl_color)
        cr_lbl_rect = cr_lbl.get_rect()
        cr_lbl_rect.midleft = (custom_rect.x + 12, custom_rect.centery)
        screen.blit(cr_lbl, cr_lbl_rect)

        # small swatch on the right inside the button
        sw_w = 44
        sw_h = custom_rect.height - 12
        sw_rect = pygame.Rect(custom_rect.right - sw_w - 8, custom_rect.y + 6, sw_w, sw_h)
        pygame.draw.rect(screen, current_custom, sw_rect)
        pygame.draw.rect(screen, BLACK, sw_rect, 1)

        # Handle click for custom color button: open modal color wheel
        if is_click and custom_rect.collidepoint(mouse_pos):
            newcol = modal_color_wheel(screen, clock, font, current_custom)
            if newcol:
                custom_r, custom_g, custom_b = newcol
                settings['color'] = [custom_r, custom_g, custom_b]
                # derive head color as darker variant
                settings['head_color'] = [max(0, custom_r - 40), max(0, custom_g - 40), max(0, custom_b - 40)]
                settings['difficulty'] = selected_difficulty
                save_settings(settings)
                # return the new selection immediately
                return tuple(settings['color']), tuple(settings['head_color']), selected_difficulty
        pygame.draw.rect(screen, BLACK, sw_rect, 1)
        # clicking opens wheel modal to pick custom color
        if is_click and custom_rect.collidepoint(mouse_pos):
            newcol = modal_color_wheel(screen, clock, font, current_custom)
            if newcol is not None:
                custom_r, custom_g, custom_b = newcol

        # Draw preview snake segments on screen
        for j, (sx, sy) in enumerate(preview_segments):
            r = pygame.Rect(sx * CELL_SIZE, sy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = px_head if j == 0 else px_col
            pygame.draw.rect(screen, color, r)
            pygame.draw.rect(screen, BLACK, r, 1)

        pygame.display.update()
        clock.tick(60)


def color_selection_screen(screen, clock, font):
    # Color presets
    options = [
        ("Green", (0, 255, 0), (0, 155, 0)),
        ("Blue", (0, 120, 255), (0, 80, 180)),
        ("Purple", (160, 64, 255), (120, 40, 200)),
        ("Orange", (255, 140, 0), (200, 100, 0)),
    ]

    buttons = []
    button_w, button_h = 220, 50
    start_y = 160
    gap = 20
    for i, (label, col, head_col) in enumerate(options):
        rect = pygame.Rect(0, 0, button_w, button_h)
        rect.center = (WINDOW_WIDTH // 2, start_y + i * (button_h + gap))
        buttons.append((rect, label, col, head_col))

    title_font = pygame.font.SysFont(None, 60)
    title = title_font.render('Pick Snake Color', True, BLACK)
    title_rect = title.get_rect()
    title_rect.center = (WINDOW_WIDTH // 2, 80)

    # Position custom button below the last color option to avoid overlap
    last_rect = buttons[-1][0]
    custom_btn = pygame.Rect(last_rect.x, last_rect.bottom + 16, last_rect.w, 40)
    # Ensure save/back sit below the custom button
    save_btn = pygame.Rect(WINDOW_WIDTH // 2 - 120, custom_btn.bottom + 20, 100, 40)
    back_btn = pygame.Rect(WINDOW_WIDTH // 2 + 20, custom_btn.bottom + 20, 100, 40)

    # preview setup (side preview)
    preview_tick = 0
    preview_move_delay = 8
    preview_offset = 0
    preview_dir = 1  # 1 moves right, -1 moves left

    key_to_index = {K_1: 0, K_2: 1, K_3: 2, K_4: 3}

    settings = load_settings()
    selected_color = tuple(settings.get('color', [0, 255, 0]))
    selected_head = tuple(settings.get('head_color', [0, 155, 0]))
    selected_index = 0
    # custom swatch will show current selected_color; use modal wheel for editing

    while True:
        mouse_pos = pygame.mouse.get_pos()
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return None
                elif event.key in key_to_index:
                    idx = key_to_index[event.key]
                    lbl, col, head = options[idx]
                    selected_color, selected_head = col, head
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                click = True

        # preview motion (small oscillation)
        preview_tick += 1
        if preview_tick >= preview_move_delay:
            preview_tick = 0
            preview_offset += preview_dir
            if preview_offset > 2:
                preview_dir = -1
                preview_offset = 2
            elif preview_offset < -2:
                preview_dir = 1
                preview_offset = -2

        screen.fill(WHITE)
        screen.blit(title, title_rect)

        for i, (rect, label, col, head_col) in enumerate(buttons):
            hover = rect.collidepoint(mouse_pos)
            pygame.draw.rect(screen, head_col if hover else col, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            lbl = font.render(f'{i+1}. {label}', True, WHITE)
            lbl_rect = lbl.get_rect()
            lbl_rect.center = rect.center
            screen.blit(lbl, lbl_rect)
            if click and hover:
                selected_color, selected_head = col, head_col

        # custom button (left side) showing swatch and H/S/V text
        current_custom = tuple(selected_color)
        pygame.draw.rect(screen, current_custom, custom_btn)
        pygame.draw.rect(screen, BLACK, custom_btn, 2)
        # label text
        luminance = (0.2126 * current_custom[0] + 0.7152 * current_custom[1] + 0.0722 * current_custom[2])
        lbl_color = BLACK if luminance > 160 else WHITE
        c_lbl = font.render('custom colour', True, lbl_color)
        c_lbl_rect = c_lbl.get_rect()
        c_lbl_rect.midleft = (custom_btn.x + 12, custom_btn.centery)
        screen.blit(c_lbl, c_lbl_rect)
        # small swatch on the right
        sw_w = 44
        sw_h = custom_btn.height - 12
        sw_rect = pygame.Rect(custom_btn.right - sw_w - 8, custom_btn.y + 6, sw_w, sw_h)
        pygame.draw.rect(screen, current_custom, sw_rect)
        pygame.draw.rect(screen, BLACK, sw_rect, 1)
        # clicking behavior: clicking the custom button opens the wheel modal
        if click and custom_btn.collidepoint(mouse_pos):
            newcol = modal_color_wheel(screen, clock, font, selected_color)
            if newcol is not None:
                selected_color = newcol
                selected_head = (max(0, newcol[0] - 40), max(0, newcol[1] - 40), max(0, newcol[2] - 40))

        # Save / Back
        pygame.draw.rect(screen, (100, 200, 100), save_btn)
        pygame.draw.rect(screen, BLACK, save_btn, 2)
        pygame.draw.rect(screen, (200, 100, 100), back_btn)
        pygame.draw.rect(screen, BLACK, back_btn, 2)
        screen.blit(font.render('Save', True, BLACK), (save_btn.x + 20, save_btn.y + 8))
        screen.blit(font.render('Back', True, BLACK), (back_btn.x + 25, back_btn.y + 8))
        if click and save_btn.collidepoint(mouse_pos):
            settings['color'] = list(selected_color)
            settings['head_color'] = list(selected_head)
            save_settings(settings)
            return selected_color, selected_head
        if click and back_btn.collidepoint(mouse_pos):
            return None

        # preview (right-side)
        preview_box = pygame.Rect(WINDOW_WIDTH - 160, 140, 120, 160)
        pygame.draw.rect(screen, (240, 240, 240), preview_box)
        pygame.draw.rect(screen, BLACK, preview_box, 2)
        preview_label = font.render('Preview', True, BLACK)
        preview_label_rect = preview_label.get_rect()
        preview_label_rect.center = (preview_box.centerx, preview_box.y + 16)
        screen.blit(preview_label, preview_label_rect)

        # draw a small 3-segment snake inside preview box, oscillating horizontally
        unit = 20
        cx = preview_box.centerx
        cy = preview_box.centery
        # positions relative to center, head on the left
        rel_positions = [(-1 + preview_offset, 0), (0 + preview_offset, 0), (1 + preview_offset, 0)]
        for j, (rx, ry) in enumerate(rel_positions):
            px = cx + rx * unit
            py = cy + ry * unit
            rr = pygame.Rect(px - unit // 2, py - unit // 2, unit, unit)
            color = selected_head if j == 0 else selected_color
            pygame.draw.rect(screen, color, rr)
            pygame.draw.rect(screen, BLACK, rr, 1)

        pygame.display.update()
        clock.tick(60)


def difficulty_selection_screen(screen, clock, font):
    difficulties = ['Easy', 'Normal', 'Hard']
    diff_w = 240
    diff_h = 50
    diff_rects = []
    start_x = WINDOW_WIDTH // 2 - diff_w // 2
    start_y = 160
    for i, d in enumerate(difficulties):
        r = pygame.Rect(start_x, start_y + i * (diff_h + 16), diff_w, diff_h)
        diff_rects.append((r, d))

    title_font = pygame.font.SysFont(None, 60)
    title = title_font.render('Select Difficulty', True, BLACK)
    title_rect = title.get_rect()
    title_rect.center = (WINDOW_WIDTH // 2, 80)

    settings = load_settings()
    selected = settings.get('difficulty', 'Normal')

    save_btn = pygame.Rect(WINDOW_WIDTH // 2 - 120, 420, 100, 40)
    back_btn = pygame.Rect(WINDOW_WIDTH // 2 + 20, 420, 100, 40)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return None
                elif event.key == K_1:
                    selected = 'Easy'
                elif event.key == K_2:
                    selected = 'Normal'
                elif event.key == K_3:
                    selected = 'Hard'
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                click = True

        screen.fill(WHITE)
        screen.blit(title, title_rect)

        for r, d in diff_rects:
            is_sel = (d == selected)
            pygame.draw.rect(screen, (100, 100, 100) if is_sel else (200, 200, 200), r)
            pygame.draw.rect(screen, BLACK, r, 2)
            lbl = font.render(d, True, BLACK)
            lbl_rect = lbl.get_rect()
            lbl_rect.center = r.center
            screen.blit(lbl, lbl_rect)
            if click and r.collidepoint(mouse_pos):
                selected = d

        pygame.draw.rect(screen, (100, 200, 100), save_btn)
        pygame.draw.rect(screen, BLACK, save_btn, 2)
        pygame.draw.rect(screen, (200, 100, 100), back_btn)
        pygame.draw.rect(screen, BLACK, back_btn, 2)
        screen.blit(font.render('Save', True, BLACK), (save_btn.x + 20, save_btn.y + 8))
        screen.blit(font.render('Back', True, BLACK), (back_btn.x + 25, back_btn.y + 8))

        if click and save_btn.collidepoint(mouse_pos):
            settings['difficulty'] = selected
            save_settings(settings)
            return selected
        if click and back_btn.collidepoint(mouse_pos):
            return None

        pygame.display.update()
        clock.tick(60)


def main_menu(screen, clock, font):
    # Buttons: Start, Change Color, Change Difficulty, Quit
    btn_w, btn_h = 300, 60
    start_btn = pygame.Rect(0, 0, btn_w, btn_h)
    start_btn.center = (WINDOW_WIDTH // 2, 180)
    color_btn = pygame.Rect(0, 0, btn_w, btn_h)
    color_btn.center = (WINDOW_WIDTH // 2, 260)
    diff_btn = pygame.Rect(0, 0, btn_w, btn_h)
    diff_btn.center = (WINDOW_WIDTH // 2, 340)
    quit_btn = pygame.Rect(0, 0, btn_w, btn_h)
    quit_btn.center = (WINDOW_WIDTH // 2, 420)

    title_font = pygame.font.SysFont(None, 72)
    title = title_font.render('Snake', True, BLACK)
    title_rect = title.get_rect()
    title_rect.center = (WINDOW_WIDTH // 2, 100)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                click = True

        screen.fill(WHITE)
        screen.blit(title, title_rect)

        for rect, text in ((start_btn, 'Start Game'), (color_btn, 'Change Color'), (diff_btn, 'Change Difficulty'), (quit_btn, 'Quit')):
            pygame.draw.rect(screen, (100, 150, 200), rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            lbl = font.render(text, True, BLACK)
            lbl_rect = lbl.get_rect()
            lbl_rect.center = rect.center
            screen.blit(lbl, lbl_rect)

        if click and start_btn.collidepoint(mouse_pos):
            # load settings and return to start
            return load_settings()
        if click and color_btn.collidepoint(mouse_pos):
            res = color_selection_screen(screen, clock, font)
            if res:
                col, head = res
                s = load_settings()
                s['color'] = list(col)
                s['head_color'] = list(head)
                save_settings(s)
        if click and diff_btn.collidepoint(mouse_pos):
            res = difficulty_selection_screen(screen, clock, font)
            if res:
                s = load_settings()
                s['difficulty'] = res
                save_settings(s)
        if click and quit_btn.collidepoint(mouse_pos):
            pygame.quit()
            sys.exit()

        pygame.display.update()
        clock.tick(60)


def draw_food(surface, food):
    x, y = food.position
    r = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, RED, r)


def run_game():
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Snake')

    font = pygame.font.SysFont(None, 36)
    game_over_font = pygame.font.SysFont(None, 72)

    # optional music: place an MP3 at assets/music/stay_with_me.mp3 to enable
    music_path = os.path.join(os.path.dirname(__file__), 'assets', 'music', 'stay_with_me.mp3')
    music_playing = False
    music_available = False
    music_volume = 0.8
    try:
        if os.path.exists(music_path):
            pygame.mixer.init()
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(music_volume)
            pygame.mixer.music.play(-1)
            music_playing = True
            music_available = True
    except Exception:
        music_playing = False
        music_available = False

    while True:  # Outer loop allows restarting the game
        # Show main menu which can navigate to color/difficulty screens
        settings = main_menu(screen, clock, font)
        snake_color = tuple(settings.get('color', [0, 255, 0]))
        snake_head_color = tuple(settings.get('head_color', [0, 155, 0]))
        selected_difficulty = settings.get('difficulty', 'Normal')

        # Map difficulty to starting speed
        difficulty_map = {'Easy': 6, 'Normal': 10, 'Hard': 14}
        start_speed = difficulty_map.get(selected_difficulty, 10)

        snake = Snake(color=snake_color, head_color=snake_head_color)
        food = Food(snake)
        score = 0
        speed = start_speed
        god_mode = False  # secret cheat: toggle immortality with key 9
        # visual effects for wraps (list of {'pos':(x,y),'ttl':int})
        wrap_effects = []
        # (music already initialized once at startup)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_9:
                        god_mode = not god_mode
                    elif event.key == K_m:
                        # toggle music if available
                        try:
                            if music_available and pygame.mixer.get_init():
                                if music_playing and pygame.mixer.music.get_busy():
                                    pygame.mixer.music.pause()
                                    music_playing = False
                                else:
                                    # resume or start
                                    pygame.mixer.music.unpause()
                                    music_playing = True
                        except Exception:
                            pass
                    elif event.key in (K_KP_PLUS, K_EQUALS):
                        # increase volume
                        try:
                            music_volume = min(1.0, music_volume + 0.05)
                            if music_available and pygame.mixer.get_init():
                                pygame.mixer.music.set_volume(music_volume)
                        except Exception:
                            pass
                    elif event.key in (K_KP_MINUS, K_MINUS):
                        # decrease volume
                        try:
                            music_volume = max(0.0, music_volume - 0.05)
                            if music_available and pygame.mixer.get_init():
                                pygame.mixer.music.set_volume(music_volume)
                        except Exception:
                            pass
                    elif event.key in (K_UP, K_w):
                        snake.turn(UP)
                    elif event.key in (K_DOWN, K_s):
                        snake.turn(DOWN)
                    elif event.key in (K_LEFT, K_a):
                        snake.turn(LEFT)
                    elif event.key in (K_RIGHT, K_d):
                        snake.turn(RIGHT)
                    elif event.key == K_ESCAPE:
                        # Pause the game until ESC is pressed again
                        paused = True
                        pause_font = pygame.font.SysFont(None, 72)
                        resume_btn = pygame.Rect(WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT // 2 + 60, 120, 40)
                        while paused:
                            mouse_pos_p = pygame.mouse.get_pos()
                            click_p = False
                            for pe in pygame.event.get():
                                if pe.type == QUIT:
                                    pygame.quit()
                                    sys.exit()
                                elif pe.type == KEYDOWN:
                                    if pe.key == K_ESCAPE:
                                        paused = False
                                    elif pe.key == K_s:
                                        # open settings while paused; reload settings afterwards
                                        settings_screen(screen, clock, font)
                                        settings = load_settings()
                                        # apply any setting changes (color/difficulty persistent later)
                                elif pe.type == MOUSEBUTTONDOWN and pe.button == 1:
                                    click_p = True
                            # draw overlay
                            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                            overlay.fill((0, 0, 0, 160))
                            screen.blit(overlay, (0, 0))
                            p_surf = pause_font.render('Paused', True, WHITE)
                            p_rect = p_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
                            screen.blit(p_surf, p_rect)
                            info = font.render('Press ESC to resume. Press S for Settings.', True, WHITE)
                            i_rect = info.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
                            screen.blit(info, i_rect)
                            # resume button
                            pygame.draw.rect(screen, (100, 200, 100), resume_btn)
                            pygame.draw.rect(screen, BLACK, resume_btn, 2)
                            rtxt = font.render('Resume', True, BLACK)
                            rtr = rtxt.get_rect(center=resume_btn.center)
                            screen.blit(rtxt, rtr)
                            if click_p and resume_btn.collidepoint(mouse_pos_p):
                                paused = False
                            pygame.display.update()
                            clock.tick(20)

            # Move snake
            snake.move()

            head_x, head_y = snake.get_head_position()

            # If god_mode is enabled, wrap around the screen edges
            if god_mode:
                wrapped_x = head_x % CELL_WIDTH
                wrapped_y = head_y % CELL_HEIGHT
                if (wrapped_x, wrapped_y) != (head_x, head_y):
                    # teleport head to opposite side
                    snake.segments[0] = (wrapped_x, wrapped_y)
                    head_x, head_y = wrapped_x, wrapped_y
                    # add a brief visual effect at the teleport target
                    wrap_effects.append({'pos': (wrapped_x, wrapped_y), 'ttl': 12})
                    # if food landed on the wrapped head, re-randomize it
                    if food.position == (wrapped_x, wrapped_y):
                        food.randomize_position(snake)

            # Check collisions with walls
            if not god_mode and (head_x < 0 or head_x >= CELL_WIDTH or head_y < 0 or head_y >= CELL_HEIGHT):
                running = False

            # Check collisions with self
            if not god_mode and snake.collides_with_self():
                running = False

            # Check food
            if snake.get_head_position() == food.position:
                score += 1
                snake.move(grow=True)
                food.randomize_position(snake)
                # increase speed slightly
                speed = min(25, speed + 0.5)

            # Draw
            screen.fill(WHITE)
            # Respect user setting for grid visibility
            try:
                if settings.get('show_grid', True):
                    draw_grid(screen)
            except Exception:
                # fallback: draw grid if settings missing or error
                draw_grid(screen)
            draw_snake(screen, snake)
            draw_food(screen, food)

            # draw wrap effects (simple expanding circles)
            if wrap_effects:
                remaining = []
                for eff in wrap_effects:
                    ex, ey = eff['pos']
                    ttl = eff['ttl']
                    px = ex * CELL_SIZE + CELL_SIZE // 2
                    py = ey * CELL_SIZE + CELL_SIZE // 2
                    # radius grows as ttl decreases
                    max_ttl = 12
                    radius = CELL_SIZE // 2 + int((max_ttl - ttl) * 2)
                    alpha_col = (255, 210, 0)
                    pygame.draw.circle(screen, alpha_col, (px, py), radius)
                    eff['ttl'] = ttl - 1
                    if eff['ttl'] > 0:
                        remaining.append(eff)
                wrap_effects = remaining

            # Draw score
            score_surf = font.render(f'Score: {score}', True, BLACK)
            screen.blit(score_surf, (10, 10))
            # Draw god mode indicator
            if god_mode:
                gm_surf = font.render('GOD MODE', True, (200, 50, 50))
                screen.blit(gm_surf, (WINDOW_WIDTH - 140, 10))
            # Draw music HUD indicator (music note) if audio is playing
            try:
                music_active = pygame.mixer.get_init() and pygame.mixer.music.get_busy()
            except Exception:
                music_active = False
            note_color = (50, 120, 200) if music_active else (170, 170, 170)
            note_surf = font.render('♪', True, note_color)
            note_rect = note_surf.get_rect()
            note_rect.topright = (WINDOW_WIDTH - 20, 10)
            screen.blit(note_surf, note_rect)
            # volume percentage
            try:
                if music_available:
                    vol_pct = int(music_volume * 100)
                    vol_s = font.render(f'{vol_pct}%', True, BLACK)
                    vol_r = vol_s.get_rect()
                    vol_r.topright = (note_rect.left - 8, 10)
                    screen.blit(vol_s, vol_r)
            except Exception:
                pass

            pygame.display.update()
            clock.tick(speed)

        # Game over screen with Restart button
        go_surf = game_over_font.render('Game Over', True, RED)
        go_rect = go_surf.get_rect()
        go_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60)

        score_surf = font.render(f'Final Score: {score}', True, BLACK)
        score_rect = score_surf.get_rect()
        score_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 10)

        # update high scores
        high_scores = load_high_scores()
        # selected_difficulty may be in scope from menu; otherwise default
        try:
            current_diff = selected_difficulty
        except Exception:
            current_diff = 'Normal'
        if score > high_scores.get(current_diff, 0):
            high_scores[current_diff] = score
            save_high_scores(high_scores)

        # Buttons: Restart, Settings
        button_w, button_h = 160, 44
        restart_rect = pygame.Rect(0, 0, button_w, button_h)
        restart_rect.center = (WINDOW_WIDTH // 2 - 110, WINDOW_HEIGHT // 2 + 60)
        settings_rect = pygame.Rect(0, 0, button_w, button_h)
        settings_rect.center = (WINDOW_WIDTH // 2 + 110, WINDOW_HEIGHT // 2 + 60)
        button_color = DARK_GREEN
        button_hover = (0, 200, 0)

        while True:
            mouse_pos = pygame.mouse.get_pos()
            restart_hover = restart_rect.collidepoint(mouse_pos)
            settings_hover = settings_rect.collidepoint(mouse_pos)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if restart_hover:
                        # Restart the outer loop, which resets the game
                        break
                    if settings_hover:
                        # open settings screen
                        settings_screen(screen, clock, font)
                        # reload settings in case difficulty changed
                        settings = load_settings()
                        # update selected_difficulty for next run
                        selected_difficulty = settings.get('difficulty', 'Normal')
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            # draw game over screen
            screen.fill(WHITE)
            screen.blit(go_surf, go_rect)
            screen.blit(score_surf, score_rect)

            # draw restart button
            pygame.draw.rect(screen, button_hover if restart_hover else button_color, restart_rect)
            pygame.draw.rect(screen, BLACK, restart_rect, 2)
            btn_label = font.render('Restart', True, WHITE)
            btn_label_rect = btn_label.get_rect()
            btn_label_rect.center = restart_rect.center
            screen.blit(btn_label, btn_label_rect)

            # draw settings button
            pygame.draw.rect(screen, (120, 120, 200) if settings_hover else (80, 80, 160), settings_rect)
            pygame.draw.rect(screen, BLACK, settings_rect, 2)
            s_label = font.render('Settings', True, WHITE)
            s_rect = s_label.get_rect()
            s_rect.center = settings_rect.center
            screen.blit(s_label, s_rect)

            # draw high score for current difficulty
            hs = load_high_scores()
            hs_text = font.render(f'Best ({current_diff}): {hs.get(current_diff,0)}', True, BLACK)
            hs_rect = hs_text.get_rect()
            hs_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)
            screen.blit(hs_text, hs_rect)

            pygame.display.update()

            # If the user clicked the restart button, break to restart
            if pygame.mouse.get_pressed()[0] and restart_hover:
                break

            clock.tick(30)


if __name__ == '__main__':
    run_game()
