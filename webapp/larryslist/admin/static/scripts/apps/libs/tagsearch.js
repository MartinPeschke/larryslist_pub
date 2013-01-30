define(["tools/ajax", "libs/abstractsearch"], function(ajax, AbstractSearch){
    var
        getRec = hnc.getRecursive
        , re = /-[0-9]+\./g
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
        , TagModels = Backbone.Collection.extend({
            model: PlainResult
        })
        , TagView = Backbone.View.extend({
            template : _.template('<span class="tag">{{ model.getSearchLabel() }}<span class="close">×</span><input type="hidden" name="{{ prefix }}-{{ pos }}.name" value="{{ model.id }}"/></span>')
            , events: {'click .close':"destroy"}
            , initialize: function(opts){
                this.setElement(this.template({model:this.model, prefix: opts.prefix, pos:opts.pos}));
            }
            , destroy: function(e){
                this.model.destroy();
                this.remove()
            }
            , render: function(){
                return this.$el;
            }
        })
        , TagSearchView = Backbone.View.extend({
            initialize: function(opts){
                var view = this;
                this.$input = this.$(".query");
                this.$result = this.$(".current-tags");

                this.model = new TagModels();
                this.model.on("add", this.addOne, this);
                this.model.on("destroy", this.reIndex, this);

                this.search = this.getSearch(opts);
                this.search.on('selected', function(term){
                    view.search.hide();
                    view.model.add(term);
                    view.$input.val("");
                });
                this.search.on('extraItemSelected unknownterm:selected unknownterm:metaSelected', function(termname){
                    if(termname){
                        view.search.hide();
                        view.model.add({name: termname});
                        view.$input.val("");
                    }
                });
            }
            , addOne: function(model){
                this.$result.append((new TagView({model: model, prefix: this.options.prefix, pos: this.model.length - 1})).render());
                this.search.rePosition();
            }
            , reIndex: function(){
                this.$result.find("input[name]").each(function(idx, elem){
                    var elem = $(elem);
                    elem.attr('name', elem.attr('name').replace(re, "-"+(idx-1)+"."));
                });
            }
            , getSearch: function(opts){
                return new AbstractSearch({
                    el:this.$el
                    , model: new PlainSearchResult([], {apiResult: opts.apiResult})
                    , searchUrl: opts.apiUrl
                });
            }
        })
        , widgets = []
        , init = function(opts){
            widgets.push(new TagSearchView(opts));
        };
    return {init: init, TagSearch: TagSearchView};
});