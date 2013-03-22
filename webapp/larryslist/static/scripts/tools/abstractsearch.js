define(["tools/hash", "tools/ajax", "text!tools/templates/searchresult.html"]
    , function(hashlib, ajax, search_result_template){

        var numberMap = {48:0,  49:1, 50:2, 51:3, 52:4, 53:5, 54:6, 55:7, 56:8, 57:9, 96:0, 97:1, 98:2, 99:3, 100:4, 101:5, 102:6, 103:7, 104:8, 105:9}
        , AbstractSearch = Backbone.View.extend({
            shown : false
            , PAGE_SIZE: 9
            , template:_.template(search_result_template)
            , submitFunc : _.bind(ajax.submitPrefixed, ajax)
            , initialize: function(opts){
                this.id = hashlib.UUID();
                this.template = this.options.template||this.template;
                this.suppressExtra = this.options.suppressExtra;
                this.searchUrl = opts.searchUrl;

                var view = this;
                this.$searchBox = this.$el.find(".query");
                this.$searchBoxC = this.$el.find(".search-field");
                this.$scrollWrap = this.$el.closest(".fixed-height");
                this.$searchBox
                    .on('keydown', $.proxy(this.keypress, this))
                    .on('keyup',    $.proxy(this.keyup, this))
                    .on('focus', function(e){view.doSearch(e.target.value);})
                    .on('blur', $.proxy(this.hideonBlur, this));

                this.model.on("reset", _.bind(this.onSearchResult, this));
                this.$resultNode = $('<div class="entity-search-result hide"></div>').appendTo("body");


                this.$resultNode.on({'mouseenter' : $.proxy(this.mouseenter, this),
                        'click':_.bind(this.disAmbiguateEvent, this)}, '.search-result-item');
                this.$resultNode.on({'click': _.bind(this.hide, this)}, ".dismiss");
                this.deBouncedSearch = _.debounce(_.bind(this.doSearch, this), 50);
            }
            , rePosition: function(){
                var css = this.$searchBoxC.offset();
                css.top = css.top + this.$searchBoxC.height();

                if(this.$scrollWrap.length){
                    var wrap = this.$scrollWrap.offset()
                    if(css.top > this.$scrollWrap.height() + wrap.top || css.top < wrap.top)
                         css.display="none";
                    else css.display="block";
                }
                css.width =  this.$searchBoxC.width();
                this.$resultNode.css(css);
            }
            , prev: function(){
                var curnode = this.$resultNode.find(".active");
                if(curnode.length){
                    curnode.prev().addClass("active").next().removeClass("active");
                } else {
                    this.$resultNode.find(".search-result-item").last().addClass("active");
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
                            this._extraItemSelected();
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
            , _extraItemSelected: function(){
                this.trigger("extraItemSelected", this.$searchBox.val().trim());
            }
            , _metaSelect: function(item){
                var id = item.attr("data-entity-id"), model = this.model.get(id);
                if(model)this.trigger("metaSelected", model);
                else this.trigger("unknownterm:metaSelected", this.$searchBox.val().trim());
            }
            , _select: function(item){
                if(item.hasClass("create-new-entity")){
                    this._extraItemSelected();
                } else {
                    var id = item.attr("data-entity-id"), model = this.model.get(id);
                    if(model)this.trigger("selected", model)
                    else this.trigger("unknownterm:selected", this.$searchBox.val().trim());
                }
            }
            , buildQuery: function(query){
                return query?{term:query}:null;
            }
            , doSearch : function(query){
                var view = this, data = this.buildQuery(query);
                if(data){
                    var queryId = view.queryId = hashlib.UUID();
                    this.$resultNode.html('<div class="loading center"><img src="/static/img/ajax-loader.gif"/></div>');
                    this.submitFunc({url:this.searchUrl
                        , data: data
                        , success: function(resp, status, xhr){
                            if(queryId == view.queryId){
                                if(resp.dbMessage){
                                    view.model.reset([]);
                                } else {
                                    view.model.reset(view.model.parse(resp));
                                }
                            }
                        }});
                } else {
                    view.model.reset([]);
                }
            }
            , onSearchResult: function(collection){
                if(collection){
                    var models = collection.models.slice(0, this.PAGE_SIZE);
                    this.$resultNode.html(this.template({models:models, withExtra:!this.suppressExtra, total : collection.models.length}));
                    this.show();
                }
            }
            , hideonBlur : function(e){
                var view = this;
                // timeout to allow for clickevent to happen to select item
                setTimeout(function(){
                    view.hide();
                }, 200);
            }

            , show: function(){
                this.$resultNode.show();
                this.shown = true;
                this.$el.addClass("expanded");
                this.rePosition();
                if(this.$scrollWrap.length){this.$scrollWrap.on("scroll."+this.id, _.bind(this.rePosition, this));}
                $(window).on("resize."+this.id, _.bind(this.rePosition, this));
                this.trigger("show");
            }
            , hide: function(){
                this.shown = false;
                this.$el.removeClass("expanded");
                this.$resultNode.empty().hide();
                this.$scrollWrap.off("scroll."+this.id);
                $(window).off("resize."+this.id);
                this.trigger("hide");
            }
            , mouseenter: function(e){
                this.$resultNode.find(".active").removeClass("active");
                $(e.target).closest(".search-result-item").addClass("active");
            }
        });
        return AbstractSearch;
});