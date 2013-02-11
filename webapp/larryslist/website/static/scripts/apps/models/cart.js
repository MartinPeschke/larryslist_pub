define(["tools/ajax", "models/collector"], function(ajax, Collector){
    var STORAGE_KEY = 'LS_USER_CART'

    , Collectors = ajax.Collection.extend({
        model:Collector
    })
    , Cart = ajax.Model.extend({
        initialize: function(opts){
            var data = store.get(STORAGE_KEY);
            this.register({'Collectors': new Collectors()});
            if(data)this.setRecursive(data);

            this.listenTo(this, 'Collectors:add', this.persist);
            this.listenTo(this, 'Collectors:remove', this.persist);
        }
        , persist:function(collector){
            store.set(STORAGE_KEY, this.toJSON());
            this.trigger.call(this, "item:changed", collector);
        }
        , addProfile: function(collector){
            this.get("Collectors").add(collector);
        }
        , removeProfile: function(collector){
            this.get("Collectors").remove(collector.id);
        }
        , contains: function(collector){
            return !_.isEmpty(this.get("Collectors").get(collector.id))
        }
        , getItems: function(){
            return this.get("Collectors")||[];
        }
    })

    , cart = new Cart();
    return cart;
});