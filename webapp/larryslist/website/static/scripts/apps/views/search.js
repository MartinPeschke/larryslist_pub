define(
    ["tools/ajax", "text!templates/tag.html", "text!templates/searchresult.html", "text!templates/filtersection.html", "text!templates/filteroption.html"]
    , function(ajax, tagTempl, resultTempl, fsTempl, foTempl){
    var
    MODULE_KEY = 'SEARCH'
    , instance

    , Address = ajax.Model.extend({

    })
    , Addresses = ajax.Collection.extend({
        model: Address
    })
    , Collection = ajax.Model.extend({

    })
    , Collector = ajax.Model.extend({
        initialize:function(opts){
            this.register({"Address" : new Addresses(), "Collection": new Collection()});
        }
        , getName: function(){
            return this.get("initials");
        }
        , getAddress: function(){
            var a = this.get("Address");
            if(_.isEmpty(a))
                return ' ';
            else {
                a = a.first();
                return a.get("Region").name + ", " + a.get("Country").name;
            }
        }
        , getPicture: function(){
            var path = this.get("picture");
            return path?hnc.resUrl(path):"http://www.gravatar.com/avatar/00000000000000000000000000000000?d=mm";
        }
        , parseLocal: function(obj){
            obj.rank = Math.floor(Math.random()*1000);
            obj.completion = Math.floor(Math.random()*100);
            obj.subscribers = Math.floor(Math.random()*1000);
            return obj;
        }
    })
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
        , initialize: function(){
            this.setElement(this.template({model: this.model}));
            this.listenTo(this.model, "destroy", this.remove);
        }
        , toggleSelected: function(){
            var selected = this.$el.toggleClass("selected").hasClass("selected");
            this.model.set("selected", selected);
        }
        , destroy: function(){
            this.model.destroy();
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
        , getSearchQuery: function(term){
            var model = this;
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
    })
    , FilterView = ajax.View.extend({
        SECTIONS : {
            Collection: {
                root: ".collection-filters"
                , elems: {
                    "Artist": {title: "Artist", sort:1}
                    , "Genre": {title: "Genre", sort:2}
                    , "Medium": {title: "Medium", sort:3}
                    , "Origin": {title: "Origin", sort:4}
                }
            }
            , Collector: {
                root: ".collector-filters"
                , elems: {
                    "Country": {title: "Country", sort:1}
                    , "Region": {title: "Region", sort:2}
                    , "City": {title: "City", sort:3}
                    , "Gender": {title: "Gender", sort:4}
                }
            }
        }
        , initialize: function(){
            var view = this, collection_root = this.$();
            _.each(this.SECTIONS, function(val){
                view.setup(val.elems, view.$(val.root));
            });
        }
        , setup: function(props, root){
            var view = this;
            _.each(props, function(v, k){
                view.listenTo(view.model, k+":updated", view.addSection(k, v, root));
            });
        }
        , addSection: function(key, opts, root){
            var view = this;
            return function(model){
                var v = new FilterSectionView({model: model, title: opts.title});
                view.sortedInsert(root, v.$el, opts.sort);
            }
        }
    })

    , SearchTag = ajax.Model.extend({
        idAttribute:"label"
        , getLabel: function(){
            return this.get("label");
        }
    })
    , SearchTags = ajax.Collection.extend({
        model: SearchTag
        , idAttribute: "label"
        , addTags: function(label, options){
            this.addOrUpdate(_.map(label, function(l){return {label: l}}), options);
        }
        , getSearchTerm: function(){
            return this.pluck("label").join(" ");
        }
    })
    , TagView = Backbone.View.extend({
        template: _.template(tagTempl)
        , events: {'click .close': 'destroy'}
        , initialize: function(){
            this.setElement(this.template({model: this.model}));
            this.listenTo(this.model, "destroy", this.remove);
        }
        , destroy: function(){
            this.model.destroy();
        }
    })
    , SearchQueryView = Backbone.View.extend({
        events : {"submit":"onSubmit"}
        , initialize:function(opts){
            this.$query = this.$(".search-query");
            this.$tags = this.$(".search-results-tags");
            this.listenTo(this.model, "add", this.addTag);
        }
        , addTag: function(filter){
            this.$tags.append(new TagView({model: filter}).$el);
        }
        , onSubmit: function(e){
            var tags = this.$query.val().split(" ");
            if(tags){
                this.model.addTags(tags, {preserve:true});
                this.$query.val("");
            }
            e.stopPropagation();
            e.preventDefault();
            return false;
        }
    })




    , View = ajax.View.extend({
        events: {
            'change .select-sort-by': "reSort"
        }
        , initialize: function(opts){
            this.$sorting = this.$(".search-results-sorting");
            this.$results = this.$(".search-results-body");

            this.filter = new FilterModel();
            this.filterView = new FilterView({el:this.$el, model: this.filter});
            this.listenTo(this.filter, "do:filter", this.doFilter);

            this.query = new SearchTags();
            this.searchQuery = new SearchQueryView({el:this.$el, model: this.query});
            this.listenTo(this.query, "updated", this.doSearch);
            this.listenTo(this.query, "remove", this.doSearch);



            this.results = new SearchResults();
            this.listenTo(this.results, "add", this.addResult);
            this.listenTo(this.results, "updated", this.updatedResults);
        }
        , addResult: function(result){
            var t = this.$results.children(".sortable").eq(this.results.indexOf(result))
                , v = new ResultView({model: result}).$el;
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
        , search: function(resetFilters){
            var view = this, query = this.filter.getSearchQuery(this.query.getSearchTerm());
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
                        if(resetFilters)
                            view.filter.setRecursive(filters);
                    }
                    , complete: function(){
                        view.$results.removeClass("loading");
                    }
                });
            } else {
                view.results.addOrUpdate([], {'preserve':false});
                view.filter.deepClear();
                view.$(".result-count").html("0");
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
        , render: function(query){
            var tags = query?decodeURIComponent(query).split(" "):[];
            this.query.addTags(tags);
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
