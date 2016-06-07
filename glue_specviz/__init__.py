def setup():
    from .data_viewer import SpecvizViewer
    from glue.config import qt_client
    qt_client.add(SpecvizViewer)
