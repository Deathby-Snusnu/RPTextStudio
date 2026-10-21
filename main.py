from __future__ import annotations
import sys
import zipfile
import copy
from translation_links import LANGS, pool_id, read_links, write_links, reference, resolve
from pathlib import Path
from lua_text import parse_pools,update_file,validate_file,ParseError
from key_creation import new_spell
from key_deletion import spell_path, delete_from_files, prepare_deletion
from race_class_manager import load_registry, register, add_lua_profile, discover_targets
from spell_manager import COMMANDS, candidate_keys, load_mappings, save_mappings, make_macro
try:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QAction
    from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,
        QTreeWidget,QTreeWidgetItem,QListWidget,QListWidgetItem,QPlainTextEdit,QPushButton,
        QFileDialog,QMessageBox,QLabel,QLineEdit,QSplitter,QComboBox,QGroupBox,
        QFormLayout,QStatusBar,QDialog,QDialogButtonBox,QCheckBox,QTextBrowser,QSpinBox)
except ImportError as exc:
    print('PySide6 is required. Install with: pip install -r requirements.txt')
    raise SystemExit(1) from exc


class Studio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('RP Text Studio 0.1.12')
        self.resize(1320,800)
        self.root:Path|None=None
        self.files:dict[Path,dict]={}
        self.changes:dict[Path,dict[tuple[str,...],list[str]]]={}
        self.current=None
        self.active_entries=[]
        self.current_row=-1
        self.loading=False
        self.compare_loading=False
        self.compare_editors={}
        self.compare_labels={}
        self.compare_positions={}
        self.links={}
        self.links_dirty=False
        self.link_mode=False
        self.setup()

    def setup(self):
        center=QWidget();self.setCentralWidget(center)
        main=QVBoxLayout(center)
        bar=QHBoxLayout()
        for label,cb in [('Projektordner öffnen',self.open_folder),('ZIP als Projekt entpacken',self.open_zip),('Änderungen speichern',self.save_all),('Alles prüfen',self.validate_all),('Neuen Schlüssel anlegen',self.create_key),('Schlüssel löschen',self.delete_key),('Zauber-Manager',self.open_spell_manager),('Rassen-/Klassen-Manager',self.open_race_class_manager)]:
            b=QPushButton(label);b.clicked.connect(cb);bar.addWidget(b)
            b.setToolTip({"Projektordner öffnen":"Vorhandenen entpackten AddOn-Projektordner laden.","ZIP als Projekt entpacken":"AddOn-ZIP in ein leeres Arbeitsverzeichnis entpacken und dort bearbeiten.","Änderungen speichern":"Geänderte Textpools speichern. Vorher wird je Datei ein Backup angelegt.","Alles prüfen":"Alle Texte einschließlich ungespeicherter Änderungen auf häufige Probleme kontrollieren.","Neuen Schlüssel anlegen":"Neuen Rassen-, Klassen-, Rasse-Klasse- oder allgemeinen Zauberschlüssel in den vorhandenen Locale-Dateien anlegen.","Schlüssel löschen":"Entfernt den gewählten Text-/Zauberschlüssel nach Vorschau und Bestätigung in den entsprechenden Sprachdateien. Erstellt Backups.","Zauber-Manager":"Ordnet WoW-Zaubern RP-Textschlüssel zu und erzeugt passende manuelle Makros.","Rassen-/Klassen-Manager":"Verwaltet Rassen und Klassen samt RP-Stilprofil und legt auf Wunsch Textzweige in vorhandenen Lua-Dateien an."}[label])
        bar.addStretch()
        main.addLayout(bar)
        filters=QHBoxLayout()
        self.addonfilter=QComboBox();self.addonfilter.addItem('Alle AddOns');self.addonfilter.setToolTip('Nur Textpools dieses AddOns anzeigen.')
        self.addonfilter.currentIndexChanged.connect(self.rebuild_tree)
        self.language=QComboBox();self.language.addItems(LANGS);self.language.setToolTip('Sprache für die Textpool-Navigation. Im Sprachvergleich werden alle drei Sprachen gezeigt.');self.language.currentIndexChanged.connect(self.rebuild_tree)
        self.racefilter=QComboBox();self.racefilter.addItem('Alle Rassen');self.racefilter.setToolTip('Rassenspezifische Textpools in Racial.lua und AmbientRacial.lua filtern. Allgemeine Texte sind separat über Dateityp wählbar.');self.racefilter.currentIndexChanged.connect(self.rebuild_tree)
        self.kindfilter=QComboBox();self.kindfilter.addItems(['Alle Textarten','Allgemein (Texts.lua)','Rassen (Racial.lua)','Ambient (Ambient.lua)','Ambient nach Rasse (AmbientRacial.lua)']);self.kindfilter.setToolTip('Nur allgemeine, rassenbezogene oder Ambient-Textpools anzeigen.');self.kindfilter.currentIndexChanged.connect(self.rebuild_tree)
        self.search=QLineEdit();self.search.setPlaceholderText('Schlüssel oder Text suchen ...');self.search.setToolTip('Filtert die Textpool-Liste nach Schlüsseln und Textinhalt der gewählten Navigationssprache.');self.search.textChanged.connect(self.rebuild_tree)
        filters.addWidget(QLabel('Addon:'));filters.addWidget(self.addonfilter)
        filters.addWidget(QLabel('Sprache:'));filters.addWidget(self.language)
        filters.addWidget(QLabel('Textart:'));filters.addWidget(self.kindfilter)
        filters.addWidget(QLabel('Rasse:'));filters.addWidget(self.racefilter)
        filters.addWidget(self.search,1)
        main.addLayout(filters)
        splitter=QSplitter(Qt.Horizontal)
        self.tree=QTreeWidget();self.tree.setToolTip('Textpool auswählen: AddOn → Datei → Fähigkeit/Kategorie.');self.tree.setHeaderLabels(['Textpool','Anzahl']);self.tree.setAlternatingRowColors(True)
        self.tree.itemSelectionChanged.connect(self.change_pool)
        splitter.addWidget(self.tree)
        middle=QWidget();m=QVBoxLayout(middle)
        m.addWidget(QLabel('Texte (Doppelklick zur Auswahl)'))
        self.list=QListWidget();self.list.setToolTip('Ausgangstext auswählen. Andere Sprachen werden im Sprachvergleich ausdrücklich über deren Dropdowns zugeordnet.');self.list.currentRowChanged.connect(self.select_row);m.addWidget(self.list,1)
        row=QHBoxLayout()
        for label,func in [('Neu',self.add_entry),('Duplizieren',self.duplicate),('Entfernen',self.remove_entry),('↑',lambda:self.move_entry(-1)),('↓',lambda:self.move_entry(1))]:
            b=QPushButton(label);b.clicked.connect(func);row.addWidget(b)
            b.setToolTip({"Neu":"Neue Zeile am Ende dieses Sprachpools anlegen.","Duplizieren":"Ausgewählte Textzeile duplizieren.","Entfernen":"Ausgewählte Textzeile löschen (mindestens eine bleibt erhalten).","↑":"Ausgewählten Text eine Position nach oben verschieben.","↓":"Ausgewählten Text eine Position nach unten verschieben."}[label])
        m.addLayout(row);splitter.addWidget(middle)
        right=QWidget();r=QVBoxLayout(right)
        r.addWidget(QLabel('Text bearbeiten'))
        self.editor=QPlainTextEdit();self.editor.setToolTip('Text bearbeiten: normale Texte erscheinen als /say, *umklammerte Texte* als /me.');self.editor.setPlaceholderText('Text auswählen oder Neu anklicken')
        self.editor.textChanged.connect(self.edit_entry);r.addWidget(self.editor,1)
        r.addWidget(QLabel('Vorschau des aktuellen Textes'))
        self.preview=QLabel('');self.preview.setWordWrap(True);self.preview.setMinimumHeight(90)
        self.preview.setStyleSheet('QLabel { border: 1px solid palette(mid); padding: 10px; }')
        r.addWidget(self.preview)
        r.addWidget(QLabel('Konvention: *Handlung* = /me · normaler Text = /say · %s = Ziel · %p = Pet/Dämon'))
        splitter.addWidget(right)
        splitter.setSizes([350,430,520]);main.addWidget(splitter,2)
        compare_group=QGroupBox('Übersetzungen zuordnen · DE | EN | FR')
        compare_group.setToolTip('In jeder Sprache eine Textvariante aus der Liste auswählen. Angezeigt und bearbeitet wird genau diese Variante. Gleiche Zeilennummer bedeutet nicht automatisch Übersetzung.')
        compare_layout=QHBoxLayout(compare_group)
        for lang in LANGS:
            column=QVBoxLayout()
            info=QLabel(lang)
            edit=QPlainTextEdit()
            edit.setPlaceholderText('Kein entsprechender Textpool oder keine Zeile vorhanden.')
            edit.setToolTip('Einzelne Zeile direkt in dieser Sprachfassung bearbeiten. Änderungen werden erst mit „Änderungen speichern“ auf die Festplatte geschrieben.')
            edit.textChanged.connect(lambda lang=lang:self.compare_changed(lang))
            position=QComboBox()
            position.setToolTip('Gewünschte Textvariante anhand des Textanfangs auswählen. Die Vorschau darunter wechselt sofort. „Keine Auswahl“ verknüpft diese Sprache nicht.')
            position.currentIndexChanged.connect(lambda _index, lang=lang:self.preview_selected_translation(lang))
            column.addWidget(info);column.addWidget(position);column.addWidget(edit,1)
            self.compare_positions[lang]=position
            container=QWidget();container.setLayout(column)
            compare_layout.addWidget(container,1)
            self.compare_editors[lang]=edit;self.compare_labels[lang]=info
        main.addWidget(compare_group,1)
        assoc=QHBoxLayout()
        self.link_switch=QCheckBox('Gespeicherte Verknüpfung anzeigen')
        self.link_switch.setToolTip('Bei Auswahl einer links markierten Zeile werden nur die bereits gespeicherten Übersetzungsvarianten vorausgewählt.')
        self.link_switch.toggled.connect(self.toggle_links)
        assoc.addWidget(self.link_switch)
        for label, func, hint in [
            ('Diese Texte verknüpfen',self.link_selected,'Verbindet den aktuellen Text mit den ausgewählten Zeilen in den anderen Sprachpools. Bestehende Zuordnungen werden nicht automatisch überschrieben.'),
            ('Zuordnung lösen',self.unlink_selected,'Entfernt nur die Übersetzungszuordnung zur aktuellen Textzeile, niemals die Lua-Texte.'),
        ]:
            button=QPushButton(label);button.clicked.connect(func);button.setToolTip(hint);assoc.addWidget(button)
        self.link_state=QLabel('Zuordnung: nicht aktiviert')
        self.link_state.setToolTip('Übersetzungsgruppen werden in einer eigenen JSON-Datei im Projektordner gespeichert.')
        assoc.addWidget(self.link_state,1)
        main.addLayout(assoc)
        help_menu=self.menuBar().addMenu('Hilfe')
        help_action=QAction('Bedienungsanleitung',self);help_action.setShortcut('F1');help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        about_action=QAction('Über RP Text Studio',self);about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        self.info=QLabel('Bitte Projektordner oder ZIP öffnen.');main.addWidget(self.info)
        self.setStatusBar(QStatusBar())

    def open_folder(self):
        folder=QFileDialog.getExistingDirectory(self,'AddOns-Hauptordner auswählen')
        if folder:self.load(Path(folder))

    def open_zip(self):
        file,_=QFileDialog.getOpenFileName(self,'AddOns-ZIP auswählen','','ZIP-Dateien (*.zip)')
        if not file:return
        target=QFileDialog.getExistingDirectory(self,'Leeren Zielordner / Arbeitsordner wählen')
        if not target:return
        path=Path(target)
        with zipfile.ZipFile(file) as z:
            # Check the entire archive before extracting anything.
            for member in z.infolist():
                dest=(path/member.filename).resolve()
                if not dest.is_relative_to(path.resolve()):
                    QMessageBox.critical(self,'Unsicheres Archiv','Ungültiger ZIP-Pfad entdeckt.');return
                if dest.exists() and not member.is_dir():
                    QMessageBox.warning(self,'Datei existiert',f'{dest} existiert bereits. Bitte leeren Arbeitsordner verwenden.');return
            z.extractall(path)
        self.load(path)

    def maybe_save(self):
        if not self.changes and not self.links_dirty:return True
        answer=QMessageBox.question(self,'Ungespeicherte Texte','Änderungen speichern?',QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel,QMessageBox.Save)
        if answer==QMessageBox.Cancel:return False
        if answer==QMessageBox.Save:return self.save_all()
        return True

    def load(self,root:Path):
        if not self.maybe_save():return
        files={};errors=[]
        for p in sorted(root.glob('*/locales/*/*.lua')):
            if p.parent.name not in LANGS or p.name=='Expansion.lua':continue
            try:
                content=p.read_text(encoding='utf-8-sig')
                pools=parse_pools(content)
                if pools:files[p]=pools
            except (OSError,UnicodeError,ParseError) as e:errors.append(f'{p}: {e}')
        if not files:
            QMessageBox.warning(self,'Keine Daten','Keine bearbeitbaren Locale-Textpools gefunden.');return
        try:
            links=read_links(root)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self,'Zuordnungen konnten nicht geladen werden',str(exc));return
        self.root=root;self.files=files;self.changes={};self.current=None
        self.links=links;self.links_dirty=False
        self.addonfilter.blockSignals(True);self.addonfilter.clear();self.addonfilter.addItem('Alle AddOns')
        self.addonfilter.addItems(sorted({p.parts[-4] for p in files}));self.addonfilter.blockSignals(False)
        self.racefilter.blockSignals(True);self.racefilter.clear();self.racefilter.addItem('Alle Rassen')
        races=sorted({key[3] for pools in files.values() for key in pools if len(key)>3 and key[2]=='racial'})
        self.racefilter.addItems(races);self.racefilter.blockSignals(False)
        self.rebuild_tree()
        self.statusBar().showMessage(f'{len(files)} Textdateien geladen. {len(errors)} Fehler.',10000)
        if errors:QMessageBox.warning(self,'Lesefehler','\n'.join(errors[:12]))

    def locale_key(self, path, key):
        # The parsed Lua key contains its language: ('localeData', 'deDE', ...).
        # Map that segment to the requested sibling language before lookup or saving.
        if len(key) > 1 and key[0] == 'localeData' and key[1] in LANGS:
            return (key[0], path.parent.name, *key[2:])
        return key

    def get_entries(self,p,key):
        key=self.locale_key(p,key)
        return self.changes.get(p,{}).get(key,self.files[p][key].entries)

    def rebuild_tree(self):
        if not self.files:return
        filter_addon=self.addonfilter.currentText();lang=self.language.currentText();query=self.search.text().casefold().strip()
        old=self.current
        race=self.racefilter.currentText();kind=self.kindfilter.currentIndex()
        self.loading=True;self.tree.clear();groups={};selected=None
        for p,pools in self.files.items():
            addon=p.parts[-4]
            if p.parent.name != lang or (filter_addon!='Alle AddOns' and addon!=filter_addon):continue
            for key,pool in pools.items():
                if kind==1 and p.name!='Texts.lua':continue
                if kind==2 and p.name!='Racial.lua':continue
                if kind==3 and p.name!='Ambient.lua':continue
                if kind==4 and p.name!='AmbientRacial.lua':continue
                if race!='Alle Rassen' and (p.name not in ('Racial.lua','AmbientRacial.lua') or len(key)<4 or key[3]!=race):continue
                entries=self.get_entries(p,key)
                friendly='/'.join(key[2:]) if len(key)>2 else '/'.join(key)
                if query and query not in friendly.casefold() and not any(query in s.casefold() for s in entries):continue
                g=groups.get((addon,p.name))
                if not g:
                    parent=groups.get((addon,None))
                    if not parent:
                        parent=QTreeWidgetItem(self.tree,[addon,'']);groups[(addon,None)]=parent
                    g=QTreeWidgetItem(parent,[p.name,'']);groups[(addon,p.name)]=g
                item=QTreeWidgetItem(g,[friendly,str(len(entries))]);item.setData(0,Qt.UserRole,(str(p),key))
                if (p,key)==old:selected=item
        self.tree.expandToDepth(1)
        self.loading=False
        if selected:self.tree.setCurrentItem(selected)
        else:
            self.current=None;self.active_entries=[];self.list.clear();self.editor.clear();self.preview.setText('');self.refresh_compare()

    def change_pool(self):
        if self.loading:return
        items=self.tree.selectedItems()
        if not items:return
        val=items[0].data(0,Qt.UserRole)
        if not val:return
        p,key=val;p=Path(p);self.current=(p,key)
        self.active_entries=list(self.get_entries(p,key));self.list_refresh(0)
        self.info.setText(str(p.relative_to(self.root))+'  ·  '+' / '.join(key))
        self.refresh_compare()

    def list_refresh(self,index=0):
        self.loading=True;self.list.clear()
        for i,s in enumerate(self.active_entries):
            prefix='⚡ /me' if s.startswith('*') and s.endswith('*') else '💬'
            self.list.addItem(f'{i+1:02d}  {prefix}  {s[:115]}')
        if self.active_entries:self.list.setCurrentRow(max(0,min(index,len(self.active_entries)-1)))
        else:self.editor.clear()
        self.loading=False
        self.select_row(self.list.currentRow())

    def select_row(self,row):
        if self.loading:return
        self.current_row=row;self.editor.blockSignals(True)
        self.editor.setPlainText(self.active_entries[row] if 0<=row<len(self.active_entries) else '')
        self.editor.blockSignals(False);self.preview_update();self.refresh_compare()

    def edit_entry(self):
        if self.loading or self.current is None or not (0<=self.current_row<len(self.active_entries)):return
        val=self.editor.toPlainText()
        self.active_entries[self.current_row]=val
        self.list.item(self.current_row).setText(f'{self.current_row+1:02d}  {"⚡ /me" if val.startswith("*") and val.endswith("*") else "💬"}  {val[:115]}')
        self.mark_dirty();self.update_link_text(self.current[0],self.current[1],self.current_row,val);self.preview_update();self.refresh_compare()

    def sync_link_indices(self,old_entries):
        if self.current is None or self.root is None:return
        p,key=self.current
        pk=self.link_key()
        lang=p.parent.name
        new_entries=self.active_entries
        for group in self.links.get(pk,[]):
            ref=group.get(lang)
            original=resolve(old_entries,ref)
            if original is None:continue
            text=ref['text']
            matches=[i for i,t in enumerate(new_entries) if t==text]
            if len(matches)==1:
                group[lang]={'index':matches[0],'text':text}
            else:
                # Ambiguous/destroyed linkage must not attach to a wrong text.
                group.pop(lang,None)
            self.links_dirty=True
        self.links[pk]=[group for group in self.links.get(pk,[]) if group]

    def mark_dirty(self):
        if self.current is None:return
        p,key=self.current
        self.changes.setdefault(p,{})[key]=list(self.active_entries)
        self.statusBar().showMessage(f'{sum(len(x) for x in self.changes.values())} geänderte Textpools, noch nicht gespeichert')

    def preview_update(self):
        s=self.editor.toPlainText();s=s.replace('%s','Grunzbert').replace('%p','Wichtelchen').replace('%%','%')
        if s.startswith('*') and s.endswith('*'):
            self.preview.setText('Dimitri '+s[1:-1])
        else:self.preview.setText('Dimitri sagt: '+s)

    def translation_path(self, lang):
        if self.current is None:return None
        p,key=self.current
        other=p.parent.parent / lang / p.name
        return other if other in self.files and self.locale_key(other,key) in self.files[other] else None

    def link_key(self):
        if self.current is None or self.root is None:return None
        p,key=self.current
        return pool_id(str(p.relative_to(self.root)),key)

    def group_at_current(self):
        pk=self.link_key()
        if pk is None or self.current_row < 0:return None
        current_lang=self.current[0].parent.name
        entries=self.get_entries(*self.current)
        for group in self.links.get(pk,[]):
            if resolve(entries,group.get(current_lang)) == self.current_row:
                return group
        return None

    def toggle_links(self,value):
        self.link_mode=value
        self.refresh_compare()

    def link_selected(self):
        if self.current is None or self.current_row < 0 or self.root is None:
            QMessageBox.information(self,'Text wählen','Bitte zuerst links einen Ausgangstext auswählen.')
            return
        pk=self.link_key()
        current_lang=self.current[0].parent.name
        groups=self.links.setdefault(pk,[])
        selected={current_lang:reference(self.get_entries(*self.current),self.current_row)}
        for lang in LANGS:
            if lang==current_lang:continue
            path=self.translation_path(lang)
            row=self.compare_positions[lang].currentData()
            if path is None or row is None:continue
            entries=self.get_entries(path,self.current[1])
            if 0<=row<len(entries):selected[lang]=reference(entries,row)
        if len(selected)<2:
            QMessageBox.information(self,'Übersetzung auswählen',
                'Wähle mindestens eine weitere Sprache im Dropdown aus.\n'
                'Die angezeigten Texte werden anschließend miteinander verbunden.')
            if not groups:self.links.pop(pk,None)
            return
        existing=self.group_at_current()
        for lang,ref in selected.items():
            path=self.translation_path(lang)
            if path is None:continue
            entries=self.get_entries(path,self.current[1])
            for other in groups:
                if other is existing:continue
                if resolve(entries,other.get(lang))==ref['index']:
                    QMessageBox.warning(self,'Bereits verknüpft',
                        f'{lang}: Diese Variante gehört bereits zu einer anderen Übersetzungsgruppe.\n'
                        'Bitte zuerst deren Zuordnung lösen.')
                    return
        if existing is None:
            groups.append(selected)
        else:
            existing.update(selected)
        self.links_dirty=True
        self.link_switch.setChecked(True)
        self.refresh_compare()
        self.statusBar().showMessage('Übersetzungen verknüpft. Mit „Änderungen speichern“ dauerhaft sichern.')

    def unlink_selected(self):
        group=self.group_at_current()
        if group is None:return
        pk=self.link_key()
        self.links[pk].remove(group)
        if not self.links[pk]:del self.links[pk]
        self.links_dirty=True
        self.refresh_compare()

    def comparison_row(self,lang):
        if self.current is None:return -1
        row=self.compare_positions[lang].currentData()
        return row if isinstance(row,int) else -1

    def preview_selected_translation(self,lang):
        if self.compare_loading or self.current is None:return
        path=self.translation_path(lang)
        row=self.comparison_row(lang)
        entries=self.get_entries(path,self.current[1]) if path is not None else []
        editor=self.compare_editors[lang]
        editor.blockSignals(True)
        selected=0<=row<len(entries)
        editor.setEnabled(selected)
        editor.setPlainText(entries[row] if selected else '')
        editor.blockSignals(False)

    def update_link_text(self,path,key,row,text):
        if self.root is None:return
        pk=pool_id(str(path.relative_to(self.root)),key)
        for group in self.links.get(pk,[]):
            ref=group.get(path.parent.name)
            if ref and ref.get('index')==row:
                group[path.parent.name]={'index':row,'text':text}
                self.links_dirty=True

    def refresh_compare(self):
        self.compare_loading=True
        try:
            group=self.group_at_current() if self.current is not None else None
            current_lang=self.current[0].parent.name if self.current else None
            for lang,edit in self.compare_editors.items():
                path=self.translation_path(lang)
                entries=self.get_entries(path,self.current[1]) if path is not None else []
                selector=self.compare_positions[lang]
                selector.blockSignals(True)
                selector.clear()
                selector.addItem('Keine Auswahl',None)
                for index,value in enumerate(entries):
                    snippet=' '.join(value.split())[:75]
                    selector.addItem(f'{index+1:02d} · {snippet}',index)
                row=None
                if group and lang in group and path is not None:
                    row=resolve(entries,group[lang])
                elif lang==current_lang and 0<=self.current_row<len(entries):
                    row=self.current_row
                selector.setCurrentIndex(row+1 if row is not None else 0)
                selector.blockSignals(False)
                self.compare_labels[lang].setText(f'{lang} · {len(entries)} Varianten' if path else f'{lang} · kein Textpool')
                available=row is not None and 0<=row<len(entries)
                edit.blockSignals(True)
                edit.setEnabled(available)
                edit.setPlainText(entries[row] if available else '')
                edit.blockSignals(False)
            self.link_state.setText('Verbunden: '+', '.join(group.keys()) if group else 'Noch keine bestätigte Übersetzung')
        finally:self.compare_loading=False

    def compare_changed(self,lang):
        if self.compare_loading or self.current is None:return
        p=self.translation_path(lang)
        if p is None:return
        key=self.current[1];entries=list(self.get_entries(p,key))
        row=self.comparison_row(lang)
        if not isinstance(row,int) or not 0<=row<len(entries):return
        value=self.compare_editors[lang].toPlainText()
        if value==entries[row]:return
        entries[row]=value
        self.update_link_text(p,key,row,value)
        self.changes.setdefault(p,{})[self.locale_key(p,key)]=entries
        self.statusBar().showMessage(f'{sum(len(x) for x in self.changes.values())} geänderte Textpools, noch nicht gespeichert')
        if p==self.current[0] and row==self.current_row:
            self.active_entries=list(entries)
            self.loading=True
            self.editor.setPlainText(value)
            self.loading=False
            item=self.list.item(row)
            if item:item.setText(f'{row+1:02d}  {"⚡ /me" if value.startswith("*") and value.endswith("*") else "💬"}  {value[:115]}')
            self.preview_update()

    def create_key(self):
        if self.root is None:
            QMessageBox.warning(self,'Kein Projekt','Bitte zuerst einen Projektordner laden.');return
        if not self.maybe_save():return
        # Pending changes must be saved or discarded before changing structure.
        if self.changes or self.links_dirty:
            self.load(self.root)
        dlg=QDialog(self);dlg.setWindowTitle('Neuen Text-/Zauberschlüssel anlegen')
        form=QFormLayout(dlg)
        addon=QComboBox();addon.addItems(sorted({p.parts[-4] for p in self.files}))
        kind=QComboBox();kind.addItems(['Rasse (Racial.lua)','Klasse (Classes.lua)','Rasse + Klasse (RaceClass.lua)','Allgemein (Texts.lua)'])
        race=QLineEdit();race.setPlaceholderText('z. B. Gnome, Dwarf, Orc')
        klass=QLineEdit();klass.setPlaceholderText('z. B. WARLOCK, PALADIN')
        spell=QLineEdit();spell.setPlaceholderText('z. B. CURSE_RECKLESSNESS')
        for label,control,hint in [
            ('AddOn',addon,'Ziel-AddOn auswählen.'),
            ('Textstruktur',kind,'Bestimmt, in welcher bestehenden Lua-Datei der Schlüssel angelegt wird.'),
            ('Rasse',race,'Interne Race-ID; Groß-/Kleinschreibung beachten (z. B. Gnome).'),
            ('Klasse',klass,'Interne Class-ID; meist Großbuchstaben (z. B. WARLOCK).'),
            ('Zauber-/Aktionsschlüssel',spell,'Interner Schlüssel, z. B. DRAIN_LIFE. Muss in der AddOn-Logik verwendet werden, damit er im Spiel ausgelöst wird.')]:
            control.setToolTip(hint);form.addRow(label,control)
        def sync():
            mode=kind.currentIndex()
            race.setEnabled(mode in (0,2))
            klass.setEnabled(mode in (1,2))
        kind.currentIndexChanged.connect(sync);sync()
        notes=QLabel('Legt ziel/gruppe mit einem Platzhaltertext in allen vorhandenen Sprachdateien an.\n'
                     'Neue Zauber benötigen gegebenenfalls zusätzlich einen Eintrag im AddOn-Handler.\n'
                     'Die bestehenden Lua-Dateien werden vor jeder Änderung gesichert.')
        notes.setWordWrap(True);form.addRow(notes)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept);buttons.rejected.connect(dlg.reject);form.addRow(buttons)
        if dlg.exec()!=QDialog.Accepted:return
        name=addon.currentText();mode=kind.currentIndex()
        filename=['Racial.lua','Classes.lua','RaceClass.lua','Texts.lua'][mode]
        branches=([race.text().strip()] if mode in (0,2) else [])+([klass.text().strip()] if mode in (1,2) else [])
        key=spell.text().strip()
        if not key or any(not x for x in branches):
            QMessageBox.warning(self,'Fehlende Angaben','Bitte alle erforderlichen Schlüssel eintragen.');return
        matches=sorted(p for p in self.files if p.parts[-4]==name and p.name==filename)
        if not matches:
            QMessageBox.warning(self,'Dateistruktur fehlt',f'{name} enthält keine geladene {filename}. Eine passende Vorlage ist erforderlich.');return
        # Determine root via a real leaf pool in each language.
        targets=[]
        for path in matches:
            keys=list(self.files[path]);prefix=( 'localeData',path.parent.name)
            roots=[k[:3] for k in keys if len(k)>=4 and k[:2]==prefix]
            roots=list(dict.fromkeys(roots))
            if len(roots)!=1:
                QMessageBox.warning(self,'Mehrdeutige Struktur',f'Keine eindeutige Root-Tabelle in {path}.');return
            rootkey=roots[0]
            # Direct leaf entries (e.g. PaladinRP/Racial.lua) must remain direct.
            # Else preserve ziel/gruppe layout used by HexerRP/RPChatMod.
            samples=[k for k in keys if k[:3]==rootkey]
            has_nested=any(len(k)>=5 and k[-1] in ('ziel','gruppe') for k in samples)
            has_direct=any(len(k)>=5 and k[-1] not in ('ziel','gruppe') for k in samples) or any(len(k)==4 for k in samples)
            direct=not has_nested and has_direct
            targets.append((path,rootkey,direct))
        # Preflight on temp copies: no original touched until all languages pass.
        import tempfile
        try:
            for p,base,direct in targets:
                with tempfile.TemporaryDirectory() as tmp:
                    scratch=Path(tmp)/p.name;scratch.write_bytes(p.read_bytes())
                    new_spell(scratch,base,tuple(branches),key,backup=False,direct=direct)
            for p,base,direct in targets:
                new_spell(p,base,tuple(branches),key,backup=True,direct=direct)
        except (OSError,ValueError,ParseError) as exc:
            QMessageBox.critical(self,'Schlüssel nicht angelegt',str(exc));return
        root=self.root
        self.load(root)
        self.addonfilter.setCurrentText(name)
        self.kindfilter.setCurrentIndex([2,0,0,1][mode])
        self.racefilter.setCurrentText('Alle Rassen')
        self.search.setText(key)
        QMessageBox.information(self,'Schlüssel angelegt',f'{key} wurde in {len(targets)} Sprachdatei(en) hinzugefügt.\n'
            'Bitte die Platzhaltertexte jetzt bearbeiten und danach speichern.\n'
            'Hinweis: Ein neuer Zauberschlüssel muss von der AddOn-Logik erkannt werden, um im Spiel verwendet zu werden.')

    def delete_key(self):
        if self.root is None or self.current is None:
            QMessageBox.warning(self,'Keine Auswahl','Bitte einen Textpool im Projekt auswählen.');return
        if not self.maybe_save():return
        if self.changes or self.links_dirty:self.load(self.root)
        if self.current is None:
            QMessageBox.warning(self,'Auswahl verloren','Bitte nach dem Speichern den zu löschenden Textpool erneut wählen.');return
        path,pool=self.current
        try:
            target=spell_path(pool)
            parent=target[:-1];key=target[-1]
            targets=[];preview=[]
            for p in sorted(self.files):
                if p.parts[-4]!=path.parts[-4] or p.name!=path.name:continue
                localized=(target[0],p.parent.name,*target[2:]) if target[0]=='localeData' else target
                localized_parent=localized[:-1]
                # It is valid for a translation to be missing in a language.
                try:
                    raw=p.read_text(encoding='utf-8')
                    _,number=prepare_deletion(raw,localized_parent,key)
                except ValueError as exc:
                    if 'Parent-Schluessel fehlt' in str(exc) or 'Kein eigenstaendiger Textpool' in str(exc):continue
                    raise
                targets.append((p,localized_parent,key))
                preview.append(f'{p.parent.name}: {p.name} ({number} Textpools)')
            if not targets:raise ValueError('Dieser Schlüssel wurde in keiner passenden Sprachdatei gefunden.')
            # Do not silently delete stored macro mappings or translation groups.
            known=load_mappings(self.root)
            matches=[m for m in known if m['addon']==path.parts[-4] and m['key']==key]
            warning=('\nACHTUNG: '+str(len(matches))+' Makro-Zuordnung(en) verweisen noch auf diesen Schlüssel. '
                     'Sie werden NICHT automatisch gelöscht.\n' if matches else '')
            message=(f'Folgenden Schlüssel wirklich löschen?\n\n{path.parts[-4]} / {key}\n'
                     +'/'.join(target[2:-1])+'\n\nBetroffene Dateien:\n'+'\n'.join(preview)
                     +warning+'\nVor der Änderung werden Sicherungskopien (*.bak) angelegt.\n'
                     'Andere Rassen-/Klassenzweige bleiben erhalten.')
            answer=QMessageBox.warning(self,'Schlüssel endgültig aus Lua entfernen',message,
                                       QMessageBox.Yes|QMessageBox.Cancel,QMessageBox.Cancel)
            if answer!=QMessageBox.Yes:return
            delete_from_files(targets)
            root=self.root
            self.load(root)
            QMessageBox.information(self,'Schlüssel gelöscht',f'{key} aus {len(targets)} Sprachdatei(en) entfernt.\n'
                                    'Bei Bedarf aus den .bak-Dateien wiederherstellen.')
        except (ValueError,ParseError,OSError) as exc:
            QMessageBox.critical(self,'Schlüssel nicht gelöscht',str(exc))

    def open_race_class_manager(self):
        if self.root is None:
            QMessageBox.warning(self,'Kein Projekt','Bitte zuerst einen Projektordner laden.');return
        if not self.maybe_save():return
        dlg=QDialog(self);dlg.setWindowTitle('Rassen- und Klassen-Manager');dlg.resize(690,460)
        form=QFormLayout(dlg)
        kind=QComboBox();kind.addItems(['Rasse','Klasse'])
        addon=QComboBox();addon.addItem('Nur im Register (keine Lua-Änderung)')
        addon.addItems(sorted({p.parts[-4] for p in self.files}))
        key=QLineEdit('NightElf');display=QLineEdit('Nachtelf')
        style=QPlainTextEdit('Naturverbunden, geheimnisvoll, traditionsbewusst')
        spell=QLineEdit('RP_GREETING')
        for label,w,hint in [
            ('Typ',kind,'Neue RP-Rasse oder -Klasse auswählen.'),
            ('AddOn',addon,'Optional einen neuen Textzweig in einer vorhandenen Racial.lua oder Classes.lua anlegen.'),
            ('Interne ID',key,'Exakte Lua-/Spielkennung; Groß-/Kleinschreibung beachten. Beispiel: NightElf. Keine automatische Erkennung im Spiel.'),
            ('Anzeigename',display,'Frei wählbarer Name in der Editorverwaltung.'),
            ('RP-Sprachstil',style,'Beschreibt den Stil für spätere Texterstellung; wird nicht automatisch auf vorhandene Texte angewendet.'),
            ('Erster Textschlüssel',spell,'Beispiel: RP_GREETING. Erstellt eine bearbeitbare Platzhalter-Textliste.')]:
            w.setToolTip(hint);form.addRow(label,w)
        existing=QLabel();existing.setWordWrap(True);form.addRow('Vorhandene Profile',existing)
        def refresh():
            try:
                reg=load_registry(self.root)
                names=sorted(reg['races' if kind.currentIndex()==0 else 'classes'])
                existing.setText(', '.join(names) if names else 'Noch keine registriert')
            except (ValueError,OSError) as exc:existing.setText(str(exc))
        kind.currentIndexChanged.connect(lambda _:refresh())
        def update_compatibility():
            name=addon.currentText();k='race' if kind.currentIndex()==0 else 'class'
            if addon.currentIndex()==0:return
            try:matches=discover_targets(self.root,name,k)
            except Exception:return
            if not matches:QMessageBox.information(dlg,'Hinweis',f'{name} besitzt keine passende Textdatei. Bitte nur im Register speichern.')
        addon.currentIndexChanged.connect(lambda _:update_compatibility())
        refresh()
        explanation=QLabel('Ein Profil ist ein Editor-Eintrag. Nur mit ausgewähltem AddOn wird zusätzlich ein neuer Lua-Textzweig angelegt.\n'
                           'Spielbare Rassen/Klassen und Runtime-Erkennung müssen bereits im WoW-Client bzw. AddOn vorhanden sein.')
        explanation.setWordWrap(True);form.addRow(explanation)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept);buttons.rejected.connect(dlg.reject);form.addRow(buttons)
        if dlg.exec()!=QDialog.Accepted:return
        typ='race' if kind.currentIndex()==0 else 'class'
        ident=key.text().strip();name=display.text().strip();desc=style.toPlainText()
        selected=addon.currentText() if addon.currentIndex()>0 else None
        import tempfile
        from race_class_manager import validate_profile
        try:
            validate_profile(typ,ident,name,desc)
            reg=load_registry(self.root)
            if ident in reg['races' if typ=='race' else 'classes']:raise ValueError('ID bereits im Register vorhanden')
            if selected:
                # Dry-run on a complete temporary project before any real edit.
                targets=discover_targets(self.root,selected,typ)
                if not targets:raise ValueError('Keine unterstützte Lua-Textdatei vorhanden. Wähle Nur im Register.')
                with tempfile.TemporaryDirectory() as td:
                    temp_root=Path(td)
                    for p,base,direct in targets:
                        relative=p.relative_to(self.root);copy=temp_root/relative
                        copy.parent.mkdir(parents=True,exist_ok=True);copy.write_bytes(p.read_bytes())
                    add_lua_profile(temp_root,selected,typ,ident,spell.text().strip())
            # The Lua modifications have backups, while the registry is atomic JSON.
            if selected:add_lua_profile(self.root,selected,typ,ident,spell.text().strip())
            register(self.root,typ,ident,name,desc,[selected] if selected else [])
        except (ValueError,OSError,ParseError) as exc:
            QMessageBox.critical(self,'Profil nicht angelegt',str(exc));return
        project=self.root
        self.load(project)
        QMessageBox.information(self,'Profil angelegt',f'{name} ({ident}) angelegt.\n'
            + ('Lua-Textzweige in bestehenden Sprachdateien ergänzt.\n' if selected else 'Nur im Editor-Register gespeichert.\n')
            + 'Wichtig: Keine automatische Registrierung als spielbare Rasse/Klasse im WoW-Client.')

    def open_spell_manager(self):
        if self.root is None:
            QMessageBox.warning(self, 'Kein Projekt', 'Bitte zuerst ein AddOn-Projekt laden.')
            return
        try:
            mappings = load_mappings(self.root)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, 'Zuordnungen', str(exc))
            return
        dlg = QDialog(self)
        dlg.setWindowTitle('Zauber-Manager · Makro-Zuordnungen')
        dlg.resize(920, 600)
        layout = QVBoxLayout(dlg)
        note = QLabel('Dies sind manuelle Makro-Zuordnungen, keine automatische Zaubererkennung. '
                      'WoW-Zaubernamen müssen zur Sprache des Spielclients passen.')
        note.setWordWrap(True)
        layout.addWidget(note)
        grid = QHBoxLayout()
        addon = QComboBox()
        addon.addItems(sorted(COMMANDS))
        addon.setToolTip('Nur AddOns mit bekanntem RP-Slash-Befehl werden angeboten.')
        spell = QLineEdit()
        spell.setPlaceholderText('Zaubername im WoW-Client, z. B. Schattenblitz')
        spell.setToolTip('Genauer, lokalisierter Name des Zaubers für /cast.')
        key = QComboBox()
        key.setEditable(False)
        key.setToolTip('Existierender RP-Textschlüssel aus den geladenen Lua-Sprachdateien.')
        for label, widget in [('AddOn', addon), ('WoW-Zauber', spell), ('RP-Schlüssel', key)]:
            col = QVBoxLayout()
            col.addWidget(QLabel(label))
            col.addWidget(widget)
            grid.addLayout(col, 1)
        layout.addLayout(grid)
        rows = QListWidget()
        rows.setToolTip('Gespeicherte Verknüpfungen für dieses Projekt. Ein Doppelklick lädt die Zuordnung.')
        layout.addWidget(rows, 1)
        preview = QPlainTextEdit()
        preview.setReadOnly(True)
        preview.setToolTip('Makrovorlage zum Kopieren. Muss im WoW-Makrofenster eingefügt werden.')
        layout.addWidget(QLabel('Makro-Vorschau'))
        layout.addWidget(preview, 1)

        def refresh_keys():
            prev = key.currentText()
            key.clear()
            key.addItems(candidate_keys(self.files, addon.currentText()))
            if prev:
                key.setCurrentText(prev)
            refresh_preview()

        def refresh_rows():
            rows.clear()
            for row in mappings:
                rows.addItem(f"{row['addon']} · {row['spell']}  →  {row['key']}")

        def refresh_preview():
            try:
                macro = make_macro(addon.currentText(), spell.text().strip(), key.currentText(),
                                   candidate_keys(self.files, addon.currentText()))
            except ValueError as exc:
                preview.setPlainText(str(exc))
                return
            preview.setPlainText(macro)

        def select_row(index):
            if not 0 <= index < len(mappings):
                return
            item = mappings[index]
            addon.setCurrentText(item['addon'])
            spell.setText(item['spell'])
            key.setCurrentText(item['key'])
            refresh_preview()

        def add_mapping():
            name = addon.currentText()
            name_spell = spell.text().strip()
            value_key = key.currentText()
            try:
                make_macro(name, name_spell, value_key, candidate_keys(self.files, name))
            except ValueError as exc:
                QMessageBox.warning(dlg, 'Ungültige Zuordnung', str(exc))
                return
            entry = {'addon': name, 'spell': name_spell, 'key': value_key}
            if entry not in mappings:
                mappings.append(entry)
            refresh_rows()
            rows.setCurrentRow(mappings.index(entry))

        def remove_mapping():
            idx = rows.currentRow()
            if 0 <= idx < len(mappings):
                mappings.pop(idx)
                refresh_rows()

        def copy_macro():
            try:
                macro = make_macro(addon.currentText(), spell.text().strip(), key.currentText(),
                                   candidate_keys(self.files, addon.currentText()))
            except ValueError as exc:
                QMessageBox.warning(dlg, 'Makro nicht verfügbar', str(exc))
                return
            QApplication.clipboard().setText(macro)

        addon.currentIndexChanged.connect(refresh_keys)
        spell.textChanged.connect(refresh_preview)
        key.currentIndexChanged.connect(refresh_preview)
        rows.currentRowChanged.connect(select_row)
        buttons = QHBoxLayout()
        for label, callback, hint in [
            ('Zuordnung hinzufügen', add_mapping, 'Speichert die aktuelle Kombination in der Liste.'),
            ('Zuordnung entfernen', remove_mapping, 'Entfernt die markierte Kombination aus der Liste.'),
            ('Makro kopieren', copy_macro, 'Kopiert die Makro-Vorschau in die Zwischenablage.')]:
            button = QPushButton(label)
            button.setToolTip(hint)
            button.clicked.connect(callback)
            buttons.addWidget(button)
        layout.addLayout(buttons)
        actions = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        actions.button(QDialogButtonBox.Save).setText('Zuordnungen speichern')
        layout.addWidget(actions)
        actions.accepted.connect(dlg.accept)
        actions.rejected.connect(dlg.reject)
        refresh_keys()
        refresh_rows()
        if dlg.exec() == QDialog.Accepted:
            try:
                save_mappings(self.root, mappings)
            except OSError as exc:
                QMessageBox.critical(self, 'Speicherfehler', str(exc))
                return
            self.statusBar().showMessage(f'{len(mappings)} Makro-Zuordnungen gespeichert.', 10000)

    def show_help(self):
        dlg=QDialog(self);dlg.setWindowTitle('RP Text Studio · Hilfe');dlg.resize(760,580)
        layout=QVBoxLayout(dlg);view=QTextBrowser()
        doc=Path(__file__).with_name('HANDBUCH.md')
        if doc.exists():view.setMarkdown(doc.read_text(encoding='utf-8'))
        else:view.setPlainText('Handbuch nicht gefunden. Bitte HANDBUCH.md im Programmordner prüfen.')
        layout.addWidget(view)
        close=QPushButton('Schließen');close.clicked.connect(dlg.accept);layout.addWidget(close)
        dlg.exec()

    def show_about(self):
        QMessageBox.information(self,'Über RP Text Studio','RP Text Studio 0.1.11\nPySide6-Editor für RP-Textlisten in Lua.\nF1 öffnet die Hilfe.')

    def add_entry(self):
        if self.current is None:return
        old=list(self.active_entries);self.active_entries.append('Neuer RP-Text');self.sync_link_indices(old)
        self.mark_dirty();self.list_refresh(len(self.active_entries)-1);self.editor.setFocus();self.editor.selectAll()

    def duplicate(self):
        if self.current is None or self.list.currentRow()<0:return
        i=self.list.currentRow();old=list(self.active_entries);self.active_entries.insert(i+1,self.active_entries[i]);self.sync_link_indices(old);self.mark_dirty();self.list_refresh(i+1)

    def remove_entry(self):
        if self.current is None or self.list.currentRow()<0:return
        if len(self.active_entries)==1:
            QMessageBox.warning(self,'Letzter Text','Ein Pool darf nicht leer sein.');return
        i=self.list.currentRow();old=list(self.active_entries);self.active_entries.pop(i);self.sync_link_indices(old);self.mark_dirty();self.list_refresh(min(i,len(self.active_entries)-1))

    def move_entry(self,direction):
        if self.current is None:return
        i=self.list.currentRow();j=i+direction
        if i<0 or j<0 or j>=len(self.active_entries):return
        old=list(self.active_entries);self.active_entries[i],self.active_entries[j]=self.active_entries[j],self.active_entries[i]
        self.sync_link_indices(old);self.mark_dirty();self.list_refresh(j)

    def save_all(self):
        if not self.changes and not self.links_dirty:return True
        try:
            for p,updates in self.changes.items():
                update_file(p,updates,backup=True)
            if self.links_dirty and self.root is not None:
                write_links(self.root,self.links)
            changed=len(self.changes)
            self.load_after_save()
            QMessageBox.information(self,'Gespeichert',f'{changed} Lua-Datei(en) gespeichert; Zuordnungen bei Bedarf aktualisiert. Sicherungen für bestehende Dateien angelegt.')
            return True
        except (OSError,ValueError,ParseError) as e:
            QMessageBox.critical(self,'Speichern abgebrochen',str(e));return False

    def load_after_save(self):
        for p in self.files:
            self.files[p]=parse_pools(p.read_text(encoding='utf-8-sig'))
        self.changes={}
        self.links_dirty=False
        self.rebuild_tree()
        self.refresh_compare()
        self.statusBar().showMessage('Gespeichert und erneut eingelesen.',10000)

    def validate_all(self):
        if not self.files:return
        problems=[];n=0
        for p,pools in self.files.items():
            for key in pools:
                entries=self.get_entries(p,key);n+=1
                if not entries:problems.append(f'{p.name}:{key}: leerer Pool')
                for i,s in enumerate(entries,1):
                    if not s.strip():problems.append(f'{p.name}:{key}[{i}]: leer')
                    if s.startswith('*') != s.endswith('*'):problems.append(f'{p.name}:{key}[{i}]: ungleiche Sternchen')
                    import re
                    if re.search(r'%(?![%sp])',s):problems.append(f'{p.name}:{key}[{i}]: unbekannter Platzhalter')
        if problems:
            box=QMessageBox(self);box.setWindowTitle('Prüfbericht');box.setText(f'{len(problems)} Auffälligkeit(en) in {n} Pools')
            box.setDetailedText('\n'.join(problems));box.exec()
        else:QMessageBox.information(self,'Prüfbericht',f'{n} Textpools geprüft. Keine Auffälligkeiten.')

    def closeEvent(self,event):
        if self.maybe_save():event.accept()
        else:event.ignore()

if __name__=='__main__':
    app=QApplication(sys.argv)
    win=Studio();win.show()
    if len(sys.argv)>1 and Path(sys.argv[1]).is_dir():win.load(Path(sys.argv[1]))
    sys.exit(app.exec())
