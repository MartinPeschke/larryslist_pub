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
            events: {'click .close':"destroy"}
            , initialize: function(){}
            , destroy: function(e){
                this.remove();
                this.model.destroy();
            }
            , render: function(opts){
                this.setElement(opts.template({model:this.model, prefix: opts.prefix, pos:opts.pos}));
                return this.$el;
            }
        })
        , TagSearch = AbstractSearch.extend({
            buildQuery: function(query){
                var extra = this.options.queryExtra;
                return query?_.extend({'term':query}, extra):null;
            }
        })
        , TagSearchView = Backbone.View.extend({
            MODEL_CLS: TagModels
            , initialize: function(opts){
                this.$input = this.$(".query");
                this.$result = this.$(".current-tags");
                this.tagTemplate = _.template(this.$(".tag-template").html().trim());
                var view = this;

                this.model = new this.MODEL_CLS();
                this.model.on("add", this.addOne, this);
                this.model.on("destroy", this.reIndex, this);

                this.search = this.getSearch(opts);
                this.search.on('selected', function(term){
                    view.search.hide();
                    view.model.add(term);
                    view.$input.val("");
                });

                if(opts.onCreate){
                    require([opts.onCreate], function(View){
                        var v = View.init(function(model){
                            view.model.add(model);
                            view.$input.val("");
                        });
                        view.search.on('extraItemSelected unknownterm:selected unknownterm:metaSelected', v.onCreate);
                    });
                } else {
                    this.search.on('extraItemSelected unknownterm:selected unknownterm:metaSelected', function(termname){
                        if(termname){
                            view.search.hide();
                            view.model.add({name: termname});
                            view.$input.val("");
                        }
                    });
                }

                var seed = this.$result.find(".tag").find("input");
                if(seed.length)
                    this.$(".tag").each(function(idx, el){
                        var model = new PlainResult({name: $(el).find("input[name]").val()});
                        view.model.add(model, {silent:true});
                        new TagView({model: model,el:el});
                    });
            }
            , addOne: function(model){
                this.$result.append((new TagView({model: model})).render({template: this.tagTemplate, prefix: this.options.prefix, pos: this.model.length - 1}));
                this.search.rePosition();
            }
            , reIndex: function(){
                this.$result.find("input[name]").each(function(idx, elem){
                    var elem = $(elem);
                    elem.attr('name', elem.attr('name').replace(re, "-"+(idx)+"."));
                });
            }
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