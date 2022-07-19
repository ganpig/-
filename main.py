import os
import sys
import time
import tkinter
import tkinter.colorchooser
from configparser import ConfigParser

import easygui
import pygame

WINDOW_SIZE = (1000, 600)
WINDOW_TITLE = '抛物线演示器'
SIDEBAR_LEFT = WINDOW_SIZE[0]-400
SIDEBAR_MID = (SIDEBAR_LEFT+WINDOW_SIZE[0])//2
try:
    RESOURCES = sys._MEIPASS
except:
    RESOURCES = '.'


def my_round(x, n=0):
    x = round(x, n) if n else round(x)
    return int(x) if int(x) == x else x


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def askcolor(default, title):
    tk = tkinter.Tk()
    tk.withdraw()
    color = tkinter.colorchooser.askcolor(default, title=title)[1]
    tk.destroy()
    return color


class Window:
    def __init__(self, cp: ConfigParser) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption(WINDOW_TITLE)
        self.fonts = [[pygame.font.Font(os.path.join(
            RESOURCES, m), 18+i*8) for i in range(4)] for m in ('FZFWQingYinTiJWL.ttf', 'CascadiaCode.ttf')]
        self.mouse_pos = (0, 0)
        self.cp = cp

        if not self.cp.has_section('window'):
            self.cp.add_section('window')

        # 设置窗口背景
        self.background = self.get_or_set('background', '#000000')
        if self.background.startswith('#'):
            self.apply_bg_mode('color')
        else:
            self.apply_bg_mode('image')

        # 设置主题颜色
        try:
            self.main_color_hex = self.get_or_set('main_color', '#ffffff')
            self.main_color = [int(self.main_color_hex[i:i+2], 16)
                               for i in range(1, 7, 2)]
        except:
            self.main_color = (255, 255, 255)
            self.cp.set('window', 'main_color', '#ffffff')

        # 设置网格颜色
        try:
            self.grid_color_hex = self.get_or_set('grid_color', '#00ffff')
            self.grid_color = [int(self.grid_color_hex[i:i+2], 16)
                               for i in range(1, 7, 2)]
        except:
            self.grid_color = (0, 255, 255)
            self.cp.set('window', 'grid_color', '#00ffff')

        # 设置网格不透明度
        try:
            self.grid_alpha = int(self.get_or_set('grid_alpha', '100'))
            assert(0 <= self.grid_alpha <= 255)
        except:
            self.grid_alpha = 100
            self.cp.set('window', 'grid_alpha', '100')

        # 设置坐标轴颜色
        try:
            self.axis_color_hex = self.get_or_set('axis_color', '#00ffff')
            self.axis_color = [int(self.axis_color_hex[i:i+2], 16)
                               for i in range(1, 7, 2)]
        except:
            self.axis_color = (0, 255, 255)
            self.cp.set('window', 'axis_color', '#00ffff')

        # 设置坐标轴不透明度
        try:
            self.axis_alpha = int(self.get_or_set('axis_alpha', '255'))
            assert(0 <= self.axis_alpha <= 255)
        except:
            self.axis_alpha = 255
            self.cp.set('window', 'axis_alpha', '255')

        self.cp.write(open('config.ini', 'w', encoding='utf-8'))

    def get_or_set(self, key: str, default: str) -> str:
        if self.cp.has_option('window', key):
            return self.cp.get('window', key)
        else:
            self.cp.set('window', key, default)
            return default

    def apply_bg_mode(self, mode: str) -> None:
        """
        应用背景模式。
        """
        if mode == 'color':
            self.bg_mode = 'color'
            try:
                self.bg_color = tuple(int(self.background[i:i+2], 16)
                                      for i in range(1, 7, 2))
            except:
                self.background = '#000000'
                self.bg_color = (0, 0, 0)
                self.cp.set('window', 'background', '#000000')
        elif mode == 'image':
            try:
                self.bg_image = pygame.transform.scale(
                    pygame.image.load(self.background), WINDOW_SIZE)
                self.bg_image_with_mask = self.bg_image.copy()
                self.bg_color = (0, 0, 0)
                self.bg_mode = 'image'
                try:
                    self.mask_alpha = int(self.get_or_set('mask_alpha', '200'))
                    assert(0 <= self.mask_alpha <= 255)
                except:
                    self.mask_alpha = 200
                    self.cp.set('window', 'mask_alpha', '200')
                mask = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
                mask.fill((0, 0, 0, self.mask_alpha))
                self.bg_image_with_mask.blit(mask, (0, 0))
            except:
                self.bg_mode = 'color'
                self.background = '#000000'
                self.bg_color = (0, 0, 0)
                self.cp.set('window', 'background', '#000000')

    def change_bg_mode(self) -> None:
        """
        切换背景模式。
        """
        exec(f'self.set_bg_{"image" if self.bg_mode=="color" else "color"}()')

    def set_bg(self) -> None:
        """
        修改背景。
        """
        exec(f'self.set_bg_{self.bg_mode}()')

    def set_bg_color(self) -> None:
        """
        设置背景颜色。
        """
        color = askcolor(self.bg_color, '选择背景颜色')
        if color:
            self.background = color
            self.apply_bg_mode('color')
            self.cp.set('window', 'background', color)
            self.cp.write(open('config.ini', 'w', encoding='utf-8'))

    def set_bg_image(self) -> None:
        """
        设置背景图片。
        """
        image = easygui.fileopenbox('选择背景图片')
        if image:
            try:
                pygame.image.load(image)
                self.background = image
                self.apply_bg_mode('image')
                self.cp.set('window', 'background', image)
                self.cp.write(open('config.ini', 'w', encoding='utf-8'))
            except:
                self.error('无法加载所选的背景图片，请重新选择。')
                self.set_bg_image()

    def set_main_color(self) -> None:
        """
        设置主题颜色。
        """
        color = askcolor(self.main_color_hex, '选择主题颜色')
        if color:
            self.main_color_hex = color
            self.main_color = [int(color[i:i+2], 16)
                               for i in range(1, 7, 2)]
            self.cp.set('window', 'main_color', color)
            self.cp.write(open('config.ini', 'w', encoding='utf-8'))

    def set_mask_alpha(self, value: float) -> None:
        """
        设置蒙版不透明度（参数为小数）。
        """
        self.mask_alpha = int(value * 255)
        self.cp.set('window', 'mask_alpha', str(self.mask_alpha))
        self.cp.write(open('config.ini', 'w', encoding='utf-8'))
        self.bg_image_with_mask = self.bg_image.copy()
        mask = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        mask.fill((0, 0, 0, self.mask_alpha))
        self.bg_image_with_mask.blit(mask, (0, 0))

    def draw_frame(self) -> None:
        """
        绘制窗口框架。
        """
        if self.bg_mode == 'color':
            self.screen.fill(self.bg_color)
        elif self.bg_mode == 'image':
            self.screen.blit(self.bg_image_with_mask, (0, 0))
        pygame.draw.line(self.screen, self.main_color,
                         (SIDEBAR_LEFT, 0), (SIDEBAR_LEFT, 600), 3)

    def draw_text(self, text: str, pos: tuple, align: str = 'topleft', size: int = 1, font: int = 0, color: tuple = None) -> pygame.Rect:
        """
        绘制文字。
        """
        render = self.fonts[font][size].render(
            text, True, color if color else self.main_color)
        rect = render.get_rect()
        exec(f'rect.{align}=pos')
        return self.screen.blit(render, rect)

    def error(self, msg: str, serious: bool = False) -> None:
        """
        错误弹窗。
        """
        if serious:
            easygui.msgbox(msg, title='出错了', ok_button='退出程序')
            pygame.quit()
            sys.exit()
        else:
            easygui.msgbox(msg, title='提示', ok_button='我知道了')

    def process_events(self) -> list:
        """
        处理事件。
        """
        ret = []
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                ret.append(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                ret.append(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                ret.append(event)
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        return ret

    def update(self) -> None:
        """
        刷新窗口。
        """
        pygame.display.flip()


class Button:
    def __init__(self, window: Window, icon: pygame.Surface, pos: tuple, align: str = 'topleft', todo=lambda: print('Ding dong~'), background: str = '', text: str = '') -> None:
        self.window = window
        self.icon = icon
        self.align = align
        self.size = icon.get_size()
        self.todo = todo
        self.background = background
        self.text = text
        self.rect = self.icon.get_rect()
        exec(f'self.rect.{align}=pos')
        self.touch_time = 0

    def draw(self) -> pygame.Rect:
        if self.touch_time <= 0 and self.rect.collidepoint(*self.window.mouse_pos):
            self.touch_time = time.time()
        elif self.touch_time > 0 and not self.rect.collidepoint(*self.window.mouse_pos):
            self.touch_time = -time.time()-min(0.5, abs(time.time()-self.touch_time))
        alpha = int((min(0.5, time.time()-self.touch_time) if self.touch_time
                     > 0 else max(0, -time.time()-self.touch_time))*510)
        if self.background:
            alpha_surface = pygame.Surface(
                self.icon.get_size(), pygame.SRCALPHA)
            if self.background == 'circle':
                pygame.draw.circle(alpha_surface, (*self.window.main_color, alpha),
                                   (self.size[0]//2, self.size[1]//2), self.size[0]//2)
                self.window.screen.blit(alpha_surface, self.rect)
            elif self.background == 'rect':
                pygame.draw.rect(alpha_surface, (*self.window.main_color, alpha),
                                 pygame.Rect((0, 0), self.size), 0, 5)
            self.window.screen.blit(alpha_surface, self.rect)
        if self.text:
            tip = self.window.fonts[0][0].render(
                self.text, True, (0, 0, 255), self.window.main_color)
            tip.set_alpha(alpha)
            rect = tip.get_rect()
            rect.midright = self.rect.midleft
            self.window.screen.blit(tip, rect)
        return self.window.screen.blit(self.icon, self.rect)

    def move(self, pos: tuple) -> None:
        self.rect = self.icon.get_rect()
        exec(f'self.rect.{self.align}=pos')

    def process_click_event(self, mouse_pos: tuple) -> None:
        if self.rect.collidepoint(*mouse_pos):
            self.todo()


class Slider:
    def __init__(self, window: Window, pos: tuple, length: int, width: int, align: str = 'topleft', size: int = 30, getvalue=None, setvalue=None, setdirectly=None, sdtext='') -> None:
        self.window = window
        self.pos = pos
        self.length = length
        self.width = width
        self.align = align
        self.size = size
        self.getvalue = getvalue
        self.setvalue = setvalue
        self.setdirectly = setdirectly
        self.sdtext = sdtext
        self.setting = False
        self.click_pos = (0, 0)
        self.color = self.window.main_color
        self.icon = pygame.transform.scale(pygame.image.load(
            os.path.join(RESOURCES, 'icons', 'crystal.png')), (size, size))
        self.warning = pygame.transform.scale(pygame.image.load(
            os.path.join(RESOURCES, 'icons', 'warning.png')), (size, size))
        self.icon_rect = self.icon.get_rect()
        self.bar = pygame.Surface((length, width), pygame.SRCALPHA)
        pygame.draw.rect(self.bar, self.color,
                         pygame.Rect((0, 0), (length, width)), 0, width//2)
        self.bar_rect = self.bar.get_rect()
        exec(f'self.bar_rect.{self.align}=pos')
        self.touch_time = 0

    def draw(self) -> pygame.Rect:
        if self.color != self.window.main_color:
            self.color = self.window.main_color
            self.bar = pygame.Surface(
                (self.length, self.width), pygame.SRCALPHA)
            pygame.draw.rect(self.bar, self.color,
                             pygame.Rect((0, 0), (self.length, self.width)), 0, self.width//2)
            self.bar_rect = self.bar.get_rect()
            exec(f'self.bar_rect.{self.align}=self.pos')
        self.window.screen.blit(self.bar, self.bar_rect)
        if self.touch_time <= 0 and self.icon_rect.collidepoint(*self.window.mouse_pos):
            self.touch_time = time.time()
        elif self.touch_time > 0 and not self.icon_rect.collidepoint(*self.window.mouse_pos) and not self.setting:
            self.touch_time = -time.time()-min(0.5, abs(time.time()-self.touch_time))
        if self.setting:
            if not 0 <= self.getvalue() <= 1:
                self.setvalue(max(0, min(1, self.getvalue())))
            elif self.window.mouse_pos != self.click_pos:
                self.setvalue(max(0, min(1,
                                         (self.window.mouse_pos[0]-self.bar_rect.left-self.size/2)/(self.length-self.size))))
        alpha = int((min(0.5, time.time()-self.touch_time) if self.touch_time
                    > 0 else max(0, -time.time()-self.touch_time))*510)
        alpha_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(alpha_surface, (*self.window.main_color,
                           alpha), (self.size//2, self.size//2), self.size//2)
        self.icon_rect.midbottom = (
            self.bar_rect.left+self.size/2+(self.length-self.size)*max(0, min(1, self.getvalue())), self.bar_rect.centery)
        self.window.screen.blit(alpha_surface, self.icon_rect)
        self.window.screen.blit(
            self.icon if 0 <= self.getvalue() <= 1 else self.warning, self.icon_rect)
        if self.touch_time > 0 and self.setdirectly and (not pygame.mouse.get_pressed()[0] or self.window.mouse_pos == self.click_pos):
            tip = self.window.fonts[0][0].render(
                '点击以精确设置'+self.sdtext, True, (0, 0, 255), self.window.main_color)
            tip.set_alpha(alpha)
            rect = tip.get_rect()
            rect.midright = self.icon_rect.midleft
            self.window.screen.blit(tip, rect)
        return self.bar_rect

    def move(self, pos: tuple) -> None:
        self.bar_rect = self.bar.get_rect()
        exec(f'self.bar_rect.{self.align}=pos')

    def process_click_event(self, mouse_pos: tuple) -> None:
        if self.icon_rect.collidepoint(*mouse_pos):
            self.setting = True
            self.click_pos = mouse_pos

    def process_release_event(self, mouse_pos: tuple) -> None:
        if self.setting:
            self.setting = False
            if mouse_pos == self.click_pos and self.setdirectly:
                self.setdirectly()


class Graph:
    def __init__(self, window: Window) -> None:
        self.window = window
        self.bg = pygame.Surface(
            (SIDEBAR_LEFT, WINDOW_SIZE[1]), pygame.SRCALPHA)
        self.origin_pos = (SIDEBAR_LEFT//2, WINDOW_SIZE[1]//2)
        self.scale = 10
        self.a = 1
        self.b = 0
        self.c = 0
        self.calcmode = 1
        self.points = {}
        self.draw_grid()

    def draw_grid(self) -> None:
        self.bg.fill((0, 0, 0, 0))

        for i in range(self.scale, WINDOW_SIZE[1], self.scale):
            pygame.draw.line(self.bg, (*self.window.grid_color, self.window.grid_alpha//2 if i % 50 else self.window.grid_alpha),
                             (0, i), (SIDEBAR_LEFT, i), 1 if i % 50 else 2)

        for i in range(self.scale, SIDEBAR_LEFT, self.scale):
            pygame.draw.line(self.bg, (*self.window.grid_color, self.window.grid_alpha//2 if i % 50 else self.window.grid_alpha),
                             (i, 0), (i, WINDOW_SIZE[1]), 1 if i % 50 else 2)

        pygame.draw.line(self.bg, (*self.window.axis_color, self.window.axis_alpha),
                         (5, self.origin_pos[1]), (SIDEBAR_LEFT-5, self.origin_pos[1]), 3)
        pygame.draw.lines(self.bg, (*self.window.axis_color, self.window.axis_alpha), False, (
            (SIDEBAR_LEFT-15, self.origin_pos[1]-10),
            (SIDEBAR_LEFT-5, self.origin_pos[1]),
            (SIDEBAR_LEFT-15, self.origin_pos[1]+10)), 3)
        r = self.window.fonts[1][1].render('x', True, self.window.axis_color)
        r.set_alpha(self.window.axis_alpha)
        self.bg.blit(r, (SIDEBAR_LEFT-25, self.origin_pos[1]+5))

        pygame.draw.line(self.bg, (*self.window.axis_color, self.window.axis_alpha),
                         (self.origin_pos[0], 5), (self.origin_pos[0], SIDEBAR_LEFT-5), 3)
        pygame.draw.lines(self.bg, (*self.window.axis_color, self.window.axis_alpha), False, (
            (self.origin_pos[0]-10, 15),
            (self.origin_pos[0], 5),
            (self.origin_pos[0]+10, 15)), 3)
        r = self.window.fonts[1][1].render('y', True, self.window.axis_color)
        r.set_alpha(self.window.axis_alpha)
        rect = r.get_rect()
        rect.topright = (self.origin_pos[0]-5, 10)
        self.bg.blit(r, rect)

        r = self.window.fonts[1][1].render('O', True, self.window.axis_color)
        r.set_alpha(self.window.axis_alpha)
        rect = r.get_rect()
        rect.topright = (self.origin_pos[0]-5, self.origin_pos[1]+5)
        self.bg.blit(r, rect)

        for i in (-25, -20, -15, -10, -5, 5, 10, 15, 20, 25):
            r = self.window.fonts[1][0].render(
                str(i), True, self.window.axis_color)
            r.set_alpha(self.window.axis_alpha)
            rect = r.get_rect()
            rect.midtop = (self.origin_pos[0] +
                           i*self.scale, self.origin_pos[1]+5)
            self.bg.blit(r, rect)
            rect.midright = (
                self.origin_pos[0]-5, self.origin_pos[1]-i*self.scale)
            self.bg.blit(r, rect)

    def set_point(self, id: int) -> None:
        pygame.mouse.set_cursor(*pygame.cursors.tri_left)
        ok = False
        while not ok:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.bg.get_rect().collidepoint(event.pos):
                        self.points[id] = (my_round((event.pos[0]-self.origin_pos[0])/self.scale),
                                           my_round((self.origin_pos[1]-event.pos[1])/self.scale))
                        if len(set(i[0] for i in self.points.values())) < len(self.points):
                            self.window.error('不能设置横坐标相同的点!')
                            self.points.pop(id)
                        ok = True
        pygame.mouse.set_cursor(*pygame.cursors.arrow)

    def get_a(self) -> float:
        return (self.a/80)**(1/3)+0.5 if self.a > 0 else -(-self.a/80)**(1/3)+0.5

    def get_b(self) -> float:
        return self.b/20+0.5

    def get_c(self) -> float:
        return self.c/20+0.5

    def set_a(self, value: float) -> None:
        t = (value-0.5)**3*80
        self.a = my_round(t, 4 if t <= 0.01 else 3 if t <= 0.1 else 2)

    def set_b(self, value: float) -> None:
        self.b = my_round((value-0.5)*20, 1)

    def set_c(self, value: float) -> None:
        self.c = my_round((value-0.5)*20, 1)

    def set_a_d(self) -> None:
        a = easygui.enterbox(
            '请输入绝对值不超过 10 的实数（最多精确到小数点后4位）', '设置二次项系数a')
        if not a:
            return
        try:
            a = my_round(float(a), 4)
            assert(-10 <= a <= 10)
            self.a = a
        except:
            self.window.error('输入有误，请重新输入!')
            self.set_a_d()

    def help_a(self) -> None:
        easygui.msgbox("""在二次函数的一般式 y=ax²+bx+c (a≠0) 中，a为二次项系数。
a的符号决定抛物线的开口方向，a的绝对值大小决定抛物线的开口大小。
a的绝对值越大，抛物线开口越小，开口过小时难以观察，
所以本程序中a的取值范围为 ±10 以内。
当a=0时，函数不是二次函数，所得的曲线也不是抛物线而是直线。
由于a为一个较特殊的系数，本程序中a的设置与显示格式与b,c有所不同。""", '关于二次项系数a')

    def set_b_d(self) -> None:
        b = easygui.enterbox(
            '请输入绝对值不超过 10 的实数（最多精确到小数点后1位）', '设置一次项系数b')
        if not b:
            return
        try:
            b = my_round(float(b), 1)
            assert(-10 <= b <= 10)
            self.b = b
        except:
            self.window.error('输入有误，请重新输入!')
            self.set_b_d()

    def help_b(self) -> None:
        easygui.msgbox("""在二次函数的一般式 y=ax²+bx+c (a≠0) 中，b为一次项系数。
当a一定时，b的绝对值越大，抛物线对称轴离y轴越远，可能超出可见范围，
所以本程序中b的取值范围为 ±10 以内。""", '关于一次项系数b')

    def set_c_d(self) -> None:
        c = easygui.enterbox(
            '请输入绝对值不超过 10 的实数（最多精确到小数点后1位）', '设置常数项c')
        if not c:
            return
        try:
            c = my_round(float(c), 1)
            assert(-10 <= c <= 10)
            self.c = c
        except:
            self.window.error('输入有误，请重新输入!')
            self.set_c_d()

    def help_c(self) -> None:
        easygui.msgbox("""在二次函数的一般式 y=ax²+bx+c (a≠0) 中，c为常数项。
c的绝对值越大，抛物线与y轴的交点离原点越远，可能超出可见范围
所以本程序中c的取值范围为 ±10 以内。""", '关于常数项c')

    def draw(self) -> None:
        self.window.screen.blit(self.bg, (0, 0))
        if self.calcmode & 1:
            pygame.draw.lines(self.window.screen, self.window.main_color, False, [(int(self.origin_pos[0]+i*self.scale), int(self.origin_pos[1] - (
                self.a*i**2+self.b*i+self.c)*self.scale)) for i in map(lambda x:x/self.scale, range(-self.origin_pos[0], self.origin_pos[0]))], 2)
            if self.a:
                t = int(self.origin_pos[0]-self.b/self.a/2*self.scale)
                if 0 < t < SIDEBAR_LEFT:
                    for i in range(0, WINDOW_SIZE[1], 6):
                        pygame.draw.line(self.window.screen,
                                         self.window.main_color, (t, i), (t, i+3), 1)
        if self.calcmode & 2:
            for i in self.points:
                pos = (int(self.origin_pos[0]+self.points[i][0]*self.scale),
                       int(self.origin_pos[1]-self.points[i][1]*self.scale))
                pygame.draw.circle(self.window.screen,
                                   self.window.main_color, pos, 10)
                self.window.draw_text(
                    str(i), pos, 'center', 0, 1, self.window.grid_color)

    def set_grid_color(self) -> None:
        """
        设置网格颜色。
        """
        color = askcolor(self.window.grid_color_hex, '设置网格颜色')
        if color:
            self.window.grid_color_hex = color
            self.window.grid_color = [int(color[i:i+2], 16)
                                      for i in range(1, 7, 2)]
            self.window.cp.set('window', 'grid_color', color)
            self.window.cp.write(open('config.ini', 'w', encoding='utf-8'))
            self.draw_grid()

    def set_grid_alpha(self, value: float) -> None:
        """
        设置网格不透明度（参数为小数）。
        """
        self.window.grid_alpha = int(value * 255)
        self.window.cp.set('window', 'grid_alpha', str(self.window.grid_alpha))
        self.window.cp.write(open('config.ini', 'w', encoding='utf-8'))
        self.draw_grid()

    def set_axis_color(self) -> None:
        """
        设置坐标轴颜色。
        """
        color = askcolor(self.window.axis_color_hex, '设置坐标轴颜色')
        if color:
            self.window.axis_color_hex = color
            self.window.axis_color = [int(color[i:i+2], 16)
                                      for i in range(1, 7, 2)]
            self.window.cp.set('window', 'axis_color', color)
            self.window.cp.write(open('config.ini', 'w', encoding='utf-8'))
            self.draw_grid()

    def set_axis_alpha(self, value: float) -> None:
        """
        设置坐标轴不透明度（参数为小数）。
        """
        self.window.axis_alpha = int(value * 255)
        self.window.cp.set('window', 'axis_alpha', str(self.window.axis_alpha))
        self.window.cp.write(open('config.ini', 'w', encoding='utf-8'))
        self.draw_grid()


class Sidebar:
    def __init__(self, window: Window, graph: Graph) -> None:
        self.window = window
        self.graph = graph
        self.pages = {'home': '抛物线演示器', 'settings': '设置', 'calc': '计算'}
        self.icons = {name: pygame.transform.scale(pygame.image.load(
            os.path.join(RESOURCES, 'icons', name+'.png')), size) for name, size in
            [('calc', (50, 50)), ('settings', (50, 50)), ('return', (50, 50)), ('change', (65, 30)), ('set', (65, 30)), ('help', (20, 20))]}
        self.buttons = {}
        self.sliders = {}
        self.points_hash = 0
        self.open('home')

    def draw(self) -> None:
        start = self.window.draw_text(
            self.pages[self.page], (SIDEBAR_MID, 10-max(0, 1-(time.time()-self.page_open_time)/0.3)**2*100), 'midtop', 3).bottom
        if self.page == 'home':
            self.draw_home(start)
        elif self.page == 'settings':
            self.draw_settings(start)
        elif self.page == 'calc':
            self.draw_calc(start)

    def formula(self) -> str:
        ret = ''

        if self.graph.a == 1:
            ret += 'x²'
        elif self.graph.a == -1:
            ret += '-x²'
        elif abs(self.graph.a) >= 0.0001:
            ret += f'{my_round(self.graph.a,4 if abs(self.graph.a) < 0.01 else 3 if abs(self.graph.a) < 0.1 else 2)}x²'

        if ret and self.graph.b > 0:
            ret += '+'
        if self.graph.b == 1:
            ret += 'x'
        elif self.graph.b == -1:
            ret += '-x'
        elif self.graph.b:
            ret += f'{my_round(self.graph.b,1)}x'

        if ret and self.graph.c > 0:
            ret += '+'
        if self.graph.c or not ret:
            ret += f'{my_round(self.graph.c, 1)}'

        return 'y='+ret

    def draw_home(self, start) -> None:
        text = self.formula()
        self.window.draw_text(text, (SIDEBAR_MID, start+20), 'midtop',
                              3 if len(text) < 12 else 2 if len(text) < 18 else 1, 1)
        t = self.window.draw_text('a=0' if abs(self.graph.a) < 0.0001 else f'a={self.graph.a:.4f}'
                                  if abs(self.graph.a) < 0.01 else f'a={self.graph.a:.3f}'
                                  if abs(self.graph.a) < 0.1 else f'a={self.graph.a:.2f}',
                                  (SIDEBAR_LEFT+10, start+80), 'topleft', 1, 1)
        self.sliders['a'].move((SIDEBAR_LEFT+145, t.centery))
        if 'help_a' not in self.buttons:
            self.buttons['help_a'] = Button(self.window, self.icons['help'],
                                            (WINDOW_SIZE[0]-5, t.centery), 'midright', self.graph.help_a, 'circle', '什么是a')
        else:
            self.buttons['help_a'].move((WINDOW_SIZE[0]-5, t.centery))
        t = self.window.draw_text(
            f'b={my_round(self.graph.b,1)}', (SIDEBAR_LEFT+10, t.bottom+10), 'topleft', 1, 1)
        self.sliders['b'].move((SIDEBAR_LEFT+145, t.centery))
        if 'help_b' not in self.buttons:
            self.buttons['help_b'] = Button(self.window, self.icons['help'],
                                            (WINDOW_SIZE[0]-5, t.centery), 'midright', self.graph.help_b, 'circle', '什么是b')
        else:
            self.buttons['help_b'].move((WINDOW_SIZE[0]-5, t.centery))
        t = self.window.draw_text(
            f'c={my_round(self.graph.c,1)}', (SIDEBAR_LEFT+10, t.bottom+10), 'topleft', 1, 1)
        self.sliders['c'].move((SIDEBAR_LEFT+145, t.centery))
        if 'help_c' not in self.buttons:
            self.buttons['help_c'] = Button(self.window, self.icons['help'],
                                            (WINDOW_SIZE[0]-5, t.centery), 'midright', self.graph.help_c, 'circle', '什么是c')
        else:
            self.buttons['help_c'].move((WINDOW_SIZE[0]-5, t.centery))
        if self.graph.a:
            h = my_round(-self.graph.b/self.graph.a/2, 2)
            k = my_round(self.graph.c-self.graph.b**2/self.graph.a/4, 2)
            delta = self.graph.b**2-4*self.graph.a*self.graph.c
            if delta > 0:
                x = ((-self.graph.b-delta**0.5)/self.graph.a/2,
                     (-self.graph.b+delta**0.5)/self.graph.a/2)
            elif delta == 0:
                x = (-self.graph.b/self.graph.a/2,)
            else:
                x = ()

            t = self.window.draw_text(
                '开口方向:向'+'上下'[self.graph.a < 0], (SIDEBAR_LEFT+10, t.bottom+10), 'topleft', 0)
            if 'help_kkfx' not in self.buttons:
                self.buttons['help_kkfx'] = Button(self.window, self.icons['help'],
                                                   (WINDOW_SIZE[0]-5, t.centery), 'midright', self.help_kkfx, 'circle', '开口方向的变化规律')
            else:
                self.buttons['help_kkfx'].move((WINDOW_SIZE[0]-5, t.centery))

            t = self.window.draw_text(
                '对称轴:直线', (SIDEBAR_LEFT+10, t.bottom+10), 'topleft', 0)
            t = self.window.draw_text(
                f'x={h}', (t.right, t.centery), 'midleft', 0, 1)
            if 'help_dcz' not in self.buttons:
                self.buttons['help_dcz'] = Button(self.window, self.icons['help'],
                                                  (WINDOW_SIZE[0]-5, t.centery), 'midright', self.help_dcz, 'circle', '对称轴的计算方法')
            else:
                self.buttons['help_dcz'].move((WINDOW_SIZE[0]-5, t.centery))

            t = self.window.draw_text(
                '顶点坐标:', (SIDEBAR_LEFT+10, t.bottom+10), 'topleft', 0)
            t = self.window.draw_text(
                f'({h},{k})', (t.right, t.centery), 'midleft', 0, 1)
            if 'help_ddzb' not in self.buttons:
                self.buttons['help_ddzb'] = Button(self.window, self.icons['help'],
                                                   (WINDOW_SIZE[0]-5, t.centery), 'midright', self.help_ddzb, 'circle', '顶点坐标的计算方法')
            else:
                self.buttons['help_ddzb'].move((WINDOW_SIZE[0]-5, t.centery))

            t = self.window.draw_text(
                f'最{"大小"[self.graph.a > 0]}值:', (SIDEBAR_LEFT+10, t.bottom+10), 'topleft', 0)
            t = self.window.draw_text(
                f'x={h},y={k}', (t.right, t.centery), 'midleft', 0, 1)
            if 'help_zz' not in self.buttons:
                self.buttons['help_zz'] = Button(self.window, self.icons['help'],
                                                 (WINDOW_SIZE[0]-5, t.centery), 'midright', self.help_zz, 'circle', '函数最值与抛物线顶点坐标的关系')
            else:
                self.buttons['help_zz'].move((WINDOW_SIZE[0]-5, t.centery))

            t = self.window.draw_text(
                '增减性:', (SIDEBAR_LEFT+10, t.bottom+10), 'topleft', 0)
            t = self.window.draw_text(
                f'x>{h}', (t.right, t.centery), 'midleft', 0, 1)
            t = self.window.draw_text(
                '时，y随x的增大而'+('增大' if self.graph.a > 0 else '减小'), (t.right, t.centery), 'midleft', 0)
            t = self.window.draw_text(
                f'x<{h}', (t.left, t.bottom), 'topright', 0, 1)
            t = self.window.draw_text(
                '时，y随x的增大而'+('增大' if self.graph.a < 0 else '减小'), (t.right, t.centery), 'midleft', 0)
            if 'help_zjx' not in self.buttons:
                self.buttons['help_zjx'] = Button(self.window, self.icons['help'],
                                                  (WINDOW_SIZE[0]-5, t.centery), 'midright', self.help_zjx, 'circle', '增减性的变化规律')
            else:
                self.buttons['help_zjx'].move((WINDOW_SIZE[0]-5, t.centery))

            t = self.window.draw_text(
                '与x轴的交点:', (SIDEBAR_LEFT+10, t.bottom+10), 'topleft', 0)
            t = self.window.draw_text(','.join(map(lambda x: f'({my_round(x, 2)},0)', x)), (
                t.right, t.centery), 'midleft', 0, 1) if x else self.window.draw_text('无', (t.right, t.centery), 'midleft', 0)
            if 'help_xjd' not in self.buttons:
                self.buttons['help_xjd'] = Button(self.window, self.icons['help'],
                                                  (WINDOW_SIZE[0]-5, t.centery), 'midright', self.help_xjd, 'circle', '二次函数与一元二次方程的关系')
            else:
                self.buttons['help_xjd'].move((WINDOW_SIZE[0]-5, t.centery))

            t = self.window.draw_text(
                '与y轴的交点:', (SIDEBAR_LEFT+10, t.bottom+10), 'topleft', 0)
            t = self.window.draw_text(
                f'(0,{my_round(self.graph.c,2)})', (t.right, t.centery), 'midleft', 0, 1)
            if 'help_yjd' not in self.buttons:
                self.buttons['help_yjd'] = Button(self.window, self.icons['help'],
                                                  (WINDOW_SIZE[0]-5, t.centery), 'midright', self.help_yjd, 'circle', '与y轴交点的计算方法')
            else:
                self.buttons['help_yjd'].move((WINDOW_SIZE[0]-5, t.centery))
        else:
            self.window.draw_text(
                '该函数非二次函数，不支持分析。', (SIDEBAR_LEFT+10, t.bottom+10), 'topleft')
        self.sliders['a'].draw()
        self.sliders['b'].draw()
        self.sliders['c'].draw()
        self.buttons['calc'].draw()
        self.buttons['settings'].draw()
        self.buttons['help_a'].draw()
        self.buttons['help_b'].draw()
        self.buttons['help_c'].draw()
        if self.graph.a:
            self.buttons['help_kkfx'].draw()
            self.buttons['help_dcz'].draw()
            self.buttons['help_ddzb'].draw()
            self.buttons['help_zz'].draw()
            self.buttons['help_zjx'].draw()
            self.buttons['help_xjd'].draw()
            self.buttons['help_yjd'].draw()

    def help_kkfx(self) -> None:
        easygui.msgbox('当a>0时，抛物线开口向上；当a<0时，抛物线开口向下。', '开口方向的变化规律')

    def help_dcz(self) -> None:
        easygui.msgbox('抛物线的对称轴为直线x=-b/2a (其中a,b分别为二次项与一次项系数)。', '对称轴的计算方法')

    def help_ddzb(self) -> None:
        easygui.msgbox("""【方法一：配方法】
从二次函数的二次项和一次项中提出二次项系数，再将括号内式子配成完全平方，
最终化为 y=a(x-h)²+k 的形式，这个式子被称为顶点式，
抛物线的顶点坐标为(h,k)。

【方法二：公式法】
抛物线的顶点坐标可用公式(-b/2a,(4ac-b²)/4a)表示。

【方法三：代入法】
将抛物线的对称轴位置即顶点横坐标代入解析式，即可得到顶点纵坐标。""", '顶点坐标的计算方法')

    def help_zz(self) -> None:
        easygui.msgbox("""设抛物线的顶点坐标为(h,k)。
若a>0，当x=h时，二次函数有最小值k；若a<0，当x=h时，二次函数有最大值k。""", '函数最值与抛物线顶点坐标的关系')

    def help_zjx(self) -> None:
        easygui.msgbox("""若a>0，抛物线对称轴左边下降，右边上升，
即当x<h时，y随x的增大而减小，当x>h时，y随x的增大而增大；
若a<0，抛物线对称轴左边上升，右边下降，
即当x<h时，y随x的增大而增大，当x>h时，y随x的增大而减小。""", '增减性的变化规律')

    def help_xjd(self) -> None:
        easygui.msgbox("""抛物线 y=ax²+bx+c 与x轴交点的横坐标即为方程 ax²+bx+c=0 的解，
与x轴交点的数量与方程的判别式(Δ=b²-4ac)有关。
当Δ>0时，方程有两个不相等的实数根，抛物线与x轴有两个不重合的交点；
当Δ=0时，方程有两个相等的实数根，抛物线与x轴有一个交点（两个重合的交点）；
当Δ<0时，方程无实数根，抛物线与x轴无交点。
""", '二次函数与一元二次方程的关系')

    def help_yjd(self) -> None:
        easygui.msgbox('抛物线与y轴交点的纵坐标即为二次函数的常数项c。', '与y轴交点的计算方法')

    def draw_settings(self, start) -> None:
        self.buttons['return'].draw()

        t = self.window.draw_text('背景模式:'+('纯色' if self.window.bg_mode ==
                                           'color' else '图片'), (SIDEBAR_LEFT+10, start+20), 'topleft')
        if 'change_bg_mode' not in self.buttons:
            self.buttons['change_bg_mode'] = Button(
                self.window, self.icons['change'], (WINDOW_SIZE[0]-10, t.centery), 'midright', self.window.change_bg_mode, 'rect')
            self.buttons['set_bg'] = Button(self.window, self.icons['set'], (
                self.buttons['change_bg_mode'].rect.left-10, t.centery), 'midright', self.window.set_bg, 'rect')
        else:
            self.buttons['change_bg_mode'].move((WINDOW_SIZE[0]-10, t.centery))
            self.buttons['set_bg'].move(
                (self.buttons['change_bg_mode'].rect.left-10, t.centery))
        self.buttons['change_bg_mode'].draw()
        self.buttons['set_bg'].draw()
        t = self.window.draw_text(
            '当前背景:', (SIDEBAR_LEFT+10, t.bottom), 'topleft', 0)
        if self.window.bg_mode == 'color':
            pygame.draw.rect(self.window.screen, self.window.bg_color,
                             (t.right+5, t.centery-10, 20, 20), 0, 3)
            pygame.draw.rect(self.window.screen, (255, 255, 255),
                             (t.right+5, t.centery-10, 20, 20), 1, 3)
        else:
            t = self.window.draw_text(os.path.split(self.window.background)[
                                      1], (t.right, t.centery), 'midleft', 0)
            t = self.window.draw_text(
                '蒙版不透明度:'+str(self.window.mask_alpha), (SIDEBAR_LEFT+10, t.bottom+10), 'topleft')
            if 'change_mask_alpha' not in self.sliders:
                self.sliders['change_mask_alpha'] = Slider(
                    self.window, (SIDEBAR_LEFT+10, t.bottom+15), WINDOW_SIZE[0]-SIDEBAR_LEFT-20, 10, 'topleft', 20, lambda: self.window.mask_alpha/255, self.window.set_mask_alpha)
            else:
                self.sliders['change_mask_alpha'].move(
                    (SIDEBAR_LEFT+10, t.bottom+15))
            t = self.sliders['change_mask_alpha'].draw()

        t = self.window.draw_text(
            '主题颜色:', (SIDEBAR_LEFT+10, t.bottom+10), 'topleft')
        pygame.draw.rect(self.window.screen, self.window.main_color,
                         (t.right+5, t.centery-10, 20, 20), 0, 3)
        pygame.draw.rect(self.window.screen, (255, 255, 255),
                         (t.right+5, t.centery-10, 20, 20), 1, 3)
        if 'set_main_color' not in self.buttons:
            self.buttons['set_main_color'] = Button(self.window, self.icons['set'], (
                WINDOW_SIZE[0]-10, t.centery), 'midright', self.window.set_main_color, 'rect')
        else:
            self.buttons['set_main_color'].move((WINDOW_SIZE[0]-10, t.centery))
        self.buttons['set_main_color'].draw()

        t = self.window.draw_text(
            '网格颜色:', (SIDEBAR_LEFT+10, t.bottom+10), 'topleft')
        pygame.draw.rect(self.window.screen, self.window.grid_color,
                         (t.right+5, t.centery-10, 20, 20), 0, 3)
        pygame.draw.rect(self.window.screen, (255, 255, 255),
                         (t.right+5, t.centery-10, 20, 20), 1, 3)
        if 'set_grid_color' not in self.buttons:
            self.buttons['set_grid_color'] = Button(self.window, self.icons['set'], (
                WINDOW_SIZE[0]-10, t.centery), 'midright', self.graph.set_grid_color, 'rect')
        else:
            self.buttons['set_grid_color'].move((WINDOW_SIZE[0]-10, t.centery))
        self.buttons['set_grid_color'].draw()

        t = self.window.draw_text(
            '网格不透明度:'+str(self.window.grid_alpha), (SIDEBAR_LEFT+10, t.bottom+10), 'topleft')
        if 'change_grid_alpha' not in self.sliders:
            self.sliders['change_grid_alpha'] = Slider(
                self.window, (SIDEBAR_LEFT+10, t.bottom+15), WINDOW_SIZE[0]-SIDEBAR_LEFT-20, 10, 'topleft', 20, lambda: self.window.grid_alpha/255, self.graph.set_grid_alpha)
        else:
            self.sliders['change_grid_alpha'].move(
                (SIDEBAR_LEFT+10, t.bottom+15))
        start = self.sliders['change_grid_alpha'].draw().bottom

        t = self.window.draw_text(
            '坐标轴颜色:', (SIDEBAR_LEFT+10, start+10), 'topleft')
        pygame.draw.rect(self.window.screen, self.window.axis_color,
                         (t.right+5, t.centery-10, 20, 20), 0, 3)
        pygame.draw.rect(self.window.screen, (255, 255, 255),
                         (t.right+5, t.centery-10, 20, 20), 1, 3)
        if 'set_axis_color' not in self.buttons:
            self.buttons['set_axis_color'] = Button(self.window, self.icons['set'], (
                WINDOW_SIZE[0]-10, t.centery), 'midright', self.graph.set_axis_color, 'rect')
        else:
            self.buttons['set_axis_color'].move((WINDOW_SIZE[0]-10, t.centery))
        self.buttons['set_axis_color'].draw()

        t = self.window.draw_text(
            '坐标轴不透明度:'+str(self.window.axis_alpha), (SIDEBAR_LEFT+10, t.bottom+10), 'topleft')
        if 'change_axis_alpha' not in self.sliders:
            self.sliders['change_axis_alpha'] = Slider(
                self.window, (SIDEBAR_LEFT+10, t.bottom+15), WINDOW_SIZE[0]-SIDEBAR_LEFT-20, 10, 'topleft', 20, lambda: self.window.axis_alpha/255, self.graph.set_axis_alpha)
        else:
            self.sliders['change_axis_alpha'].move(
                (SIDEBAR_LEFT+10, t.bottom+15))
        start = self.sliders['change_axis_alpha'].draw().bottom

    def draw_calc(self, start) -> None:
        self.buttons['return'].draw()

        t = self.window.draw_text(
            '三点计算函数解析式', (SIDEBAR_MID, start+20), 'midtop', 2)

        if 'help' not in self.buttons:
            self.buttons['help'] = Button(self.window, self.icons['help'], (
                WINDOW_SIZE[0]-10, t.centery), 'midright', self.help_calc, 'rect', '计算原理')
        else:
            self.buttons['help'].move((WINDOW_SIZE[0]-10, t.centery))

        t = self.window.draw_text(
            '请先点击“设置”，再在网格中点击格线交点处', (SIDEBAR_MID, t.bottom+10), 'midtop', 0)

        t = self.window.draw_text(
            '点 1:'+str(self.graph.points[1] if 1 in self.graph.points else '未设置'), (SIDEBAR_LEFT+10, t.bottom+10), 'topleft')
        if 'set_point_1' not in self.buttons:
            self.buttons['set_point_1'] = Button(self.window, self.icons['set'], (
                WINDOW_SIZE[0]-10, t.centery), 'midright', lambda: self.graph.set_point(1), 'rect')
        else:
            self.buttons['set_point_1'].move((WINDOW_SIZE[0]-10, t.centery))

        t = self.window.draw_text(
            '点 2:'+str(self.graph.points[2] if 2 in self.graph.points else '未设置'), (SIDEBAR_LEFT+10, t.bottom+10), 'topleft')
        if 'set_point_2' not in self.buttons:
            self.buttons['set_point_2'] = Button(self.window, self.icons['set'], (
                WINDOW_SIZE[0]-10, t.centery), 'midright', lambda: self.graph.set_point(2), 'rect')
        else:
            self.buttons['set_point_2'].move((WINDOW_SIZE[0]-10, t.centery))

        t = self.window.draw_text(
            '点 3:'+str(self.graph.points[3] if 3 in self.graph.points else '未设置'), (SIDEBAR_LEFT+10, t.bottom+10), 'topleft')
        if 'set_point_3' not in self.buttons:
            self.buttons['set_point_3'] = Button(self.window, self.icons['set'], (
                WINDOW_SIZE[0]-10, t.centery), 'midright', lambda: self.graph.set_point(3), 'rect')
        else:
            self.buttons['set_point_3'].move((WINDOW_SIZE[0]-10, t.centery))

        if len(self.graph.points) == 3:
            self.graph.calcmode = 3
            if hash(tuple(sorted(self.graph.points.values()))) != self.points_hash:
                self.points_hash = hash(
                    tuple(sorted(self.graph.points.values())))
                self.window.draw_text(
                    '计算中...', (SIDEBAR_MID, t.bottom+10), 'midtop', 2)
                self.window.update()
                (x1, y1), (x2, y2), (x3, y3) = self.graph.points.values()
                tmp = x1**2*x2 - x1**2*x3 - x1*x2**2 + x1*x3**2 + x2**2*x3 - x2*x3**2
                t_a = -x1*y2 + x1*y3 + x2*y1 - x2*y3 - x3*y1 + x3*y2
                t_b = x1**2*y2 - x1**2*y3 - x2**2*y1 + x2**2*y3 + x3**2*y1 - x3**2*y2
                t_c = x1**2*x2*y3 - x1**2*x3*y2 - x1*x2**2 * \
                    y3 + x1*x3**2*y2 + x2**2*x3*y1 - x2*x3**2*y1
                self.graph.a = t_a/tmp
                self.graph.b = t_b/tmp
                self.graph.c = t_c/tmp
                if tmp < 0:
                    tmp = -tmp
                    t_a = -t_a
                    t_b = -t_b
                    t_c = -t_c
                g_a = gcd(t_a, tmp)
                g_b = gcd(t_b, tmp)
                g_c = gcd(t_c, tmp)
                self.result_a = f'{t_a//g_a}/{tmp//g_a}' if tmp != g_a else f'{t_a//g_a}'
                self.result_b = f'{t_b//g_b}/{tmp//g_b}' if tmp != g_b else f'{t_b//g_b}'
                self.result_c = f'{t_c//g_c}/{tmp//g_c}' if tmp != g_c else f'{t_c//g_c}'
            else:
                text = self.formula()
                start = self.window.draw_text(
                    '计算结果', (SIDEBAR_MID, t.bottom+10), 'midtop', 2).bottom
                self.window.draw_text(text, (SIDEBAR_MID, start+20), 'midtop',
                                      3 if len(text) < 12 else 2 if len(text) < 18 else 1, 1)
                start = self.window.draw_text(
                    'a='+self.result_a,  (SIDEBAR_LEFT+10, start+80), 'topleft', 1, 1).bottom
                start = self.window.draw_text(
                    'b='+self.result_b, (SIDEBAR_LEFT+10, start+10), 'topleft', 1, 1).bottom
                self.window.draw_text(
                    'c='+self.result_c, (SIDEBAR_LEFT+10, start+10), 'topleft', 1, 1)
        else:
            self.graph.calcmode = 2

        self.buttons['set_point_1'].draw()
        self.buttons['set_point_2'].draw()
        self.buttons['set_point_3'].draw()
        self.buttons['help'].draw()

    def help_calc(self) -> None:
        easygui.msgbox("""将三点坐标分别带入解析式并联立成三元一次方程组：
x1²a+x1b+c=0,
x2²a+x2b+c=0,
x3²a+x3b+c=0.
解出a,b,c的值即为函数各项系数。""", '计算原理')

    def open(self, page) -> None:
        self.page = page
        self.page_open_time = time.time()
        if page == 'home':
            self.open_home()
        elif page == 'settings':
            self.open_settings()
        elif page == 'calc':
            self.open_calc()

    def open_home(self) -> None:
        self.points_hash = 0
        self.graph.calcmode = 1
        self.graph.points = {}
        self.buttons = {'calc': Button(self.window, self.icons['calc'], (SIDEBAR_LEFT+10, WINDOW_SIZE[1]-60), 'topleft', lambda: self.open('calc'), 'circle', '计算'),
                        'settings': Button(self.window, self.icons['settings'],
                                           (WINDOW_SIZE[0]-60, WINDOW_SIZE[1]-60), 'topleft', lambda: self.open('settings'), 'circle', '设置')}
        self.sliders = {'a': Slider(self.window, (0, 0), WINDOW_SIZE[0]-SIDEBAR_LEFT-180, 10, 'midleft', 20,  self.graph.get_a, self.graph.set_a, self.graph.set_a_d, '二次项系数a'),
                        'b': Slider(self.window, (0, 0), WINDOW_SIZE[0]-SIDEBAR_LEFT-180, 10, 'midleft', 20,  self.graph.get_b, self.graph.set_b, self.graph.set_b_d, '一次项系数b'),
                        'c': Slider(self.window, (0, 0), WINDOW_SIZE[0]-SIDEBAR_LEFT-180, 10, 'midleft', 20,  self.graph.get_c, self.graph.set_c, self.graph.set_c_d, '常数项c')}

    def open_settings(self) -> None:
        self.buttons = {'return': Button(self.window, self.icons['return'],
                                         (SIDEBAR_LEFT+10, 10), 'topleft', lambda: self.open('home'), 'circle', '返回')}
        self.sliders = {}

    def open_calc(self) -> None:
        self.buttons = {'return': Button(self.window, self.icons['return'],
                                         (SIDEBAR_LEFT+10, 10), 'topleft', lambda: self.open('home'), 'circle', '返回')}
        self.sliders = {}


if __name__ == '__main__':
    cp = ConfigParser()
    if os.path.isfile('config.ini'):
        try:
            cp.read('config.ini', encoding='utf-8')
        except:
            pass
    window = Window(cp)
    graph = Graph(window)
    sidebar = Sidebar(window, graph)

    while True:
        window.draw_frame()
        graph.draw()
        sidebar.draw()
        window.update()
        for event in window.process_events():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in sidebar.buttons.values():
                    button.process_click_event(event.pos)
                for slider in sidebar.sliders.values():
                    slider.process_click_event(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                for slider in sidebar.sliders.values():
                    slider.process_release_event(event.pos)
