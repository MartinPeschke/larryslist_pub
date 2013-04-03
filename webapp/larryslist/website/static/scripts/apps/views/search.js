define(
    ["tools/hash", "tools/ajax", "models/cart", "models/user", "models/collector"
            , "tools/abstractsearch", "text!templates/taresult.html"
            , "views/colitem"
            , "text!templates/tag.html"
            , "text!templates/filtersection.html"
            , "text!templates/filteroption.html"]
    , function(hashlib, ajax, cart, user, Collector,  AbstractSearch, typeTmpl, colItem, tagTempl, fsTempl, foTempl){
    var
    MODULE_KEY = 'SEARCH'
    , instance
    , getRec = hnc.getRecursive

    , FilterTag = ajax.Model.extend({
        idAttribute: "value"
        , getValue: function(){return this.get("value");}
        , getLabel: function(){return this.get("label");}
        , isSelected: function(){return this.get("selected");}
        , getSearchLabel: function(){
            return this.get("label");
        }
    })
    , FilterTags = ajax.Collection.extend({idAttribute: "value", model: FilterTag})

    , TypeAheadSearch = AbstractSearch.extend({
        template : _.template(typeTmpl)
        , submitFunc: _.bind(ajax.submit, ajax)
        , buildQuery: function(query){
            return query?{key: this.options.apiKey, value: query}:null;
        }
    })
    , PlainTypeAhead = Backbone.View.extend({
        initialize: function(opts){
            var view = this, $el = this.$el;
            opts.mapping = opts.mapping || {};
            this.$query = this.$(".query");
            this.search = this.getSearch(opts);
        }
        , getSearch: function(opts){
            return new TypeAheadSearch({
                el:this.$el
                , suppressExtra: true
                , model: new FilterTags([])
                , searchUrl: '/search/entity'
                , apiKey: opts.apiKey
            });
        }
    })


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
        , selectSilent: function(val){
            this.model.set({selected: val}, {silent: true});
            this.$("input").prop("checked", val);
        }
    })
    , FilterSectionView = Backbone.View.extend({
        template: _.template(fsTempl)
        , defaultShow: 20
        , events: {
            "click .show-more":"showMore"
            , "click .show-less":"showLess"
        }
        , initialize: function(opts){
            var view = this;
            this.setElement(this.template(opts));
            this.selectedCount = 0;
            this.model.each(function(m){if(m.get("selected"))this.selectedCount++;}, this);

            this.allModel = new FilterTag({label: this.options.allLabel, selected:this.selectedCount===0, allModel: true});
            this.allView = new FilterOptionView({model:this.allModel, isExtra:false});
            this.render(this.model);

            this.listenTo(this.model, "add", this.addOption);
            this.listenTo(this.model, "change:selected", this.filterSelected);
            this.listenTo(this.allModel, "change:selected", this.allSelected);

            if(opts.hasMore){
                this.$(".type-ahead-field").before(this.showMoreTempl);
                var ta = new PlainTypeAhead({el: this.$(".type-ahead-field"), apiKey: opts.key});
                this.$(".type-ahead-field").find(".query").prop("placeholder", opts.placeholder);
                ta.search.on('selected', function(term){
                    ta.search.hide();
                    ta.$query.val("");
                    view.model.addOrUpdate(term, {preserve: true});
                    view.model.get(term.id).set("selected", true);
                });

            }
        }
        , render: function(model){
            var $el = this.$(".filter-list")
                , models = model.models
                , limit = this.defaultShow
                , len = Math.min(models.length, limit)
                , html = []
                , idx;
            html.push(this.allView.el);
            for(idx=0;idx<len;idx++){
                var model = models[idx], v = new FilterOptionView({model:model, isExtra:false});
                html.push(v.el);
            }
            $el.append(html);
        }
        , addOption: function(model){
            var $el = this.$(".filter-list");
            var v = new FilterOptionView({model:model, isExtra:false});
            $el.append(v.el);
        }
        , allSelected: function(){
            this.model.each(function(m){if(m.get("selected"))m.set("selected", false);}, this);
            this.allModel.set("selected", true);
        }
        , filterSelected: function(model, selected){
            if(selected)this.selectedCount++;
            else this.selectedCount--;
            this.checkAll();
        }
        , checkAll:function(e){
            this.allView.selectSilent(this.selectedCount <= 0);
        }
        , showLess: function(e){
            var removals = [];
            this.model.each(function(m, idx){if(!m.get("selected") && idx > 4 )removals.push(m)});
            _.invoke(removals, "destroy");
            this.$el.find(".show-less").hide();
            this.$el.find(".show-more").show();

        }
        , showMore: function(e){
            var view = this
                , limit = this.defaultShow
                , len = this.model.models.length;
            ajax.submit({url:'/search/entity/'+this.options.key+"/"+len, success: function(resp, status, xhr){
                view.model.addOrUpdate(resp.result, {preserve:true});
                view.$(".show-less").show();
                if(resp.isComplete){view.$(".show-more").hide();}
            }});
        }
        , getTitle: function(){
            return this.options.title;
        }
    })
    , FilterModel = ajax.Model.extend({
        FILTERS: [
            {name: "ARTIST", cls:FilterTags}
            , {name: "GENDER", cls:FilterTags}
            , {name: "GENRE", cls:FilterTags}
            , {name: "MEDIUM", cls:FilterTags}
            , {name: "ORIGIN", cls:FilterTags}
            , {name: "COUNTRY", cls:FilterTags}
            , {name: "REGION", cls:FilterTags}
            , {name: "CITY", cls:FilterTags}
        ]
        , initialize:function(filters, query){
            var model = this, filter = {};
            query = query || {};

            _.each(this.FILTERS, function(f){
                filter[f.name] = new f.cls(null);
                model.listenTo(filter[f.name], "change:selected", function(){model.trigger("do:search");})
            });

            this.register(filter);
            this.setRecursive(filters);

            // set SELECTED=TRUE for anything in QUERY
            _.each(query, function(val, key, obj){val.selected = true;});
            this.setRecursive(query, {preserve: true});

        }
        , getSearchQuery: function(){
            var model = this;
            var filters = [];
            _.each(this.FILTERS, function(f){
                model.get(f.name).each(function(m){
                    if(m.isSelected()&&m.getValue())filters.push({key:f.name, value: m.getValue()});
                });
            });
            return {"Filter": filters, userToken:user.get("token")};
        }
        , reset: function(models){
            var model = this;
            _.each(this.FILTERS, function(f){
                model.get(f.name).each(function(m){
                    if(m.get("selected"))m.set("selected", false);
                })
            })
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
        FILTER : [
            {key: "ARTIST", prop:"Artist", title: "Artist", expanded: true, allLabel: "All Artists", placeholder:"Enter artist's name", expandable:false, hasMore: true}
            , {key: "CITY", prop:"City", title: "City", expanded: true, allLabel: "All Cities", placeholder:"Enter city name", expandable:false, hasMore: true}
            , {key: "GENDER", prop:"Gender", title: "Gender", expanded: false, allLabel: "All Genders", expandable:true, hasMore: false}
            , {key: "COUNTRY", prop:"Country", title: "Country", expanded: false, allLabel: "All Countries", placeholder:"Enter country name", expandable:true, hasMore: true}
            , {key: "GENRE", prop:"Genre", title: "Genre", expanded: false, allLabel: "All Genres", placeholder:"Enter a genre", expandable:true, hasMore: true}
            , {key: "ORIGIN", prop:"Origin", title: "Region of Interest", expanded: false, allLabel: "All Regions", placeholder:"Enter region", expandable:true, hasMore: true}
            , {key: "MEDIUM", prop:"Medium", title: "Medium", expanded: false, allLabel: "All Media", placeholder:"Enter medium", expandable:true, hasMore: true}
        ]
        , events : {
            "submit .search-filters":"onSubmit"
        }
        , initialize: function(){
            var view = this, tagRoot = this.$(".search-results-tags");
            this.$form = this.$(".search-filters");
            _.each(this.FILTER, view.setup, this);
        }
        , setup: function(props){
            var root = this.$form
                , tagRoot = this.$(".search-results-tags")
                , model = this.model.get(props.key)
                , doTag = this.setTag(tagRoot);
            this.listenTo(this.model, props.key+":change:selected", doTag);
            model.each(function(m){
                if(m.get("selected"))doTag(m, true);
            });

            var v = new FilterSectionView(_.extend({model: model}, props));
            root.append(v.$el);
        }
        , setTag: function(tagRoot){
            return function(model, selected){
                if(selected){
                    tagRoot.append(new TagView({model:model}).$el);
                }
            }
        }
        , onSubmit: function(e){
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
            'click .sortable-col': "reSort"
            , "click .dismiss": "resetResults"
            , "click .show-more": "showMoreResults"
            , "change [name=myCollectors]":"switchRealm"
        }
        , count: _.template('<b class="highlight">{{ count }} Search Results</b>')
        , partialCount: _.template('<b class="highlight">{{ count }} of {{ total }} Search Results</b>')
        , showMore: '<a class="search-placeholder show-more link">Show more</a>'
        , pageSize:60
        , initialize: function(opts){
            this.$sorting = this.$(".search-results-sorting");
            this.$results = this.$(".search-results-body");
            this.setRealm(this.$(".search-realm").find("input[name=myCollectors]").filter(":checked"));

            this.filter = new FilterModel(opts.filters, opts.query);
            this.filterView = new FilterView({el:this.$el, model: this.filter});
            this.listenTo(this.filter, "do:search", this.search);

            this.results = new colItem.SearchResults();
            this.listenTo(this.results, "updated emptied", this.updatedResults);
            this.listenTo(this.results, "add", this.addResult);
            this.lastQuery = {};
            this.rawResults = [];
            this.lastResult;
        }
        , addResult: function(model){
            var t = this.$results.children(".sortable").eq(this.results.indexOf(model))
                , v = colItem.getView(model, null);
            if(t.length){
                t.before(v.$el);
            } else {
                this.$results.append(v.$el);
            }
        }
        , updatedResults: function(){
            var r = this.results, $r = this.$results;
            if(r.length >= this.rawResults.length){
                $r[r.length === 0?'addClass':'removeClass']("is-empty");
                $r.siblings(".show-more").remove();
                this.$(".results-counter").html(this.count({count: r.length}));
            } else {
                $r.removeClass("is-empty");
                var link = $r.siblings(".show-more").remove();
                if(!link.length)link = this.showMore;
                $r.after(link);
                this.$(".results-counter").html(this.partialCount({count: r.length, total: this.rawResults.length}));
            }
        }
        , switchRealm: function(e){
            this.setRealm($(e.target));
            this.search(true);
        }
        , setRealm: function($el){
            this.realm = $el.data();
        }
        , emptyResults: function(){
            this.filter.reset(false);
            this.results.addOrUpdate([], {'preserve':false});
        }
        , resetResults: function(){
            this.filter.reset(false);
            this.search();
        }
        , search: function(force){
            var view = this, query = this.filter.getSearchQuery();
            if(!_.isEqual(this.lastQuery, query) || force){
                var url = this.realm.url;
                var lastResult = this.lastResult = hashlib.UUID();
                this.$results.addClass("loading").removeClass("is-empty").siblings(".show-more").remove();
                this.$(".results-counter").html("Loading...");
                ajax.submitPrefixed({
                    url: url
                    , data: query
                    , success: function(resp, status, xhr){
                        if(lastResult != view.lastResult)return;
                        view.rawResults = hnc.getRecursive(resp, "Collectors.Collector", []);
                        view.appendResults(view.rawResults.slice(0, view.pageSize), false);
                    }
                    , complete: function(){
                        if(lastResult == view.lastResult)view.$results.removeClass("loading");
                    }
                });
            }
            this.lastQuery = query;
        }
        , appendResults: function(results, preserve){
            _.each(results, function(obj){
                cart.prepResult(user.prepResult(obj));
            });
            this.results.addOrUpdate(results, {'preserve':preserve});
        }
        , showMoreResults: function(e){
            var len = this.results.length;
            this.appendResults(this.rawResults.slice(len, len+this.pageSize), true);
        }
        , reSort: function(e){
            var sw = $(e.currentTarget);
            sw.siblings(".sortable-col").removeClass("down up")
            if(sw.hasClass("down")){
                sw.removeClass("down").addClass("up");
            } else if(sw.hasClass("up")){
                sw.removeClass("up").addClass("down");
            } else {
                sw.addClass("down");
            }
            var prop = sw.data("property");
            this.results.reSort(prop, sw.hasClass("down"));
        }
        , render: function(){
            this.search();
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
