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
            return {key: this.options.apiKey, value: query};
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
            //this.listenTo(this.model, "destroy", this.remove);


            var ta = new PlainTypeAhead({el: this.$(".type-ahead-field"), apiKey: opts.key});
            this.$(".type-ahead-field").find(".query").prop("placeholder", opts.placeholder);
            ta.search.on('selected', function(term){
                ta.search.hide();
                ta.$query.val("");
                view.model.addOrUpdate(term, {preserve: true});
                view.model.get(term.id).set("selected", true);
            });
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
            if(models.length>limit){
                $el.append('<a class="link show-more" data-toggle-text="▲ '+ (models.length - limit) +' less">▼ '+ (models.length - limit) +' more</a>')
            }
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
                model.listenTo(filter[f.name], "change:selected", function(){model.trigger("do:filter");})
            });

            this.register(filter);
            this.setRecursive(filters);

            // set SELECTED=TRUE for anything in QUERY
            _.each(query, function(val, key, obj){val.selected = true;});
            this.setRecursive(query, {preserve: true});

        }
        , getSearchQuery: function(resetFilters, allowEmpty){
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
                    m.set("selected", false);
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
            {key: "ARTIST", prop:"Artist", title: "Artist", expanded: true, allLabel: "All Artists", placeholder:"Enter artist's name", expandable:false}
            , {key: "CITY", prop:"City", title: "City", expanded: true, allLabel: "All Cities", placeholder:"Enter city name", expandable:false}
            , {key: "GENDER", prop:"Gender", title: "Gender", expanded: false, allLabel: "All Genders", expandable:true}
            , {key: "COUNTRY", prop:"Country", title: "Country", expanded: false, allLabel: "All Countries", placeholder:"Enter country name", expandable:true}
            , {key: "GENRE", prop:"Genre", title: "Genre", expanded: false, allLabel: "All Genres", placeholder:"Enter a genre", expandable:true}
            , {key: "ORIGIN", prop:"Origin", title: "Regional Art Coverage", expanded: false, allLabel: "All Regions", placeholder:"Enter region", expandable:true}
            , {key: "MEDIUM", prop:"Medium", title: "Medium", expanded: false, allLabel: "All Media", placeholder:"Enter medium", expandable:true}
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
            var view = this, root = this.$form;
            var v = new FilterSectionView(_.extend({model: view.model.get(props.key)}, props));
            root.append(v.$el);
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
            , "click .search-select-all-link" :"selectAll"
            , "change [name=myCollectors]":"switchRealm"
        }
        , initialize: function(opts){
            this.$sorting = this.$(".search-results-sorting");
            this.$results = this.$(".search-results-body");
            this.setRealm(this.$(".search-realm").find("input[name=myCollectors]").filter(":checked"));

            this.filter = new FilterModel(opts.filters, opts.query);
            this.filterView = new FilterView({el:this.$el, model: this.filter});
            this.listenTo(this.filter, "do:filter", this.doFilter);
            this.listenTo(this.filter, "do:search", this.doSearch);

            this.results = new colItem.SearchResults();
            this.listenTo(this.results, "updated emptied", this.updatedResults);
            this.lastQuery = {};
            this.lastResult;
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
            var view = this, query = this.filter.getSearchQuery(resetFilters);
            if(!_.isEqual(this.lastQuery, query)){
                var url = this.realm.url;
                this.$results.addClass("loading");
                var lastResult = this.lastResult = hashlib.UUID();
                ajax.submitPrefixed({
                    url: url
                    , data: query
                    , success: function(resp, status, xhr){
                        if(lastResult != view.lastResult)return;
                        var results = hnc.getRecursive(resp, "Collectors.Collector", []);
                        _.each(results, function(obj){
                            cart.prepResult(user.prepResult(obj));
                        });
                        view.results.addOrUpdate(results, {'preserve':false});
                        view.$(".result-count").html(results.length);
                    }
                    , complete: function(){
                        if(lastResult != view.lastResult)return;
                        view.$results.removeClass("loading");
                    }
                });
            }
            this.lastQuery = query;
        }
        , reSortResults: function(){
            this.$results.children(".sortable").off().remove();
            this.buildResults();
        }
        , reSort: function(e){
            var sw = $(e.target);
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
