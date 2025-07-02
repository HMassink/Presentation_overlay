from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import os
import sys
if sys.platform == 'win32':
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    SetWindowLong = user32.SetWindowLongW
    GetWindowLong = user32.GetWindowLongW
    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020
    def set_click_through(hwnd, enable):
        ex_style = GetWindowLong(hwnd, GWL_EXSTYLE)
        if enable:
            ex_style |= WS_EX_LAYERED | WS_EX_TRANSPARENT
        else:
            ex_style &= ~(WS_EX_TRANSPARENT)
        SetWindowLong(hwnd, GWL_EXSTYLE, ex_style)
    # Globale sneltoets voor click-through uitzetten
    try:
        import keyboard
    except ImportError:
        keyboard = None
    def setup_global_hotkey(overlay):
        if keyboard is not None:
            def disable_click_through():
                overlay.click_through = False
                overlay.setAttribute(Qt.WA_TransparentForMouseEvents, False)
                hwnd = int(overlay.winId())
                set_click_through(hwnd, False)
                overlay.setFocus()
                overlay.activateWindow()
            keyboard.add_hotkey('ctrl+alt+t', disable_click_through)
        else:
            print('keyboard-module niet geïnstalleerd, globale sneltoets werkt niet.')
else:
    def set_click_through(hwnd, enable):
        pass
    def setup_global_hotkey(overlay):
        pass

class TextOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.scale_factor, self.transparency_factor, self.margin_left, self.margin_top, self.logo_scale, self.screen_index, self.text_slides = self.load_config_and_slides("slides.txt")
        self.current_slide = 0
        self.click_through = False
        self.setup_ui()
        self.setup_tray()

    def load_config_and_slides(self, filename):
        scale = 1.0
        transparency = 1.0
        margin_left = 60
        margin_top = 0
        logo_scale = 1.0
        screen_index = 0
        slides = []
        if not os.path.exists(filename):
            return scale, transparency, margin_left, margin_top, logo_scale, screen_index, [["Geen slides gevonden", []]]
        with open(filename, encoding="utf-8") as f:
            lines = [l for l in f.readlines() if not l.strip().startswith('#')]
        # Check for scale, transparency, margin_left, margin_top, logo_scale, screen_index on first lines
        if lines and lines[0].strip().replace('.', '', 1).isdigit():
            scale = float(lines[0].strip())
            lines = lines[1:]
        if lines and lines[0].strip().replace('.', '', 1).isdigit():
            transparency = float(lines[0].strip())
            lines = lines[1:]
        if lines and lines[0].strip().isdigit():
            margin_left = int(lines[0].strip())
            lines = lines[1:]
        if lines and lines[0].strip().isdigit():
            margin_top = int(lines[0].strip())
            lines = lines[1:]
        if lines and lines[0].strip().replace('.', '', 1).isdigit():
            logo_scale = float(lines[0].strip())
            lines = lines[1:]
        if lines and lines[0].strip().isdigit():
            screen_index = int(lines[0].strip())
            lines = lines[1:]
        content = ''.join(lines)
        raw_slides = [s.strip() for s in content.split("\n\n") if s.strip()]
        for raw in raw_slides:
            lns = raw.splitlines()
            if not lns:
                continue
            title = lns[0].strip()
            bullets = [l[2:].strip() for l in lns[1:] if l.strip().startswith("-") or l.strip().startswith("*")]
            slides.append([title, bullets])
        return scale, transparency, margin_left, margin_top, logo_scale, screen_index, slides

    def setup_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: transparent;")

        # Achtergrondlabel (half-transparant wit)
        self.bg_label = QLabel(self)
        alpha = int(self.transparency_factor * 255)
        self.bg_label.setStyleSheet(f"background: rgba(255,255,255,{alpha});")
        self.bg_label.setGeometry(0, 0, 1, 1)  # Wordt geschaald in resizeEvent
        self.bg_label.lower()

        # Avans logo linksonder
        self.logo_label = QLabel(self)
        self.logo_label.setStyleSheet("background: transparent;")
        self.logo_pixmap = None
        try:
            pixmap = QPixmap("Avans.svg")
            if not pixmap.isNull():
                self.logo_pixmap = pixmap
        except Exception:
            pass
        self.logo_label.raise_()  # Zorg dat logo boven bg staat

        # Tekstlabel voor de slide
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setFocusPolicy(Qt.NoFocus)
        self.label.setStyleSheet(f"background: transparent;")
        self.label.setWordWrap(True)

        # Status label linksboven
        self.status_label = QLabel(self)
        self.status_label.setStyleSheet("color: black; background: rgba(255,255,255,0.7); padding: 4px; font-size: 12px;")
        self.status_label.move(10, 10)
        self.status_label.setFixedWidth(700)
        self.status_label.setFixedHeight(24)
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_label.setAttribute(Qt.WA_TranslucentBackground)
        self.status_label.setFocusPolicy(Qt.NoFocus)

        # Maak het venster schermvullend op het gekozen scherm
        app = QApplication.instance()
        screens = app.screens()
        if len(screens) == 1:
            screen = app.primaryScreen()
        elif 0 <= self.screen_index < len(screens):
            screen = screens[self.screen_index]
        else:
            screen = app.primaryScreen()
        rect = screen.geometry()
        self.setGeometry(rect)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        self.show_slide(0)
        self.show()

    def resizeEvent(self, event):
        # Schaal de achtergrondlabel altijd mee
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        # Zet logo linksonder, schaal met logo_scale, max 200px breed
        if self.logo_pixmap:
            max_width = int(200 * self.logo_scale)
            scaled_pixmap = self.logo_pixmap.scaledToWidth(max_width, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
            logo_w = scaled_pixmap.width()
            logo_h = scaled_pixmap.height()
            self.logo_label.setFixedSize(logo_w, logo_h)
            self.logo_label.move(10, self.height() - logo_h - 10)
        # Pas ook de tekstlabel aan bij resize
        self.show_slide(self.current_slide)
        super().resizeEvent(event)

    def show_slide(self, slide_index):
        if 0 <= slide_index < len(self.text_slides):
            self.current_slide = slide_index
            title, bullets = self.text_slides[slide_index]
            tsize = int(50 * self.scale_factor)
            bsize = int(25 * self.scale_factor)
            html = f'<div style="text-align:left;">'
            html += f'<div style="color:#b71234;font-family:Arial,sans-serif;font-size:{tsize}px;font-weight:bold;font-style:italic;margin-bottom:32px;">{title}</div>'
            if bullets:
                html += '<table>'
                for b in bullets:
                    html += f'<tr><td style="color:#111;font-family:Arial,sans-serif;font-size:{bsize}px;padding-bottom:8px;" align="left">&#8226; {b}</td></tr>'
                html += '</table>'
            html += '</div>'
            # Zet het label fysiek op de juiste plek
            label_width = self.width() - self.margin_left - 20
            label_height = self.height() - self.margin_top - 20
            self.label.setText(html)
            self.label.setGeometry(self.margin_left, self.margin_top, label_width, label_height)
            click_status = "AAN" if self.click_through else "UIT"
            self.status_label.setText(f"Schaal: {self.scale_factor} | Transparantie: {int(self.transparency_factor*100)}% | Margin: {self.margin_left}px | Margin-top: {self.margin_top}px | Click-through: {click_status}")
            self.status_label.raise_()
            self.label.raise_()
        # Update de achtergrondtransparantie
        alpha = int(self.transparency_factor * 255)
        self.bg_label.setStyleSheet(f"background: rgba(255,255,255,{alpha});")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.show_slide(self.current_slide - 1)
        elif event.key() == Qt.Key_Right:
            self.show_slide(self.current_slide + 1)
        elif event.key() == Qt.Key_Escape:
            self.close()
            QApplication.quit()
        elif event.key() == Qt.Key_Home:
            self.show_slide(0)
        elif event.key() == Qt.Key_End:
            self.show_slide(len(self.text_slides) - 1)
        elif event.key() == Qt.Key_T:
            self.click_through = not self.click_through
            self.setAttribute(Qt.WA_TransparentForMouseEvents, self.click_through)
            self.show_slide(self.current_slide)
            # Windows native click-through
            if sys.platform == 'win32':
                hwnd = int(self.winId())
                set_click_through(hwnd, self.click_through)
            # Update tray menu
            self.action_toggle.setChecked(self.click_through)
            if self.click_through:
                self.action_toggle.setText("Click-through uit")
            else:
                self.action_toggle.setText("Click-through aan")
            if not self.click_through:
                self.setFocus()
                self.activateWindow()

    def wheelEvent(self, event):
        # Pas transparantie aan met muiswiel
        delta = event.angleDelta().y()
        if delta > 0:
            self.transparency_factor = min(1.0, self.transparency_factor + 0.05)
        else:
            self.transparency_factor = max(0.05, self.transparency_factor - 0.05)
        self.show_slide(self.current_slide)

    def setup_tray(self):
        self.tray = QSystemTrayIcon(self)
        from PyQt5.QtWidgets import QStyle
        icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray.setIcon(icon)
        menu = QMenu()
        self.action_toggle = QAction("Click-through aan", self, checkable=True)
        self.action_toggle.setChecked(self.click_through)
        self.action_toggle.triggered.connect(self.toggle_click_through_from_tray)
        menu.addAction(self.action_toggle)
        action_quit = QAction("Afsluiten", self)
        action_quit.triggered.connect(QApplication.quit)
        menu.addAction(action_quit)
        self.tray.setContextMenu(menu)
        self.tray.setToolTip("Overlay controller")
        self.tray.show()

    def toggle_click_through_from_tray(self):
        self.click_through = not self.click_through
        self.setAttribute(Qt.WA_TransparentForMouseEvents, self.click_through)
        self.show_slide(self.current_slide)
        # Windows native click-through
        if sys.platform == 'win32':
            hwnd = int(self.winId())
            set_click_through(hwnd, self.click_through)
        # Update menu
        self.action_toggle.setChecked(self.click_through)
        if self.click_through:
            self.action_toggle.setText("Click-through uit")
        else:
            self.action_toggle.setText("Click-through aan")
        if not self.click_through:
            self.setFocus()
            self.activateWindow()

def show_intro_image(image_path):
    class IntroWindow(QWidget):
        def __init__(self, image_path):
            super().__init__()
            self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
            self.setWindowState(Qt.WindowFullScreen)
            self.setStyleSheet("background: black;")
            label = QLabel(self)
            self.label = label
            label.setAlignment(Qt.AlignCenter)
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                screen = QApplication.primaryScreen()
                rect = screen.geometry()
                scaled = pixmap.scaled(rect.width(), rect.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label.setPixmap(scaled)
            else:
                label.setText("dia1.jpg niet gevonden")
                label.setStyleSheet("color: white; font-size: 48px;")
            label.setGeometry(0, 0, self.width(), self.height())

        def resizeEvent(self, event):
            if hasattr(self, 'label') and self.label is not None:
                self.label.setGeometry(0, 0, self.width(), self.height())
            super().resizeEvent(event)

        def keyPressEvent(self, event):
            self.close()

        def mousePressEvent(self, event):
            self.close()

    intro = IntroWindow(image_path)
    intro.show()
    app = QApplication.instance()
    while intro.isVisible():
        app.processEvents()

if __name__ == '__main__':
    app = QApplication([])
    # Toon eerst dia1.jpg fullscreen
    show_intro_image("dia1.jpg")
    overlay = TextOverlay()
    app.exec_() 


# pyinstaller --onefile --windowed --add-data "Avans.svg;." overlay_text.py

# venv\\Scripts\\activate
# python overlay_text.py

# .\build_overlay.bat