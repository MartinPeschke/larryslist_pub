from jsonclient import Mapping, TextField, DictField


class LocationModel(Mapping):
    name = TextField()
    token = TextField()

    def toQuery(self):
        return {'label': self.name, 'value': self.token}


class AddressModel(Mapping):
    line1 = TextField()
    line2 = TextField()
    line3 = TextField()
    postCode = TextField()
    Country = DictField(LocationModel)
    Region = DictField(LocationModel)
    City = DictField(LocationModel)
    website = TextField()

    def getLines(self, request):
        return '<br/>'.join([getattr(self, v) for v in ['line1', 'line2', 'line3'] if getattr(self, v, None)])

    def getCityPostCode(self, request):
        if self.postCode and self.City:
            return u'{}, {}'.format(self.City.name, self.postCode)
        elif self.postCode:
            return self.postCode
        elif self.City:
            return self.City.name
        else:
            return ''

    def getRegion(self, request):
        return self.Region.name if self.Region else ''

    def getCountry(self, request):
        return self.Country.name if self.Country else ''