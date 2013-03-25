from jsonclient import Mapping, TextField, IntegerField, ListField, DictField, DecimalField
from pyramid.decorator import reify


class ArtworkModel(Mapping):
    title = TextField()
    year = TextField()
    material = TextField()
    medium = TextField()
    width = DecimalField()
    height = DecimalField()
    depth = DecimalField()
    measurement = TextField()

    def getMeasure(self):
        return 'cm' if self.measurement == 'METRIC' else 'in'
    @reify
    def size(self):
        m = ''
        if self.width:
            w = self.width
            m += u'w: {} '.format(int(w) if w ==int(w) else w)
        if self.height:
            h = self.height
            m += u'h: {} '.format(int(h) if h ==int(h) else h)
        if self.depth:
            d = self.depth
            m += u'd: {} '.format(int(d) if d ==int(d) else d)
        if m: m += self.getMeasure()
        return m

    def getLabel(self, request):
        if self.year:
            return u'{} ({})'.format(self.title, self.year)
        else:
            return self.title

class ArtistModel(Mapping):
    id = IntegerField()
    name = TextField()
    year = TextField()
    ArtWork = ListField(DictField(ArtworkModel))
    def getLabel(self, request):
        if self.year:
            return u'{} ({})'.format(self.name, self.year)
        else:
            return self.name

    def toQuery(self):
        return {'label': self.name, 'value': self.id}
