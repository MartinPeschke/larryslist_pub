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
            return this.get("firstName") + " " + this.get("lastName");
        }
        , getAddress: function(){
            var a = this.get("Address")
            if(_.isEmpty(a))
                return ' ';
            else {
                a = a.first();
                return a.get("City").name + " " + a.get("Country").name;
            }
        }
        , getPicture: function(){
            var path = this.get("picture");
            return path?hnc.resUrl(path):"http://www.gravatar.com/avatar/00000000000000000000000000000000?d=mm";
        }
    })
    , SearchResults = ajax.Collection.extend({
        model: Collector
    })
    , ResultView = Backbone.View.extend({
        template: _.template(resultTempl)
        , initialize: function(){
            this.setElement(this.template({model: this.model}));
            this.listenTo(this.model, "destroy", this.remove);
        }
        , destroy: function(){
            this.model.destroy();
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
    })

    , FilterTag = ajax.Model.extend({
        idAttribute: "name"
        , getValue: function(){
            return this.get("name");
        }
        , isSelected: function(){
            return this.get("selected");
        }
    })
    , FilterTags = ajax.Collection.extend({
        idAttribute: "name"
        , model: FilterTag
    })


    , FilterOptionView = Backbone.View.extend({
        template: _.template(foTempl)
        , events: {"change input": "onChange"}
        , initialize: function(opts){
            this.setElement(this.template({model: this.model}));
            this.listenTo(this.model, "destroy", this.remove);
        }
        , onChange: function(){
            this.model.set("selected", this.$("input").is(":checked"));
        }
    })

    , FilterSectionView = Backbone.View.extend({
        template: _.template(fsTempl)
        , initialize: function(opts){
            this.setElement(this.template({model: this.model, title:opts.title}));
            this.listenTo(this.model, "destroy", this.remove);
            this.listenTo(this.model, "updated", this.onUpdate);
        }
        , onUpdate: function(models){
            var $el = this.$(".filter-list");
            models.each(function(model){
                var v = new FilterOptionView({model:model});
                $el.append(v.$el);
            });
        }
        , getTitle: function(){
            return this.options.title;
        }
    })
    , FilterModel = ajax.Model.extend({
        FILTERS: ["Artist", "Gender", "Genre", "Medium", "Origin"]
        , initialize:function(opts){
            var model = this, filter = {};
            _.each(this.FILTERS, function(k){
                filter[k] = new FilterTags();
                model.listenTo(filter[k], "change:selected", function(){model.trigger("do:filter");})
            });
            filter.tags = new SearchTags();
            this.register(filter);
        }
        , addTags: function(label, options){
            this.get("tags").addOrUpdate(_.map(label, function(l){return {label: l}}), options);
        }
        , getSearchQuery: function(){
            var model = this, tags = this.get("tags"), term = tags.pluck("label").join(" ");
            if(term.length > 2){
                var filters = {}
                _.each(this.FILTERS, function(k){
                    var l = [];
                    model.get(k).each(function(m){if(m.isSelected())l.push({name: m.getValue()})});
                    if(l.length)filters[k] = l;
                });
                return {"term":term, "Filters": filters};
            }
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
    , FilterView = Backbone.View.extend({
        SECTIONS : {
            "Artist": {title: "Artist"}
            , "Genre": {title: "Genre"}
            , "Medium": {title: "Medium"}
            , "Origin": {title: "Origin"}
        }
        , events : {"submit":"onSubmit"}
        , initialize: function(){
            var view = this;
            this.$query = this.$(".search-query");
            this.$tags = this.$(".search-results-tags");
            this.listenTo(this.model, "tags:add", this.addTag);

            _.each(this.SECTIONS, function(v, k, obj){
                obj.view = new FilterSectionView({model: view.model.get(k), title: v.title});
                view.$(".collection-filters").append(obj.view.$el);
            });

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



    , View = Backbone.View.extend({
        initialize: function(opts){
            this.$sorting = this.$(".search-results-sorting");
            this.$results = this.$(".search-results-body");

            this.filter = new FilterModel();
            this.searchQuery = new FilterView({el:this.$el, model: this.filter});
            this.listenTo(this.filter, "tags:updated", this.doSearch);
            this.listenTo(this.filter, "tags:remove", this.doSearch);
            this.listenTo(this.filter, "do:filter", this.doFilter);



            this.results = new SearchResults();
            this.listenTo(this.results, "add", this.addResult);
            this.listenTo(this.results, "updated", this.updatedResults);
        }
        , addResult: function(result){
            this.$results.append(new ResultView({model: result}).$el);
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
            var view = this, query = this.filter.getSearchQuery();
            if(query){
                this.$results.addClass("loading");
                ajax.submitPrefixed({
                    url: '/web/search/collector'
                    , data: query
                    , success: function(resp, status, xhr){
                        var results = hnc.getRecursive(resp, "Collectors.Collector", []);
                        view.results.addOrUpdate(results, {'preserve':false});

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
            }
        }
        , render: function(query){
            var tags = query?decodeURIComponent(query).split(" "):[];
            this.filter.addTags(tags);
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
