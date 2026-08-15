"""
======================================================================
VERTICAL SCROLLING SHOOTER - A simple 1945/Star Force style game
======================================================================

A beginner-friendly arcade shooter written with Pygame.
You fly upward (the world scrolls down past you), shooting enemies
that fly down toward you. Avoid their bullets and don't get rammed!

CONTROLS:
    Arrow keys or WASD .... Move ship
    Space or Z ............ Shoot
    P ..................... Pause
    R ..................... Restart (after game over)
    Esc ................... Quit

REQUIREMENTS:
    Python 3.8+
    pygame   (install with: pip install pygame)

The whole game lives in this single file and uses NO external
images, sounds, or fonts. Everything visual is drawn with Pygame's
basic shape primitives so you can read and tweak it easily.
"""

import math
import random
import sys

import pygame


# =====================================================================
# CONFIGURATION CONSTANTS
# =====================================================================
# Tweak any of these to change how the game looks and feels.
# They are grouped by topic so you can find what you want quickly.
# ---------------------------------------------------------------------

# --- Window / display -------------------------------------------------
SCREEN_WIDTH = 480           # Window width in pixels.  Try 360 for a
                             # narrower "arcade cabinet" feel, or 600+ for
                             # more room to dodge.
SCREEN_HEIGHT = 720           # Window height in pixels.  Vertical shooters
                              # traditionally use a tall (portrait) screen.
FPS = 60                      # Frames per second.  Higher = smoother, but
                              # more CPU.  All movement values below are
                              # tuned for 60 FPS.
WINDOW_TITLE = "Sky Striker"  # Text in the window's title bar.

# --- Colors (RGB tuples, 0..255) -------------------------------------
# Change these to recolor the entire game.
COLOR_BG_TOP    = (5, 5, 30)       # Sky color at the top of the screen.
COLOR_BG_BOTTOM = (20, 0, 50)      # Sky color at the bottom (gradient).
# COLOR_BG_TOP / COLOR_BG_BOTTOM are reassigned at runtime (via `global`)
# when the player defeats a Boss, to simulate a level transition without
# a full scene/state-machine rewrite. We snapshot the originals here so
# Game.reset() can restore the level-1 sky when starting a new game.
_ORIGINAL_COLOR_BG_TOP = COLOR_BG_TOP
_ORIGINAL_COLOR_BG_BOTTOM = COLOR_BG_BOTTOM
COLOR_STAR      = (255, 255, 255)  # Color of the scrolling star field.
COLOR_PLAYER    = (90, 200, 255)   # Player ship body.
COLOR_PLAYER_HI = (220, 240, 255)  # Player ship cockpit highlight.
COLOR_PLAYER_THRUST = (255, 180, 60)  # Engine flame.
COLOR_PLAYER_BULLET = (255, 240, 120)  # Your bullets.
COLOR_ENEMY     = (255, 80, 80)    # Standard enemy color.
COLOR_ENEMY_FAST = (255, 160, 60)  # Fast (smaller) enemy color.
COLOR_ENEMY_TANK = (160, 80, 200)  # Tough (larger) enemy color.
COLOR_ENEMY_BULLET = (255, 120, 200)  # Enemy bullets.
COLOR_EXPLOSION = (255, 200, 80)   # Explosion particles.
COLOR_HUD_TEXT  = (230, 230, 230)  # Score / lives text.
COLOR_HUD_DIM   = (140, 140, 160)  # Less important HUD text.

# --- Neon / futuristic accents ----------------------------------------
# Used by the redesigned Player and Boss draw() methods, plus the start
# screen. Keeping them separate from the "gameplay" colors above makes
# it easy to swap the whole neon palette without touching hitboxes/logic.
NEON_CYAN     = (100, 240, 255)   # Player trim / glow.
NEON_CYAN_DIM = (40, 120, 140)    # Player glow, outer/faint layer.
NEON_MAGENTA  = (255, 60, 200)    # Boss trim / glow.
NEON_MAGENTA_DIM = (140, 20, 110) # Boss glow, outer/faint layer.
NEON_WHITE    = (235, 250, 255)   # Bright core highlights.

# --- Start screen -------------------------------------------------------
START_TITLE_TEXT  = "SKY STRIKER"
START_PROMPT_TEXT = "Presiona ENTER para iniciar"
START_BLINK_MS    = 500        # Half-period of the blink (on/off) in ms.

# --- Star field (background) -----------------------------------------
NUM_STARS = 80                # How many stars are visible at once.
                              # Lower this on slow machines.
STAR_SPEED_MIN = 1.0          # Slowest star speed (pixels/frame).
STAR_SPEED_MAX = 4.0          # Fastest star speed.  The variation is
                              # what creates the parallax depth effect.

# --- Player ship ------------------------------------------------------
PLAYER_WIDTH = 36             # Ship hitbox/visual width.
PLAYER_HEIGHT = 36            # Ship hitbox/visual height.
PLAYER_SPEED = 5.5            # Movement speed in pixels/frame.  Higher
                              # = twitchier; lower = more deliberate.
PLAYER_FIRE_COOLDOWN_MS = 180 # Milliseconds between shots.  Lower this
                              # for a rapid-fire feel.
PLAYER_START_LIVES = 3        # Extra lives on a fresh game.
PLAYER_INVULN_MS = 1500       # How long the player flashes and is
                              # immune after losing a life.

# --- Bullets ----------------------------------------------------------
PLAYER_BULLET_SPEED = 10.0    # How fast your shots travel upward.
PLAYER_BULLET_WIDTH = 4
PLAYER_BULLET_HEIGHT = 14

# --- Special attack ('B' key) -----------------------------------------
# A limited-ammo, high-impact volley meant as an emergency "get me out of
# this" button when the screen fills up with enemies. Deliberately much
# stronger per-bullet than the regular shot, but scarce.
PLAYER_SPECIAL_START_AMMO = 3      # Charges available on a fresh game.
PLAYER_SPECIAL_COOLDOWN_MS = 600   # Minimum time between uses, even with
                                    # ammo to spare — stops instant double
                                    # taps from a single key-down.
PLAYER_SPECIAL_BULLET_COUNT = 5    # Bullets fired per use, in a fan.
PLAYER_SPECIAL_BULLET_SPREAD_DEG = 40  # Total angular spread of the fan.
PLAYER_SPECIAL_BULLET_SPEED = 12.0
PLAYER_SPECIAL_BULLET_WIDTH = 10   # Visibly bigger than a normal bullet.
PLAYER_SPECIAL_BULLET_HEIGHT = 22
PLAYER_SPECIAL_BULLET_DAMAGE = 3   # Regular shots deal 1; this hits hard.
COLOR_PLAYER_SPECIAL_BULLET = (170, 120, 255)  # Violet, reads as "different".

ENEMY_BULLET_SPEED = 4.5      # How fast enemy shots travel downward.
                              # Keep this well below player bullet speed
                              # so the player can outrun their own shots.
ENEMY_BULLET_RADIUS = 5

# --- Enemies ----------------------------------------------------------
# We have three "kinds" of enemies. Each kind has its own stats below.
# A new enemy spawns roughly every ENEMY_SPAWN_INTERVAL_MS milliseconds.
ENEMY_SPAWN_INTERVAL_MS = 800   # Lower = more enemies = harder.
ENEMY_SPAWN_JITTER_MS = 400     # Random extra time added to each spawn,
                                # so the rhythm doesn't feel mechanical.

# Probability weights for each enemy type. They don't need to sum to 1.0;
# they're relative to each other.
ENEMY_WEIGHT_BASIC = 6.0
ENEMY_WEIGHT_FAST  = 3.0
ENEMY_WEIGHT_TANK  = 1.0

# Basic enemy: average size, average speed, 1 HP.
ENEMY_BASIC_SIZE = 32
ENEMY_BASIC_SPEED = 2.2
ENEMY_BASIC_HP = 1
ENEMY_BASIC_SCORE = 100
ENEMY_BASIC_FIRE_CHANCE = 0.004  # Per-frame chance to shoot.  At 60 FPS,
                                 # 0.004 ≈ once every ~4 seconds per enemy.

# Fast enemy: small, quick, can't take a punch but rarely shoots.
ENEMY_FAST_SIZE = 24
ENEMY_FAST_SPEED = 4.0
ENEMY_FAST_HP = 1
ENEMY_FAST_SCORE = 200
ENEMY_FAST_FIRE_CHANCE = 0.002

# Tank enemy: big, slow, takes several hits, fires more often.
ENEMY_TANK_SIZE = 48
ENEMY_TANK_SPEED = 1.4
ENEMY_TANK_HP = 4
ENEMY_TANK_SCORE = 400
ENEMY_TANK_FIRE_CHANCE = 0.008

ENEMY_BOSS_SIZE = 80
ENEMY_BOSS_SPEED = 1.4
ENEMY_BOSS_HP = 80
ENEMY_BOSS_SCORE = 500
ENEMY_BOSS_FIRE_CHANCE = 0.003
# Unlike regular enemies, the Boss shouldn't just fly past and off the
# bottom of the screen — it descends to this Y and then hovers there,
# wobbling side to side, so the fight actually has time to happen.
ENEMY_BOSS_HOVER_Y = 110

# --- Power-ups ----------------------------------------------------------
# Dropped by regular enemies (never the Boss — its reward is the
# permanent buff below) and picked up by flying into them. Effects are
# temporary and timed with pygame.time.get_ticks(), same pattern as the
# player's invulnerability window.
POWERUP_DROP_CHANCE = 0.22     # Chance a killed regular enemy drops one.
POWERUP_SIZE = 20
POWERUP_FALL_SPEED = 2.0
POWERUP_DURATION_MS = 5000     # How long an active effect lasts.
POWERUP_KIND_DOUBLE_SHOT = "double_shot"
POWERUP_KIND_RAPID_FIRE = "rapid_fire"
POWERUP_KINDS = (POWERUP_KIND_DOUBLE_SHOT, POWERUP_KIND_RAPID_FIRE)
COLOR_POWERUP_DOUBLE_SHOT = (90, 230, 150)   # Green.
COLOR_POWERUP_RAPID_FIRE  = (255, 205, 70)   # Amber.
PLAYER_RAPID_FIRE_COOLDOWN_MS = 70  # Replaces PLAYER_FIRE_COOLDOWN_MS
                                     # while rapid_fire is active.
PLAYER_DOUBLE_SHOT_OFFSET = 9       # Horizontal gap between the two
                                     # bullets fired during double_shot.

# --- Boss reward: permanent speed upgrade -------------------------------
# Granted once per Boss kill, stacks additively, and is completely
# independent from the temporary power-ups above (it lives on the Player
# as a separate attribute, so both systems can be active at once).
BOSS_PERMANENT_SPEED_BONUS = 1.2

# --- Level 2 palette ------------------------------------------------------
# Swapped into the (normally constant) COLOR_BG_TOP / COLOR_BG_BOTTOM
# globals when the Boss dies, so the sky itself signals "new level"
# without needing a scene/state-machine rewrite.
LEVEL_2_COLOR_BG_TOP = (5, 25, 10)     # Sky color at the top, level 2.
LEVEL_2_COLOR_BG_BOTTOM = (0, 45, 15)  # Sky color at the bottom, level 2.


# Difficulty ramp: every DIFFICULTY_RAMP_SECONDS, spawn interval shrinks
# by DIFFICULTY_RAMP_FACTOR (multiplicative). Set RAMP_FACTOR to 1.0 to
# disable the ramp entirely.
DIFFICULTY_RAMP_SECONDS = 20
DIFFICULTY_RAMP_FACTOR = 0.92
ENEMY_SPAWN_INTERVAL_MIN_MS = 250  # Floor — never spawn faster than this.

# --- Explosions / particles ------------------------------------------
EXPLOSION_PARTICLES = 14      # Particles per explosion.  Bigger numbers
                              # look juicier but cost more performance.
EXPLOSION_SPEED_MIN = 1.0
EXPLOSION_SPEED_MAX = 4.0
EXPLOSION_LIFE_FRAMES = 30    # How many frames each particle lives.

# --- HUD --------------------------------------------------------------
HUD_FONT_SIZE = 22
HUD_MARGIN = 10               # Distance from screen edges, in pixels.

# =====================================================================
# END OF CONFIGURATION
# =====================================================================


# ---------------------------------------------------------------------
# Helper: pick a weighted random choice.
# ---------------------------------------------------------------------
# random.choices does this for us, but a tiny wrapper makes the calling
# code easier to read.
def weighted_choice(options_with_weights):
    """Return one option chosen by weight.

    `options_with_weights` is a list of (option, weight) tuples.
    """
    options = [pair[0] for pair in options_with_weights]
    weights = [pair[1] for pair in options_with_weights]
    return random.choices(options, weights=weights, k=1)[0]


# ---------------------------------------------------------------------
# Neon drawing helpers
# ---------------------------------------------------------------------
# pygame.draw has no built-in "glow"/blur. We fake one cheaply by
# blitting a few translucent copies of a shape at increasing size onto a
# temporary per-pixel-alpha surface, then blitting that once onto the
# real screen with additive-ish blending. It's a handful of extra draw
# calls per ship, which is trivial at this game's scale.
def draw_glow_polygon(surface, points, glow_color, spread=3, layers=4, max_alpha=90):
    """Draw a soft glow behind `points` (a polygon) using `glow_color`.

    `points` are absolute screen coordinates. `spread` controls how far
    the glow expands outward per layer (in pixels); `layers` controls
    how many translucent rings are stacked; `max_alpha` is the alpha of
    the innermost (brightest) layer, fading out toward the edge.
    """
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    pad = spread * layers + 4
    min_x, max_x = min(xs) - pad, max(xs) + pad
    min_y, max_y = min(ys) - pad, max(ys) + pad
    w, h = int(max_x - min_x), int(max_y - min_y)
    if w <= 0 or h <= 0:
        return

    glow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = (min_x + max_x) / 2, (min_y + max_y) / 2
    local_points = [(px - min_x, py - min_y) for px, py in points]
    local_cx, local_cy = cx - min_x, cy - min_y

    # Draw from the outside in, so the brightest/smallest layer ends up
    # on top with the least amount of alpha-blending overdraw.
    for i in range(layers, 0, -1):
        scale = 1.0 + (i * spread) / max(1.0, (max_x - min_x))
        scaled = [
            (local_cx + (px - local_cx) * scale, local_cy + (py - local_cy) * scale)
            for px, py in local_points
        ]
        alpha = int(max_alpha * (1 - i / (layers + 1)))
        color = (*glow_color[:3], alpha)
        pygame.draw.polygon(glow_surf, color, scaled)

    # BLEND_ADD makes overlapping translucent layers brighten like real
    # neon light instead of just darkening/greying toward opaque.
    surface.blit(glow_surf, (int(min_x), int(min_y)), special_flags=pygame.BLEND_RGBA_ADD)


def draw_neon_line(surface, points, color, width=2, closed=False):
    """A thin bright line on top of the glow, for crisp neon edges."""
    if closed:
        pygame.draw.polygon(surface, color, points, width)
    else:
        pygame.draw.lines(surface, color, False, points, width)


# ---------------------------------------------------------------------
# Star: a single twinkling dot in the parallax background.
# ---------------------------------------------------------------------
class Star:
    """One pixel of the scrolling star field.

    Stars at different speeds create a sense of depth (parallax):
    fast stars feel close, slow stars feel far away.
    """
    def __init__(self):
        # Pick a random position and a random speed.
        # We re-randomize on respawn (when the star scrolls off the bottom).
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(0, SCREEN_HEIGHT)
        self.speed = random.uniform(STAR_SPEED_MIN, STAR_SPEED_MAX)
        # Faster stars are drawn brighter to enhance the depth illusion.
        brightness_ratio = (self.speed - STAR_SPEED_MIN) / max(
            0.0001, (STAR_SPEED_MAX - STAR_SPEED_MIN)
        )
        gray = int(120 + 135 * brightness_ratio)  # 120..255
        self.color = (gray, gray, gray)

    def update(self):
        # Move down by the star's speed each frame.
        self.y += self.speed
        # Wrap to the top once we leave the screen.
        if self.y > SCREEN_HEIGHT:
            self.y = 0.0
            self.x = random.uniform(0, SCREEN_WIDTH)
            # Re-pick speed/brightness for variety.
            self.speed = random.uniform(STAR_SPEED_MIN, STAR_SPEED_MAX)

    def draw(self, surface):
        # A 1- or 2-pixel rectangle is cheaper than a circle and looks fine.
        size = 1 if self.speed < (STAR_SPEED_MIN + STAR_SPEED_MAX) / 2 else 2
        surface.fill(self.color, (int(self.x), int(self.y), size, size))


# ---------------------------------------------------------------------
# Bullet: used for both the player's shots and enemy shots.
# ---------------------------------------------------------------------
class Bullet:
    """A simple projectile that moves in a straight line.

    `vy` (vertical velocity) is negative for upward (player) shots
    and positive for downward (enemy) shots. The same class handles both.

    `vx` (horizontal velocity) defaults to 0 for normal straight-up/down
    shots, but is used by the special attack's fan spread below.

    `is_special` marks the bigger, higher-damage variant fired by the
    player's limited-ammo special attack (see Player.use_special). It's
    always a player bullet; passing is_special=True implies
    is_player_bullet=True regardless of what's passed for that argument.
    """
    def __init__(self, x, y, vy, color, is_player_bullet,
                 vx=0.0, damage=1, is_special=False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.is_player_bullet = is_player_bullet or is_special
        self.is_special = is_special
        self.damage = damage
        self.alive = True

        # Player bullets are little rectangles; enemy bullets are circles;
        # special bullets are bigger rectangles so they read as "stronger"
        # at a glance. That makes it easy to distinguish friend/foe/special
        # without needing a legend.
        if is_special:
            w, h = PLAYER_SPECIAL_BULLET_WIDTH, PLAYER_SPECIAL_BULLET_HEIGHT
            self.rect = pygame.Rect(int(x - w / 2), int(y - h / 2), w, h)
        elif self.is_player_bullet:
            self.rect = pygame.Rect(
                int(x - PLAYER_BULLET_WIDTH / 2),
                int(y - PLAYER_BULLET_HEIGHT / 2),
                PLAYER_BULLET_WIDTH,
                PLAYER_BULLET_HEIGHT,
            )
        else:
            r = ENEMY_BULLET_RADIUS
            self.rect = pygame.Rect(int(x - r), int(y - r), r * 2, r * 2)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        # Sync the collision rectangle to the new position.
        self.rect.centery = int(self.y)
        self.rect.centerx = int(self.x)
        # Mark dead once off-screen (top, bottom, or now sides too, since
        # the special attack's fan can drift out horizontally).
        if (self.y < -20 or self.y > SCREEN_HEIGHT + 20
                or self.x < -20 or self.x > SCREEN_WIDTH + 20):
            self.alive = False

    def draw(self, surface):
        if self.is_special:
            # Bright core rectangle plus a thin glowing outline so it
            # stands out clearly from regular shots at a glance.
            draw_glow_polygon(
                surface,
                [self.rect.topleft, self.rect.topright,
                 self.rect.bottomright, self.rect.bottomleft],
                self.color, spread=3, layers=3, max_alpha=100,
            )
            pygame.draw.rect(surface, self.color, self.rect, border_radius=4)
            pygame.draw.rect(surface, NEON_WHITE, self.rect, width=1, border_radius=4)
        elif self.is_player_bullet:
            # A bright rectangle with a slightly lighter center for "pew" feel.
            pygame.draw.rect(surface, self.color, self.rect, border_radius=2)
        else:
            pygame.draw.circle(
                surface, self.color, (int(self.x), int(self.y)),
                ENEMY_BULLET_RADIUS,
            )
            # Inner highlight makes enemy bullets pop against dark sky.
            pygame.draw.circle(
                surface, (255, 230, 240),
                (int(self.x), int(self.y)),
                max(1, ENEMY_BULLET_RADIUS - 2),
            )


# ---------------------------------------------------------------------
# Player: the ship you control.
# ---------------------------------------------------------------------
class Player:
    """The player's ship.

    Holds position, lives, and shooting cooldown. Also handles brief
    invulnerability after being hit, so the player isn't instantly killed
    again after respawning at the center.
    """
    def __init__(self):
        # Start near the bottom-center.
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT - PLAYER_HEIGHT * 1.5
        self.lives = PLAYER_START_LIVES
        self.last_shot_time_ms = 0
        # Limited-ammo special attack (see use_special below). Separate
        # cooldown from the regular shot so mashing 'B' can't bypass the
        # brief "can't refire instantly" window even while ammo remains.
        self.special_ammo = PLAYER_SPECIAL_START_AMMO
        self.last_special_time_ms = -PLAYER_SPECIAL_COOLDOWN_MS

        # Permanent, stacking speed bonus granted by defeating a Boss.
        # Deliberately separate from PLAYER_SPEED itself so it survives
        # across resets-of-nothing (it only resets with a full new Player,
        # i.e. a brand new game) and stacks additively each time a Boss
        # falls, independent of whatever temporary power-up is active.
        self.permanent_speed_bonus = 0.0

        # Temporary power-ups: kind -> expiry timestamp (ms). A kind only
        # counts as "active" while now_ms < active_powerups[kind]; we
        # don't proactively delete expired entries, has_powerup() just
        # ignores them, which keeps activate_powerup() a single dict write.
        self.active_powerups = {}

        # When pygame.time.get_ticks() < invuln_until_ms, we ignore hits
        # and flicker the sprite to signal "just respawned".
        self.invuln_until_ms = pygame.time.get_ticks() + PLAYER_INVULN_MS

        # The collision rectangle. We center it on (x, y) and update each
        # frame inside `update`.
        self.rect = pygame.Rect(0, 0, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.rect.center = (int(self.x), int(self.y))

    def is_invulnerable(self, now_ms):
        return now_ms < self.invuln_until_ms

    def effective_speed(self):
        """Base movement speed plus any permanent Boss-kill bonuses."""
        return PLAYER_SPEED + self.permanent_speed_bonus

    def activate_powerup(self, kind, now_ms):
        """Start (or refresh) a timed effect. Called on pickup collision."""
        self.active_powerups[kind] = now_ms + POWERUP_DURATION_MS

    def has_powerup(self, kind, now_ms):
        """True if `kind` is currently active (hasn't expired yet)."""
        return now_ms < self.active_powerups.get(kind, 0)

    def update(self, keys, now_ms):
        # --- Movement --------------------------------------------------
        # Read both arrow keys and WASD so users can pick.
        dx = 0.0
        dy = 0.0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            dx -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1.0
        if keys[pygame.K_UP]    or keys[pygame.K_w]:
            dy -= 1.0
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]:
            dy += 1.0

        # Diagonal movement should not be faster than straight movement.
        # We normalize the (dx, dy) vector so its length is 1, then scale
        # by PLAYER_SPEED. This is a classic 2D-game gotcha worth knowing!
        if dx != 0.0 or dy != 0.0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length

        self.x += dx * self.effective_speed()
        self.y += dy * self.effective_speed()

        # Keep the ship inside the play area.
        half_w = PLAYER_WIDTH / 2
        half_h = PLAYER_HEIGHT / 2
        if self.x < half_w:
            self.x = half_w
        if self.x > SCREEN_WIDTH - half_w:
            self.x = SCREEN_WIDTH - half_w
        if self.y < half_h:
            self.y = half_h
        if self.y > SCREEN_HEIGHT - half_h:
            self.y = SCREEN_HEIGHT - half_h

        self.rect.center = (int(self.x), int(self.y))

    def can_shoot(self, now_ms):
        # rapid_fire replaces the normal cooldown with a much shorter one.
        cooldown = (
            PLAYER_RAPID_FIRE_COOLDOWN_MS
            if self.has_powerup(POWERUP_KIND_RAPID_FIRE, now_ms)
            else PLAYER_FIRE_COOLDOWN_MS
        )
        return (now_ms - self.last_shot_time_ms) >= cooldown

    def shoot(self, bullets, now_ms):
        """Spawn one bullet (or two, side-by-side, during double_shot)."""
        if not self.can_shoot(now_ms):
            return
        self.last_shot_time_ms = now_ms

        if self.has_powerup(POWERUP_KIND_DOUBLE_SHOT, now_ms):
            x_offsets = (-PLAYER_DOUBLE_SHOT_OFFSET, PLAYER_DOUBLE_SHOT_OFFSET)
        else:
            x_offsets = (0,)

        for x_offset in x_offsets:
            bullets.append(Bullet(
                x=self.x + x_offset,
                y=self.y - PLAYER_HEIGHT / 2,
                vy=-PLAYER_BULLET_SPEED,    # Negative = moving UP the screen.
                color=COLOR_PLAYER_BULLET,
                is_player_bullet=True,
            ))

    def can_use_special(self, now_ms):
        """True if the player has ammo left AND the cooldown has passed.

        The cooldown exists on top of the ammo check so a single 'B'
        key-down can't somehow fire twice in the same frame/near-frame;
        it's mostly a safety net, since the actual "don't fire every
        frame while held" logic lives in Game._handle_continuous_input
        via edge-detection.
        """
        if self.special_ammo <= 0:
            return False
        return (now_ms - self.last_special_time_ms) >= PLAYER_SPECIAL_COOLDOWN_MS

    def use_special(self, bullets, now_ms):
        """Consume one special charge and fire a fan of big bullets.

        Returns True if the attack actually fired (False if it was on
        cooldown or out of ammo), so the caller can decide whether to
        e.g. play a "no ammo" sound/flash instead.
        """
        if not self.can_use_special(now_ms):
            return False

        self.special_ammo -= 1
        self.last_special_time_ms = now_ms

        # Fan the bullets out evenly across PLAYER_SPECIAL_BULLET_SPREAD_DEG,
        # centered straight up (-90 degrees in standard screen-space angles,
        # where 0 degrees points right and angles increase clockwise).
        count = PLAYER_SPECIAL_BULLET_COUNT
        spread = math.radians(PLAYER_SPECIAL_BULLET_SPREAD_DEG)
        base_angle = -math.pi / 2  # Straight up.
        start_angle = base_angle - spread / 2
        step = spread / max(1, count - 1) if count > 1 else 0.0

        origin_y = self.y - PLAYER_HEIGHT / 2
        for i in range(count):
            angle = start_angle + step * i
            vx = math.cos(angle) * PLAYER_SPECIAL_BULLET_SPEED
            vy = math.sin(angle) * PLAYER_SPECIAL_BULLET_SPEED
            bullets.append(Bullet(
                x=self.x,
                y=origin_y,
                vx=vx,
                vy=vy,
                color=COLOR_PLAYER_SPECIAL_BULLET,
                is_player_bullet=True,
                is_special=True,
                damage=PLAYER_SPECIAL_BULLET_DAMAGE,
            ))
        return True

    def hit(self, now_ms):
        """Called when an enemy or enemy bullet touches the ship.

        Returns True if the hit actually counted (i.e., not invulnerable).
        """
        if self.is_invulnerable(now_ms):
            return False
        self.lives -= 1
        # Re-grant invulnerability so the next frame doesn't kill us again.
        self.invuln_until_ms = now_ms + PLAYER_INVULN_MS
        # Recenter the ship so the player has a moment to reorient.
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT - PLAYER_HEIGHT * 1.5
        self.rect.center = (int(self.x), int(self.y))
        return True

    def draw(self, surface, now_ms):
        # Flicker while invulnerable: skip drawing every other ~80 ms.
        if self.is_invulnerable(now_ms):
            # Integer-divide the time to get a slow on/off cycle.
            if (now_ms // 80) % 2 == 0:
                return  # Skip this frame's draw; ship "blinks".

        cx, cy = int(self.x), int(self.y)
        hw = PLAYER_WIDTH // 2
        hh = PLAYER_HEIGHT // 2

        # ---- Engine glow (drawn first so it sits *under* the hull) -----
        flame_jitter = random.randint(-2, 2)
        flame_points = [
            (cx - 6, cy + hh - 2),
            (cx + 6, cy + hh - 2),
            (cx,     cy + hh + 12 + flame_jitter),
        ]
        draw_glow_polygon(surface, flame_points, COLOR_PLAYER_THRUST,
                           spread=4, layers=3, max_alpha=110)
        pygame.draw.polygon(surface, COLOR_PLAYER_THRUST, flame_points)
        pygame.draw.polygon(surface, NEON_WHITE, [
            (cx - 2, cy + hh - 2), (cx + 2, cy + hh - 2),
            (cx, cy + hh + 5 + flame_jitter),
        ])  # Bright inner flame core.

        # ---- Hull: an angular, faceted fuselage instead of a plain -----
        # ---- triangle — a narrow nose, a wider mid-body "collar", ------
        # ---- and a swept-back tail.                                    -
        hull_points = [
            (cx,          cy - hh),        # Nose tip
            (cx - 4,      cy - hh + 8),    # Nose shoulder (left)
            (cx - hw + 2, cy + 2),         # Mid-body collar (left)
            (cx - hw,     cy + hh - 4),    # Tail (left)
            (cx,          cy + hh - 10),   # Tail notch (center)
            (cx + hw,     cy + hh - 4),    # Tail (right)
            (cx + hw - 2, cy + 2),         # Mid-body collar (right)
            (cx + 4,      cy - hh + 8),    # Nose shoulder (right)
        ]
        draw_glow_polygon(surface, hull_points, NEON_CYAN,
                           spread=3, layers=4, max_alpha=80)
        pygame.draw.polygon(surface, COLOR_PLAYER, hull_points)
        draw_neon_line(surface, hull_points, NEON_CYAN, width=2, closed=True)

        # ---- Wings: angular, swept shapes instead of plain rectangles --
        wing_left = [
            (cx - hw + 2, cy + 2),
            (cx - hw - 10, cy + hh - 2),
            (cx - hw + 2, cy + hh - 2),
            (cx - hw + 6, cy + 6),
        ]
        wing_right = [
            (cx + hw - 2, cy + 2),
            (cx + hw + 10, cy + hh - 2),
            (cx + hw - 2, cy + hh - 2),
            (cx + hw - 6, cy + 6),
        ]
        for wing in (wing_left, wing_right):
            pygame.draw.polygon(surface, COLOR_PLAYER, wing)
            draw_neon_line(surface, wing, NEON_CYAN_DIM, width=1, closed=True)

        # Wingtip lights — tiny pulsing neon dots, offset in phase so
        # left/right blink alternately (classic "running lights" feel).
        pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2  # 0..1
        tip_color = tuple(int(NEON_CYAN_DIM[i] + (NEON_CYAN[i] - NEON_CYAN_DIM[i]) * pulse)
                           for i in range(3))
        pygame.draw.circle(surface, tip_color, (cx - hw - 8, cy + hh - 3), 2)
        pygame.draw.circle(surface, tip_color, (cx + hw + 8, cy + hh - 3), 2)

        # ---- Neon spine line down the center of the hull ----------------
        draw_neon_line(surface, [(cx, cy - hh + 6), (cx, cy + hh - 8)],
                        NEON_CYAN, width=1)

        # ---- Cockpit: glowing canopy instead of a flat highlight -------
        draw_glow_polygon(surface, [
            (cx - 3, cy - 6), (cx + 3, cy - 6), (cx + 2, cy + 3), (cx - 2, cy + 3),
        ], NEON_CYAN, spread=2, layers=3, max_alpha=100)
        pygame.draw.circle(surface, COLOR_PLAYER_HI, (cx, cy - 2), 4)
        pygame.draw.circle(surface, NEON_WHITE, (cx, cy - 3), 2)


# ---------------------------------------------------------------------
# Enemy: comes in three flavors driven by `kind`.
# ---------------------------------------------------------------------
class Enemy:
    """An enemy ship that flies down and occasionally shoots.

    `kind` is one of "basic", "fast", "tank". Each kind reads its own
    constants from the configuration block above. Centralizing them
    there means you can rebalance the game without touching this code.
    """
    def __init__(self, kind):
        self.kind = kind
        if kind == "fast":
            self.size = ENEMY_FAST_SIZE
            self.speed = ENEMY_FAST_SPEED
            self.hp = ENEMY_FAST_HP
            self.score = ENEMY_FAST_SCORE
            self.fire_chance = ENEMY_FAST_FIRE_CHANCE
            self.color = COLOR_ENEMY_FAST
        elif kind == "tank":
            self.size = ENEMY_TANK_SIZE
            self.speed = ENEMY_TANK_SPEED
            self.hp = ENEMY_TANK_HP
            self.score = ENEMY_TANK_SCORE
            self.fire_chance = ENEMY_TANK_FIRE_CHANCE
            self.color = COLOR_ENEMY_TANK
        else:  # "basic"
            self.size = ENEMY_BASIC_SIZE
            self.speed = ENEMY_BASIC_SPEED
            self.hp = ENEMY_BASIC_HP
            self.score = ENEMY_BASIC_SCORE
            self.fire_chance = ENEMY_BASIC_FIRE_CHANCE
            self.color = COLOR_ENEMY

        # Spawn at a random horizontal position, just above the screen.
        half = self.size / 2
        self.x = random.uniform(half, SCREEN_WIDTH - half)
        self.y = -half

        # Light side-to-side wobble so enemies don't fly in straight lines.
        # `wobble_phase` is just the starting angle of the sine wave.
        self.wobble_phase = random.uniform(0, math.tau)
        self.wobble_amount = random.uniform(0.5, 1.5)
        # `age_frames` drives the wobble over time.
        self.age_frames = 0

        self.alive = True
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.rect.center = (int(self.x), int(self.y))

    def update(self, bullets):
        # Move straight down + a little sideways sine-wave wobble.
        self.age_frames += 1
        self.y += self.speed
        wobble_dx = math.sin(self.age_frames * 0.05 + self.wobble_phase)
        self.x += wobble_dx * self.wobble_amount

        # Stay on-screen horizontally (for tanks especially, the sprite is wide).
        half = self.size / 2
        if self.x < half:
            self.x = half
        if self.x > SCREEN_WIDTH - half:
            self.x = SCREEN_WIDTH - half

        self.rect.center = (int(self.x), int(self.y))

        # If we've left the bottom, mark dead so the game removes us.
        if self.y - half > SCREEN_HEIGHT:
            self.alive = False
            return

        # Random chance to shoot. Only shoot once we're actually on-screen,
        # so the player isn't surprised by bullets from invisible enemies.
        if self.y > 0 and random.random() < self.fire_chance:
            bullets.append(Bullet(
                x=self.x,
                y=self.y + half,
                vy=ENEMY_BULLET_SPEED,   # Positive = moving DOWN.
                color=COLOR_ENEMY_BULLET,
                is_player_bullet=False,
            ))

    def take_damage(self, amount=1):
        """Subtract HP and return True if the enemy just died."""
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        half = self.size // 2

        # Body: a triangle pointing DOWN (toward the player).
        body = [
            (cx,         cy + half),       # Bottom point
            (cx - half,  cy - half + 4),   # Top-left
            (cx + half,  cy - half + 4),   # Top-right
        ]
        pygame.draw.polygon(surface, self.color, body)

        # Tank enemies get an extra "armor band" rectangle for visual weight.
        if self.kind == "tank":
            pygame.draw.rect(
                surface, (40, 20, 60),
                (cx - half + 4, cy - 4, self.size - 8, 8),
            )

        # A small dark "cockpit" circle near the top.
        pygame.draw.circle(surface, (30, 0, 30), (cx, cy - half + 8), 4)


class Boss:
    def __init__(self):
        self.size = ENEMY_BOSS_SIZE
        self.speed = ENEMY_BOSS_SPEED
        self.hp = ENEMY_BOSS_HP
        self.score = ENEMY_BOSS_SCORE
        self.fire_chance = ENEMY_BOSS_FIRE_CHANCE
        self.color = COLOR_ENEMY


        # Spawn at a random horizontal position, just above the screen.
        half = self.size / 2
        self.x = random.uniform(half, SCREEN_WIDTH - half)
        self.y = -half

        # Light side-to-side wobble so enemies don't fly in straight lines.
        # `wobble_phase` is just the starting angle of the sine wave.
        self.wobble_phase = random.uniform(0, math.tau)
        self.wobble_amount = random.uniform(0.5, 1.5)
        # `age_frames` drives the wobble over time.
        self.age_frames = 0

        self.alive = True
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.rect.center = (int(self.x), int(self.y))

    def update(self, bullets):
        # Unlike a regular Enemy, the Boss descends to a fixed hover
        # line (ENEMY_BOSS_HOVER_Y) and then STOPS descending -- it just
        # wobbles side to side and keeps firing. Without this override
        # it would inherit straight-down movement, drift off the bottom
        # of the screen within a few seconds, and die "off-screen"
        # before the player could realistically bring its 80 HP down.
        self.age_frames += 1
        if self.y < ENEMY_BOSS_HOVER_Y:
            self.y += self.speed

        wobble_dx = math.sin(self.age_frames * 0.03 + self.wobble_phase)
        self.x += wobble_dx * self.wobble_amount * 2

        half = self.size / 2
        if self.x < half:
            self.x = half
        if self.x > SCREEN_WIDTH - half:
            self.x = SCREEN_WIDTH - half

        self.rect.center = (int(self.x), int(self.y))

        # Only fire once it's reached the hover line -- otherwise it
        # could start shooting while still off-screen above the player.
        if self.y >= ENEMY_BOSS_HOVER_Y and random.random() < self.fire_chance:
            bullets.append(Bullet(
                x=self.x,
                y=self.y + half,
                vy=ENEMY_BULLET_SPEED,   # Positive = moving DOWN.
                color=COLOR_ENEMY_BULLET,
                is_player_bullet=False,
            ))

    def take_damage(self, amount=1):
        """Subtract HP and return True if the enemy just died."""
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        half = self.size // 2
        now_ms = pygame.time.get_ticks()

        # ---- Outer hull: a wide, faceted "warship prow" pointing down --
        # instead of a simple triangle -- flatter shoulders and a jagged
        # underside read as heavier armor plating.
        body = [
            (cx,             cy + half),        # Bottom point (prow)
            (cx - half // 3, cy + half - 14),   # Prow shoulder (left)
            (cx - half,      cy - half + 10),   # Top-left wingtip
            (cx - half + 10, cy - half),        # Top-left shoulder
            (cx + half - 10, cy - half),        # Top-right shoulder
            (cx + half,      cy - half + 10),   # Top-right wingtip
            (cx + half // 3, cy + half - 14),   # Prow shoulder (right)
        ]
        draw_glow_polygon(surface, body, NEON_MAGENTA,
                           spread=4, layers=5, max_alpha=70)
        pygame.draw.polygon(surface, self.color, body)
        draw_neon_line(surface, body, NEON_MAGENTA, width=2, closed=True)

        # ---- Armor ribs: parallel neon trim lines across the hull ------
        for t in (0.35, 0.6, 0.8):
            y = cy - half + int(self.size * t)
            span = int(half * (1.0 - t * 0.6))
            draw_neon_line(
                surface,
                [(cx - span, y), (cx + span, y - 4)],
                NEON_MAGENTA_DIM, width=1,
            )

        # ---- Wing-mounted engine glows (pulse independently) -----------
        pulse_a = (math.sin(now_ms * 0.006) + 1) / 2
        pulse_b = (math.sin(now_ms * 0.006 + math.pi) + 1) / 2
        for (ex, ey), pulse in (
            ((cx - half + 6, cy - half + 14), pulse_a),
            ((cx + half - 6, cy - half + 14), pulse_b),
        ):
            radius = 3 + int(2 * pulse)
            glow_color = tuple(
                int(NEON_MAGENTA_DIM[i] + (NEON_MAGENTA[i] - NEON_MAGENTA_DIM[i]) * pulse)
                for i in range(3)
            )
            pygame.draw.circle(surface, glow_color, (ex, ey), radius + 3, width=1)
            pygame.draw.circle(surface, glow_color, (ex, ey), radius)

        # ---- Core "eye": a glowing, pulsing neon cockpit/reactor --------
        core_pulse = (math.sin(now_ms * 0.008) + 1) / 2
        core_radius = 5 + int(2 * core_pulse)
        draw_glow_polygon(
            surface,
            [
                (cx - core_radius, cy - half + 8 - core_radius),
                (cx + core_radius, cy - half + 8 - core_radius),
                (cx + core_radius, cy - half + 8 + core_radius),
                (cx - core_radius, cy - half + 8 + core_radius),
            ],
            NEON_MAGENTA, spread=3, layers=4, max_alpha=110,
        )
        pygame.draw.circle(surface, (30, 0, 30), (cx, cy - half + 8), core_radius + 2)
        pygame.draw.circle(surface, NEON_MAGENTA, (cx, cy - half + 8), core_radius, width=2)
        pygame.draw.circle(surface, NEON_WHITE, (cx, cy - half + 8), max(1, core_radius - 3))

        # ---- HP bar: thin neon health readout above the Boss ------------
        # Purely cosmetic, but reinforces "this is a big, important target".
        bar_w = self.size
        bar_h = 5
        bar_x = cx - bar_w // 2
        bar_y = cy - half - 16
        ratio = max(0.0, min(1.0, self.hp / ENEMY_BOSS_HP))
        pygame.draw.rect(surface, (40, 10, 40), (bar_x, bar_y, bar_w, bar_h), border_radius=2)
        pygame.draw.rect(surface, NEON_MAGENTA, (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=2)
        pygame.draw.rect(surface, NEON_MAGENTA_DIM, (bar_x, bar_y, bar_w, bar_h), width=1, border_radius=2)


# ---------------------------------------------------------------------
# Particle: a single dot in an explosion.
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# PowerUp: a temporary-effect pickup dropped by defeated enemies.
# ---------------------------------------------------------------------
class PowerUp:
    """A pickup that drifts downward and grants a timed effect on contact.

    `kind` is one of the POWERUP_KIND_* constants. The PowerUp itself
    doesn't track *when* the effect ends — that timer lives on the
    Player (see Player.activate_powerup), the same way Player already
    tracks its own invulnerability window with a `..._until_ms` field.
    This object's only job is to exist, fall, and be picked up.
    """
    _glyph_font = None  # Lazily created on first draw(); shared by all instances.

    def __init__(self, x, y, kind):
        self.kind = kind
        self.x = x
        self.y = y
        self.alive = True
        self.color = (
            COLOR_POWERUP_DOUBLE_SHOT if kind == POWERUP_KIND_DOUBLE_SHOT
            else COLOR_POWERUP_RAPID_FIRE
        )
        self.rect = pygame.Rect(0, 0, POWERUP_SIZE, POWERUP_SIZE)
        self.rect.center = (int(x), int(y))

    def update(self):
        self.y += POWERUP_FALL_SPEED
        self.rect.centery = int(self.y)
        if self.y - POWERUP_SIZE / 2 > SCREEN_HEIGHT:
            self.alive = False

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        half = POWERUP_SIZE // 2
        # A pulsing glowing diamond — the same "this is special" language
        # as the special-attack ammo icons in the HUD, so pickups read as
        # related to that system even though the mechanic differs.
        pulse = (math.sin(pygame.time.get_ticks() * 0.008) + 1) / 2
        r = half + int(2 * pulse)
        points = [
            (cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy),
        ]
        draw_glow_polygon(surface, points, self.color, spread=3, layers=3, max_alpha=100)
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, NEON_WHITE, points, width=1)

        # A tiny letter in the center as a legend-free hint at what it
        # does: "2" for double_shot, ">" (rapid) for rapid_fire. Cached
        # on the class so we're not building a new Font 60 times a
        # second per pickup on screen.
        if PowerUp._glyph_font is None:
            PowerUp._glyph_font = pygame.font.SysFont(None, 18)
        glyph = "2" if self.kind == POWERUP_KIND_DOUBLE_SHOT else ">"
        glyph_surf = PowerUp._glyph_font.render(glyph, True, (20, 20, 20))
        surface.blit(
            glyph_surf,
            (cx - glyph_surf.get_width() // 2, cy - glyph_surf.get_height() // 2),
        )


class Particle:
    """One spark of an explosion.

    Particles are intentionally simple — just position, velocity, and a
    countdown timer. When the timer hits zero, they're removed.
    """
    def __init__(self, x, y):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(EXPLOSION_SPEED_MIN, EXPLOSION_SPEED_MAX)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = EXPLOSION_LIFE_FRAMES
        # A tiny size variation makes the explosion look less uniform.
        self.size = random.randint(2, 4)
        # Slight color variation per particle.
        r = min(255, COLOR_EXPLOSION[0] + random.randint(-20, 20))
        g = min(255, COLOR_EXPLOSION[1] + random.randint(-30, 30))
        b = min(255, COLOR_EXPLOSION[2] + random.randint(-20, 20))
        self.color = (max(0, r), max(0, g), max(0, b))

    @property
    def alive(self):
        return self.life > 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        # A bit of "drag" so particles slow to a halt instead of flying off.
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= 1

    def draw(self, surface):
        # Particles fade out by shrinking near end-of-life.
        # (We could also fade alpha, but that's slower and not needed here.)
        s = self.size if self.life > 8 else max(1, self.size - 1)
        surface.fill(self.color, (int(self.x), int(self.y), s, s))


# ---------------------------------------------------------------------
# Game: the top-level state machine.
# ---------------------------------------------------------------------
class Game:
    """Owns every entity and the main loop's per-frame logic.

    Putting the loop body in methods keeps `main()` short and makes it
    easy for a beginner to find a specific feature (e.g. "where do
    collisions happen?" -> `_handle_collisions`).
    """
    # State constants — using plain strings keeps them readable when printed.
    STATE_START = "start"       # Title screen, before the run begins.
    STATE_PLAYING = "playing"
    STATE_PAUSED = "paused"
    STATE_GAME_OVER = "game_over"

    def __init__(self, screen, font_big, font_small):
        self.screen = screen
        self.font_big = font_big
        self.font_small = font_small
        self.reset()
        # Begin on the title screen rather than dropping straight into
        # gameplay -- reset() above still sets up a full, ready-to-play
        # world (stars, player, spawner timers), we just don't let
        # update() advance it until the player presses ENTER.
        self.state = Game.STATE_START

    def reset(self):
        """Start (or restart) a fresh game."""
        self.state = Game.STATE_PLAYING
        self.score = 0

        self.player = Player()
        self.player_bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.particles = []
        self.powerups = []
        self._boss_spawned = False
        self.level = 1
        # Edge-detection flag for the 'B' special-attack key -- see
        # _handle_continuous_input. Without this, holding B down would
        # fire (and consume ammo for) the special every single frame.
        self._b_key_was_held = False

        self.stars = [Star() for _ in range(NUM_STARS)]

        # Restore the level-1 sky palette in case a previous run advanced
        # to level 2 and left the (module-level) colors changed -- see
        # _advance_to_level_2. Without this, starting a new game after
        # beating a Boss would keep the level-2 sky.
        global COLOR_BG_TOP, COLOR_BG_BOTTOM
        COLOR_BG_TOP = _ORIGINAL_COLOR_BG_TOP
        COLOR_BG_BOTTOM = _ORIGINAL_COLOR_BG_BOTTOM

        # Spawn timing:
        now_ms = pygame.time.get_ticks()
        self.next_enemy_spawn_ms = now_ms + ENEMY_SPAWN_INTERVAL_MS
        self.current_spawn_interval_ms = ENEMY_SPAWN_INTERVAL_MS
        self.last_difficulty_ramp_ms = now_ms
        self.start_ms = now_ms

    # -----------------------------------------------------------------
    # Spawning
    # -----------------------------------------------------------------
    def _maybe_spawn_enemy(self, now_ms):
        if now_ms < self.next_enemy_spawn_ms:
            return
        kind = weighted_choice([
            ("basic", ENEMY_WEIGHT_BASIC),
            ("fast",  ENEMY_WEIGHT_FAST),
            ("tank",  ENEMY_WEIGHT_TANK),
        ])
        self.enemies.append(Enemy(kind))
        # Schedule the next spawn with a little randomness.
        jitter = random.randint(-ENEMY_SPAWN_JITTER_MS, ENEMY_SPAWN_JITTER_MS)
        self.next_enemy_spawn_ms = (
            now_ms + max(50, self.current_spawn_interval_ms + jitter)
        )

    def _maybe_ramp_difficulty(self, now_ms):
        # Every DIFFICULTY_RAMP_SECONDS, shrink the spawn interval.
        if now_ms - self.last_difficulty_ramp_ms < DIFFICULTY_RAMP_SECONDS * 1000:
            return
        self.last_difficulty_ramp_ms = now_ms
        new_interval = self.current_spawn_interval_ms * DIFFICULTY_RAMP_FACTOR
        self.current_spawn_interval_ms = max(
            ENEMY_SPAWN_INTERVAL_MIN_MS, new_interval
        )

    def _spawn_explosion(self, x, y):
        for _ in range(EXPLOSION_PARTICLES):
            self.particles.append(Particle(x, y))

    # -----------------------------------------------------------------
    # Input
    # -----------------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Start screen -> gameplay
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.state == Game.STATE_START:
                self.state = Game.STATE_PLAYING
                self.start_ms = pygame.time.get_ticks()  # Restart the HUD hint timer too.
            # Pause toggling
            if event.key == pygame.K_p and self.state == Game.STATE_PLAYING:
                self.state = Game.STATE_PAUSED
            elif event.key == pygame.K_p and self.state == Game.STATE_PAUSED:
                self.state = Game.STATE_PLAYING
            # Restart after game over
            elif event.key == pygame.K_r and self.state == Game.STATE_GAME_OVER:
                self.reset()

    def _handle_continuous_input(self, now_ms):
        keys = pygame.key.get_pressed()
        self.player.update(keys, now_ms)
        # Holding Space or Z = continuous fire (rate-limited by cooldown).
        if keys[pygame.K_SPACE] or keys[pygame.K_z]:
            self.player.shoot(self.player_bullets, now_ms)

        # Special attack on 'B'. keys[] is a snapshot of "is this key down
        # right now", so if we fired every frame it was held, one long
        # press would drain all 3 charges almost instantly. We only fire
        # on the frame the key transitions from up -> down (the "rising
        # edge"), then wait for it to be released before it can fire
        # again -- exactly like a single key-press event, but read here
        # via polling instead of pygame's event queue.
        b_key_held = keys[pygame.K_b]
        if b_key_held and not self._b_key_was_held:
            self.player.use_special(self.player_bullets, now_ms)
        self._b_key_was_held = b_key_held

    # -----------------------------------------------------------------
    # Per-frame update
    # -----------------------------------------------------------------
    def update(self):
        if self.state == Game.STATE_START:
            # Keep the starfield drifting behind the title text so the
            # title screen doesn't feel like a frozen, static image.
            for star in self.stars:
                star.update()
            return

        if self.state != Game.STATE_PLAYING:
            return  # Pause and game-over freeze the world.

        now_ms = pygame.time.get_ticks()

        # 1) Background
        for star in self.stars:
            star.update()

        # 2) Input + player movement / shooting
        self._handle_continuous_input(now_ms)

        # 3) Bullets
        for b in self.player_bullets:
            b.update()
        for b in self.enemy_bullets:
            b.update()

        # 4) Enemies
        self._maybe_ramp_difficulty(now_ms)
        self._maybe_spawn_enemy(now_ms)
        for e in self.enemies:
            e.update(self.enemy_bullets)

        # 5) Particles
        for p in self.particles:
            p.update()

        # 5b) Power-ups (falling pickups dropped by defeated enemies)
        for pu in self.powerups:
            pu.update()

        # 6) Collisions
        self._handle_collisions(now_ms)

        # 7) Cull dead objects.
        # Doing this *after* collision keeps the per-frame logic tidy:
        # collisions just flip `alive` flags or call hit/take_damage.
        self.player_bullets = [b for b in self.player_bullets if b.alive]
        self.enemy_bullets  = [b for b in self.enemy_bullets  if b.alive]
        self.enemies        = [e for e in self.enemies        if e.alive]
        self.particles      = [p for p in self.particles      if p.alive]
        self.powerups       = [pu for pu in self.powerups     if pu.alive]

        # 8) Game over check
        if self.player.lives <= 0:
            self.state = Game.STATE_GAME_OVER

    def _handle_collisions(self, now_ms):
        # --- Player bullets vs enemies --------------------------------
        # rect-vs-rect collision is plenty for an arcade shooter; no need
        # for pixel-perfect masks.
        for bullet in self.player_bullets:
            if not bullet.alive:
                continue
            for enemy in self.enemies:
                if not enemy.alive:
                    continue
                if bullet.rect.colliderect(enemy.rect):
                    bullet.alive = False
                    died = enemy.take_damage(bullet.damage)
                    if died:
                        self._handle_enemy_death(enemy, full_score=True)
                    break  # One bullet, one hit.

        # --- Enemy bullets vs player ----------------------------------
        for bullet in self.enemy_bullets:
            if not bullet.alive:
                continue
            if bullet.rect.colliderect(self.player.rect):
                bullet.alive = False
                if self.player.hit(now_ms):
                    self._spawn_explosion(self.player.x, self.player.y)

        # --- Enemies vs player (ramming) ------------------------------
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            if enemy.rect.colliderect(self.player.rect):
                if self.player.hit(now_ms):
                    self._spawn_explosion(self.player.x, self.player.y)
                # Ramming kills the enemy too — feels fair and clears the
                # screen — but only for half score, same as a normal kill
                # would be worth if you'd chipped it down instead of
                # ramming it. Goes through the same death handling as a
                # bullet kill so a rammed Boss still grants its reward.
                enemy.alive = False
                self._handle_enemy_death(enemy, full_score=False)

        # --- Player vs power-ups ---------------------------------------
        for pu in self.powerups:
            if not pu.alive:
                continue
            if pu.rect.colliderect(self.player.rect):
                pu.alive = False
                self.player.activate_powerup(pu.kind, now_ms)

    def _handle_enemy_death(self, enemy, full_score=True):
        """Shared death handling for both bullet kills and ramming.

        Centralizing this means the Boss-defeat reward and the regular
        power-up drop both trigger no matter *how* the enemy died,
        instead of only being wired up in one of the two collision paths.
        """
        self.score += enemy.score if full_score else enemy.score // 2
        self._spawn_explosion(enemy.x, enemy.y)

        if isinstance(enemy, Boss):
            self._on_boss_defeated()
            return  # Bosses don't drop the regular temporary power-ups.

        # Only non-Boss kills can trigger the *next* Boss to spawn, and
        # only non-Boss kills can drop a temporary power-up.
        if self.score >= 1000 and not self._boss_spawned:
            self.enemies.append(Boss())
            self._boss_spawned = True

        if random.random() < POWERUP_DROP_CHANCE:
            kind = random.choice(POWERUP_KINDS)
            self.powerups.append(PowerUp(enemy.x, enemy.y, kind))

    def _on_boss_defeated(self):
        """Boss reward: a permanent, stacking speed buff + level 2 sky.

        The speed buff stacks additively (see Player.effective_speed) and
        is completely independent from the timed power-ups — a player
        could have rapid_fire active, pick up double_shot, AND carry a
        permanent speed bonus all at the same time; they're tracked in
        totally separate places on Player (a float vs. a dict of timers).
        """
        self.player.permanent_speed_bonus += BOSS_PERMANENT_SPEED_BONUS
        self.level += 1
        self._advance_to_level_2()

    def _advance_to_level_2(self):
        """Swap the sky gradient to the level-2 palette.

        COLOR_BG_TOP / COLOR_BG_BOTTOM are read directly by
        _draw_background() as module-level globals, so we reassign them
        here with `global` rather than threading a "current palette"
        value through the draw call — the smallest change that makes
        the existing background code pick up the new colors automatically.
        """
        global COLOR_BG_TOP, COLOR_BG_BOTTOM
        COLOR_BG_TOP = LEVEL_2_COLOR_BG_TOP
        COLOR_BG_BOTTOM = LEVEL_2_COLOR_BG_BOTTOM

    # -----------------------------------------------------------------
    # Drawing
    # -----------------------------------------------------------------
    def draw(self):
        self._draw_background()

        for star in self.stars:
            star.draw(self.screen)

        if self.state == Game.STATE_START:
            # Title screen: background + drifting stars are already
            # drawn above; layer the logo/prompt on top and stop --
            # no player, enemies, or HUD exist meaningfully yet.
            self._draw_start_screen()
            return

        for e in self.enemies:
            e.draw(self.screen)

        for pu in self.powerups:
            pu.draw(self.screen)

        for b in self.player_bullets:
            b.draw(self.screen)
        for b in self.enemy_bullets:
            b.draw(self.screen)

        # Player on top of bullets so it's never hidden by its own shots.
        now_ms = pygame.time.get_ticks()
        self.player.draw(self.screen, now_ms)

        for p in self.particles:
            p.draw(self.screen)

        self._draw_hud()

        # Overlay messages
        if self.state == Game.STATE_PAUSED:
            self._draw_center_message("PAUSED", "Press P to resume")
        elif self.state == Game.STATE_GAME_OVER:
            self._draw_center_message(
                "GAME OVER",
                f"Final score: {self.score}    Press R to restart",
            )

    def _draw_start_screen(self):
        """Title screen shown before STATE_PLAYING begins.

        Reuses the same starfield background as gameplay so the game
        doesn't feel like two disconnected apps stitched together, then
        layers a glowing title, a small preview of the player ship, and
        a blinking "press ENTER" prompt on top.
        """
        now_ms = pygame.time.get_ticks()

        # Dark veil so text stays readable over busy stars, same trick
        # used by _draw_center_message for pause/game-over overlays.
        veil = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 90))
        self.screen.blit(veil, (0, 0))

        # --- Title, with a soft neon glow behind the text -----------------
        title_surf = self.font_big.render(START_TITLE_TEXT, True, NEON_WHITE)
        title_x = SCREEN_WIDTH // 2 - title_surf.get_width() // 2
        title_y = SCREEN_HEIGHT // 3 - title_surf.get_height() // 2

        glow_surf = self.font_big.render(START_TITLE_TEXT, True, NEON_CYAN)
        glow_surf.set_alpha(70)
        for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            self.screen.blit(glow_surf, (title_x + ox, title_y + oy))
        self.screen.blit(title_surf, (title_x, title_y))

        # --- A small preview of the redesigned ship, hovering with a ------
        # gentle bob so the title screen feels alive.
        preview_x = SCREEN_WIDTH // 2
        preview_y = title_y + title_surf.get_height() + 70
        preview_y += int(6 * math.sin(now_ms * 0.003))
        # Player.draw() reads position from the instance itself, so we
        # temporarily move the real player here, draw it, then put it back
        # -- avoids needing a second throwaway Player just for the preview.
        # We also zero out its spawn invulnerability window so the preview
        # doesn't flicker/blink (Player.draw skips drawing every other
        # ~80ms while invulnerable) -- that flicker is meant to read as
        # "just respawned", which is a confusing thing for a title screen
        # to imply.
        original_x, original_y = self.player.x, self.player.y
        original_invuln_until = self.player.invuln_until_ms
        self.player.x, self.player.y = preview_x, preview_y
        self.player.invuln_until_ms = 0
        self.player.draw(self.screen, now_ms)
        self.player.x, self.player.y = original_x, original_y
        self.player.invuln_until_ms = original_invuln_until

        # --- Blinking "press ENTER" prompt --------------------------------
        if (now_ms // START_BLINK_MS) % 2 == 0:
            prompt_surf = self.font_small.render(START_PROMPT_TEXT, True, NEON_CYAN)
            self.screen.blit(
                prompt_surf,
                (SCREEN_WIDTH // 2 - prompt_surf.get_width() // 2,
                 preview_y + 60),
            )

        # --- Tiny control reminder at the bottom, always visible ----------
        hint_surf = self.font_small.render(
            "Move: arrows/WASD   Shoot: Space/Z", True, COLOR_HUD_DIM,
        )
        self.screen.blit(
            hint_surf,
            (SCREEN_WIDTH // 2 - hint_surf.get_width() // 2,
             SCREEN_HEIGHT - HUD_MARGIN - hint_surf.get_height()),
        )


    def _draw_background(self):
        # A very simple top-to-bottom gradient using horizontal lines.
        # For a flat color, replace this whole method with screen.fill(...).
        for y in range(SCREEN_HEIGHT):
            t = y / max(1, SCREEN_HEIGHT - 1)  # 0.0 .. 1.0
            r = int(COLOR_BG_TOP[0] + (COLOR_BG_BOTTOM[0] - COLOR_BG_TOP[0]) * t)
            g = int(COLOR_BG_TOP[1] + (COLOR_BG_BOTTOM[1] - COLOR_BG_TOP[1]) * t)
            b = int(COLOR_BG_TOP[2] + (COLOR_BG_BOTTOM[2] - COLOR_BG_TOP[2]) * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    def _draw_hud(self):
        # Score (top-left)
        score_surf = self.font_small.render(
            f"SCORE  {self.score:07d}", True, COLOR_HUD_TEXT
        )
        self.screen.blit(score_surf, (HUD_MARGIN, HUD_MARGIN))

        # Special ammo (below the score, top-left) — a small diamond icon
        # per charge, colored to match the special bullets themselves so
        # the HUD and the projectiles read as "the same thing".
        ammo_y = HUD_MARGIN + score_surf.get_height() + 6
        ammo_label = self.font_small.render("SPECIAL", True, COLOR_HUD_DIM)
        self.screen.blit(ammo_label, (HUD_MARGIN, ammo_y))
        icon_start_x = HUD_MARGIN + ammo_label.get_width() + 8
        max_ammo = PLAYER_SPECIAL_START_AMMO
        for i in range(max_ammo):
            icon_x = icon_start_x + i * 16
            icon_cy = ammo_y + ammo_label.get_height() // 2
            filled = i < self.player.special_ammo
            color = COLOR_PLAYER_SPECIAL_BULLET if filled else (60, 55, 75)
            # A tiny diamond (rotated square) reads as "ammo charge" more
            # distinctly than another triangle, which is already used for
            # lives just below.
            points = [
                (icon_x + 5, icon_cy - 6),
                (icon_x + 10, icon_cy),
                (icon_x + 5, icon_cy + 6),
                (icon_x, icon_cy),
            ]
            pygame.draw.polygon(self.screen, color, points)
            if filled:
                pygame.draw.polygon(self.screen, NEON_WHITE, points, width=1)

        # Lives (top-right) — one tiny ship icon per life.
        lives_label = self.font_small.render("LIVES", True, COLOR_HUD_DIM)
        self.screen.blit(
            lives_label,
            (SCREEN_WIDTH - HUD_MARGIN - lives_label.get_width() - 8 - 18 * self.player.lives,
             HUD_MARGIN),
        )
        for i in range(self.player.lives):
            icon_x = SCREEN_WIDTH - HUD_MARGIN - (i + 1) * 18
            icon_y = HUD_MARGIN + 4
            # Mini triangle in the player's color.
            points = [
                (icon_x + 7,  icon_y),
                (icon_x,      icon_y + 14),
                (icon_x + 14, icon_y + 14),
            ]
            pygame.draw.polygon(self.screen, COLOR_PLAYER, points)

        # Level indicator (below lives, top-right) — only interesting once
        # it's changed from 1, but always shown for consistency.
        level_surf = self.font_small.render(f"LEVEL {self.level}", True, COLOR_HUD_DIM)
        self.screen.blit(
            level_surf,
            (SCREEN_WIDTH - HUD_MARGIN - level_surf.get_width(),
             HUD_MARGIN + lives_label.get_height() + 6),
        )

        # Active temporary power-ups (bottom-right) — name + a countdown
        # in seconds, so the player knows exactly how long they've got
        # left rather than being surprised when it wears off.
        now_ms = pygame.time.get_ticks()
        active = [
            (kind, expiry) for kind, expiry in self.player.active_powerups.items()
            if now_ms < expiry
        ]
        for row, (kind, expiry) in enumerate(active):
            remaining_s = (expiry - now_ms) / 1000.0
            label = "DOUBLE SHOT" if kind == POWERUP_KIND_DOUBLE_SHOT else "RAPID FIRE"
            color = COLOR_POWERUP_DOUBLE_SHOT if kind == POWERUP_KIND_DOUBLE_SHOT else COLOR_POWERUP_RAPID_FIRE
            surf = self.font_small.render(f"{label}  {remaining_s:0.1f}s", True, color)
            self.screen.blit(
                surf,
                (SCREEN_WIDTH - HUD_MARGIN - surf.get_width(),
                 SCREEN_HEIGHT - HUD_MARGIN - surf.get_height() * (row + 1) - row * 4),
            )

        # Hint line (bottom-left) — only while playing, fades after a bit.
        elapsed_ms = pygame.time.get_ticks() - self.start_ms
        if self.state == Game.STATE_PLAYING and elapsed_ms < 4000:
            hint = self.font_small.render(
                "Move: arrows/WASD   Shoot: Space/Z   Special: B   Pause: P",
                True, COLOR_HUD_DIM,
            )
            self.screen.blit(
                hint,
                (HUD_MARGIN, SCREEN_HEIGHT - HUD_MARGIN - hint.get_height()),
            )



    def _draw_center_message(self, big_text, small_text):
        # Translucent dark veil makes overlay text readable.
        veil = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 140))  # The 4th value is alpha (0..255).
        self.screen.blit(veil, (0, 0))

        big_surf = self.font_big.render(big_text, True, COLOR_HUD_TEXT)
        small_surf = self.font_small.render(small_text, True, COLOR_HUD_TEXT)

        self.screen.blit(
            big_surf,
            (SCREEN_WIDTH // 2 - big_surf.get_width() // 2,
             SCREEN_HEIGHT // 2 - big_surf.get_height()),
        )
        self.screen.blit(
            small_surf,
            (SCREEN_WIDTH // 2 - small_surf.get_width() // 2,
             SCREEN_HEIGHT // 2 + 8),
        )


# ---------------------------------------------------------------------
# main(): set up Pygame, then run the loop until the user quits.
# ---------------------------------------------------------------------
def main():
    # pygame.init initializes ALL pygame submodules (display, font, ...).
    # If you're worried about startup time, you can init them individually.
    pygame.init()

    # Create the window. The flags argument (3rd positional) can include
    # pygame.RESIZABLE or pygame.FULLSCREEN if you want to experiment.
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    # The Clock keeps the frame rate steady. tick(FPS) sleeps just long
    # enough to hold the game at FPS frames per second.
    clock = pygame.time.Clock()

    # We use the default system font (None) so we don't need a .ttf file.
    # Try changing the family name to e.g. "consolas" or "couriernew" for
    # a different look — pygame will fall back to a default if not found.
    font_small = pygame.font.SysFont(None, HUD_FONT_SIZE)
    font_big   = pygame.font.SysFont(None, HUD_FONT_SIZE * 3, bold=True)

    game = Game(screen, font_big, font_small)

    # The main loop. This pattern — events, update, draw, flip — is the
    # backbone of essentially every Pygame game.
    running = True
    while running:
        # 1) Process discrete events (key presses, window close, ...).
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            else:
                game.handle_event(event)

        # 2) Update the game state.
        game.update()

        # 3) Draw the new frame.
        game.draw()

        # 4) Show what we drew.
        pygame.display.flip()

        # 5) Wait so we hit (at most) FPS frames per second.
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


# Standard "only run when executed directly, not when imported" idiom.
if __name__ == "__main__":
    main()
