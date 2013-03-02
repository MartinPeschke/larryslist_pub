define(["tools/ajax", "tools/abstractsearch", "libs/tagsearch"], function(ajax, AbstractSearch, tsv){
    var
    getRec = hnc.getRecursive
    , PlainResult = ajax.Model.extend({
        getSearchLabel: function(){
            if(this.get('yob')) return this.get("name") + " - " + this.get("yob");
            else return this.get("name");
        }
    })
    , PlainSearchResult = ajax.Collection.extend({
        model:PlainResult
        , initialize: function(models, opts){
            this.apiResult = opts.apiResult;
        }
        , idAttribute:'name'
        , parse: function(resp){
            return getRec(resp, this.apiResult);
        }
    })
    , TagModels = Backbone.Collection.extend({
        model: PlainResult
    })
    , TagSearch = AbstractSearch.extend({
        buildQuery: function(query){
            var extra = this.options.queryExtra;
            return query?_.extend({'term':query}, extra):null;
        }
    })
    , TagSearchView = tsv.TagSearch.extend({
        MODEL_CLS: TagModels
        , getSearch: function(opts){
            return new TagSearch({
                el:this.$el
                , suppressExtra: opts.apiAllowNew
                , model: new PlainSearchResult([], {apiResult: opts.apiResult})
                , searchUrl: opts.apiUrl
                , queryExtra: opts.queryExtra
            });
        }
    })
    , widgets = []
    , init = function(opts){
        widgets.push(new TagSearchView(opts));
    };
    return {init: init, TagSearch: TagSearchView};
});