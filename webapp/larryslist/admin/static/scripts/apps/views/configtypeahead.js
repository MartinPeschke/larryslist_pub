define(["tools/ajax", "libs/abstractsearch", "tools/config"], function(ajax, AbstractSearch, config){
    var
    getRec = hnc.getRecursive
    , PlainResult = ajax.Model.extend({
        idAttribute:'name'
        , getSearchLabel: function(){
            return this.id;
        }
    })
    , PlainSearchResult = ajax.Collection.extend({
        model:PlainResult
        , idAttribute:'name'
    })
    , ConfigSearch = AbstractSearch.extend({
        doSearch : function(query){
            var view = this;
            if(query){
                config.fetch(function(cfg){
                    var result = cfg.get(this.options.configAttr), search = [];
                    result.each(function(elem){
                        if(!!~elem.id.toLowerCase().indexOf(query)){
                            search.push(elem.attributes);
                        }
                    });
                    view.model.reset(search);
                }, this);
            } else {
                view.model.reset([]);
            }
        }
    })
    , ConfigTypeAhead = Backbone.View.extend({
        initialize: function(opts){
            var view = this;
            this.$filter = this.$(".query");
            this.current = new PlainResult({name: this.$filter.val()});
            this.search = this.getSearch(opts);
            this.search.on('selected', function(term){
                view.search.hide();
                view.$filter.val(term.getSearchLabel());
                view.current = term;
            });
            this.search.on("extraItemSelected unknownterm:selected unknownterm:metaSelected", function(query){
                view.search.hide();
                view.$filter.val(query);
                view.$filter.trigger("change");
            });
        }
        , getSearch: function(opts){
            return new ConfigSearch({
                el:this.$el
                , suppressExtra: false
                , model: new PlainSearchResult([])
                , configAttr: opts.configAttr
            });
        }
    })

    , widgets = []
    , init = function(opts){
        widgets.push(new ConfigTypeAhead(opts));
    };
    return {init: init};
});