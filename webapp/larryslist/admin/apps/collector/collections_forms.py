from jsonclient.backend import DBException
from larryslist.admin.apps.collector.models import CreateCollectionProc, EditCollectionBaseProc, EditCollectionArtistsProc, EditCollectionPublicationsProc
from larryslist.admin.apps.collector.sources_form import BaseAdminForm
from larryslist.lib.formlib.formfields import BaseForm, IntField, CheckboxField, IMPORTANT, StringField, MultiConfigChoiceField, ApproxField, HiddenField, MultipleFormField, TypeAheadField, PlainHeadingField, ConfigChoiceField, URLField, TagSearchField

__author__ = 'Martin'


class RegionOfInterest(MultipleFormField):
    fields = [
        StringField('name', "Name")
    ]

class BaseCollectionForm(BaseAdminForm):
    id = 'basic'
    label = 'Basic'
    fields = [
        ApproxField('totalWorks', 'totalWorksAprx', "Total number of artworks in collection", IMPORTANT, label_classes="double")
        , ApproxField('totalArtists', 'totalArtistsAprx', "Total number of artists in collection", IMPORTANT, label_classes="double")
        , StringField("name", "Name of collection", IMPORTANT)
        , StringField("foundation", "Name of foundation")
        , IntField('started', "Started collecting in year")
        , PlainHeadingField("Themes in collection")
        , TagSearchField('Theme', "Tags", "/admin/search/theme", "Theme", classes='tagsearch input-xxlarge')
        , PlainHeadingField("Art Genre / Movement")
        , MultiConfigChoiceField('name', 'Name', "Genre", "Genre")
        , PlainHeadingField("Medium of artworks")
        , MultiConfigChoiceField('name', 'Name', "Medium", "Medium")
        , PlainHeadingField("Region of interest")
        , RegionOfInterest('Region', '')
    ]

    @classmethod
    def persist(cls, request, values):
        collectorId = request.matchdict['collectorId']
        values = {'id': request.matchdict['collectorId'], 'Collection':values}
        try:
            collection = CreateCollectionProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'redirect': request.fwd_url("admin_collection_edit", collectorId = collectorId, stage='basic')}


class CollectionEditForm(BaseCollectionForm):
    fields = BaseCollectionForm.fields  + [
            HiddenField('id')
        ]
    @classmethod
    def persist(cls, request, values):
        values = {'id': request.matchdict['collectorId'], 'Collection':values}
        try:
            collection = EditCollectionBaseProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}

class ArtistForm(MultipleFormField):
    fields = [
        TypeAheadField('name', "Artist", "/admin/search/artist", "Artist", classes='typeahead input-xxlarge')
    ]


class CollectionArtistsForm(BaseAdminForm):
    id = 'artist'
    label = 'Artists'
    fields = [
        HiddenField('id')
        , PlainHeadingField("Artists in Collection")
        , ArtistForm('Artist', "Artist")
    ]

    @classmethod
    def persist(cls, request, values):
        values = {'id': request.matchdict['collectorId'], 'Collection':values}
        try:
            collection = EditCollectionArtistsProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}

class PublicationsForm(MultipleFormField):
    fields = [
        StringField('title', "Title")
        , ConfigChoiceField('publisher', 'Publisher', 'Publisher')
        , IntField('year', "Year")
    ]


class CollectionWebsiteForm(BaseAdminForm):
    id = 'website'
    label = 'Communication Platforms'
    fields = [
        HiddenField('id')
        , PlainHeadingField("Website")
        , URLField('url', "Webpage", attrs = IMPORTANT)
        , PlainHeadingField("Publications")
        , PublicationsForm('Publication', "", classes = "form-embedded-wrapper form-inline")
    ]

    @classmethod
    def persist(cls, request, values):
        values = {'id': request.matchdict['collectorId'], 'Collection': values}
        try:
            collection = EditCollectionPublicationsProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}