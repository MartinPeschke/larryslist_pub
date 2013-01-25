from jsonclient.backend import DBException
from larryslist.admin.apps.collector.models import CreateCollectionProc
from larryslist.lib.formlib.formfields import BaseForm, IntField, CheckboxField, IMPORTANT, StringField, MultiConfigChoiceField

__author__ = 'Martin'


class BaseCollectionForm(BaseForm):
    id = 'basic'
    label = 'Basic'
    fields = [
        IntField('totalWorks', "Total number of artworks in collection", IMPORTANT, group_classes="extra-wide inline")
        , CheckboxField('totalWorksAprx', "Approximation?")

        , IntField('totalArtists', "Total number of artists in collection", IMPORTANT, group_classes="extra-wide inline")
        , CheckboxField('totalArtistsAprx', "Approximation?")

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
    @classmethod
    def on_success(cls, request, values):
        values = {'id': request.matchdict['collectorId'], 'Collection':values}
        try:
            collection = CreateCollectionProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'redirect': request.fwd_url("admin_collection_edit", collectionId = collection.id, stage='basic')}
