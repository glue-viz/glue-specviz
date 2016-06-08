import os

from glue.core import Subset
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

        # We set up the specviz viewer and controller as done for the standalone
        # specviz application
        self.viewer = Viewer()
        self.controller = Controller(self.viewer)
        self.setCentralWidget(self.viewer)

        # We now set up the options widget. This controls for example which
        # attribute should be used to indicate the filenames of the spectra.
        self._options_widget = OptionsWidget(data_viewer=self)

        # The layer widget is used to select which data or subset to show.
        # We don't use the default layer list, because in this case we want to
        # make sure that only one dataset or subset can be selected at any one
        # time.
        self._layer_widget = LayerWidget()

        # We keep a cache of the specviz data objects that correspond to a given
        # filename - although this could take up a lot of memory if there are
        # many spectra, so maybe this isn't needed
        self._specviz_data_cache = {}

        # Make sure we update the viewer if either the selected layer or the
        # column specifying the filename is changed.
        self._layer_widget.ui.combo_active_layer.currentIndexChanged.connect(nonpartial(self._update_options))
        self._layer_widget.ui.combo_active_layer.currentIndexChanged.connect(nonpartial(self._refresh_specviz_data))
        self._options_widget.ui.combo_file_attribute.currentIndexChanged.connect(nonpartial(self._refresh_specviz_data))

    # The following two methods are required by glue - they are used to specify
    # which widgets to put in the bottom left and middle left panel.

    def options_widget(self):
        return self._options_widget

    def layer_view(self):
        return self._layer_widget

    # The following method is required by glue - it is used to subscribe the
    # viewer to various messages sent by glue.

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

    # The following two methods are required by glue - they are what gets called
    # when a dataset or subset gets dragged and dropped onto the viewer.

    def add_data(self, data):
        if data not in self._layer_widget:
            self._layer_widget.add_layer(data)
        self._layer_widget.layer = data
        self._refresh_specviz_data()
        return True

    def add_subset(self, subset):
        if subset not in self._layer_widget:
            self._layer_widget.add_layer(subset)
        self._layer_widget.layer = subset
        self._refresh_specviz_data()
        return True

    # The following four methods are used to receive various messages related
    # to updates to data or subsets.

    def _update_data(self, message):
        self._refresh_specviz_data()

    def _add_subset(self, message):
        self.add_subset(message.subset)

    def _update_subset(self, message):
        self._refresh_specviz_data()

    def _remove_subset(self, message):
        if message.subset in self._layer_widget:
            self._layer_widget.remove_layer(message.subset)
        self._refresh_specviz_data()

    # When the selected layer is changed, we need to update the combo box with
    # the attributes from which the filename attribute can be selected. The
    # following method gets called in this case.

    def _update_options(self):
        self._options_widget.set_data(self._layer_widget.layer)

    # The following method does the bulk of the interfacing of this plugin with
    # specviz - it essentially makes sure that that list of datasets in the
    # viewer's own data collection is up to date with the active data or subset.

    def _refresh_specviz_data(self):

        if self._options_widget.file_att is None:
            return

        if self._layer_widget.layer is None:
            return

        if isinstance(self._layer_widget.layer, Subset):
            subset = self._layer_widget.layer
            cid = subset.data.id[self._options_widget.file_att[0]]
            mask = subset.to_mask(None)
            component = subset.data.get_component(cid)
        else:
            cid = self._layer_widget.layer.id[self._options_widget.file_att[0]]
            mask = None
            component = self._layer_widget.layer.get_component(cid)

        # TODO: need a better way to clear the data manager
        [data_manager.remove(data) for data in data_manager._members[:]]

        if not component.categorical:
            return

        filenames = component.labels

        if mask is not None:
            filenames = filenames[mask]

        for filename in filenames:

            if filename in self._specviz_data_cache:

                data = self._specviz_data_cache[filename]
                data_manager.add(data)

            else:

                # TODO: For now we replicate the logic from read_file since we
                # need to keep a reference to the data object. Need to make this
                # easier in specviz API.

                file_name = str(filename)
                file_ext = os.path.splitext(file_name)[-1]

                if file_ext in ('.txt', '.dat'):
                    file_filter = 'ASCII (*.txt *.dat)'
                else:
                    file_filter = 'Generic Fits (*.fits *.mits)'

                data = data_manager.load(filename, file_filter)
                self._specviz_data_cache[filename] = data
