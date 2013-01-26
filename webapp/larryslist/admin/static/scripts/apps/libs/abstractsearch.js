define(["tools/ajax", "text!templates/searchresult.html"]
    , function(ajax, search_result_template){

        var numberMap = {48:0,  49:1, 50:2, 51:3, 52:4, 53:5, 54:6, 55:7, 56:8, 57:9, 96:0, 97:1, 98:2, 99:3, 100:4, 101:5, 102:6, 103:7, 104:8, 105:9}
        , AbstractSearch = Backbone.View.extend({
            shown : false
            , template:_.template(search_result_template)
            , initialize: function(opts){
                this.template = this.options.template||this.template;
                this.suppressExtra = this.options.suppressExtra;
                this.searchUrl = opts.searchUrl;

                var view = this;
                this.$searchBox = this.$el.find(".query");
                this.$searchBox
                    .on('keypress', $.proxy(this.keypress, this))
                    .on('keyup',    $.proxy(this.keyup, this))
                    .on('focus', function(e){view.doSearch(e.target.value);})
                    .on('blur', $.proxy(this.hideonBlur, this));

                if ($.browser.webkit || $.browser.msie) {
                    this.$searchBox.on('keydown', $.proxy(this.keypress, this));
                }


                this.model.on("reset", _.bind(this.onSearchResult, this));
                this.$resultNode = $('<div class="entity-search-result hide"></div>').appendTo(this.$el);
                this.$resultNode.on({'mouseenter' : $.proxy(this.mouseenter, this),
                        'click':_.bind(this.disAmbiguateEvent, this)}, '.search-result-item');
                this.$resultNode.on({'click': _.bind(this.hide, this)}, ".dismiss");
                this.deBouncedSearch = _.debounce(_.bind(this.doSearch, this), 50);
            }
            , prev: function(){
                var curnode = this.$resultNode.find(".active");
                if(curnode.length){
                    curnode.prev().addClass("active").next().removeClass("active");
                }
            }
            , next: function(){
                var curnode = this.$resultNode.find(".active");
                if(curnode.length){
                    curnode.next().addClass("active").prev().removeClass("active");
                } else {
                    this.$resultNode.find(".search-result-item").first().addClass("active");
                }
            }
            , first: function(){
                this.$resultNode.find(".active").removeClass('active');
                this.$resultNode.find(".search-result-item").first().addClass("active");
            }
            , last: function(){
                this.$resultNode.find(".active").removeClass('active');
                this.$resultNode.find(".search-result-item").last().addClass("active");
            }

            , keyup : function(e){
                switch(e.keyCode) {
                    case 40: // down arrow
                    case 38: // up arrow
                        break;
                    case 13: // enter
                        this.disAmbiguateEvent(e);
                        break;
                    case 27: // escape
                        if (!this.shown) {
                            this.$searchBox.blur();
                        } else {
                            this.hide();
                        }
                        break;
                    case 9: // tab
                    case 33:
                        this.first();
                        break;
                    case 34:
                        this.last();
                        break;
                    default:
                        this.deBouncedSearch(e.target.value);
                }
                e.stopPropagation();
                e.preventDefault();
            }

            , keypress: function (e) {
                if (!this.shown) return

                switch(e.keyCode) {
                    case 9: // tab
                        this.hide();
                        break;
                    case 13: // enter
                    case 27: // escape
                        e.preventDefault()
                        break

                    case 38: // up arrow
                        if (e.type != 'keydown') break
                        e.preventDefault()
                        this.prev()
                        break

                    case 40: // down arrow
                        if (e.type != 'keydown') break
                        e.preventDefault()
                        this.next()
                        break
                    case 48: case 49 :case 50 :case 51 :case 52 :case 53 :case 54 :case 55 :case 56 :case 57 :
                    case 96: case 97 :case 98 :case 99 :case 100:case 101:case 102:case 103:case 104:case 105:
                    if(e.ctrlKey||e.metaKey){
                        var number = numberMap[e.keyCode];
                        this.$resultNode.find(".search-result-item.active").removeClass("active");
                        this.$resultNode.find(".search-result-item[shortcut="+number+"]").addClass("active");
                        if(number == 0){
                            this._specialItemSelected();
                        } else {
                            this.disAmbiguateEvent(e);
                        }
                        this.hide();
                        e.stopPropagation();
                        e.preventDefault();
                    }
                    break
                }
                e.stopPropagation()
            }
            , disAmbiguateEvent: function(e){
                var res = this.$resultNode.find(".active")
                    , res = res.length?res:this.$resultNode.find(".search-result-item").first();
                if(e.shiftKey){
                    this._metaSelect(res);
                } else {
                    this._select(res);
                }
            }
            , _specialItemSelected: function(){
                this.trigger("specialItemSelected");
            }
            , _metaSelect: function(item){
                var id = item.attr("data-entity-id"), model = this.model.get(id);
                if(model)this.trigger("metaSelected", model);
            }
            , _select: function(item){
                if(item.hasClass("create-new-entity")){
                    this._specialItemSelected();
                } else {
                    var id = item.attr("data-entity-id"), model = this.model.get(id);
                    if(model)this.trigger("selected", model);
                }
            }
            , buildQuery: function(query){
                return {term:query};
            }
            , doSearch : function(query){
                var view = this, data, data = this.buildQuery(query);
                if(data){
                    ajax.submitPrefixed({url:this.searchUrl
                        , data: data
                        , success: function(resp, status, xhr){
                            if(resp.dbMessage){
                                view.model.reset([]);
                            } else {
                                view.model.reset(view.model.parse(resp));
                            }
                        }});
                } else {
                    view.model.reset([]);
                }
            }
            , onSearchResult: function(collection){
                if(collection){
                    var models = collection.models.slice(0, 9);
                    this.$resultNode.show().html(this.template({models:models, withExtra:!this.suppressExtra, total : collection.models.length}));
                    this.shown = true;
                    this.$el.addClass("expanded");
                }
            }
            , hideonBlur : function(e){
                var view = this;
                setTimeout(function(){
                    view.hide();
                }, 200);
            }
            , hide: function(){
                this.shown = false;
                this.$el.removeClass("expanded");
                this.$resultNode.empty().hide();
                this.trigger("hide");
            }
            , mouseenter: function(e){
                this.$resultNode.find(".active").removeClass("active");
                $(e.target).closest(".search-result-item").addClass("active");
            }
        });
        return AbstractSearch;
});