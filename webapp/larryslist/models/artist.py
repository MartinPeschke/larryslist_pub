from jsonclient import Mapping, TextField, IntegerField, ListField, DictField
from pyramid.decorator import reify


class ArtworkModel(Mapping):
    title = TextField()
    year = TextField()
    material = TextField()
    medium = TextField()
    width = IntegerField()
    height = IntegerField()
    depth = IntegerField()
    measurement = TextField()

    def getMeasure(self):
        return 'cm' if self.measurement == 'METRIC' else 'in'
    @reify
    def size(self):
        m = ''
        if self.width:
            m += u'w: {} '.format(self.width)
        if self.height:
            m += u'h: {} '.format(self.height)
        if self.depth:
            m += u'd: {} '.format(self.depth)
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
