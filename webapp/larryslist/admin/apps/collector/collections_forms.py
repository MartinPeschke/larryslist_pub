from jsonclient.backend import DBException
from larryslist.admin.apps.collector.models import CreateCollectionProc, EditCollectionBaseProc
from larryslist.lib.formlib.formfields import BaseForm, IntField, CheckboxField, IMPORTANT, StringField, MultiConfigChoiceField, ApproxField, HiddenField

__author__ = 'Martin'


class BaseCollectionForm(BaseForm):
    id = 'basic'
    label = 'Basic'
    fields = [
        ApproxField('totalWorks', 'totalWorksAprx', "Total number of artworks in collection", IMPORTANT, label_classes="double")
        , ApproxField('totalArtists', 'totalArtistsAprx', "Total number of artists in collection", IMPORTANT, label_classes="double")
        , StringField("name", "Name of collection", IMPORTANT)
        , StringField("foundation", "Name of foundation")
        , IntField('started', "Started collecting in year")
        , MultiConfigChoiceField('name', 'Art Genre / Movemment', "Genre", "Genre")
        , MultiConfigChoiceField('name', 'Medium of artworks', "Medium", "Medium")
    ]

    @classmethod
    def on_success(cls, request, values):
        values = {'id': request.matchdict['collectorId'], 'Collection':values}
        try:
            collection = CreateCollectionProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'redirect': request.fwd_url("admin_collection_edit", collectionId = collection.id, stage='basic')}


class CollectionEditForm(BaseCollectionForm):
    fields = BaseCollectionForm.fields  + [
            HiddenField('id')
        ]
    @classmethod
    def on_success(cls, request, values):
        values = {'id': request.matchdict['collectorId'], 'Collection':values}
        try:
            collection = EditCollectionBaseProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}
