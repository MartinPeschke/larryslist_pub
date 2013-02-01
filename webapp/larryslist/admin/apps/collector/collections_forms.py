from jsonclient.backend import DBException
from larryslist.admin.apps.collector.collector_forms import TypedFileUploadField
from larryslist.admin.apps.collector.models import CreateCollectionProc, EditCollectionBaseProc, EditCollectionArtistsProc, EditCollectionPublicationsProc, SaveCollectionDocumentsProc
from larryslist.admin.apps.collector.sources_form import BaseAdminForm
from larryslist.lib.formlib.formfields import BaseForm, IntField, CheckboxField, IMPORTANT, StringField, MultiConfigChoiceField, ApproxField, HiddenField, MultipleFormField, TypeAheadField, PlainHeadingField, ConfigChoiceField, URLField, TagSearchField

__author__ = 'Martin'


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
        , TagSearchField('Theme', "Tags", "/admin/search/theme", "Theme", api_allow_new = True, classes='tagsearch input-xxlarge')
        , PlainHeadingField("Art Genre / Movement")
        , MultiConfigChoiceField('name', 'Name', "Genre", "Genre")
        , PlainHeadingField("Medium of artworks")
        , MultiConfigChoiceField('name', 'Name', "Medium", "Medium")
        , PlainHeadingField("Region of interest")
        , TagSearchField('Origin', "Tags", "/admin/search/address", "Country", api_allow_new = False, classes='tagsearch input-xxlarge')
    ]

    @classmethod
    def persist(cls, request, values):
        collectorId = request.matchdict['collectorId']
        values = {'id': request.matchdict['collectorId'], 'Collection':values}
        try:
            collection = CreateCollectionProc(request, values)
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
            collection = EditCollectionBaseProc(request, values)
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
            collection = EditCollectionArtistsProc(request, values)
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
            collection = EditCollectionPublicationsProc(request, values)
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}


class CollectionUploadForm(BaseAdminForm):
    id = "uploads"
    label = "Uploads"
    fields = [
        PlainHeadingField("Collection Documents")
        , TypedFileUploadField("Document", classes = 'form-embedded-wrapper form-inline')
        , HiddenField('id')
    ]
    @classmethod
    def persist(cls, request, values):
        try:
            data = {'id':request.matchdict['collectorId'], 'Collection': values}
            collector = SaveCollectionDocumentsProc(request, {'Collection':data})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}