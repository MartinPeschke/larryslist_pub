define(["tools/ajax"], function(ajax){

    var
        NamedModel = ajax.Model.extend({
            idAttribute: 'name'
            , getSearchLabel: function(){return this.get('name')}
        })
        , NamedModelCollection = ajax.Collection.extend({idAttribute: 'name', model: NamedModel})
        , TopMuseum  = ajax.Model.extend({
            getSearchLabel: function(){return this.get('name')}
            , parseLocal: function(data){
                data.id = data.name+"-"+data.city;
                return data;
            }
        })
        , TopMuseumCollection = ajax.Collection.extend({idAttribute: 'id', model: TopMuseum})

        , ConfigModel = ajax.Model.extend({
            initialize:function(){
                this.register({
                    TopMuseum: new TopMuseumCollection()
                    , Publisher : new NamedModelCollection()
                    , CooperationType: new NamedModelCollection()
                    , EngagementPosition: new NamedModelCollection()
                    , ArtFair: new NamedModelCollection()});
                this.onLoaded = $.Deferred();
                this.load();
            }
            , getMuseum: function(name){
                return this.get("TopMuseum").get(name);
            }
            , fetch: function(cb, ctxt){
                this.onLoaded.done(function(){
                    cb.apply(ctxt, arguments);
                });
            }
            , load: function(){
                var model = this;
                if(_.isEmpty(hnc.Config)){
                    ajax.submitPrefixed({url: "/config", success: function(resp, sttaus, xhr){
                        model.deepClear();
                        model.setRecursive(resp.Config);
                        model.onLoaded.resolve(model);
                    }});
                } else {
                    model.deepClear();
                    model.setRecursive(hnc.Config);
                    model.onLoaded.resolve(model);
                }
            }
        })
        , config = new ConfigModel();
    return config;
});
