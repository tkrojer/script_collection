import os
import glob

import pygtk, gtk, pango
import coot

class GUI(object):

    def __init__(self):

        self.projectDir = None
        self.index = -1
        self.Todo = []

        self.autoproc_software = [
            'autoproc',
            'fastdp',
            'edna',
            'dials',
            'xdsapp',
            'xdsxcale'
        ]

        self.refine_software = [
            'dimple',
            'pipedream'
        ]

        self.autoproc = self.autoproc_software[0]
        self.autorefine = self.refine_software[0]


    def StartGUI(self):

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", gtk.main_quit)
        self.window.set_border_width(10)
        self.window.set_default_size(400, 600)
        self.window.set_title("browse structures")
        self.vbox = gtk.VBox()  # this is the main container

        self.vbox.add(gtk.Label('project directory (paste absolute path below)'))

        projectDir_entry = gtk.Entry()
        projectDir_entry.add_events(gtk.gdk.KEY_RELEASE_MASK)
        projectDir_entry.connect("key-release-event", self.on_key_release_projectDir)
        projectDir_entry.set_text('')
        self.vbox.add(projectDir_entry)

        self.vbox.add(gtk.Label())
        frame = gtk.Frame()
        frame.add(gtk.Label('current project directory'))
        self.vbox.add(frame)
        frame = gtk.Frame()
        self.current_project_directory_label = gtk.Label()
        frame.add(self.current_project_directory_label)
        self.vbox.add(frame)

        parseProjectDirbutton = gtk.Button(label="read project directory")
        parseProjectDirbutton.connect("clicked", self.parseProjectDir)
        self.vbox.add(parseProjectDirbutton)

        self.vbox.add(gtk.Label())

        outer_frame = gtk.Frame()
        hbox = gtk.HBox()
        frame = gtk.Frame(label='auto-processing')
        vbox = gtk.VBox()
        for n, button in enumerate(self.autoproc_software):
            if n == 0:
                new_button = gtk.RadioButton(None, button)
            else:
                new_button = gtk.RadioButton(new_button, button)
            new_button.connect("toggled", self.selected_autoprocessing)
            vbox.pack_start(new_button,False,False,0)
        frame.add(vbox)
        hbox.pack_start(frame)
        frame = gtk.Frame(label='auto-refinement')
        vbox = gtk.VBox()
        for n, button in enumerate(self.refine_software):
            if n == 0:
                new_button = gtk.RadioButton(None, button)
            else:
                new_button = gtk.RadioButton(new_button, button)
            new_button.connect("toggled", self.selected_autorefinement)
            vbox.pack_start(new_button,False,False,0)
        frame.add(vbox)
        hbox.pack_start(frame)
        outer_frame.add(hbox)
        self.vbox.pack_start(outer_frame)

        frame = gtk.Frame()
        self.number_pdb_files_found = gtk.Label()
        frame.add(self.number_pdb_files_found)
        self.vbox.add(frame)

        self.vbox.add(gtk.Label())
        self.PREVbutton = gtk.Button(label="<<<")
        self.NEXTbutton = gtk.Button(label=">>>")
        self.PREVbutton.connect("clicked", self.backward)
        self.NEXTbutton.connect("clicked", self.forward)
        hbox = gtk.HBox()
        hbox.pack_start(self.PREVbutton)
        hbox.pack_start(self.NEXTbutton)
        self.vbox.add(hbox)

        self.vbox.add(gtk.Label())
        frame = gtk.Frame()
        frame.add(gtk.Label('current folder'))
        self.vbox.add(frame)
        frame = gtk.Frame()
        self.current_folder_label = gtk.Label()
        frame.add(self.current_folder_label)
        self.vbox.add(frame)

        self.vbox.add(gtk.Label())
        frame = gtk.Frame()
        frame.add(gtk.Label('current PDB file'))
        self.vbox.add(frame)
        frame = gtk.Frame()
        self.current_pdb_label = gtk.Label()
        frame.add(self.current_pdb_label)
        self.vbox.add(frame)

        self.vbox.add(gtk.Label())
        frame = gtk.Frame()
        frame.add(gtk.Label('current MTZ file'))
        self.vbox.add(frame)
        frame = gtk.Frame()
        self.current_mtz_label = gtk.Label()
        frame.add(self.current_mtz_label)
        self.vbox.add(frame)


        self.window.add(self.vbox)
        self.window.show_all()

    def selected_autoprocessing(self, widget):
        self.autoproc = widget.get_label()
        print('selected auto-processing program: {0!s}'.format(self.autoproc))


    def selected_autorefinement(self, widget):
        self.autorefine = widget.get_label()
        print('selected auto-refinement program: {0!s}'.format(self.autorefine))

    def RefreshData(self):
        if self.index < 0:
            self.index = 0
        if self.index > len(self.Todo) - 1:
            self.index = len(self.Todo) - 1

        if len(molecule_number_list()) > 0:
            for item in molecule_number_list():
                coot.close_molecule(item)
        coot.set_nomenclature_errors_on_read("ignore")
        coot.handle_read_draw_molecule_with_recentre(self.Todo[self.index][1], 0)
        coot.auto_read_make_and_draw_maps(self.Todo[self.index][2])
        self.current_folder_label.set_label(self.Todo[self.index][0])
        self.current_pdb_label.set_label(self.Todo[self.index][3])
        self.current_mtz_label.set_label(self.Todo[self.index][4])

    def backward(self, widget):
        self.index -= 1
        self.RefreshData()

    def forward(self, widget):
        self.index += 1
        self.RefreshData()

    def parseProjectDir(self, widget):
        typical_names = ['refine', 'dimple','final']
        for pdbFile in sorted(glob.glob(os.path.join(self.projectDir,'*',self.autoproc,self.autorefine,'*.pdb'))):
            pdb = pdbFile.split('/')[len(pdbFile.split('/'))-1]
            pdbRoot = pdb.replace('.pdb','')
            folderName = pdbFile.split('/')[len(pdbFile.split('/'))-4]
            print('checking folder {0!s}'.format(folderName))
            if pdbRoot in typical_names:
                if os.path.isfile(pdbFile.replace('.pdb','.mtz')):
                    mtzFile = pdbFile.replace('.pdb','.mtz')
                    mtz = pdb.replace('.pdb','.mtz')
                    self.Todo.append([folderName,pdbFile,mtzFile,pdb,mtz])
                    print('folder: {0!s} PDB: {1!s} MTZ: {2!s}'.format(folderName,pdbFile,mtzFile))
                    continue
        self.number_pdb_files_found.set_label('found {0!s} PDB files'.format(len(self.Todo)))



    def on_key_release_projectDir(self, widget, event):
        self.projectDir = widget.get_text()
#        if os.path.isdir(self.projectDir)
        self.current_project_directory_label.set_label(self.projectDir)
        if os.path.isdir(self.projectDir):
            self.current_project_directory_label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("darkgreen"))
        else:
            self.current_project_directory_label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("red"))



    def CANCEL(self, widget):
        self.window.destroy()





if __name__ == '__main__':
    GUI().StartGUI()
