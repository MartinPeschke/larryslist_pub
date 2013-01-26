define(["tools/ajax", "libs/abstractsearch"], function(ajax, AbstractSearch){
    var

    Result = ajax.Model.extend({
        idAttribute:'token'
        , getSearchLabel: function(){
            return this.get('name');
        }
    })
    , SearchResult = ajax.Collection.extend({
        model:Result
        , idAttribute:'token'
        , parse: function(resp){
            return resp.AddressSearchResult;
        }
    })

    , TypeAheadSearch = AbstractSearch.extend({
        buildQuery: function(query){
            if(this.options.$dependency)
                return {filter: this.options.$dependency.val(), type: this.options.apiType, term:query};
            else
                return {type: this.options.apiType, term:query};
        }
    })

    , View = Backbone.View.extend({
        initialize: function(opts){
            var view = this;
            this.url = opts.apiUrl;
            this.$token = this.$('.typehead-token');
            this.$filter = this.$(".query");
            this.current = null;
            var searchParams = {
                el:this.$el
                , model: new SearchResult()
                , searchUrl: this.url
                , apiType: opts.apiType
                , suppressExtra: true
            };
            this.search = new TypeAheadSearch(this.getSearchParams(searchParams));
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
        , getSearchParams: function(params){
            return params;
        }
    })

    , ViewWithDependency = View.extend({
        initialize: function(opts){
            this.dependency = opts.apiDependency;
            this.$dependency = this.$el
                                    .closest('[data-sequence], .form-validated')
                                    .find('[data-api-type='+this.dependency+']')
                                    .find('.typehead-token');
            this.$dependency.on({change: _.bind(this.toggleEnabled, this)});

            View.prototype.initialize.apply(this, arguments);

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
        , getSearchParams: function(params){
            params['$dependency'] = this.$dependency;
            return params;
        }
    });
    return {View:View, ViewWithDependency: ViewWithDependency};
});