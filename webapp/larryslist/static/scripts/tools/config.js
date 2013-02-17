define(["tools/ajax"], function(ajax){

    var
        Museum = ajax.Model.extend({
            idAttribute: 'name'
        })
        , MuseumCollection = ajax.Collection.extend({idAttribute: 'name', model: Museum})
        , ConfigModel = ajax.Model.extend({
            initialize:function(){
                this.register({TopMuseum: new MuseumCollection()});
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
