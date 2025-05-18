#NINJA SCROLL by LARISSA VIEIRA
#-----CONTROLS-----
# A = move left / D = move right / Z = attack / SPACE = Jump
# Atividade desenvolvida para teste de tutores da KodLand


import random

WIDTH, HEIGHT = 1024, 640

STATE_MENU, STATE_PLAY, STATE_OVER, STATE_WIN = "menu", "play", "over", "win"
state = STATE_MENU

music_on, sounds_on, pending_win = True, True, False

menu_btns = [
    {"label": "START", "rect": Rect(412, 250, 200, 60), "action": "start"},
    {"label": lambda: "MUSIC/SOUND ON" if music_on else "MUSIC/SOUND OFF", "rect": Rect(362, 340, 300, 60), "action": "toggle_audio",},
    {"label": "EXIT", "rect": Rect(462, 430, 100, 60), "action": "exit"}
]
platforms = [Rect(0, HEIGHT-60, WIDTH, 62)]

class Hero:
    def __init__(self):
        self.x, self.y, self.w, self.h = 120, HEIGHT-124, 56, 64
        self.vy, self.no_chao = 0, False
        self.dir, self.state = False, "idle"
        self.fidx, self.ftmr = 0, 0
        self.attack_anim, self.attack_idx, self.attack_tmr = False, 0, 0
        self.hurt_anim, self.hurt_tmr, self.morto = False, 0, False
        self.complete_anim, self.complete_tmr = False, 0
        self.img = "idle_0"
        self.lives = 3  # <- O herói tem tres vidas!

    def rect(self): return Rect(self.x, self.y, self.w, self.h)

    def update(self):
        if self.morto: return
        if self.hurt_anim:
            self.hurt_tmr += 1
            self.img = "hurt_1"
            if self.hurt_tmr > 30: self.hurt_anim = False
            return
        if self.complete_anim:
            self.complete_tmr += 1
            self.img = "complete"
            return
        if self.attack_anim:
            self.attack_tmr += 1
            if self.attack_tmr % 6 == 0: self.attack_idx += 1
            if self.attack_idx >= 3: self.attack_anim, self.attack_idx, self.attack_tmr = False, 0, 0
            self.img = f"attack_{self.attack_idx%3}"
            return
        mv = False
        if keyboard.d: self.x += 5; self.dir = False; mv = True
        if keyboard.a: self.x -= 5; self.dir = True; mv = True
        if keyboard.space and self.no_chao: self.vy = -15
        if keyboard.z and self.no_chao and not self.attack_anim:
            self.attack_anim, self.attack_idx, self.attack_tmr = True, 0, 0
            if sounds_on: sounds.attack.play(); return
        self.vy = min(self.vy+1, 18); self.y += self.vy; self.no_chao = False
        for p in platforms:
            if self.rect().colliderect(p) and self.vy >= 0:
                self.y = p.top - self.h
                self.vy, self.no_chao = 0, True
        self.x = max(0, min(WIDTH-self.w, self.x))
        if self.y > HEIGHT and not self.hurt_anim and not self.complete_anim and not self.morto:
            self.take_damage()  # Se cair, também perde vida
        self.animar(mv)

    def animar(self, mv):
        self.ftmr += 1
        if self.ftmr >= 6: self.ftmr, self.fidx = 0, self.fidx+1
        if not self.no_chao:
            self.img = f"jump_{self.fidx%4}"
        elif mv:
            self.img = f"run_{self.fidx%6}"
        else:
            self.img = f"idle_{self.fidx%3}"

    def draw(self):
        a = Actor(self.img, (self.x+self.w//2, self.y+self.h//2))
        a.flip_x = self.dir
        a.draw()

    def take_damage(self):
        if self.hurt_anim or self.morto: return
        self.lives -= 1
        self.hurt_anim, self.hurt_tmr = True, 0
        if self.lives <= 0:
            self.morto = True

    def start_hurt(self): self.take_damage()
    def start_complete(self): self.complete_anim, self.complete_tmr = True, 0

class Enemy:
    def __init__(self, x, y):
        self.x, self.y, self.w, self.h = x, y, 56, 64
        self.vx = random.choice([-2,2]); self.left, self.right = x-60, x+60
        self.anim_idx, self.anim_tmr = 0, 0
        self.dir = self.vx < 0; self.hp = 2
        self.hurt_tmr, self.state = 0, "run"
        self.dying, self.dead = False, False
        self.attack_anim, self.attack_idx, self.attack_tmr, self.cool, self.has_hit = False, 0, 0, 0, False

    def rect(self): return Rect(self.x, self.y, self.w, self.h)

    def update(self):
        if self.dead: return
        if self.dying: self.hurt_tmr += 1; self.state = "hurt"
        if self.dying and self.hurt_tmr > 20: self.dead = True; return
        if self.state == "hurt":
            self.hurt_tmr += 1
            if self.hurt_tmr > 20:
                if self.hp <= 0: self.dying = True
                self.state, self.hurt_tmr = "run", 0
            return
        if self.cool > 0: self.cool -= 1
        if self.attack_anim:
            self.attack_tmr += 1
            if self.attack_tmr % 6 == 0: self.attack_idx += 1
            if self.attack_idx >= 8:
                self.attack_anim, self.attack_idx, self.attack_tmr = False, 0, 0
                self.cool, self.has_hit = 60, False
            return
        dist = abs(hero.x - self.x)
        if not self.attack_anim and self.cool == 0 and dist < 60 and hero.y == self.y and not hero.morto:
            self.attack_anim, self.attack_idx, self.attack_tmr, self.has_hit = True, 0, 0, False
            return
        self.x += self.vx
        if self.x < self.left or self.x > self.right:
            self.vx = -self.vx; self.dir = self.vx < 0
        self.anim_tmr += 1
        if self.anim_tmr > 6: self.anim_idx, self.anim_tmr = (self.anim_idx+1)%6, 0

    def draw(self):
        if self.dead: return
        if self.dying or self.state == "hurt": img = "ehurt_1"
        elif self.attack_anim: img = f"eattack_{self.attack_idx%8}"
        else: img = f"erun_{self.anim_idx%6}"
        a = Actor(img, (self.x+self.w//2, self.y+self.h//2))
        a.flip_x = self.dir
        a.draw()

    def take_damage(self):
        if not self.dead and not self.dying:
            self.hp -= 1; self.state, self.hurt_tmr = "hurt", 0
            if sounds_on: sounds.enemy_damage.play()

class Item:
    def __init__(self, x, y):
        self.x, self.y, self.w, self.h, self.collected, self.frame, self.timer = x, y, 40, 40, False, 0, 0
    def rect(self): return Rect(self.x, self.y, self.w, self.h)
    def draw(self):
        if not self.collected:
            self.timer += 1
            if self.timer >= 12: self.frame, self.timer = (self.frame + 1) % 2, 0
            screen.blit(f"item{self.frame}", (self.x, self.y))

def reset_game():
    global hero, enemies, item, state, pending_win
    hero = Hero()
    enemies = [Enemy(WIDTH//3, HEIGHT-124), Enemy(2*WIDTH//3, HEIGHT-124)]
    item = Item(WIDTH-80, HEIGHT-110)
    state, pending_win = STATE_PLAY, False
    music.play("fase1") if music_on else music.stop()

def update():
    global state, pending_win
    if state == STATE_PLAY:
        hero.update()
        for e in enemies: e.update()
        # Herói ataca inimigo (normal)
        for e in enemies:
            if not e.dead and hero.rect().colliderect(e.rect()):
                if hero.attack_anim and e.state != "hurt" and not e.dying:
                    e.take_damage()
        # Inimigo só causa dano durante a animação de ataque, em qualquer frame
        for e in enemies:
            if (not e.dead and not e.dying and e.attack_anim and
                hero.rect().colliderect(e.rect()) and not hero.hurt_anim and not hero.complete_anim and
                not hero.morto and not e.has_hit):
                hero.take_damage(); e.has_hit = True
                if sounds_on: sounds.damage.play()
        if not item.collected and hero.rect().colliderect(item.rect()):
            item.collected = True; hero.start_complete()
            if sounds_on: sounds.complete.play(); pending_win = True
        if hero.morto: state = STATE_OVER; music.stop()
        if pending_win and hero.complete_anim and hero.complete_tmr > 40:
            pending_win, state = False, STATE_WIN; music.stop()

def draw():
    screen.clear()
    if state == STATE_MENU:
        screen.blit("fundo_menu", (0,0))
        screen.draw.text("NINJA SCROLL", center=(WIDTH//2, 120), fontsize=80, color=(255,255,64), shadow=(2,2), fontname="ninja")
        for btn in menu_btns: draw_btn(btn)
    elif state == STATE_PLAY:
        screen.blit("fundo01", (0, 0))
        for plat in platforms:
            screen.draw.filled_rect(plat, (72, 61, 139))
            screen.draw.rect(plat, (48, 38, 90))
        # Exibe vidas (corações) no canto superior esquerdo
        for i in range(hero.lives):
            screen.blit("coracao", (24 + i * 40, 24))
        item.draw(); hero.draw()
        for e in enemies: e.draw()
    elif state == STATE_OVER:
        screen.fill((30, 0, 0))
        screen.draw.text("GAME OVER", center=(WIDTH//2, 200), fontsize=64, color="red")
        screen.draw.text("Click to Restart", center=(WIDTH//2, 320), fontsize=40, color="white")
    elif state == STATE_WIN:
        screen.fill((0, 50, 100))
        screen.draw.text("Congratulations!", center=(WIDTH//2, 200), fontsize=56, color="yellow", fontname="unageo-regular")
        screen.draw.text("You found the Scroll", center=(WIDTH//2, 280), fontsize=40, color="white", fontname="unageo-regular")
        screen.draw.text("Click to come back to menu", center=(WIDTH//2, 400), fontsize=32, color="white", fontname="unageo-regular")

def draw_btn(btn):
    rect, label = btn["rect"], btn["label"]
    if callable(label): label = label()
    screen.draw.filled_rect(rect, (110, 90, 150))
    screen.draw.rect(rect, (70, 40, 110))
    screen.draw.text(label, center=rect.center, fontsize=32, color="white")

def on_mouse_down(pos):
    global state, music_on, sounds_on
    if state == STATE_MENU:
        for btn in menu_btns:
            if btn["rect"].collidepoint(pos):
                if sounds_on: sounds.menu_click.play()
                if btn["action"] == "start": reset_game()
                elif btn["action"] == "toggle_audio":
                    music_on, sounds_on = not music_on, not sounds_on
                    music.play("musica_menu") if music_on else music.stop()
                elif btn["action"] == "exit": exit()
    elif state == STATE_OVER: reset_game()
    elif state == STATE_WIN:
        state = STATE_MENU
        music.play("musica_menu") if music_on else music.stop()

def on_key_down(key):
    if state == STATE_MENU and key == keys.RETURN: reset_game()
def on_key_up(key): pass
def on_start(): music.play("musica_menu") if music_on else music.stop()
on_start()