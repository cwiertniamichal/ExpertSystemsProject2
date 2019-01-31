# -*- coding: utf-8 -*-
import pysmile

# noinspection PyUnresolvedReferences
import pysmile_license

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

import wx
import matplotlib.pyplot as plt

plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

import wx.lib.scrolledpanel as scrolled

net = pysmile.Network()
net.read_file("operator_sieci_komorkowej_v3.xdsl")
net.update_beliefs()

options = [
    'Brak_stalej_oplaty', 'Na_firme', 'Brak_umowy', 'Nowy_telefon',
    'Znajomi_maja_iPhoney'
]

indirect_facts = ['Doladowania', 'Oferta_MIX_z_telefonem',
                  'Oferta_z_telefonem', 'Abonament_z_telefonem']

offers = ['Oferta_na_karte', 'Oferta_MIX', 'Oferta_MIX_z_Androidem',
          'Oferta_MIX_z_iPhonem', 'Abonament_z_iPhonem',
          'Abonament_z_Androidem', 'Abonament']

FRAME_SIZE = (1700, 1200)
TITLE = ''

OPTIONS_Y = 1
OPTIONS_X = 5
OPTIONS_X_SPACE = 10
OPTIONS_Y_SPACE = 20

user_choices_mapping = {
    0: 'Nie',
    1: 'Nie_wiem',
    2: 'Moze',
    3: 'Tak'
}


def set_background(obj, image_path):
    try:
        # pick an image file you have in the working folder
        # you can load .jpg  .png  .bmp  or .gif files
        image_file = image_path
        bmp1 = wx.Image(image_file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        # image's upper left corner anchors at panel coordinates (0, 0)
        obj.bitmap1 = wx.StaticBitmap(obj, -1, bmp1, (0, 0))
        # show some image details
    except IOError:
        print "Image file %s not found" % image_file
        raise SystemExit


class OptionsView(wx.Panel):
    def __init__(self, parent, option_name):
        wx.Panel.__init__(self, parent, style=wx.RAISED_BORDER,
                          size=(250, 160))
        # set_background(self, 'im2.resized.jpeg')
        self.option_name = option_name
        self.value = 0
        self.option_slider = None
        self.checkbox = None
        self.checkbox_label = None

        options_sizer = wx.BoxSizer(wx.VERTICAL)
        options_sizer.AddSpacer(30)
        options_sizer.Add(wx.StaticText(self,
                                        label=option_name.replace('_', ' '),
                                        size=(200, 20),
                                        style=wx.ALIGN_CENTRE), flag=wx.CENTER)
        options_sizer.AddSpacer(20)
        options_sizer.Add(self.add_checkbox_label(), flag=wx.CENTER)
        options_sizer.Add(self.add_checkbox(), flag=wx.CENTER)
        options_sizer.Add(self.add_option_slider(), 1,
                          flag=wx.CENTER)
        self.SetSizer(options_sizer)

    def add_option_slider(self):
        self.option_slider = wx.Slider(self, value=0, minValue=0, maxValue=3,
                                       style=wx.SL_HORIZONTAL | wx.SL_LABELS,
                                       size=(200, 10))
        self.option_slider.Disable()
        self.option_slider.Bind(wx.EVT_SLIDER, self.on_slide)
        return self.option_slider

    def on_slide(self, event):
        event_object = event.GetEventObject()
        event_value = event_object.GetValue()
        self.value = event_value

    def add_checkbox(self):
        self.checkbox = wx.CheckBox(self)
        self.checkbox.Bind(wx.EVT_CHECKBOX, self.on_checked)
        return self.checkbox

    def add_checkbox_label(self):
        self.checkbox_label = wx.StaticText(self, label='Czy uwzględnić '
                                                        'te opcję?',
                                            style=wx.ALIGN_CENTRE,
                                            size=(200, 20))
        return self.checkbox_label

    def on_checked(self, _):
        active = self.checkbox.GetValue()
        self.option_slider.Enable(active)

    def reset(self):
        self.checkbox.SetValue(False)
        self.value = 0
        self.option_slider.SetValue(0)
        self.option_slider.Disable()


def display_probabilities(facts, title, fig):
    y_pos = np.arange(len(facts))
    probabilities = list(map(lambda x: net.get_node_value(x)[0], facts))
    plt.sca(fig.axes[0])
    plt.cla()
    plt.grid(zorder=0)
    plt.bar(y_pos, probabilities, align='center', alpha=0.5)
    plt.xticks(y_pos, facts)
    plt.title(title)
    fig.canvas.draw()


class Form(scrolled.ScrolledPanel):
    def __init__(self, parent, size):
        scrolled.ScrolledPanel.__init__(self, parent, size=size)
        # set_background(self, 'background.resized.jpeg')
        self.options_views = []

        self.offers_fig = None

        self.indirect_facts_fig = None
        self.SetBackgroundColour(wx.WHITE)
        self.SetSizer(self.new_root_sizer())
        self.SetupScrolling()

    def new_root_sizer(self):
        root_sizer = wx.BoxSizer(wx.VERTICAL)
        root_sizer.AddSpacer(30)
        self.options_grid(root_sizer)
        root_sizer.Add(self.new_buttons_sizer(), flag=wx.CENTER)
        root_sizer.AddSpacer(10)
        root_sizer.Add(self.new_indirect_facts_canvas(), flag=wx.CENTER)
        root_sizer.Add(self.new_offers_canvas(), flag=wx.CENTER)
        root_sizer.Layout()
        return root_sizer

    def options_grid(self, root_sizer):
        for i in range(OPTIONS_Y):
            horiz_options = wx.BoxSizer(wx.HORIZONTAL)
            for j in range(OPTIONS_X):
                options_view = OptionsView(self, options[i * OPTIONS_X + j])
                self.options_views.append(options_view)
                horiz_options.Add(options_view)
                horiz_options.AddSpacer(OPTIONS_X_SPACE)
            root_sizer.Add(horiz_options, flag=wx.CENTER)
            root_sizer.AddSpacer(OPTIONS_Y_SPACE)

    def new_buttons_sizer(self):
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        recalculate_btn = wx.Button(self, label='Oblicz ponownie')
        reset_btn = wx.Button(self, label='Resetuj')
        button_sizer.Add(recalculate_btn)
        button_sizer.AddSpacer(10)
        button_sizer.Add(reset_btn)
        recalculate_btn.Bind(wx.EVT_BUTTON, self.on_recalculate)
        reset_btn.Bind(wx.EVT_BUTTON, self.on_reset)
        return button_sizer

    def update_network(self, update_fun):
        net.clear_all_evidence()
        update_fun()
        net.update_beliefs()
        display_probabilities(offers, 'Oferty', self.offers_fig)
        display_probabilities(indirect_facts, 'Fakty posrednie',
                              self.indirect_facts_fig)

    def on_reset(self, _):
        def update_fun():
            for ov in self.options_views:
                ov.reset()
        self.update_network(update_fun)

    def on_recalculate(self, _):
        def update_fun():
            for ov in self.options_views:
                if ov.checkbox.GetValue():
                    probability = ov.value
                    net.set_evidence(ov.option_name,
                                     user_choices_mapping[probability])

        self.update_network(update_fun)

    def new_bar_chart_canvas(self):
        figure = plt.figure()
        width, height = 1500, 400
        ppiw, ppih = wx.GetDisplayPPI()
        figure.set_size_inches((width / ppiw, height / ppih))
        return FigureCanvas(self, -1, figure)

    def new_offers_canvas(self):
        res = self.new_bar_chart_canvas()
        self.offers_fig, _ = plt.gcf(), plt.gca()
        display_probabilities(offers, 'Oferty', self.offers_fig)
        return res

    def new_indirect_facts_canvas(self):
        res = self.new_bar_chart_canvas()
        self.indirect_facts_fig, _ = plt.gcf(), plt.gca()
        display_probabilities(indirect_facts, 'Fakty posrednie',
                              self.indirect_facts_fig)
        return res


class AppFrame(wx.Frame):
    def __init__(self):
        super(AppFrame, self).__init__(None, size=FRAME_SIZE, title=TITLE)
        Form(self, FRAME_SIZE)


def main():
    app = wx.App()
    frame = AppFrame()
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
