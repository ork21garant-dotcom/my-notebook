from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from datetime import datetime
import os
import json

# Шифрование
try:
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except:
    HAS_CRYPTO = False

Window.clearcolor = (0.93, 0.93, 0.95, 1)

FILE = 'notes_encrypted.json'
KEY_FILE = 'secret.key'

class NotebookApp(App):
    def build(self):
        self.root = BoxLayout(orientation='vertical', padding=15, spacing=12)
        
        # Заголовок
        title = Label(
            text='MY NOTEBOOK',
            font_size=72,
            color=(0.15, 0.35, 0.75, 1),
            bold=True,
            size_hint=(1, 0.08)
        )
        
        # Поле ввода
        self.input = TextInput(
            hint_text='Write note or password...',
            font_size=56,
            multiline=True,
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            cursor_color=(0.2, 0.5, 0.9, 1),
            size_hint=(1, 0.22)
        )
        
        # Категория (Spinner)
        self.category = Spinner(
            text='General',
            values=('General', 'Work', 'Personal', 'Passwords', 'Shopping'),
            font_size=44,
            size_hint=(1, 0.08),
            background_color=(0.9, 0.9, 1, 1)
        )
        
        # Кнопка добавить
        btn_add = Button(
            text='+ ADD NOTE',
            font_size=52,
            background_color=(0.2, 0.7, 0.3, 1),
            color=(1, 1, 1, 1),
            size_hint=(1, 0.1)
        )
        btn_add.bind(on_press=self.add_note)
        
        # Поиск
        self.search = TextInput(
            hint_text='Search...',
            font_size=48,
            multiline=False,
            background_color=(1, 0.97, 0.85, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            size_hint=(1, 0.08)
        )
        self.search.bind(text=self.on_search)
        
        # Кнопка экспорта
        btn_export = Button(
            text='EXPORT ALL',
            font_size=44,
            background_color=(0.6, 0.4, 0.8, 1),
            color=(1, 1, 1, 1),
            size_hint=(1, 0.08)
        )
        btn_export.bind(on_press=self.export_notes)
        
        # Список заметок
        self.scroll = ScrollView(size_hint=(1, 1))
        self.list = StackLayout(orientation='tb-lr', spacing=12, padding=5)
        self.scroll.add_widget(self.list)
        
        self.root.add_widget(title)
        self.root.add_widget(self.input)
        self.root.add_widget(self.category)
        self.root.add_widget(btn_add)
        self.root.add_widget(self.search)
        self.root.add_widget(btn_export)
        self.root.add_widget(self.scroll)
        
        self.load_notes()
        return self.root
    
    def get_key(self):
        """Получить или создать ключ шифрования"""
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(KEY_FILE, 'wb') as f:
                f.write(key)
            return key
    
    def encrypt_text(self, text):
        """Зашифровать текст"""
        if HAS_CRYPTO:
            key = self.get_key()
            f = Fernet(key)
            return f.encrypt(text.encode()).decode()
        return text
    
    def decrypt_text(self, text):
        """Расшифровать текст"""
        if HAS_CRYPTO:
            try:
                key = self.get_key()
                f = Fernet(key)
                return f.decrypt(text.encode()).decode()
            except:
                return text
        return text
    
    def add_note(self, *a):
        text = self.input.text.strip()
        if text:
            date = datetime.now().strftime("%d.%m.%Y %H:%M")
            category = self.category.text
            
            # Шифруем только если категория "Passwords"
            encrypted = False
            save_text = text
            if category == 'Passwords' and HAS_CRYPTO:
                save_text = self.encrypt_text(text)
                encrypted = True
            
            notes = self.read()
            notes.append({
                'date': date,
                'text': save_text,
                'category': category,
                'encrypted': encrypted
            })
            self.write(notes)
            self.input.text = ''
            self.load_notes()
    
    def on_search(self, *a):
        self.load_notes(self.search.text if self.search.text else None)
    
    def load_notes(self, filt=None):
        self.list.clear_widgets()
        notes = self.read()
        
        if filt:
            notes = [n for n in notes if filt.lower() in n.get('text', '').lower() 
                     or filt.lower() in n.get('category', '').lower()]
        
        if not notes:
            lab = Label(
                text='No notes',
                font_size=60,
                color=(0.5, 0.5, 0.5, 1),
                size_hint=(1, None),
                height=150
            )
            self.list.add_widget(lab)
            return
        
        # Цвета категорий
        cat_colors = {
            'General': (0.5, 0.5, 0.5, 1),
            'Work': (0.2, 0.5, 0.9, 1),
            'Personal': (0.9, 0.5, 0.2, 1),
            'Passwords': (0.9, 0.2, 0.2, 1),
            'Shopping': (0.2, 0.7, 0.3, 1)
        }
        
        for i, n in enumerate(reversed(notes)):
            card = BoxLayout(
                orientation='vertical',
                spacing=8,
                size_hint=(1, None),
                height=360,
                padding=12
            )
            
            # Дата и категория
            cat = n.get('category', 'General')
            cat_color = cat_colors.get(cat, (0.5, 0.5, 0.5, 1))
            date_text = f"{n['date']} [{cat}]"
            if n.get('encrypted'):
                date_text += ' 🔒'
            
            date_lab = Label(
                text=date_text,
                font_size=44,
                color=cat_color,
                size_hint=(1, 0.15),
                halign='left',
                bold=True
            )
            
            # Текст заметки (расшифровываем если нужно)
            display_text = n['text']
            if n.get('encrypted'):
                display_text = self.decrypt_text(n['text'])
            
            text_inp = TextInput(
                text=display_text,
                font_size=56,
                readonly=True,
                background_color=(1, 1, 1, 1),
                foreground_color=(0.1, 0.1, 0.1, 1),
                size_hint=(1, 0.6),
                multiline=True
            )
            
            # Кнопки
            btns = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.25))
            
            btn_copy = Button(
                text='Copy',
                font_size=44,
                background_color=(0.2, 0.5, 0.9, 1),
                color=(1, 1, 1, 1)
            )
            btn_copy.bind(on_press=lambda x, t=display_text: self.copy(t))
            
            btn_del = Button(
                text='Delete',
                font_size=44,
                background_color=(0.85, 0.2, 0.2, 1),
                color=(1, 1, 1, 1)
            )
            idx = len(notes) - 1 - i
            btn_del.bind(on_press=lambda x, j=idx: self.delete(j))
            
            btns.add_widget(btn_copy)
            btns.add_widget(btn_del)
            
            card.add_widget(date_lab)
            card.add_widget(text_inp)
            card.add_widget(btns)
            self.list.add_widget(card)
    
    def copy(self, text):
        Clipboard.copy(text)
        self.show_popup('Copied!', 'Text copied to clipboard')
    
    def delete(self, idx):
        notes = self.read()
        if 0 <= idx < len(notes):
            notes.pop(idx)
            self.write(notes)
            self.load_notes(self.search.text if self.search.text else None)
    
    def export_notes(self, *a):
        notes = self.read()
        export_text = ''
        for n in notes:
            display = n['text']
            if n.get('encrypted'):
                display = self.decrypt_text(n['text'])
            export_text += f"[{n.get('category', 'General')}] {n['date']}\n{display}\n\n"
        
        with open('exported_notes.txt', 'w', encoding='utf-8') as f:
            f.write(export_text)
        
        self.show_popup('Exported!', f'All notes saved to exported_notes.txt\nTotal: {len(notes)} notes')
    
    def show_popup(self, title, text):
        content = BoxLayout(orientation='vertical', spacing=20, padding=20)
        lab = Label(text=text, font_size=48, color=(0.1, 0.1, 0.1, 1))
        btn = Button(text='OK', font_size=44, size_hint=(1, 0.3), background_color=(0.2, 0.5, 0.9, 1))
        content.add_widget(lab)
        content.add_widget(btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.9, 0.5))
        btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def read(self):
        if os.path.exists(FILE):
            with open(FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def write(self, notes):
        with open(FILE, 'w', encoding='utf-8') as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    NotebookApp().run()
