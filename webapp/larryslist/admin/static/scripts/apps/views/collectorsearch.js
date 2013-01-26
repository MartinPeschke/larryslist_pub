define(["tools/ajax", "libs/abstractsearch"], function(ajax, AbstractSearch){
    var
        getRec = hnc.getRecursive
        , Collector = ajax.Model.extend({
            getName: function(){
                return this.get("firstName") +" " + this.get("lastName");
            }
            , getSearchLabel: function(){
                var location = this.get("Address");
                if(location && location.length)
                    return this.getName() + ' ('+location[0].City.name+'/'+location[0].Country.name+')';
                else
                    return this.getName();
            }
        })
        , SearchResult = ajax.Collection.extend({
            model : Collector
            , parse: function(resp) {
                return getRec(resp, "Collectors.Collector", []);
            }
        })

        , init = function(el, createUrl, editUrlTempl){

            var editUrl = _.template(editUrlTempl)
            , search = new AbstractSearch({el:el, model: new SearchResult(), searchUrl: "/admin/search/collector"})
            , onSpecialSelected = function(){
                window.location.href = createUrl;
                search.hide();
                search.$searchBox.blur();
            }
            , onSelected = function(collector){
                var id = collector.id;
                window.location.href = editUrl({model:collector});
                search.hide();
                search.$searchBox.val(collector.getSearchLabel()).blur();
            };
            search.on("selected", onSelected, this);
            search.on("specialItemSelected", onSpecialSelected, this);
        };
    return init;
});