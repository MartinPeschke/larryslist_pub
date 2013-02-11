define(
    ["tools/ajax", "models/cart", "models/collector"
            , "text!templates/tag.html"
            , "text!templates/searchresult.html"
            , "text!templates/filtersection.html"
            , "text!templates/filteroption.html"
            , "text!templates/flyout.html"]
    , function(ajax, cart, Collector, tagTempl, resultTempl, fsTempl, foTempl, flyoutTempl){
    var
    MODULE_KEY = 'SEARCH'
    , instance

    , SearchResults = ajax.Collection.extend({
        model: Collector
        , compField: "initials"
        , comparator : function(model){
            return model.get(this.compField);
        }
        , reSort: function(field){
            this.compField = field;
            this.sort();
        }
    })
    , ResultView = Backbone.View.extend({
        events: {click:"toggleSelected"}
        , template: _.template(resultTempl)
        , initialize: function(opts){
            this.setElement(this.template({model: this.model, inCart:opts.inCart}));
            this.listenTo(this.model, "destroy", this.remove);
            this.$button = this.$el.find(".btn");
            if(opts.inCart)this.toggleSelected();
        }
        , toggleSelected: function(){
            var selected = this.$el.toggleClass("selected").hasClass("selected");
            this.model.set("selected", selected);
            cart[selected?'addProfile':'removeProfile'](this.model);
            var btnData = this.$button.data();
            this.$button.html(btnData[selected?'textUnselected':'textSelected'])[selected?'removeClass':'addClass']("btn-primary");
            this.$el.trigger("collector:"+(selected?"selected":"unselected"));
        }
        , destroy: function(){
            this.model.destroy();
        }
    })
    , CartFlyout = Backbone.View.extend({
        template: _.template(flyoutTempl)
        , tagName: "div"
        , className: "cart-flyout"
        , initialize:function(opts){
            this.model = cart;
            this.listenTo(this.model, "item:changed", this.render);
            this.render();
            this.$el.appendTo(opts.root);
            this.offset = opts.root.offset();
            opts.root.on("collector:selected collector:unselected", _.bind(this.adjust, this));

        }
        , render: function(){
            var show =  this.model.getItems().length>0;
            this.$el.html(this.template({total:this.model.getItems().length}));
            this.$el[show?'removeClass':'addClass']("invisi");
        }
        , adjust: function(e){
            var pos = $(e.target).offset();
            this.$el.css({top:pos.top - this.offset.top});
        }
    })

    , FilterTag = ajax.Model.extend({
        idAttribute: "name"
        , getValue: function(){return this.get("name");}
        , getLabel: function(){return this.get("name");}
        , isSelected: function(){return this.get("selected");}
    })
    , FilterTags = ajax.Collection.extend({idAttribute: "name", model: FilterTag})

    , TokenTag = ajax.Model.extend({
        idAttribute: "name"
        , getValue: function(){return this.get("token");}
        , getLabel: function(){return this.get("name");}
        , isSelected: function(){return this.get("selected");}
    })
    , TokenTags = ajax.Collection.extend({idAttribute: "name", model: TokenTag})

    , FilterOptionView = Backbone.View.extend({
        template: _.template(foTempl)
        , events: {"change input": "onChange"}
        , initialize: function(opts){
            this.setElement(this.template({model: this.model, isExtra:opts.isExtra}));
            this.listenTo(this.model, "destroy", this.remove);
            this.listenTo(this.model, "change:selected", this.change);
        }
        , change: function(model, selected){
            this.$("input").prop("checked", selected);
        }
        , onChange: function(){
            this.model.set("selected", this.$("input").is(":checked"));
        }
    })
    , FilterSectionView = Backbone.View.extend({
        template: _.template(fsTempl)
        , defaultShow: 5
        , initialize: function(opts){
            this.setElement(this.template({model: this.model, title:opts.title}));
            if(this.model.length){this.onUpdate(this.model);}
            this.listenTo(this.model, "destroy", this.remove);
        }
        , onUpdate: function(models){
            var $el = this.$(".filter-list"), limit = this.defaultShow;
            models.each(function(model, idx){
                var v = new FilterOptionView({model:model, isExtra:idx>=limit});
                $el.append(v.$el);
            });
            if(models.length>limit){
                $el.append('<a class="link show-more" data-toggle-text="▲ '+ (models.length - limit) +' less" data-toggle-target=".filter-section" data-toggle-class="expanded">▼ '+ (models.length - limit) +' more</a>')
            }
        }
        , getTitle: function(){
            return this.options.title;
        }
    })
    , FilterModel = ajax.Model.extend({
        FILTERS: [
            {name: "Artist", cls:FilterTags}
            , {name: "Gender", cls:FilterTags}
            , {name: "Genre", cls:FilterTags}
            , {name: "Medium", cls:FilterTags}
            , {name: "Origin", cls:FilterTags}
            , {name: "Country", cls:TokenTags}
            , {name: "Region", cls:TokenTags}
            , {name: "City", cls:TokenTags}
        ]
        , initialize:function(opts){
            var model = this, filter = {};

            _.each(this.FILTERS, function(f){
                filter[f.name] = new f.cls();
                model.listenTo(filter[f.name], "change:selected", function(){model.trigger("do:filter");})
            });

            this.register(filter);
        }
        , getSearchQuery: function(){
            var model = this, term = this.get("term");
            if(term.length > 2){
                var filters = {};
                _.each(this.FILTERS, function(f){
                    var l = [];
                    model.get(f.name).each(function(m){if(m.isSelected())l.push({name: m.getValue()})});
                    if(l.length)filters[f.name] = l;
                });
                return {"term":term, "Filters": filters};
            }
        }
        , reset: function(models){
            var term = this.get("term");
            this.deepClear();
            if(models !== false){
                this.setRecursive(models);
                this.set("term", term);
            }
        }
    })
    , TagView = Backbone.View.extend({
        template: _.template(tagTempl)
        , events: {'click .close': 'change'}
        , initialize: function(){
            this.setElement(this.template({model: this.model}));
            this.listenTo(this.model, "destroy", this.remove);
            this.listenTo(this.model, "change:selected", this.remove);
        }
        , change: function(){
            this.model.set("selected", false);
        }
    })

    , FilterView = ajax.View.extend({
        SECTIONS : { Collection: { root: ".collection-filters"
                , elems: {
                    "Artist": {title: "Artist", sort:1}
                    , "Genre": {title: "Genre", sort:2}
                    , "Medium": {title: "Medium", sort:3}
                    , "Origin": {title: "Origin", sort:4}
            }}
            , Collector: { root: ".collector-filters"
                , elems: {
                    "Country": {title: "Country", sort:1}
                    , "Region": {title: "Region", sort:2}
                    , "City": {title: "City", sort:3}
                    , "Gender": {title: "Gender", sort:4}
            }}
        }
        , events : {
            "submit .search-filters":"onSubmit"
        }
        , initialize: function(){
            var view = this, tagRoot = this.$(".search-results-tags");

            this.$form = this.$(".search-filters");
            this.$query = this.$form.find(".search-query");
            this.model.set("term", this.$query.val());
            this.model.listenTo(this.model, "change:term", function(e){
                view.$query.val(view.model.get("term"));
            });

            _.each(this.SECTIONS, function(val){
                view.setup(val.elems, view.$(val.root), tagRoot);
            });
        }
        , setup: function(props, root, tagRoot){
            var view = this;
            _.each(props, function(v, k){
                view.listenTo(view.model, k+":updated", view.addSection(k, v, root));
                view.listenTo(view.model, k+":change:selected", view.setTag(k, v, tagRoot));
            });
        }
        , setTag: function(key, opts, root){
            return function(model, selected){
                if(selected){
                    root.append(new TagView({model:model}).$el);
                }
            }
        }
        , addSection: function(key, opts, root){
            var view = this;
            return function(model){
                var v = new FilterSectionView({model: model, title: opts.title});
                view.sortedInsert(root, v.$el, opts.sort);
            }
        }
        , onSubmit: function(e){
            var val = this.$query.val().trim();
            if(val.length){
                this.model.set("term", val);
                this.model.trigger("do:search");
            }
            e.stopPropagation();
            e.preventDefault();
            return false;
        }
    })


    , View = ajax.View.extend({
        events: {
            'change .select-sort-by': "reSort"
            , "click .dismiss": "emptyResults"
        }
        , initialize: function(opts){
            this.$sorting = this.$(".search-results-sorting");
            this.$results = this.$(".search-results-body");
            this.cartFlyout = new CartFlyout({root: this.$results});


            this.filter = new FilterModel();
            this.filterView = new FilterView({el:this.$el, model: this.filter});
            this.listenTo(this.filter, "do:filter", this.doFilter);
            this.listenTo(this.filter, "do:search", this.doSearch);

            this.results = new SearchResults();
            this.listenTo(this.results, "add", this.addResult);
            this.listenTo(this.results, "updated", this.updatedResults);
        }
        , addResult: function(result){
            var t = this.$results.children(".sortable").eq(this.results.indexOf(result))
                , v = new ResultView({model: result, inCart: cart.contains(result)}).$el;
            if(t.length){
                t.before(v);
            } else {
                this.$results.append(v);
            }
        }
        , updatedResults: function(){
            this.$results.find(".empty")[this.results.length?"addClass":"removeClass"]("hide");
        }
        , doFilter: function(){
            this.search(false);
        }
        , doSearch: function(){
            this.search(true);
        }
        , emptyResults: function(){
            this.results.addOrUpdate([], {'preserve':false});
            this.filter.reset(false);
            this.$(".result-count").html("0");
        }
        , search: function(resetFilters){
            var view = this, query = this.filter.getSearchQuery();
            if(query){
                this.$results.addClass("loading");
                ajax.submitPrefixed({
                    url: '/web/search/collector'
                    , data: query
                    , success: function(resp, status, xhr){
                        var results = hnc.getRecursive(resp, "Collectors.Collector", []);
                        view.results.addOrUpdate(results, {'preserve':false});
                        view.$(".result-count").html(results.length);

                        var filters = hnc.getRecursive(resp, "Filters", []);
                        if(resetFilters){
                            view.filter.reset(filters);
                        }
                    }
                    , complete: function(){
                        view.$results.removeClass("loading");
                    }
                });
            } else {
                this.emptyResults();
            }
        }
        , reSortResults: function(){
            this.$results.children(".sortable").off().remove();
            this.results.each(this.addResult, this);
        }
        , reSort: function(e){
            this.results.reSort($(e.target).val());
            this.reSortResults();
        }
        , render: function(){
            this.doSearch(true);
        }
    })
    , init = function(opts){
        if(!instance){
            var opts = opts.pageconfig[MODULE_KEY];
            instance = new View(opts);
        }
        return instance;
    };
return {init:init, View:View};
});
