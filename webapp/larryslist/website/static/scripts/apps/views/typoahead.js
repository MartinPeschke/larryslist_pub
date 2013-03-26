define(["tools/ajax", "tools/abstractsearch", "text!templates/taresult.html"], function(ajax, AbstractSearch, tmpl){
    var
        getRec = hnc.getRecursive
            , PlainResult = ajax.Model.extend({
            idAttribute:'value'
            , getSearchLabel: function(){
                return this.get("label");
            }
        })
        , PlainSearchResult = ajax.Collection.extend({
            model:PlainResult
            , initialize: function(models, opts){
                this.apiResult = opts.apiResult;
            }
            , idAttribute:'value'
            , parse: function(resp){
                return getRec(resp, this.apiResult);
            }
        })
        , TypeAheadSearch = AbstractSearch.extend({
            template : _.template(tmpl)
            , buildQuery: function(query){
                return {term:query};
            }
        })
        , PlainTypeAhead = Backbone.View.extend({
            initialize: function(opts){
                var view = this, $el = this.$el;
                opts.mapping = opts.mapping || {};
                this.$query = this.$(".query");
                this.current = null;
                this.search = this.getSearch(opts);
                this.search.on('selected', function(term){
                    view.search.hide();
                    view.$query.val(term.getSearchLabel());
                    view.$query.prev(".key").attr("name", term.get('key')).val(term.get('value'));
                    view.current = term;

                });
                this.search.on('extraItemSelected unknownterm:selected unknownterm:metaSelected', function(termname){view.$query.val("");view.current=null;});
                this.search.on('hide', function(){
                    if(!view.current || view.current.getSearchLabel() != view.$query.val()){
                        view.$query.val("");
                        view.current = null;
                    }
                });

            }
            , getSearch: function(opts){
                return new TypeAheadSearch({
                    el:this.$el
                    , suppressExtra: true
                    , model: new PlainSearchResult([], {apiResult: opts.apiResult})
                    , searchUrl: opts.apiUrl
                });
            }
        });
    return PlainTypeAhead;
});