from larryslist.models.collector import CollectorModel, CollectionModel, MetaDataProc
from larryslist.models import ClientTokenProc


__author__ = 'Martin'




SetSourcesProc = ClientTokenProc("/admin/collector/sourceedit", root_key = 'Collector', result_cls=CollectorModel)
SetCollectorStatusProc = ClientTokenProc("/admin/collector/status")
DeactivateCollectorProc = ClientTokenProc("/admin/collector/inactive")


CreateCollectorProc = ClientTokenProc("/admin/collector/create", root_key = 'Collector', result_cls=CollectorModel)
GetCollectorDetailsProc = ClientTokenProc("/admin/collector", root_key = 'Collector', result_cls=CollectorModel)

EditCollectorBaseProc = ClientTokenProc("/admin/collector/basicedit", root_key = 'Collector', result_cls=CollectorModel)
EditCollectorContactsProc = ClientTokenProc("/admin/collector/contactedit", root_key = 'Collector', result_cls=CollectorModel)
EditCollectorBusinessProc = ClientTokenProc("/admin/collector/businessedit", root_key = 'Collector', result_cls=CollectorModel)
SaveCollectorDocumentsProc = ClientTokenProc("/admin/collector/document", root_key = 'Collector', result_cls=CollectorModel)
SaveCollectorOtherFactsProc = ClientTokenProc("/admin/collector/fact", root_key = 'Collector', result_cls=CollectorModel)



SetCollectorMetaProc = MetaDataProc("/admin/collector/metaset")
SetCollectionMetaProc = MetaDataProc("/admin/collection/metaset")


CreateCollectionProc = ClientTokenProc("/admin/collection/create", root_key = 'Collection', result_cls=CollectionModel)
EditCollectionBaseProc = ClientTokenProc("/admin/collection/basicedit", root_key = 'Collection', result_cls=CollectionModel)
EditCollectionArtistsProc = ClientTokenProc("/admin/collection/artistedit", root_key = 'Collection', result_cls=CollectionModel)
EditCollectionPublicationsProc = ClientTokenProc("/admin/collection/communicationedit", root_key = 'Collection', result_cls=CollectionModel)
SaveCollectionDocumentsProc = ClientTokenProc("/admin/collection/document", root_key = 'Collection', result_cls=CollectionModel)
SaveCollectionMuseumProc = ClientTokenProc("/admin/collector/directorMuseum", root_key = 'Collection', result_cls=CollectionModel)
SaveArtworkProc = ClientTokenProc("/admin/artist/artwork")

