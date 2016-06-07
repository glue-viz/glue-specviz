import os

from glue.viewers.common.qt.data_viewer import DataViewer
from glue.core import message as msg
from glue.utils import nonpartial

from specviz.ui.viewer import Viewer
from specviz.ui.controller import Controller
from specviz.interfaces.managers import data_manager

from .viewer_options import OptionsWidget
from .layer_widget import LayerWidget


__all__ = ['SpecvizViewer']


class SpecvizViewer(DataViewer):

    LABEL = "SpecViz viewer"

    def __init__(self, session, parent=None):

        super(SpecvizViewer, self).__init__(session, parent=parent)

        self.viewer = Viewer()
        self.controller = Controller(self.viewer)

        self.setCentralWidget(self.viewer)

        self._options_widget = OptionsWidget(data_viewer=self)

        self._layer_widget = LayerWidget()

        # We keep a cache of the specviz data objects that correspond to a given
        # filename.
        self._specviz_data_cache = {}

        self._layer_widget.ui.combo_active_layer.currentIndexChanged.connect(nonpartial(self._update_options))

        self._layer_widget.ui.combo_active_layer.currentIndexChanged.connect(nonpartial(self._refresh_specviz_data))
        self._options_widget.ui.combo_file_attribute.currentIndexChanged.connect(nonpartial(self._refresh_specviz_data))

    def options_widget(self):
        return self._options_widget

    def layer_view(self):
        return self._layer_widget

    def _update_options(self):
        self._options_widget.set_data(self._layer_widget.layer)

    def register_to_hub(self, hub):

        super(SpecvizViewer, self).register_to_hub(hub)

        hub.subscribe(self, msg.SubsetCreateMessage,
                      handler=self._add_subset)

        hub.subscribe(self, msg.SubsetUpdateMessage,
                      handler=self._update_subset)

        hub.subscribe(self, msg.SubsetDeleteMessage,
                      handler=self._remove_subset)

        hub.subscribe(self, msg.DataUpdateMessage,
                      handler=self._update_data)

    # The following two methods are required of data viewers - they are what
    # gets called when a dataset or subset gets dragged and dropped onto the
    # viewer.

    def add_data(self, data):
        if data not in self._layer_widget:
            self._layer_widget.add_layer(data)
        self._layer_widget.layer = data
        self._refresh_specviz_data()
        return True

    def _update_data(self, message):
        self._refresh_specviz_data()

    def add_subset(self, subset):
        if subset not in self._layer_widget:
            self._layer_widget.add_layer(subset)
        self._layer_widget.layer = subset
        self._refresh_specviz_data()
        return True

    def _add_subset(self, message):
        self.add_subset(message.subset)

    def _update_subset(self, message):
        self._refresh_specviz_data()

    def _remove_subset(self, message):
        if message.subset in self._layer_widget:
            self._layer_widget.remove_layer(message.subset)
        self._refresh_specviz_data()

    def _refresh_specviz_data(self):

        print('REFRESH', data_manager._members)

        if self._options_widget.file_att is None:
            return

        if self._layer_widget.layer is None:
            return

        cid = self._layer_widget.layer.id[self._options_widget.file_att[0]]

        component = self._layer_widget.layer.get_component(cid)

        # TODO: need a better way to clear the data manager
        data_manager._members.clear()

        if not component.categorical:
            return

        filenames = component.labels

        added = []

        print("BEFORE", data_manager._members)

        for filename in filenames:

            print("Attempting to load {0}".format(filename))

            if filename in self._specviz_data_cache:

                data = self._specviz_data_cache[filename]
                data_manager.add(data)
                added.append(data)

            else:

                # TODO: Replicate the logic from read_file since we need to keep
                # a reference to the data object. Need to make this easier in
                # specviz API.

                file_name = str(filename)
                file_ext = os.path.splitext(file_name)[-1]

                if file_ext in ('.txt', '.dat'):
                    file_filter = 'ASCII (*.txt *.dat)'
                else:
                    file_filter = 'Generic Fits (*.fits *.mits)'

                data = data_manager.load(filename, file_filter)
                added.append(data)
                self._specviz_data_cache[filename] = data
