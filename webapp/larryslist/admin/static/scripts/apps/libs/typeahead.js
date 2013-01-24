define(["tools/ajax"], function(ajax){
    var Result = ajax.Model.extend({idAttribute:'token'})
    , ResultCollection = ajax.Collection.extend({model:Result, idAttribute:'token'})
    , ResultView = Backbone.View.extend({
        template: _.template('{{ model.get("name") }}')
        , tagName : "div"
        , classname: 'single-result'
        , events :{"click":"onSelected"}
        , initialize: function(){
            this.$el.html(this.template({model:this.model}));
            this.model.on("destroy", this.remove, this);
        }
        , remove: function(){
            this.$el.off().remove();
        }
        , render: function(){
            return this.$el;
        }
        , onSelected: function(){
            this.model.trigger("selected", this.model);
        }
    })
    , View = Backbone.View.extend({
        events: {
            "keyup .typeahead": "onKeyUp"
        }
        , template: '<div class="typeahead-result hide"><div class="typeahead-result-inner"></div></div>'
        , initialize: function(opts){
            this.url = this.$(".typeahead").data("apiUrl");
            this.type = this.$(".typeahead").data("apiType");
            this.$results = this.$el.append(this.template).find(".typeahead-result-inner");
            this.model = new ResultCollection();
            this.model.on("add", this.addOne, this);
            this.model.on("selected", this.onSelected, this);
        }
        , addOne: function(model){
            this.$results.append((new ResultView({model:model})).render());
        }
        , onKeyUp: function(e){
            var view = this;
            ajax.submitPrefixed({
                url: this.url
                , data: {'type':this.type, term: e.target.value}
                , success: function(resp, xhr, status){
                    view.toggle(resp.AddressSearchResult.length>0);
                    view.model.addOrUpdate(resp.AddressSearchResult,{preserve: false});
                }
            })
        }
        , toggle: function(show){
            this.$(".typeahead-result")[show?'removeClass':'addClass']("hide");
        }
        , onSelected: function(model){
            this.$("input[type=text]").val(model.get("name"));
            this.$("input[type=hidden]").val(model.id);
            this.toggle(false);
        }
    });
    return View;
});