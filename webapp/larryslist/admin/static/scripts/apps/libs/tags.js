define(["tools/ajax", "libs/abstractsearch"], function(ajax, AbstractSearch){
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
            , initialize: function(models, opts){
                this.apiResult = opts.apiResult;
            }
            , idAttribute:'name'
            , parse: function(resp){
                return getRec(resp, this.apiResult);
            }
        })
        , TypeAheadSearch = AbstractSearch.extend({
            buildQuery: function(query){
                return {type: this.options.apiType, term:query};
            }
        })
        , TagSearch = Backbone.View.extend({
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
            }
            , getSearch: function(opts){
                return new TypeAheadSearch({
                    el:this.$el
                    , suppressExtra: true
                    , model: new PlainSearchResult([], {apiResult: opts.apiResult}), apiType: opts.apiType, searchUrl: opts.apiUrl
                });
            }
        })
        , widgets = []
        , init = function(opts){
            widgets.push(new PlainTypeAhead(opts));
        };
    return {init: init, TagSearch: TagSearch};
});