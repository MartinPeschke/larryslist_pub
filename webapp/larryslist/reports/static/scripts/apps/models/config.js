define(["tools/ajax"], function(ajax){
    var
        Duration = ajax.Model.extend({
            getKey: function(){return this.get("name")}
            , getName: function(){
                var name = hnc.translate(this.get("name")).split(" "), val = name[0];
                name = name[1];
                return '<em>'+val+'</em>'+name;
            }
        })
        , Intensity = ajax.Model.extend({
            getKey: function(){return this.get("name")}
            , getName: function(){
                var name = hnc.translate(this.get("name")).split(" "), val = name[0];
                name = name[1];
                return '<em>'+val+'</em>'+name;
            }
        })
        , Segment = ajax.Model.extend({
            idAttribute: 'surKey'
            , parseLocal: function(data){
                data.surKey = data.clusterId +"_" + data.goalDetailToken;
                return data;
            }
            , assign: function(assigned, vsId){
                if(assigned && this.get("assigned")){
                    this.trigger("reassigned", this, vsId);
                } else {
                    this.set({assigned:assigned});
                }
            }
            , getDetailName: function(){
                return this.get("goalDetailName")
            }
            , getClusterName: function(){
                return this.get("clusterName")
            }
            , getKey: function(){return this.get("goalDetailName")}
            , getName: function(){
                return this.get("goalDetailName")
            }
        })
        , Durations = ajax.Collection.extend({model: Duration})
        , Intensitys = ajax.Collection.extend({model: Intensity})
        , Segments = ajax.Collection.extend({model: Segment})
        , Goal = ajax.Model.extend({
            idAttribute: "type"
            , initialize:function(opts){
                this.register({"Duration" : new Durations(), "Intensity": new Intensitys(), "Segment": new Segments()});
            }
            , getKey: function(){return this.get("type")}
            , getName: function(){
                return hnc.translate(this.get("type"))
            }
        })
        , Goals = ajax.Collection.extend({model: Goal})
        , Challenge = ajax.Model.extend({
            getName: function(){
                return hnc.translate(this.get("name"))
            }
        })
        , Challenges = ajax.Collection.extend({model: Challenge})
        , Config = ajax.Model.extend({
            loaded : false
            , loading : false
            , initialize:function(opts){
                this.register({Goal : new Goals(), Challenge: new Challenges()});
                this.load();
            }
            , stale: function(){
                return ((new Date()).getTime() - this._timestamp) > 86400000;
            }
            , getConfig: function(callback, context){
                if(!this.loading && (!this.loaded || this.stale()))this.load();
                if(!this.loaded)
                    this.on("reload", callback, context);
                else
                    callback.apply(context, [this]);
            }
            , load: function(){
                var model = this;
                model.loading = true;
                ajax.submitPrefixed({url:"/admin/config", method:"POST", success:function(resp, status, xhr){
                    model.setRecursive(resp.Config);
                    model.loaded = true;
                    model.loading = false;
                    model._timestamp = (new Date()).getTime();
                    model.trigger("reload", model);
                }});
            }
        })
        , config = new Config();
    return config;
});