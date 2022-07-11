import os
import sys
import time
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


class Window:
    def __init__(self, cp: ConfigParser) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption(WINDOW_TITLE)
        self.fonts = {i: pygame.font.Font(os.path.join(
            RESOURCES, 'FZFWQingYinTiJWL.TTF'), 15+i*10) for i in range(4)}
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
        self.main_color_hex = self.get_or_set('main_color', '#ffffff')
        try:
            self.main_color = [int(self.main_color_hex[i:i+2], 16)
                               for i in range(1, 7, 2)]
        except:
            self.error('config.txt 中的主题颜色格式不正确，已修改为默认值 #ffffff。')
            self.main_color_hex = '#ffffff'
            self.main_color = (255, 255, 255)
            self.cp.set('window', 'main_color', '#ffffff')

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
                self.error('config.txt 中的窗口背景颜色格式不正确，已修改为默认值 #000000。')
                self.background = '#000000'
                self.bg_color = (0, 0, 0)
                self.cp.set('window', 'background', '#000000')
        elif mode == 'image':
            try:
                self.bg_image = pygame.transform.scale(
                    pygame.image.load(self.background), WINDOW_SIZE)
                self.bg_image_with_mask = self.bg_image.copy()
                self.bg_mode = 'image'
                # 设置蒙版不透明度
                try:
                    self.mask_alpha = int(self.get_or_set('mask_alpha', '127'))
                    assert(0 <= self.mask_alpha <= 255)
                except:
                    self.error('config.txt 中的蒙版不透明度格式不正确，已修改为默认值 127。')
                    self.mask_alpha = 127
                    self.cp.set('window', 'mask_alpha', '127')
                mask = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
                mask.fill((0, 0, 0, self.mask_alpha))
                self.bg_image_with_mask.blit(mask, (0, 0))
            except:
                self.error('config.txt 中的窗口背景图片无法加载，已修改为使用颜色 #000000 填充。')
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
        color = easygui.enterbox(
            '请输入十六进制格式的背景颜色', default=self.background if self.bg_mode == 'color' else '#000000')
        if not color:
            return
        if color.startswith('#') and len(color) == 7 and all(c in '0123456789abcdef' for c in color[1:]):
            self.background = color
            self.apply_bg_mode('color')
            self.cp.set('window', 'background', color)
            self.cp.write(open('config.ini', 'w', encoding='utf-8'))
        else:
            self.error('背景颜色格式不正确，请重新输入。')
            self.set_bg_color()

    def set_bg_image(self) -> None:
        """
        设置背景图片。
        """
        image = easygui.fileopenbox('请选择背景图片')
        if not image:
            return
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
        color = easygui.enterbox(
            '请输入十六进制格式的主题颜色', default=self.main_color_hex)
        if not color:
            return
        if color.startswith('#') and len(color) == 7 and all(c in '0123456789abcdef' for c in color[1:]):
            self.main_color_hex = color
            self.main_color = [int(color[i:i+2], 16)
                               for i in range(1, 7, 2)]
            self.cp.set('window', 'main_color', color)
            self.cp.write(open('config.ini', 'w', encoding='utf-8'))
        else:
            self.error('主题颜色格式不正确，请重新输入。')
            self.set_main_color()

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

    def draw_text(self, text: str, pos: tuple, align: str = 'topleft', size: int = 1) -> pygame.Rect:
        """
        绘制文字。
        """
        render = self.fonts[size].render(text, True, self.main_color)
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
    def __init__(self, window: Window, icon: pygame.Surface, pos: tuple, align: str = 'topleft', todo=lambda: print('Ding dong~'), background: str = None) -> None:
        self.window = window
        self.icon = icon
        self.align = align
        self.size = icon.get_size()
        self.todo = todo
        self.background = background
        self.rect = self.icon.get_rect()
        exec(f'self.rect.{align}=pos')
        self.touch_time = 0

    def draw(self) -> pygame.Rect:
        if self.touch_time <= 0 and self.rect.collidepoint(*self.window.mouse_pos):
            self.touch_time = time.time()
        elif self.touch_time > 0 and not self.rect.collidepoint(*self.window.mouse_pos):
            self.touch_time = -time.time()-min(0.5, abs(time.time()-self.touch_time))
        if self.background:
            alpha = int((min(0.5, time.time()-self.touch_time) if self.touch_time
                        > 0 else max(0, -time.time()-self.touch_time))*510)
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
        return self.window.screen.blit(self.icon, self.rect)

    def move(self, pos: tuple) -> None:
        self.rect = self.icon.get_rect()
        exec(f'self.rect.{self.align}=pos')

    def process_click_event(self, mouse_pos: tuple) -> None:
        if self.rect.collidepoint(*mouse_pos):
            self.todo()


class Slider:
    def __init__(self, window: Window, pos: tuple, length: int, width: int, align: str = 'topleft', size: int = 30, getvalue=None, setvalue=None):
        self.window = window
        self.pos = pos
        self.align = align
        self.size = size
        self.length = length
        self.getvalue = getvalue
        self.setvalue = setvalue
        self.setting = False
        self.icon = pygame.transform.scale(pygame.image.load(
            os.path.join(RESOURCES, 'icons', 'crystal.png')), (size, size))
        self.icon_rect = self.icon.get_rect()
        self.bar = pygame.Surface((length, width), pygame.SRCALPHA)
        pygame.draw.rect(self.bar, self.window.main_color,
                         pygame.Rect((0, 0), (length, width)), 0, width//2)
        self.bar_rect = self.bar.get_rect()
        exec(f'self.bar_rect.{self.align}=pos')
        self.touch_time = 0

    def draw(self) -> pygame.Rect:
        self.window.screen.blit(self.bar, self.bar_rect)
        if self.touch_time <= 0 and self.icon_rect.collidepoint(*self.window.mouse_pos):
            self.touch_time = time.time()
        elif self.touch_time > 0 and not self.icon_rect.collidepoint(*self.window.mouse_pos) and not self.setting:
            self.touch_time = -time.time()-min(0.5, abs(time.time()-self.touch_time))
        if self.setting:
            self.setvalue(
                min(1, max(0, (self.window.mouse_pos[0]-self.bar_rect.left)/self.length)))
        alpha = int((min(0.5, time.time()-self.touch_time) if self.touch_time
                    > 0 else max(0, -time.time()-self.touch_time))*510)
        alpha_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(alpha_surface, (*self.window.main_color,
                           alpha), (self.size//2, self.size//2), self.size//2)
        self.icon_rect.midbottom = (
            self.bar_rect.left+self.bar_rect.width*self.getvalue(), self.bar_rect.centery)
        self.window.screen.blit(alpha_surface, self.icon_rect)
        self.window.screen.blit(self.icon, self.icon_rect)
        return self.bar_rect

    def move(self, pos: tuple) -> None:
        self.bar_rect = self.bar.get_rect()
        exec(f'self.bar_rect.{self.align}=pos')

    def process_click_event(self, mouse_pos: tuple) -> None:
        if self.icon_rect.collidepoint(*mouse_pos):
            self.setting = True

    def process_release_event(self) -> None:
        self.setting = False


class Sidebar:
    def __init__(self, window: Window) -> None:
        self.window = window
        self.pages = {'home': '主页', 'settings': '设置', 'about': '关于'}
        self.icons = {name: pygame.transform.scale(pygame.image.load(
            os.path.join(RESOURCES, 'icons', name+'.png')), size) for name, size in
            [('settings', (50, 50)), ('return', (50, 50)), ('change', (65, 30)), ('set', (65, 30))]}
        self.buttons = {}
        self.sliders = {}
        self.open('home')

    def draw(self) -> None:
        start = self.window.draw_text(
            self.pages[self.page], (SIDEBAR_MID, 10-max(0, 1-(time.time()-self.page_open_time)/0.3)**2*100), 'midtop', 3).bottom
        if self.page == 'home':
            self.draw_home(start)
        elif self.page == 'settings':
            self.draw_settings(start)
        elif self.page == 'about':
            self.draw_about(start)

    def draw_home(self, start) -> None:
        self.window.draw_text(
            '欢迎使用抛物线演示器!', (SIDEBAR_LEFT+10, start+20), 'topleft')
        self.buttons['settings'].draw()

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
        start = self.window.draw_text(
            '当前背景:'+self.window.background, (SIDEBAR_LEFT+10, t.bottom), 'topleft', 0).bottom

        if self.window.bg_mode == 'image':
            start = self.window.draw_text(
                '蒙版不透明度:'+str(self.window.mask_alpha), (SIDEBAR_LEFT+10, start+10), 'topleft').bottom
            if 'change_mask_alpha' not in self.sliders:
                self.sliders['change_mask_alpha'] = Slider(
                    self.window, (SIDEBAR_LEFT+10, start+15), WINDOW_SIZE[0]-SIDEBAR_LEFT-20, 10, 'topleft', 20, lambda: self.window.mask_alpha/255, self.window.set_mask_alpha)
            else:
                self.sliders['change_mask_alpha'].move(
                    (SIDEBAR_LEFT+10, start+15))
            start = self.sliders['change_mask_alpha'].draw().bottom

        t = self.window.draw_text(
            '主题颜色:'+self.window.main_color_hex, (SIDEBAR_LEFT+10, start+10), 'topleft')
        if 'set_main_color' not in self.buttons:
            self.buttons['set_main_color'] = Button(self.window, self.icons['set'], (
                WINDOW_SIZE[0]-10, t.centery), 'midright', self.window.set_main_color, 'rect')
        else:
            self.buttons['set_main_color'].move((WINDOW_SIZE[0]-10, t.centery))
        self.buttons['set_main_color'].draw()

    def draw_about(self, start) -> None:
        pass

    def open(self, page) -> None:
        self.page = page
        self.page_open_time = time.time()
        if page == 'home':
            self.open_home()
        elif page == 'settings':
            self.open_settings()
        elif page == 'about':
            self.open_about()

    def open_home(self) -> None:
        self.buttons = {'settings': Button(self.window, self.icons['settings'],
                                           (WINDOW_SIZE[0]-60, WINDOW_SIZE[1]-60), 'topleft', lambda: self.open('settings'), 'circle')}
        self.sliders = {}

    def open_settings(self) -> None:
        self.buttons = {'return': Button(self.window, self.icons['return'],
                                         (SIDEBAR_LEFT+10, 10), 'topleft', lambda: self.open('home'), 'circle')}
        self.sliders = {}

    def open_about(self) -> None:
        pass


if __name__ == '__main__':
    cp = ConfigParser()
    if os.path.isfile('config.ini'):
        try:
            cp.read('config.ini', encoding='utf-8')
        except:
            pass
    window = Window(cp)
    sidebar = Sidebar(window)

    while True:
        window.draw_frame()
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
                    slider.process_release_event()
