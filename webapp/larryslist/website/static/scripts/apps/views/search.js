define(
    ["tools/ajax", "models/cart", "models/user", "models/collector"
            , "views/colitem"
            , "text!templates/tag.html"
            , "text!templates/filtersection.html"
            , "text!templates/filteroption.html"]
    , function(ajax, cart, user, Collector, colItem, tagTempl, fsTempl, foTempl, srTempl, fsrTempl){
    var
    MODULE_KEY = 'SEARCH'
    , instance
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
        , events: {"click .show-more":"showMore"}
        , initialize: function(opts){
            this.setElement(this.template({model: this.model, title:opts.title}));
            if(this.model.length){this.onUpdate(this.model);}
            this.listenTo(this.model, "destroy", this.remove);
        }
        , onUpdate: function(model){
            var $el = this.$(".filter-list")
                , models = model.models
                , limit = this.defaultShow
                , len = Math.min(models.length, limit)
                , html = []
                , idx;
            for(idx=0;idx<len;idx++){
                var model = models[idx], v = new FilterOptionView({model:model, isExtra:false});
                html.push(v.el);
            }
            $el.html(html);
            if(models.length>limit){
                $el.append('<a class="link show-more" data-toggle-text="▲ '+ (models.length - limit) +' less">▼ '+ (models.length - limit) +' more</a>')
            }
        }
        , showMore: function(e){
            var $el = this.$(".filter-list")
                , current = this.$(".filter-list").children(".checkbox")
                , limit = this.defaultShow
                , models = this.model.models
                , len = models.length
                , expanded = this.$el.toggleClass("expanded").hasClass("expanded")
                , $t = $(e.target)
                , html = []
                , idx;
            if(!$t.data("backupText")){$t.data("backupText", $t.html());}
            if(expanded){
                $t.html($t.data("toggleText"));
            } else {
                $t.html($t.data("backupText"));
            }
            if(current.length < len){
                for(idx=limit;idx<len;idx++){
                    var model = models[idx], v = new FilterOptionView({model:model, isExtra:true});
                    html.push(v.el);
                }
                $(e.target).before(html);
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
        , getSearchQuery: function(resetFilters, allowEmpty){
            var model = this, term = this.get("term")||'';
            if(term.length > 2 || allowEmpty){
                var filters = {};
                if(!resetFilters){
                    _.each(this.FILTERS, function(f){
                        var l = [];
                        model.get(f.name).each(function(m){if(m.isSelected())l.push({name: m.getValue()})});
                        if(l.length)filters[f.name] = l;
                    });
                }
                return {"term":term, "Filters": filters, userToken:user.get("token")};
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
                , elems: [
                    {key: "Genre", title: "Category / Genre / Stylistic Period"}
                    , {key: "Origin", title: "Region / Origin of Artist"}
                    , {key: "Medium", title: "Medium"}
                    , {key: "Artist", title: "Artist"}
            ]}
            , Collector: { root: ".collector-filters"
                , elems: [
                    {key: "Country", title: "Country"}
                    , {key: "Region", title: "Region"}
                    , {key: "City", title: "City"}
                    , {key: "Gender", title: "Gender"}
            ]}
        }
        , events : {
            "submit .search-filters":"onSubmit"
        }
        , initialize: function(){
            var view = this, tagRoot = this.$(".search-results-tags");

            this.$form = this.$(".search-filters");
            this.$query = this.$form.find(".search-query");
            this.model.set("term", this.$query.val());

            _.each(this.SECTIONS, function(val){
                view.setup(val.elems, view.$(val.root), tagRoot);
            });
        }
        , setup: function(props, root, tagRoot){
            var view = this;
            _.each(props, function(v){
                view.listenTo(view.model, v.key+":updated", view.addSection(v, root));
                view.listenTo(view.model, v.key+":change:selected", view.setTag(v, tagRoot));
            });
        }
        , setTag: function(opts, root){
            return function(model, selected){
                if(selected){
                    root.append(new TagView({model:model}).$el);
                }
            }
        }
        , addSection: function(opts, root){
            var view = this;
            return function(model){
                var v = new FilterSectionView({model: model, title: opts.title});
                root.append(v.$el);
            }
        }
        , onSubmit: function(e){
            var val = this.$query.val().trim();
            this.model.set("term", val);
            this.model.trigger("do:search");
            if(!_.isEmpty(e)){
                e.stopPropagation();
                e.preventDefault();
            }
            return false;
        }
    })

    , View = ajax.View.extend({
        events: {
            'change .select-sort-by': "reSort"
            , "click .dismiss": "resetResults"
            , "click .search-select-all-link" :"selectAll"
            , "change [name=myCollectors]":"switchRealm"
        }
        , initialize: function(opts){
            this.$sorting = this.$(".search-results-sorting");
            this.$results = this.$(".search-results-body");
            this.setRealm(this.$(".search-realm").find("input[name=myCollectors]").filter(":checked"));

            new colItem.CartFlyout({root: this.$results});

            this.filter = new FilterModel();
            this.filterView = new FilterView({el:this.$el, model: this.filter});
            this.listenTo(this.filter, "do:filter", this.doFilter);
            this.listenTo(this.filter, "do:search", this.doSearch);

            this.results = new colItem.SearchResults();
            this.listenTo(this.results, "updated", this.updatedResults);
        }

        , buildResults: function(){
            var res = [];
            this.results.each(function(item){
                var v = colItem.getView(item, null);
                res.push(v.$el);
            });
            this.$results.append(res);
        }
        , updatedResults: function(){
            this.buildResults();
            this.$results.find(".empty")[this.results.length?"addClass":"removeClass"]("hide");
            this.checkAllSelected();
        }
        , switchRealm: function(e){
            this.setRealm($(e.target));
            this.filterView.onSubmit(false);
        }
        , setRealm: function($el){
            this.realm = $el.data();
            this.$(".search-select-all-link")[this.realm.ownedProfile?'addClass':'removeClass']('hide');
        }
        , doFilter: function(){
            this.search(false);
        }
        , doSearch: function(){
            this.search(true);
        }
        , emptyResults: function(){
            this.filter.reset(false);
            this.results.addOrUpdate([], {'preserve':false});
            this.$(".result-count").html("0");
        }
        , resetResults: function(){
            this.filter.reset(false);
            this.doSearch(true);
        }
        , search: function(resetFilters){
            var view = this, query = this.filter.getSearchQuery(resetFilters, this.realm.allowEmptySearch);
            if(query){
                var url = this.realm.url;
                this.$results.addClass("loading");
                ajax.submitPrefixed({
                    url: url
                    , data: query
                    , success: function(resp, status, xhr){
                        var results = hnc.getRecursive(resp, "Collectors.Collector", []);
                        _.each(results, function(obj){
                            cart.prepResult(user.prepResult(obj));
                        });
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
            this.buildResults();
        }
        , reSort: function(e){
            var el = $(e.target).find("option").filter(":selected");
            this.results.reSort(el.val(), el.data("reverse"));
            this.reSortResults();
        }
        , selectAll: function(e){
            var $t = $(e.currentTarget), selected = $t.toggleClass("selected").hasClass("selected");
            if(selected){
                $t.data("backupText", $t.find(".text").text());
                $t.find(".text").html($t.data("toggleText"));
            } else {
                $t.find(".text").text($t.data("backupText"));
            }
            cart[selected?'addProfiles':'removeProfiles'](this.results);
        }
        , checkAllSelected: function(){
            var results = this.$results.find(".search-results-row"), $t = this.$(".search-select-all-link"), selected = results.length == results.filter(".selected").length;
            if(selected){
                $t.addClass("selected");
                $t.data("backupText", $t.find(".text").text());
                $t.find(".text").html($t.data("toggleText"));
            } else {
                $t.removeClass("selected");
                $t.find(".text").text($t.data("backupText"));
            }
        }
        , render: function(){
            this.doSearch(true);
        }
    })
    , init = function(opts){
        if(!instance){
            var opts = opts.pageconfig[MODULE_KEY]||{};
            instance = new View(opts);
        }
        return instance;
    };
return {init:init, View:View};
});
