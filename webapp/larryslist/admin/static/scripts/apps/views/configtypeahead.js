define(["tools/ajax", "libs/abstractsearch", "tools/config"], function(ajax, AbstractSearch, config){
    var
    ConfigSearch = AbstractSearch.extend({
        doSearch : function(query){
            var attr = this.options.configAttr, cfg = this.options.cfg;
            if(query){
                var result = cfg.get(attr), search = [];
                result.each(function(elem){
                    if(!!~elem.id.toLowerCase().indexOf(query)){
                        search.push(elem);
                    }
                });
                this.model.reset(search);
            } else {
                this.model.reset(
                    cfg.get(attr).models
                );
            }
        }
    })
    , ConfigTypeAhead = Backbone.View.extend({
        initialize: function(opts){
            var view = this;
            this.$filter = this.$(".query");

            config.fetch(function(cfg){

                this.search = this.getSearch(opts, cfg);
                this.search.on('selected', function(term){
                    view.search.hide();
                    view.$filter.val(term.getSearchLabel());
                });
                this.search.on("extraItemSelected unknownterm:selected unknownterm:metaSelected", function(query){
                    view.search.hide();
                    view.$filter.val(query);
                    view.$filter.trigger("change");
                });

            }, this);
        }
        , getSearch: function(opts, cfg){
            return new ConfigSearch({
                el:this.$el
                , suppressExtra: false
                , model: new Backbone.Collection()
                , configAttr: opts.configAttr
                , cfg: cfg
            });
        }
    })

    , widgets = []
    , init = function(opts){
        widgets.push(new ConfigTypeAhead(opts));
    };
    return {init: init};
});