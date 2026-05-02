import pygame
import random
import math
from configuration import screen

FPS = 60
PANEL_W = 260

WIN_W, WIN_H = 0, 0
CANVAS_W, CANVAS_H = 0, 0
CANVAS_X, CANVAS_Y = 0, 0


_canvas_initialisé = False


def _init_canvas():
    global WIN_W, WIN_H, CANVAS_W, CANVAS_H, CANVAS_X, CANVAS_Y, carte_maison, _canvas_initialisé
    if _canvas_initialisé:
        return
    WIN_W, WIN_H = screen.get_size()
    CANVAS_W = WIN_W - PANEL_W - 40
    CANVAS_H = WIN_H - 40
    CANVAS_X = (WIN_W - PANEL_W - CANVAS_W) // 2
    CANVAS_Y = (WIN_H - CANVAS_H) // 2
    carte_maison = pygame.Surface((CANVAS_W, CANVAS_H))
    _canvas_initialisé = True


WALL_THICK = 6
DOOR_W = 24
DOOR_THICK = WALL_THICK + 2
MIN_ROOM = 80

FLOOR_NAMES = {-1: "Sous-sol", 0: "Rez-de-chaussée", 1: "1er étage", 2: "2e étage"}

PAL = {
    "bg": (245, 238, 225),
    "wall": (90, 78, 65),
    "wall_outer": (70, 60, 50),
    "door": (160, 120, 60),
    "door_arc": (130, 95, 45),
    "text": (55, 45, 35),
    "text_light": (240, 230, 210),
    "floor_ind": (180, 130, 40),
    "btn_bg": (80, 70, 58),
    "btn_hover": (110, 96, 78),
    "btn_border": (140, 122, 95),
    "stair": (210, 185, 110),
    "stair_line": (170, 148, 80),
    "arrow": (230, 180, 40),
    "panel_bg": (55, 48, 40),
    "grid": (230, 222, 208),
}

ROOM_DEFS = {
    "Salon": {"color": (205, 185, 155), "weight": 9, "unique": True, "floors": [0]},
    "Chambre": {
        "color": (185, 165, 205),
        "weight": 6,
        "unique": False,
        "floors": [0, 1, 2],
    },
    "Hall d'entrée": {
        "color": (215, 205, 185),
        "weight": 4,
        "unique": True,
        "floors": [0],
    },
    "Cuisine": {"color": (190, 215, 175), "weight": 4, "unique": True, "floors": [0]},
    "Salle de bain": {
        "color": (165, 198, 218),
        "weight": 2,
        "unique": False,
        "floors": [0, 1, 2, -1],
    },
    "Escaliers": {
        "color": (220, 200, 140),
        "weight": 2,
        "unique": False,
        "floors": [0, 1, 2, -1],
    },
    "Cave": {"color": (155, 148, 138), "weight": 7, "unique": True, "floors": [-1]},
    "Buanderie": {
        "color": (178, 198, 178),
        "weight": 3,
        "unique": True,
        "floors": [-1],
    },
}


class BSPNode:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.left = None
        self.right = None
        self.room = None

    def is_leaf(self):
        return self.left is None and self.right is None

    def get_leaves(self):
        if self.is_leaf():
            return [self]
        leaves = []
        if self.left:
            leaves += self.left.get_leaves()
        if self.right:
            leaves += self.right.get_leaves()
        return leaves


def bsp_split(node, rng, depth=0, max_depth=4):
    if depth >= max_depth:
        node.room = (node.x, node.y, node.w, node.h)
        return

    can_h = node.w >= MIN_ROOM * 2
    can_v = node.h >= MIN_ROOM * 2

    if not can_h and not can_v:
        node.room = (node.x, node.y, node.w, node.h)
        return

    if can_h and can_v:
        horiz = rng.random() > 0.5
    else:
        horiz = can_v

    if horiz:
        cut = rng.randint(int(node.h * 0.35), int(node.h * 0.65))
        cut = max(cut, MIN_ROOM)
        cut = min(cut, node.h - MIN_ROOM)
        node.left = BSPNode(node.x, node.y, node.w, cut)
        node.right = BSPNode(node.x, node.y + cut, node.w, node.h - cut)
    else:
        cut = rng.randint(int(node.w * 0.35), int(node.w * 0.65))
        cut = max(cut, MIN_ROOM)
        cut = min(cut, node.w - MIN_ROOM)
        node.left = BSPNode(node.x, node.y, cut, node.h)
        node.right = BSPNode(node.x + cut, node.y, node.w - cut, node.h)

    bsp_split(node.left, rng, depth + 1, max_depth)
    bsp_split(node.right, rng, depth + 1, max_depth)


def choose_rooms(floor_idx, rng, n_rooms):
    if floor_idx == 0:
        mandatory = ["Salon", "Hall d'entrée", "Cuisine", "Salle de bain", "Escaliers"]
        optional = ["Chambre"] * 3
    elif floor_idx == -1:
        mandatory = ["Cave", "Escaliers"]
        optional = ["Buanderie", "Salle de bain"]
    else:
        mandatory = ["Escaliers", "Salle de bain"]
        optional = ["Chambre"] * 4

    rooms = mandatory[:]
    rng.shuffle(optional)
    for o in optional:
        if len(rooms) >= n_rooms:
            break
        rooms.append(o)

    while len(rooms) > n_rooms:
        supprime = False
        for removable in ["Chambre", "Buanderie", "Salle de bain"]:
            if removable in rooms and len(rooms) > n_rooms:
                rooms.remove(removable)
                supprime = True
        if not supprime:
            break

    return rooms


def generate_floor(floor_idx: int, seed: int) -> dict:
    rng = random.Random(seed)

    n_rooms = rng.randint(3, 6)
    room_types = choose_rooms(floor_idx, rng, n_rooms)
    n = len(room_types)

    depth = max(1, min(4, math.ceil(math.log2(max(n, 2)))))

    root = BSPNode(0, 0, CANVAS_W, CANVAS_H)
    bsp_split(root, rng, depth=0, max_depth=depth)

    leaves = root.get_leaves()

    while len(leaves) > n:
        leaves.pop(rng.randint(0, len(leaves) - 1))
    while len(leaves) < n:
        leaves.append(leaves[rng.randint(0, len(leaves) - 1)])

    leaves.sort(key=lambda l: l.w * l.h, reverse=True)
    room_types_sorted = sorted(
        room_types, key=lambda t: ROOM_DEFS[t]["weight"], reverse=True
    )

    rooms = []
    for i, rtype in enumerate(room_types_sorted):
        if i >= len(leaves):
            break
        leaf = leaves[i]
        pad = WALL_THICK
        rx, ry = leaf.x + pad, leaf.y + pad
        rw, rh = leaf.w - pad * 2, leaf.h - pad * 2
        if rw < 30 or rh < 30:
            rx, ry, rw, rh = leaf.x, leaf.y, leaf.w, leaf.h
        rooms.append(
            {
                "name": rtype,
                "rect": (rx, ry, rw, rh),
                "leaf": (leaf.x, leaf.y, leaf.w, leaf.h),
                "color": ROOM_DEFS[rtype]["color"],
                "is_stair": rtype == "Escaliers",
            }
        )

    doors = _generate_doors(rooms, leaves, rng)

    return {
        "rooms": rooms,
        "doors": doors,
        "leaves": [(l.x, l.y, l.w, l.h) for l in leaves[:n]],
        "root": root,
        "seed": seed,
        "floor_idx": floor_idx,
    }


def _safe_randint(rng, a, b):
    if a >= b:
        return a
    return rng.randint(a, b)


def _generate_doors(rooms, leaves, rng):
    doors = []
    n = len(rooms)
    TOLERANCE = WALL_THICK

    for i in range(n):
        for j in range(i + 1, n):
            if j >= len(leaves) or i >= len(leaves):
                continue
            la = leaves[i]
            lb = leaves[j]
            ax, ay, aw, ah = la.x, la.y, la.w, la.h
            bx, by, bw, bh = lb.x, lb.y, lb.w, lb.h

            if abs((ax + aw) - bx) <= TOLERANCE:
                shared_x = ax + aw
                ov_top = max(ay, by) + WALL_THICK * 2
                ov_bot = min(ay + ah, by + bh) - WALL_THICK * 2
                if ov_bot - ov_top >= DOOR_W:
                    dy = _safe_randint(rng, ov_top, ov_bot - DOOR_W)
                    doors.append(
                        {
                            "type": "v",
                            "rect": (
                                shared_x - WALL_THICK // 2,
                                dy,
                                WALL_THICK + 2,
                                DOOR_W,
                            ),
                            "rooms": (i, j),
                        }
                    )

            elif abs((bx + bw) - ax) <= TOLERANCE:
                shared_x = bx + bw
                ov_top = max(ay, by) + WALL_THICK * 2
                ov_bot = min(ay + ah, by + bh) - WALL_THICK * 2
                if ov_bot - ov_top >= DOOR_W:
                    dy = _safe_randint(rng, ov_top, ov_bot - DOOR_W)
                    doors.append(
                        {
                            "type": "v",
                            "rect": (
                                shared_x - WALL_THICK // 2,
                                dy,
                                WALL_THICK + 2,
                                DOOR_W,
                            ),
                            "rooms": (i, j),
                        }
                    )

            elif abs((ay + ah) - by) <= TOLERANCE:
                shared_y = ay + ah
                ov_l = max(ax, bx) + WALL_THICK * 2
                ov_r = min(ax + aw, bx + bw) - WALL_THICK * 2
                if ov_r - ov_l >= DOOR_W:
                    dx = _safe_randint(rng, ov_l, ov_r - DOOR_W)
                    doors.append(
                        {
                            "type": "h",
                            "rect": (
                                dx,
                                shared_y - WALL_THICK // 2,
                                DOOR_W,
                                WALL_THICK + 2,
                            ),
                            "rooms": (i, j),
                        }
                    )

            elif abs((by + bh) - ay) <= TOLERANCE:
                shared_y = by + bh
                ov_l = max(ax, bx) + WALL_THICK * 2
                ov_r = min(ax + aw, bx + bw) - WALL_THICK * 2
                if ov_r - ov_l >= DOOR_W:
                    dx = _safe_randint(rng, ov_l, ov_r - DOOR_W)
                    doors.append(
                        {
                            "type": "h",
                            "rect": (
                                dx,
                                shared_y - WALL_THICK // 2,
                                DOOR_W,
                                WALL_THICK + 2,
                            ),
                            "rooms": (i, j),
                        }
                    )

    return doors


class House:
    def __init__(self):
        self.master_seed = random.randint(0, 99999)
        self._floors: dict[int, dict] = {}
        self.current_floor = 0
        rng = random.Random(self.master_seed)
        self.has_basement = True
        self.num_upper = rng.randint(0, 2)
        self._build_floor(0)

    def _floor_seed(self, idx):
        return (self.master_seed * 1000 + (idx + 10)) % (2**31)

    def _build_floor(self, idx):
        if idx not in self._floors:
            self._floors[idx] = generate_floor(idx, self._floor_seed(idx))

    def go_to_floor(self, idx):
        self._build_floor(idx)
        self.current_floor = idx

    def current(self):
        return self._floors[self.current_floor]

    def can_go_up(self):
        return self.current_floor < self.num_upper

    def can_go_down(self):
        if self.current_floor > 0:
            return True
        if self.current_floor == 0 and self.has_basement:
            return True
        return False

    def reset(self):
        self.__init__()


def _draw_stair_lines(surf, rx, ry, rw, rh):
    n_lines = max(3, rh // 14)
    for i in range(n_lines):
        t = i / max(n_lines - 1, 1)
        y = ry + int(t * rh)
        margin = int(t * rw * 0.25)
        pygame.draw.line(
            surf, PAL["stair_line"], (rx + margin, y), (rx + rw - margin, y), 1
        )


def _draw_door(surf, door, ox=0, oy=0):
    dx, dy, dw, dh = door["rect"]
    rx, ry = dx + ox, dy + oy

    pygame.draw.rect(surf, PAL["bg"], (rx, ry, dw, dh))

    if door["type"] == "v":
        cx = rx + dw // 2
        pygame.draw.line(surf, PAL["door"], (cx - 3, ry), (cx - 3, ry + dh), 3)
        pygame.draw.line(surf, PAL["door"], (cx + 3, ry), (cx + 3, ry + dh), 3)
        arc_r = dh // 2
        pygame.draw.arc(
            surf, PAL["door_arc"], (cx - arc_r, ry, arc_r * 2, arc_r * 2), 0, math.pi, 2
        )
    else:
        cy = ry + dh // 2
        pygame.draw.line(surf, PAL["door"], (rx, cy - 3), (rx + dw, cy - 3), 3)
        pygame.draw.line(surf, PAL["door"], (rx, cy + 3), (rx + dw, cy + 3), 3)
        arc_r = dw // 2
        pygame.draw.arc(
            surf, PAL["door_arc"], (rx, cy - arc_r, arc_r * 2, arc_r * 2), 0, math.pi, 2
        )


carte_maison = None

_house: House | None = None
_fade_alpha = 255
_fading = True
_pending_floor = None
_btn_rects: dict[str, pygame.Rect] = {}
_events: list = []

_fonts: dict = {}


def set_events(events):
    global _events
    _events = events


def _init_fonts():
    global _fonts
    if _fonts:
        return
    try:
        _fonts["title"] = pygame.font.SysFont("Georgia", 17, bold=True)
        _fonts["room"] = pygame.font.SysFont("Georgia", 13, bold=True)
        _fonts["small"] = pygame.font.SysFont("Georgia", 10)
        _fonts["ui"] = pygame.font.SysFont("Verdana", 11)
    except Exception:
        f = pygame.font.SysFont(None, 14)
        _fonts = {"title": f, "room": f, "small": f, "ui": f}


def _ensure_house():
    global _house
    if _house is None:
        _house = House()


def _draw_plan_on_canvas(mouse_canvas):
    floor_data = _house.current()
    font_room = _fonts["room"]
    font_small = _fonts["small"]

    carte_maison.fill(PAL["bg"])

    for gx in range(0, CANVAS_W, 20):
        pygame.draw.line(carte_maison, PAL["grid"], (gx, 0), (gx, CANVAS_H))
    for gy in range(0, CANVAS_H, 20):
        pygame.draw.line(carte_maison, PAL["grid"], (0, gy), (CANVAS_W, gy))

    for room in floor_data["rooms"]:
        rx, ry, rw, rh = room["rect"]
        pygame.draw.rect(carte_maison, room["color"], (rx, ry, rw, rh))

        if room["is_stair"]:
            _draw_stair_lines(carte_maison, rx + 4, ry + 4, rw - 8, rh - 8)

    for lx, ly, lw, lh in floor_data["leaves"]:
        pygame.draw.rect(carte_maison, PAL["wall"], (lx, ly, lw, lh), WALL_THICK)

    for door in floor_data["doors"]:
        _draw_door(carte_maison, door)

    for room in floor_data["rooms"]:
        rx, ry, rw, rh = room["rect"]
        name = room["name"]
        font = font_room if (rw > 120 and rh > 60) else font_small
        if font is font_small and rw < 70:
            name = name[:6] + "."
        txt = font.render(name, True, PAL["text"])
        tx = rx + (rw - txt.get_width()) // 2
        ty = ry + (rh - txt.get_height()) // 2
        if rw > txt.get_width() + 4 and rh > txt.get_height() + 4:
            shadow = font.render(name, True, (200, 190, 170))
            carte_maison.blit(shadow, (tx + 1, ty + 1))
            carte_maison.blit(txt, (tx, ty))

    pygame.draw.rect(
        carte_maison, PAL["wall_outer"], (0, 0, CANVAS_W, CANVAS_H), WALL_THICK + 2
    )


def _draw_ui(mouse_pos):
    mx, my = mouse_pos
    font_ui = _fonts["ui"]

    fl_name = FLOOR_NAMES.get(_house.current_floor, f"Étage {_house.current_floor}")
    fs = font_ui.render(fl_name, True, PAL["floor_ind"])
    screen.blit(fs, (CANVAS_X + CANVAS_W - fs.get_width() - 6, 18))

    px = CANVAS_X + CANVAS_W + 12
    pw = WIN_W - px - 10
    panel_rect = pygame.Rect(px - 6, CANVAS_Y - 6, pw + 12, CANVAS_H + 12)
    pygame.draw.rect(screen, PAL["panel_bg"], panel_rect, border_radius=8)
    pygame.draw.rect(screen, PAL["btn_border"], panel_rect, 1, border_radius=8)

    py = CANVAS_Y + 8

    screen.blit(font_ui.render("Pièces :", True, PAL["text_light"]), (px, py))
    py += 24
    shown = set()
    for room in _house.current()["rooms"]:
        n = room["name"]
        if n in shown:
            continue
        shown.add(n)
        pygame.draw.rect(screen, room["color"], (px, py, 14, 13))
        pygame.draw.rect(screen, PAL["wall"], (px, py, 14, 13), 1)
        screen.blit(font_ui.render(n, True, PAL["text_light"]), (px + 20, py - 1))
        py += 20
    py += 10

    screen.blit(
        font_ui.render(f"Seed : {_house.master_seed}", True, (140, 128, 108)), (px, py)
    )
    py += 18

    screen.blit(font_ui.render("Structure :", True, PAL["text_light"]), (px, py))
    py += 20
    structure = []
    if _house.has_basement:
        structure.append((-1, "Sous-sol"))
    structure.append((0, "Rez-de-chaussée"))
    for i in range(1, _house.num_upper + 1):
        structure.append((i, FLOOR_NAMES[i]))
    for fidx, fname in structure:
        is_cur = fidx == _house.current_floor
        col = PAL["floor_ind"] if is_cur else (155, 140, 118)
        label = ("▶ " if is_cur else "  ") + fname
        screen.blit(font_ui.render(label, True, col), (px + 4, py))
        py += 17
    py += 10

    _btn_rects.clear()
    btn = pygame.Rect(px, WIN_H - 100, pw, 38)
    hover = btn.collidepoint(mx, my)
    pygame.draw.rect(
        screen, PAL["btn_hover"] if hover else PAL["btn_bg"], btn, border_radius=6
    )
    pygame.draw.rect(screen, PAL["btn_border"], btn, 1, border_radius=6)
    bs = font_ui.render("🔀  Nouvelle maison", True, PAL["text_light"])
    screen.blit(
        bs,
        (btn.x + (btn.w - bs.get_width()) // 2, btn.y + (btn.h - bs.get_height()) // 2),
    )
    _btn_rects["nouvelle_maison"] = btn

    hint = font_ui.render("Clic escalier ▲▼ = changer d'étage", True, (115, 105, 88))
    screen.blit(hint, (px, WIN_H - 30))


def _draw_tooltip(text, mx, my):
    font = _fonts["ui"]
    s = font.render(text, True, PAL["text_light"])
    tw, th = s.get_width() + 14, s.get_height() + 8
    tx = min(mx + 16, WIN_W - tw - 4)
    ty = min(my + 12, WIN_H - th - 4)
    pygame.draw.rect(screen, (40, 34, 28), (tx, ty, tw, th), border_radius=4)
    pygame.draw.rect(screen, PAL["btn_border"], (tx, ty, tw, th), 1, border_radius=4)
    screen.blit(s, (tx + 7, ty + 4))


def dessin_maison():
    global _house, _fade_alpha, _fading, _pending_floor

    _init_fonts()
    _init_canvas()
    _ensure_house()

    screen.fill(PAL["bg"])

    mx, my = pygame.mouse.get_pos()
    mcx, mcy = mx - CANVAS_X, my - CANVAS_Y

    for event in _events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            for bkey, brect in _btn_rects.items():
                if brect.collidepoint(mx, my):
                    if bkey == "nouvelle_maison":
                        _house = House()
                        _fade_alpha = 255
                        _fading = True
                        _pending_floor = None

            if 0 <= mcx <= CANVAS_W and 0 <= mcy <= CANVAS_H:
                for room in _house.current()["rooms"]:
                    if room["is_stair"]:
                        rx, ry, rw, rh = room["rect"]
                        if pygame.Rect(rx, ry, rw, rh).collidepoint(mcx, mcy):
                            going_up = mcy < ry + rh // 2
                            if going_up and _house.can_go_up():
                                _pending_floor = _house.current_floor + 1
                                _fade_alpha = 0
                                _fading = True
                            elif not going_up and _house.can_go_down():
                                _pending_floor = _house.current_floor - 1
                                _fade_alpha = 0
                                _fading = True

    if _fading:
        if _pending_floor is not None:
            _fade_alpha = min(255, _fade_alpha + 18)
            if _fade_alpha >= 255:
                _house.go_to_floor(_pending_floor)
                _pending_floor = None
        else:
            _fade_alpha = max(0, _fade_alpha - 18)
            if _fade_alpha == 0:
                _fading = False

    _draw_plan_on_canvas((mcx, mcy))

    floor_data = _house.current()
    for room in floor_data["rooms"]:
        if room["is_stair"]:
            rx, ry, rw, rh = room["rect"]
            hover = pygame.Rect(rx, ry, rw, rh).collidepoint(mcx, mcy)
            cx, cy = rx + rw // 2, ry + rh // 2
            ac = PAL["arrow"] if hover else (190, 155, 50)
            pygame.draw.polygon(
                carte_maison, ac, [(cx, cy - 16), (cx - 9, cy - 4), (cx + 9, cy - 4)]
            )
            pygame.draw.polygon(
                carte_maison, ac, [(cx, cy + 16), (cx - 9, cy + 4), (cx + 9, cy + 4)]
            )

    screen.blit(carte_maison, (CANVAS_X, CANVAS_Y))

    if _fading and _fade_alpha > 0:
        ov = pygame.Surface((CANVAS_W, CANVAS_H))
        ov.set_alpha(_fade_alpha)
        ov.fill((20, 15, 10))
        screen.blit(ov, (CANVAS_X, CANVAS_Y))

    _draw_ui((mx, my))

    if 0 <= mcx <= CANVAS_W and 0 <= mcy <= CANVAS_H:
        for room in floor_data["rooms"]:
            if room["is_stair"]:
                rx, ry, rw, rh = room["rect"]
                if pygame.Rect(rx, ry, rw, rh).collidepoint(mcx, mcy):
                    going_up = mcy < ry + rh // 2
                    if going_up:
                        if _house.can_go_up():
                            nf = _house.current_floor + 1
                            _draw_tooltip(f"↑ → {FLOOR_NAMES.get(nf, str(nf))}", mx, my)
                        else:
                            _draw_tooltip("↑ Pas d'étage supérieur", mx, my)
                    else:
                        if _house.can_go_down():
                            nf = _house.current_floor - 1
                            _draw_tooltip(f"↓ → {FLOOR_NAMES.get(nf, str(nf))}", mx, my)
                        else:
                            _draw_tooltip("↓ Pas d'étage inférieur", mx, my)
