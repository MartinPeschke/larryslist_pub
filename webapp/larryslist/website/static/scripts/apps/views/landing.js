define(["tools/ajax", "tools/abstractsearch", "text!templates/taresult.html"], function(ajax, AbstractSearch, tmpl){
        var
        getRec = hnc.getRecursive
        , PlainResult = ajax.Model.extend({
            idAttribute:'value'
            , getKey: function(){
                return this.get("key")||'ARTIST'
            }
            , getSearchLabel: function(){
                if(this.get('country'))
                    return this.get("label") +", " + this.get('country');
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
                if(this.apiResult)
                    return getRec(resp, this.apiResult);
                else
                    return resp
            }
        })
        , TypeAheadSearch = AbstractSearch.extend({
            template : _.template(tmpl)
            , submitFunc : _.bind(ajax.submit, ajax)
            , buildQuery: function(query){
                if(this.options.apiKey)
                    return query?{key: this.options.apiKey, value: query}:null;
                else
                    return query?{term:query}:null;
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
                    view.$query.prev(".key").attr("name", term.getKey()).val(term.get('value'));
                    view.current = term;

                });
                this.search.on('extraItemSelected unknownterm:selected unknownterm:metaSelected', function(termname){view.$query.val("");view.current=null;});
                this.search.on('hide', function(){
                    if(!view.current || view.current.getSearchLabel() != view.$query.val()){
                        view.$query.val("");
                        view.current = null;
                        view.$query.prev(".key").removeAttr("name").val("");
                    }
                });
            }
            , getSearch: function(opts){
                return new TypeAheadSearch({
                    el:this.$el
                    , suppressExtra: true
                    , model: new PlainSearchResult([], {apiResult: opts.apiResult})
                    , searchUrl: opts.apiUrl
                    , apiKey: opts.apiKey
                });
            }
        })
    , View = Backbone.View.extend({
        events: {"submit":"onSubmit"}
        , initialize: function(opts){
            var view = this;
            view.typeaheads = [];
            this.$(".typeahead").each(function(idx, elem){
                view.typeaheads.push(new PlainTypeAhead(_.extend({el:elem}, $(elem).data())));
            });
        }
        , onSubmit: function(e){
            var submittable = false, len = this.typeaheads.length, i=0;
            for(i;i<len;i++){
                var v = this.typeaheads[i];
                v.search.hide();
                submittable = submittable || !!v.current;
            }
            return submittable;
        }
    });
    return View;
});