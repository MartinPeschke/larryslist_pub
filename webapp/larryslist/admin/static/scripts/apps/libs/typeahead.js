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
    , PlainTypeAhead = Backbone.View.extend({
        initialize: function(opts){
            var view = this;
            this.$filter = this.$(".query");
            this.current = null;
            this.search = this.getSearch(opts);
            this.search.on('selected', function(term){
                view.search.hide();
                view.$filter.val(term.getSearchLabel());
                view.current = term;
            });
            this.search.on("hide", function(){
                if(!view.current || view.$filter.val() != view.current.getSearchLabel()){
                    view.$filter.val("");
                }
            })
        }
        , getSearch: function(opts){
            return new TypeAheadSearch({
                el:this.$el
                , suppressExtra: true
                , model: new PlainSearchResult([], {apiResult: opts.apiResult}), apiType: opts.apiType, searchUrl: opts.apiUrl
            });
        }
    })


    , Result = ajax.Model.extend({
        idAttribute:'token'
        , getSearchLabel: function(){
            return this.get('name');
        }
        , parse: function(attrs){
            console.log(attrs);
            return attrs;

        }
    })
    , SearchResult = ajax.Collection.extend({
        model:Result
        , initialize: function(models, opts){
            this.apiResult = opts.apiResult;
        }
        , idAttribute:'token'
        , parse: function(resp){
            return getRec(resp, this.apiResult);
        }
    })
    , TokenTypeAhead = Backbone.View.extend({
        initialize: function(opts){
            var view = this;
            this.url = opts.apiUrl;
            this.$token = this.$('.typehead-token');
            this.$filter = this.$(".query");
            this.current = null;
            this.search = this.getSearch(opts);
            this.search.on('selected', function(term){
                view.search.hide();
                view.$filter.val(term.getSearchLabel());
                view.$token.val(term.id).trigger("change");
                view.current = term;
            });
            this.search.on("hide", function(){
                if(!view.current || view.$filter.val() != view.current.getSearchLabel())    {
                    view.$filter.val("");
                    view.$token.val("").trigger("change");
                }
            })
        }
        , getSearch: function(opts){
            return new TypeAheadSearch({
                el:this.$el
                , suppressExtra: true
                , model: new SearchResult([], {apiResult: opts.apiResult})
                , apiType: opts.apiType
                , searchUrl: opts.apiUrl
            });
        }
    })


    , DependentTAS = AbstractSearch.extend({
        buildQuery: function(query){
            return {filter: this.options.$dependency.val(), type: this.options.apiType, term:query};
        }
    })
    , DependentTA = TokenTypeAhead.extend({
        initialize: function(opts){
            this.dependency = opts.apiDependency;
            this.$dependency = this.$el
                                    .closest('[data-sequence], .form-validated')
                                    .find('[data-api-type='+this.dependency+']')
                                    .find('.typehead-token');
            this.$dependency.on({change: _.bind(this.toggleEnabled, this)});

            TokenTypeAhead.prototype.initialize.apply(this, arguments);

            this.toggleEnabled(false);
        }
        , toggleEnabled: function(e){
            var enabled = !!this.$dependency.val();
            if(enabled){
                this.$filter.removeAttr('disabled');
                if(e){
                    this.$filter.val("");
                    this.$token.val("").trigger("change");
                }
            } else {
                this.$filter.attr('disabled', 'disabled').val("");;
                this.$token.val("").trigger("change");
            }
        }
        , getSearch: function(opts){
            return new DependentTAS({
                el:this.$el
                , suppressExtra: true
                , model: new SearchResult([], {apiResult: opts.apiResult})
                , apiType: opts.apiType
                , searchUrl: opts.apiUrl
                , '$dependency': this.$dependency
            });
        }
    })
    , widgets = []
    , init = function(opts){
        if(opts.apiType){
            if(opts.apiDependency)
                widgets.push(new DependentTA(opts));
            else
                widgets.push(new TokenTypeAhead(opts));
        } else
            widgets.push(new PlainTypeAhead(opts));
    };
    return {init: init, PlainTypeAhead: PlainTypeAhead, TokenTypeAhead:TokenTypeAhead, DependentTA: DependentTA};
});