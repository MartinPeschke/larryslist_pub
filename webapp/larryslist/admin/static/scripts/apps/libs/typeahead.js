define(["tools/ajax", "libs/abstractsearch"], function(ajax, AbstractSearch){
    var
    View = Backbone.View.extend({
        initialize: function(opts){
            this.search = new AbstractSearch({el: this.$el});

        }
    })

    , ViewWithDependency = View.extend({
        initialize: function(opts){
            View.prototype.initialize.apply(this, arguments);
            this.dependency = opts.apiDependency;
            this.$dependency = this.$el
                                    .closest('[data-sequence], .form-validated')
                                    .find('[data-api-type='+this.dependency+']')
                                    .find('.typehead-token');
            this.$dependency.on({change: _.bind(this.toggleEnabled, this)});
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
        , doSearch: function(term){
            var view = this;
            ajax.submitPrefixed({
                url: this.url
                , data: {'type':this.type, term: term, filter: this.$dependency.val()}
                , success: function(resp, xhr, status){
                    view.toggle(resp.AddressSearchResult.length>0);
                    view.model.addOrUpdate(resp.AddressSearchResult,{preserve: false});
                }
            })
        }
    });
    return {View:View, ViewWithDependency: ViewWithDependency};
});