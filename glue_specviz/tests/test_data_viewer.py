from glue.core import Session, Data, DataCollection
from ..data_viewer import SpecvizViewer


def test_init():
    data = Data(x=[1, 2, 3], y=[2, 3, 4], filename=['a.fits', 'b.fits', 'c.fits'])
    dc = DataCollection([data])
    session = Session(data_collection=dc, hub=dc.hub)
    SpecvizViewer(session)
